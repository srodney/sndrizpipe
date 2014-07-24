#! /usr/bin/env python
# S.Rodney
# 2014.03.04
"""Process a set of flt files to produce wcs- and pixel-registered
images across all filters and epochs, following the Drizzlepac
tweakreg/astrodrizzle/tweakback registration sequence as described in
section 7.5 of the drizzlepac handbook:

- Sort the flts by epoch, visit and filter
- [ Use tweakreg for intra-visit alignment ]
- Use astrodrizzle to combine each single-visit set into a drz_sci.fits product
- Define a wcs reference frame using one of the images
- Improve the wcs-alignment between all single-visit drizzled images and the ref image, using tweakreg.
- Using tweakback, propagate the new tweaked solutions back to the original flt.fits images.
- Drizzle-combine the updated flt.fits images to make single-epoch, single-filter registered drz products.
- Subtract a template epoch.

"""

import glob
import exceptions
import os
import register, exposures, drizzle, badpix, imarith
import numpy as np
import stat

# file permissions for chmod ug+rw o+r
PERMISSIONS = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH

def multipipe() : 
    """ 
    Run the pipeline for all <rootname>.flt directories found
    within the current directory
    """
    # TODO : use parallel processing
    # look for flt/flc files in directories called flt.<rootname>
    fltdirlist = glob.glob("*.flt")
    if not len(fltdirlist) : 
        exceptions.RuntimeError( "There is no <rootname>.flt directory!")
        for fltdir in fltdirlist : 
            runpipe( fltdir )



# TODO : write a log file, recording user settings and results
def runpipe( outroot, onlyfilters=[], onlyepochs=[],
              # Run all the processing steps
              doall=False,
              # Setup : copy flts into sub-directories
              dosetup=False, epochlistfile=None,
              # construct a ref image
              dorefim=False,
              # Single Visit tweakreg/drizzle pass : 
              dodriz1=False, drizcr=1, intravisitreg=False,
              # Register to a given image or  epoch, visit and filter
              doreg=False, singlestar=False,
              refim=None, refepoch=None, refvisit=None, reffilter=None,
              # Drizzle registered flts by epoch and filter
              dodriz2=False, singlesci=False,
              # make diff images
              dodiff=False, tempepoch=0, tempfilters=None, singlesubs=False,
              # make multi-epoch stack images
              dostack=False,
              # source detection and matching
              interactive=False, threshold=5, nbright=None,
              peakmin=None, peakmax=None, # fluxmin=None, fluxmax=None,
              searchrad=1.5, minobj=10, mjdmin=0, mjdmax=0, epochspan=5,
              refcat=None, rfluxmax=None, rfluxmin=None, refnbright=None,
              nclip=3, sigmaclip=3.0,
              shiftonly=False, ra=None, dec=None, rot=0, imsize_arcsec=None,
              pixscale=None, pixfrac=None, wht_type='IVM',
              stackepochs=None, stacktemplate=False,
              stackpixscale=None, stackpixfrac=None,
              clean=False, clobber=False, verbose=True, debug=False ):
    """ 
    Primary pipeline function.  Executes all the intermediate steps: 
       register, sort, drizzle, subtract, mask
    """
    import pyfits
    import shutil
    if debug : import pdb; pdb.set_trace()
    from drizzlepac.tweakback import tweakback
    from pseudodiff import mkscaledtemplate, camfiltername

    # Check for logically incompatible parameters
    if nbright and minobj and (nbright < minobj-1) :
        raise exceptions.RuntimeError(
            ' nbright < minobj \n'
            'You have nbright=%i and minobj=%i\n'%(nbright,minobj) +
            "That doesn't work." )
    if shiftonly : fitgeometry='shift'
    else : fitgeometry = 'rscale'
    if fitgeometry=='rscale' and ((nbright and nbright<3) or minobj<3):
        raise exceptions.RuntimeError(
            ' Not requiring enough stars for rotation+scale fit.\n'
            'You have nbright=%i and minobj=%i\n'%(nbright,minobj) +
            "and you also have fitgeometry='rscale'."
            "Try again with --shiftonly" )
    if onlyfilters :
        if type(onlyfilters)==str :
            onlyfilters = onlyfilters.lower().split(',')
        onlyfilters = [ filt[:5].lower() for filt in onlyfilters ]
    if type(onlyepochs) in [str,int,float] :
        onlyepochs = [ int(ep) for ep in str(onlyepochs).split(',') ]
    if tempfilters is not None and len(onlyfilters) != 1 :
        raise exceptions.RuntimeError(
            'You specified filter(s) to combine/scale for the template epoch'
            'but you did not limit the processing to a single filter.'
            "If you use --tempfilters then you must also specify a "
            "single filter for processing with '--filters X'")
    if singlestar and ((ra is None) or (dec is None)) :
        raise exceptions.RuntimeError(
            'If you set the --singlestar flag for processing a single '
            '(standard) star then you MUST also provide a target RA and '
            'DEC with the --ra and --dec options.' )

    topdir = os.path.abspath( '.' )
    fltdir = outroot + '.flt' 

    if doall :
        dosetup=True
        dorefim=True
        dodriz1=True
        doreg=True
        dodriz2=True
        dodiff=True
        dostack=True

    # For single-star registrations, set some useful defaults when the user doesn't
    if singlestar :
        if not searchrad : searchrad=10
        if threshold>0.5 : threshold=0.5 # this becomes threshmin, so we only allow the user to decrease from 0.5
        if wht_type=='ERR' :
            print("WARNING :forcing the final_wht_type to EXP instead of ERR"
                  ' (best for bright sources dominated by poisson noise)' )
            wht_type = 'EXP'  #
        if drizcr==1 :
            print("WARNING :forcing a re-run of driz_cr for multi-visit stacks"
                  ' (important to to avoid suppressing flux in bright stars)' )
            drizcr = 2  #

    # STAGE 0 : (always runs)
    # get a list of exposures and epochs, sorting flt files into epochs
    if not epochlistfile :
        epochlistfile =  "%s_epochs.txt"%outroot
    fltlist = glob.glob( "%s/*fl?.fits"%fltdir )
    if not len( fltlist ) :
        raise( exceptions.RuntimeError( "There are no flt/flc files in %s !!"%fltdir) )

    if os.path.exists( epochlistfile ) :
        if verbose: print( "%s exists. Adopting existing exposure list and epoch sorting."%epochlistfile )
        explist_all = exposures.read_explist( epochlistfile )
        exposures.print_epochs( explist_all, outfile=None,
                                verbose=verbose, clobber=False,
                                onlyfilters=None, onlyepochs=None )
    else :
        if verbose: print( "Generating exposure list and epoch sorting from %s/*fl?.fits."%fltdir )
        explist_all = exposures.get_explist( fltlist, outroot=outroot, targetradec=[ra,dec])
        exposures.define_epochs( explist_all, epochspan=epochspan,
                                 mjdmin=mjdmin, mjdmax=mjdmax )
        exposures.print_epochs( explist_all, outfile=epochlistfile,
                                verbose=verbose, clobber=False,
                                onlyfilters=None, onlyepochs=None )
    if len(explist_all) < len(fltlist) :
        print("New flt files detected in %s."%fltdir )
        if not clobber :
            print( "Turn on --clobber to rewrite the epochs list %s"%(epochlistfile))
        else :
            print("Updating %s with new flt files detected in %s"%(epochlistfile,fltdir))
            explist_all = exposures.update_epochs( explist_all, fltlist, epochspan=epochspan,
                                                   mjdmin=mjdmin, mjdmax=mjdmax )
            exposures.print_epochs( explist_all, outfile=epochlistfile,
                                    verbose=verbose, clobber=clobber,
                                    onlyfilters=None, onlyepochs=None )

    if refim and not os.path.exists( refim ) :
        raise exceptions.RuntimeError( 'Ref image %s does not exist.'%refim )
    if not refim :
        # No refimage has been specified, so set the default refimage name
        refdrzdir = '%s.refim'%outroot
        refimbasename = '%s_wcsref_drz_sci.fits'%(outroot)
        refim = os.path.abspath( os.path.join( refdrzdir, refimbasename ) )
        if os.path.exists( refim.replace('_drz_sci','_drc_sci') ):
            refim = refim.replace('_drz_sci','_drc_sci')

    if refcat : refcat = os.path.abspath(refcat)

    # reduce the working exposure list to contain only those exposures
    # that we actually want to process
    explist = []
    for exp in explist_all:
        if exp.epoch<0 or not exp.ontarget :
            continue
        if onlyfilters and exp.filter not in onlyfilters :
            continue
        elif onlyepochs and exp.epoch not in onlyepochs :
            continue
        else:
            explist.append( exp )

    # STAGE 1 :
    # copy pristine flt files into epoch sub-directories
    if dosetup :
        if verbose :
            print("sndrizpipe : (1) SETUP : copying flt files into subdirs")
        exposures.copy_to_epochdirs( explist,
                              onlyfilters=onlyfilters, onlyepochs=onlyepochs,
                              verbose=verbose, clobber=clobber )

    FEVgrouplist = sorted( np.unique( [ exp.FEVgroup for exp in explist ] ) )
    FEgrouplist = sorted( np.unique( [ exp.FEgroup for exp in explist ] ) )
    filterlist = sorted( np.unique( [ exp.filter for exp in explist ] ) )
    epochlist = sorted( np.unique([ exp.epoch for exp in explist ] ) )

    # STAGE 2 :
    # Construct the WCS reference image
    if dorefim and not singlestar :
        refimclobber = clobber and (reffilter or refepoch or refvisit)
        if verbose :
            print("sndrizpipe : (2) REFIM : Constructing WCS ref image.")
        if os.path.exists( refim ) and refimclobber :
            os.remove( refim )
        if os.path.exists( refim ) :
            print("%s already exists.  Not clobbering."%refim)
            if clobber :
                print("To clobber and remake the ref image, you must provide "
                      "at least one of --reffilter, --refepoch, --refvisit")
        else :
            refdrzdir = os.path.dirname( refim )
            if verbose :
                print( " Constructing reference image %s in %s"%(
                    os.path.basename(refim), refdrzdir ) )

            # Collect the necessary flt files for constructing the ref image
            if not refepoch :
                refepoch = np.min( epochlist )
            if not reffilter :
                reffilter = sorted( [ exp.filter for exp in explist
                                      if exp.epoch==refepoch ] )[0]
            reffilter = reffilter.lower()
            
            # if refvisit is not set, then use the visit with the most exposures
            if not refvisit :
                #visits, exp_times, visit_depth = np.array( ([], [], []) )
                explistRIvisfind = [ exp for exp in explist_all
                        if (exp.epoch==refepoch and exp.filter==reffilter) ]
                pidvisits = [exp.pidvisit for exp in explistRIvisfind ]
                unique_visits = np.unique( pidvisits )
                if len(unique_visits)==1:
                    refvisit = unique_visits[0]
                elif len(unique_visits)<1:
                    raise exceptions.RuntimeError(
                        "No visits satisfy the refimage requirements:\n"+\
                        "  filter = %s     epoch = %s"%(reffilter,refepoch) )
                else :
                    Nexp_per_visit = [ len(np.where(np.char.equal(pidvisits,vis))[0])
                                       for vis in unique_visits ]
                    ideepest  = np.argmax( Nexp_per_visit )
                    refvisit = unique_visits[ideepest]
            refvisit = refvisit.upper()
            if refvisit.find('.') > 0 :
                refvisit = refvisit.replace('.','_')
            
            explistRI = sorted( [ exp for exp in explist_all if exp.epoch==refepoch
                                  and exp.filter==reffilter and exp.pidvisit==refvisit ] )
            if len(explistRI)<1 :
                raise exceptions.RuntimeError(
                    "Error : not enough exposures for refim with"
                    "epoch %i  ;  filter %s  ;  visit %s  "%(
                        refepoch, reffilter, refvisit ) )
            refdrzdir = os.path.dirname( refim )
            if not os.path.isdir( refdrzdir ) :
                os.makedirs( refdrzdir )
            for exp in explistRI :
                fltfile = os.path.basename( exp.filename )
                refsrcdir = os.path.abspath( fltdir )
                shutil.copy( os.path.join( refsrcdir, fltfile ), refdrzdir )
                os.chmod( os.path.join(refdrzdir,fltfile), PERMISSIONS )
            fltlistRI = [ exp.filename for exp in explistRI ]

            refimbasename = os.path.basename( refim )
            drzpt = max( refimbasename.find('_drz_sci.fits'),refimbasename.find('_drc_sci.fits') )
            refimroot = refimbasename[:drzpt]
            os.chdir( refdrzdir )

            # drizzle the ref image using firstDrizzle :
            # (full frame, native rotation, auto-selecting the optimal
            # pixscale and pixfrac based on number of flts)
            refdrzsci, refimwht = drizzle.firstDrizzle(
                fltlistRI, refimroot, driz_cr=drizcr, clean=clean )
            refim = os.path.join( os.path.abspath(refdrzdir),os.path.basename(refdrzsci) )

            if refcat :
                # Update the WCS header info in the ref image to match the
                # given reference catalog
                if verbose : print( " Registering reference image"
                                    "%s to ref catalog %s"%(refdrzsci, refcat))
                wcsname = register.RunTweakReg(
                    refdrzsci, refim=refim, refcat=refcat,
                    wcsname='REFCAT:%s'%os.path.basename(refcat),
                    searchrad=searchrad,
                    refnbright=refnbright, rfluxmax=rfluxmax,
                    rfluxmin=rfluxmin, peakmin=peakmin, peakmax=peakmax,
                    # fluxmin=fluxmin, fluxmax=fluxmax,
                    fitgeometry=fitgeometry,
                    threshold=threshold, minobj=minobj,
                    nbright=nbright, nclip=nclip, sigmaclip=sigmaclip,
                    clean=clean, verbose=verbose,
                    interactive=interactive, clobber=clobber, debug=debug )

            if clean :
                for fltfile in fltlistRI :
                    if os.path.isfile( fltfile ) :
                        os.remove( fltfile )
                    if os.path.isfile( 'OrIg_files/%s'%fltfile) :
                        os.remove( 'OrIg_files/%s'%fltfile)
                if os.path.isdir( 'OrIg_files') :
                    os.rmdir( 'OrIg_files')
                refimwht = refdrzsci.replace('sci.fits','wht.fits')
                if os.path.isfile( refimwht ) :
                    os.remove( refimwht )
                refimctx = refdrzsci.replace('sci.fits','ctx.fits')
                if os.path.isfile( refimctx ) :
                    os.remove( refimctx )

            os.chdir(topdir)

    # If refnbright was provided, then we must make an RA,Dec reference
    # catalog when one does not already exist
    if refnbright and not refcat and not singlestar :
        assert( os.path.exists( refim ) )
        refdrzdir = os.path.dirname( refim )
        os.chdir( refdrzdir)
        refcatfile = register.mkSourceCatalog(
            os.path.basename(refim), threshold=threshold,
            peakmin=peakmin, peakmax=peakmax )[0]
        os.chdir( topdir )
        refcat = os.path.abspath( os.path.join( refdrzdir, refcatfile ) )

    # STAGE 3 :
    # Drizzle together each drizzle group (same epoch, visit and
    # filter), using almost-default parameters, doing CR rejection
    # and applying intravisit registrations if requested.  The output
    # is a drz_sci.fits file in the native rotation.
    if dodriz1 :
        if verbose :
            print("sndrizpipe : (3) DRIZ1 : first astrodrizzle pass.")
        for FEVgroup in FEVgrouplist :
            explistFEV = [ exp for exp in explist if exp.FEVgroup == FEVgroup ]
            thisepoch = explistFEV[0].epoch
            thisfilter = explistFEV[0].filter
            if onlyepochs and thisepoch not in onlyepochs : continue
            if onlyfilters and thisfilter not in onlyfilters : continue

            epochdir = explistFEV[0].epochdir
            fltlistFEV = [ exp.filename for exp in explistFEV ] 
            outrootFEV = '%s_%s_nat'%(outroot,FEVgroup)

            os.chdir( epochdir )
            outsciFEV = '%s_%s_sci.fits'%(outrootFEV,explistFEV[0].drzsuffix)
            if os.path.exists( outsciFEV ) and clobber : 
                os.remove( outsciFEV )
            if os.path.exists( outsciFEV ) :
                if verbose: print("%s exists.  Not clobbering."%outsciFEV )
                os.chdir( topdir )
                continue
            if intravisitreg : 
                # run tweakreg for intravisit registration tweaks
                wcsname = register.RunTweakReg(
                    fltlistFEV, wcsname='INTRAVIS', refcat=refcat,
                    searchrad=searchrad, threshold=threshold, minobj=minobj,
                    peakmin=peakmin, peakmax=peakmax,
                    # fluxmin=fluxmin, fluxmax=fluxmax,
                    fitgeometry=fitgeometry, nbright=nbright, clean=clean,
                    refnbright=refnbright, nclip=nclip, sigmaclip=sigmaclip,
                    rfluxmin=rfluxmin, rfluxmax=rfluxmax,
                    verbose=verbose, interactive=interactive, clobber=clobber, debug=debug )
            drizzle.firstDrizzle(
                fltlistFEV, outrootFEV, driz_cr=drizcr,
                wcskey=((intravisitreg and 'INTRAVIS') or ''),
                clobber=clobber, verbose=verbose, clean=clean )
            os.chdir( topdir )
            continue

    # STAGE 4 :
    # Run tweakreg to register all the single-visit drz images
    # to a common WCS defined by the refcat/refim, updating the drz file headers.
    # Then use tweakback to propagate that back into the flt files
    if doreg :
        if verbose :
            print("sndrizpipe : (4) REG : registering images.")

        if not singlestar :
            refim = os.path.abspath( refim )
            if not os.path.exists( refim ):
                raise exceptions.RuntimeError("No refim file %s!  Maybe you should re-run with dorefim=True."%refim)

            # Fix the output  ra and dec center point if not provided by the user.
            if not ra and not dec :
                ra = pyfits.getval( refim, "CRVAL1" )
                dec = pyfits.getval( refim, "CRVAL2" )

        for FEVgroup in FEVgrouplist :
            explistFEV = [ exp for exp in explist if exp.FEVgroup == FEVgroup ]
            thisepoch = explistFEV[0].epoch
            thisfilter = explistFEV[0].filter
            if onlyepochs and thisepoch not in onlyepochs : continue
            if onlyfilters and thisfilter not in onlyfilters : continue

            epochdir = explistFEV[0].epochdir
            fltlistFEV = [ exp.filename for exp in explistFEV ] 
            outrootFEV = '%s_%s_nat'%(outroot,FEVgroup)
            outsciFEV = '%s_%s_sci.fits'%(outrootFEV,explistFEV[0].drzsuffix)

            os.chdir( epochdir )

            if not os.path.exists( outsciFEV ) :
                exceptions.RuntimeError( "Missing %s."%outsciFEV )
            origwcs = pyfits.getval( outsciFEV,'WCSNAME').strip()

            if singlestar :
                # Special case for handling standard star images:
                wcsname=register.SingleStarReg( outsciFEV, ra, dec,
                                                refim=None, threshmin=threshold,
                                                peakmin=peakmin, peakmax=peakmax,
                                                wcsname='SINGLESTAR:%.6f,%.6f'%(ra,dec),
                                                verbose=verbose )

            else :
                # register to the ref image and ref catalog
                wcsname = register.RunTweakReg(
                    outsciFEV, wcsname='REFIM:%s'%os.path.basename(refim),
                    refim=refim, refcat=refcat,
                    searchrad=searchrad, threshold=threshold, minobj=minobj,
                    peakmin=peakmin, peakmax=peakmax,
                    # fluxmin=fluxmin, fluxmax=fluxmax,
                    fitgeometry=fitgeometry, nbright=nbright, clean=clean,
                    refnbright=refnbright, rfluxmin=rfluxmin, rfluxmax=rfluxmax,
                    nclip=nclip, sigmaclip=sigmaclip,
                    verbose=verbose,interactive=interactive, clobber=clobber, debug=debug )

            # Run tweakback to update the constituent flts
            tweakback( outsciFEV, input=fltlistFEV, origwcs=origwcs,
                       wcsname=wcsname, verbose=verbose, force=clobber )
            os.chdir(topdir)
              

    # STAGE 5
    # Second astrodrizzle pass, wherein we rerun
    # astrodrizzle to get wcs- and pixel-registered drz images
    # combining all flt files with the same filter and epoch.
    if dodriz2 :
        if verbose :
            print("sndrizpipe : (5) DRIZ2 : second astrodrizzle pass.")
        for FEgroup in FEgrouplist :
            explistFE = [ exp for exp in explist if exp.FEgroup == FEgroup ]
            thisepoch = explistFE[0].epoch
            thisfilter = explistFE[0].filter
            if onlyepochs and thisepoch not in onlyepochs : continue
            if onlyfilters and thisfilter not in onlyfilters : continue

            epochdir = explistFE[0].epochdir
            fltlistFE = [ exp.filename for exp in explistFE ] 
            outrootFE = '%s_%s_reg'%(outroot,FEgroup)

            err = None
            os.chdir( epochdir )
            outsciFE = '%s_%s_sci.fits'%(outrootFE,explistFE[0].drzsuffix)
            if os.path.exists( outsciFE ) and clobber : 
                os.remove( outsciFE )
            if os.path.exists( outsciFE ) :
                if verbose: print("%s exists.  Not clobbering."%outsciFE )
                os.chdir( topdir )
                continue

            # use imedian combination for bright stars (where high poisson noise
            # leads to flux suppression for iminmed) and for cases where we
            # have a large number of input flts.  Otherwise, iminmed is safer
            # and does not introduce a bias.
            combine_type='iminmed'
            if singlestar or len(fltlistFE)>7:
                combine_type='imedian'

            outscilist, outwhtlist, outbpxlist = drizzle.secondDrizzle(
                fltlistFE, outrootFE, refimage=None, ra=ra, dec=dec, rot=rot,
                imsize_arcsec=imsize_arcsec, wht_type=wht_type,
                pixscale=pixscale, pixfrac=pixfrac,
                combine_type=combine_type, driz_cr=(drizcr>1),
                singlesci=(singlesubs or singlesci), clean=clean,
                clobber=clobber, verbose=verbose, debug=debug )

            os.chdir( topdir )


    # STAGE 6
    # Define a template epoch for each filter and subtract it from the other epochs
    if dodiff :
        if verbose :
            print("sndrizpipe : (6) DIFF : subtracting template images.")
        for filter in filterlist :
            if onlyfilters and filter not in onlyfilters : continue
            topdir = os.path.abspath( '.' )
            for epoch in epochlist :
                if onlyepochs and epoch not in onlyepochs : continue
                if epoch == tempepoch : continue
                explistFE = [ exp for exp in explist if exp.filter==filter and exp.epoch==epoch ]
                if len(explistFE)==0 : continue
                epochdirFE = explistFE[0].epochdir
                outrootFE =  "%s_%s"%(outroot,explistFE[0].FEgroup)
                drzsuffix = explistFE[0].drzsuffix
                regsci = "%s_reg_%s_sci.fits"%(outrootFE,drzsuffix)

                os.chdir( epochdirFE )
                if not os.path.isfile( regsci ) :
                    os.chdir( topdir ) 
                    continue

                # Locate and/or construct templates
                tempdir = os.path.join( os.path.abspath(topdir), outroot+'.e%02i'%tempepoch )
                if tempfilters is not None :
                    tempsci = os.path.join( tempdir, '%s_~%s_e%02i_reg_%s_sci.fits'%(outroot,filter,tempepoch,drzsuffix))
                else :
                    tempsci = os.path.join( tempdir, '%s_%s_e%02i_reg_%s_sci.fits'%(outroot,filter,tempepoch,drzsuffix))
                if tempfilters and not os.path.exists( tempsci ) :
                    # Combine multiple filters from the template epoch
                    # to make a pseudo-template with ~filtername in the filename.
                    tempfilter1 = tempfilters.split(',')[0]
                    tempsci1 = os.path.join( tempdir, '%s_%s_e%02i_reg_%s_sci.fits'%(outroot,tempfilter1,tempepoch,drzsuffix))
                    if ',' in tempfilters :
                        tempfilter2 = tempfilters.split(',')[1]
                        tempsci2 = os.path.join( tempdir, '%s_%s_e%02i_reg_%s_sci.fits'%(outroot,tempfilter2,tempepoch,drzsuffix))
                    else :
                        tempfilter2, tempsci2 = None, None
                    targetfilter = camfiltername( regsci )
                    tempsci, tempwht, tempbpx = mkscaledtemplate(
                        targetfilter, tempsci1, tempsci2, outfile=tempsci,
                        filtdir='HSTFILTERS', verbose=verbose, clobber=clobber )
                tempwht = tempsci.replace('sci.fits','wht.fits')
                tempbpx = tempsci.replace('sci.fits','bpx.fits')

                regscilist = [regsci]
                subscilist = [ outrootFE + "-e%02i_sub_sci.fits"%tempepoch ]

                if singlesubs or singlesci:
                    for exp in explistFE :
                        singlesci = '%s_reg_%s_single_sci.fits'%( outrootFE, exp.rootname )
                        subsci = '%s-e%02i_%s_single_sub_sci.fits'%( outrootFE, tempepoch, exp.rootname )
                        regscilist.append( singlesci )
                        subscilist.append( subsci )
                for regsci, subsci in zip( regscilist, subscilist ):
                    if not os.path.isfile( tempsci ) or not os.path.isfile( regsci) :
                        print( "Can't create diff image %s"%subsci )
                        print( "  missing either  %s"%tempsci )
                        print( "    or  %s"%regsci )
                        continue

                    regwht = regsci.replace( '_sci.fits','_wht.fits')
                    regbpx = regsci.replace( '_sci.fits','_bpx.fits')

                    diffim = imarith.imsubtract( tempsci, regsci, outfile=subsci,
                                                  clobber=clobber, verbose=verbose, debug=debug)
                    diffwht = imarith.combine_ivm_maps( regwht, tempwht,
                                                       diffim.replace('sci.fits','wht.fits'),
                                                       clobber=clobber, verbose=verbose )
                    diffbpx = badpix.unionmask( tempbpx, regbpx,
                                         diffim.replace('sci.fits','bpx.fits'),
                                         clobber=clobber, verbose=verbose)
                    diffim_masked = badpix.applymask( diffim, diffbpx,
                                                     clobber=clobber, verbose=verbose)
                    if clean :
                        # delete the sub_sci.fits, b/c it is superseded
                        os.remove( diffim )
                    print("Created diff image %s, wht map %s, and bpx mask %s"%(
                        diffim_masked, diffwht, diffbpx ) )
                os.chdir( topdir )
            pass # end for epoch in epochlist
        pass # end for filter in filterlist

    # STAGE 7
    # Drizzle together all specified non-template epochs into a single stack
    # e.g. for use in defining the source position
    if dostack :
        if verbose :
            print("sndrizpipe : (7) STACK : stack together source images.")
        topdir = os.path.abspath( '.' )
        stackdir = '%s.stack'%outroot
        if stackepochs is not None :
            if type(stackepochs) in [str,int,float] :
                stackepochs = [int(ep) for ep in str(stackepochs).split(',')]
            if tempepoch in stackepochs : stacktemplate=True
        else :
            stackepochs = onlyepochs
        if not os.path.isdir( stackdir ):
            os.mkdir( stackdir )
        for filter in filterlist :
            if onlyfilters and filter not in onlyfilters : continue
            fltlistStack = []
            for epoch in epochlist :
                if stackepochs and epoch not in stackepochs : continue
                if epoch == tempepoch and not stacktemplate : continue
                explistFE = [ exp for exp in explist if exp.filter==filter and exp.epoch==epoch ]
                if len(explistFE)==0 : continue
                epochdirFE = explistFE[0].epochdir
                fltlistStack += [ os.path.join(epochdirFE,exp.filename) for exp in explistFE ]

            if len(fltlistStack)==0 :
                print( "Cannot create a stack for filter %s : no non-template images available."%filter)
                if verbose :
                    print( "Use --stacktemplate to allow template images to be included, or specify")
                    print( "particular epochs with --stackepochs X,Y,Z" )
                continue

            for flt in fltlistStack :
                if not os.path.exists( os.path.join(stackdir, os.path.basename(flt))) :
                    shutil.copy( flt, stackdir )
            fltlistStack = [ os.path.basename( flt ) for flt in fltlistStack ]
            outrootStack = outroot + '_%s_stack'%filter.lower()
            outsciStack = os.path.join( stackdir, outrootStack+'_drz_sci.fits')
            if os.path.isfile( outsciStack ) :
                print(" Stacked image %s already exists "% outsciStack )
                if not clobber :
                    print(" Not clobbering. ")
                    continue
            if verbose :
                if stackepochs : epochstr = ','.join( [ str(ep) for ep in stackepochs ] ).rstrip(',')
                else : epochstr = 'ALL'
                print(" Constructing stacked image %s_drz_sci.fits from epochs %s"%(
                    outrootStack,epochstr) )

            # set the combine type carefully, as above for the driz2 stage.
            combine_type='iminmed'
            if singlestar or len(fltlistStack)>7:
                combine_type='imedian'

            if stackpixscale is None : stackpixscale = pixscale
            if stackpixfrac is None : stackpixfrac = pixfrac
            os.chdir( stackdir )
            outscilist, outwhtlist, outbpxlist = drizzle.secondDrizzle(
                fltlistStack, outrootStack,
                refimage=None, ra=ra, dec=dec, rot=rot,
                imsize_arcsec=imsize_arcsec, wht_type=wht_type,
                pixscale=stackpixscale, pixfrac=stackpixfrac, driz_cr=drizcr,
                singlesci=False, clean=clean, combine_type=combine_type,
                clobber=clobber, verbose=verbose, debug=debug )
            os.chdir( topdir )
            pass # end for filter in filterlist

    if clean > 1 :
        topdir = os.path.abspath( '.' )
        if verbose :
            print("sndrizpipe : (7) CLEAN level 2 : remove OrIg flt files.")
            if clean>2: print("Clean level 3 : remove last-drizzle flt files")
        for filter in filterlist :
            if onlyfilters and filter not in onlyfilters : continue
            for epoch in epochlist :
                if onlyepochs and epoch not in onlyepochs : continue
                explistFE = [ exp for exp in explist if exp.filter==filter and exp.epoch==epoch ]
                if len(explistFE) == 0 : continue
                epochdirFE = explistFE[0].epochdir
                if not os.path.isdir( epochdirFE ) : continue
                os.chdir( epochdirFE )
                for exp in explistFE :
                    fltfile = exp.filename
                    fltfileOrIg = os.path.join('OrIg_files',fltfile)
                    if os.path.isfile( fltfileOrIg ) :
                        os.remove( fltfileOrIg )
                    if clean>2 and os.path.isfile( fltfile ) :
                        os.remove( fltfile )
                os.chdir( topdir )

    if clean > 3 :
        if verbose :
            print("Clean level 4 : remove single-visit 'nat' drizzle and tweakreg products")
            if clean > 4 :
                print("Clean level 5 : remove all temporary files (race condition possible when processing multiple filters in the same epoch simultaneously)")
        for FEVgroup in FEVgrouplist :
            explistFEV = [ exp for exp in explist if exp.FEVgroup == FEVgroup ]
            if len(explistFEV)==0 : continue
            thisepoch = explistFEV[0].epoch
            thisfilter = explistFEV[0].filter
            if onlyepochs and thisepoch not in onlyepochs : continue
            if onlyfilters and thisfilter not in onlyfilters : continue
            epochdir = explistFEV[0].epochdir
            outrootFEV = '%s_%s_nat'%(outroot,FEVgroup)

            if not os.path.isdir( epochdir ) : continue
            os.chdir( epochdir )
            drzsuffix = explistFEV[0].drzsuffix
            natsci = "%s_%s_sci.fits"%(outrootFEV,drzsuffix)
            if clean>3 and os.path.isfile( natsci ) :
                os.remove( natsci )
            natwht = natsci.replace('sci.fits','wht.fits')
            if clean>3 and os.path.isfile( natwht ) :
                os.remove( natwht )
            natctx = natsci.replace('sci.fits','ctx.fits')
            if clean>3 and os.path.isfile( natctx ) :
                os.remove( natctx )
            if clean > 3 :
                natroot = natsci.replace('.fits','')
                natcoolist = glob.glob( natroot+'_*.coo') + \
                             glob.glob( natroot+'_*.match' ) + \
                             glob.glob( natroot+'_*.list' )
                for natcoo in natcoolist :
                    os.remove( natcoo )
            if clean > 4 :
                # Nuclear option : causes a race condition when processing
                # with separate filters in the same epoch on separate processes
                tmpmasklist = glob.glob( 'tmp*staticMask.fits' )
                for tmpmask in tmpmasklist :
                    if os.path.exists( tmpmask ):
                        os.remove( tmpmask )
                if os.path.exists('OrIg_files') :
                    shutil.rmtree( 'OrIg_files' )

            os.chdir( topdir )


    return 0

def mkparser():
    import argparse

    parser = argparse.ArgumentParser(
        description='Run astrodrizzle and tweakreg on a set of flt or flc' +
        'images, building single-epoch drizzled images and diff images.' )

    # Required positional argument
    parser.add_argument('rootname', help='Root name for the input flt dir (<rootname>.flt), also used for the output _drz products. ')

    # optional arguments :
    parser.add_argument('--filters', metavar='X,Y,Z', help='Process only these filters (comma-seperated list)',default='')
    parser.add_argument('--epochs', metavar='X,Y,Z', help='Process only these epochs (comma-seperated list)',default='')
    parser.add_argument('--clobber', action='store_true', help='Turn on clobber mode. [False]', default=False)
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbosity. [default is ON]', default=True )
    parser.add_argument('--verboselevel', type=int, dest='verbose', help='Turn up the verbosity (0-10).', default=1 )
    parser.add_argument('--quiet', dest='verbose', action='store_false', help='Turn off verbosity. [default is ON]', default=True )
    parser.add_argument('--clean', type=int, choices=[0,1,2,3,4,5], default=1,
                        help='Clean up cruft: '
                         " [0] Keep all intermediate files. "
                         " [1] Remove intermediate drizzle and diff files, including ctx.fits and sub_sci.fits (the default); "
                         " [2] and clear out OrIg_files/*fl?.fits; "
                         " [3] and remove last-drizzle flts in epoch sub-dirs; "
                         " [4] and delete nat_drz products and tweakreg catalogs; "
                         " [5] and remove any tmp*staticMask.fits files (Warning: race conditions possible).")
    parser.add_argument('--debug', action='store_true', help='Enter debug mode. [False]', default=False)
    parser.add_argument('--dotest', action='store_true', help='Process the SN Colfax test data (all other options ignored)', default=False)

    parser.add_argument('--singlestar', action='store_true', help='Special case for registering images with only a single bright source, e.g. standard stars.', default=False)

    proc = parser.add_argument_group("Processing stages")
    proc.add_argument('--dosetup', action='store_true', help='(1) copy flt files into epoch subdirs', default=False)
    proc.add_argument('--dorefim', action='store_true', help='(2) build the WCS ref image', default=False)
    proc.add_argument('--dodriz1', action='store_true', help='(3) first astrodrizzle pass (pre-registration)', default=False)
    proc.add_argument('--doreg', action='store_true', help='(4) run tweakreg to align with refimage', default=False)
    proc.add_argument('--dodriz2', action='store_true', help='(5) second astrodrizzle pass (registered)', default=False)
    proc.add_argument('--dodiff', action='store_true', help='(6) subtract and mask to make diff images', default=False)
    proc.add_argument('--dostack', action='store_true', help='(7) construct a multi-epoch stack image', default=False)
    proc.add_argument('--doall', action='store_true', help='Run all necessary processing stages', default=False)

    sortpar = parser.add_argument_group( "(1) Settings for epoch sorting stage")
    sortpar.add_argument('--mjdmin', metavar='0', type=float, help='All observations prior to this date are put into epoch 0.',default=0)
    sortpar.add_argument('--mjdmax', metavar='inf', type=float, help='All observations after this date are put into the last epoch.',default=0)
    sortpar.add_argument('--epochspan', metavar='5', type=float, help='Max number of days spanning a single epoch.',default=5)

    refpar = parser.add_argument_group( "(2) Settings for constructing the TweakReg WCS reference image")
    refpar.add_argument('--refimage', metavar='Z.fits', help='Existing tweakreg ref image. Full path is required.',default='')
    refpar.add_argument('--refepoch', metavar='X', type=int, help='Use this epoch to define the tweakreg refimage.',default=0)
    refpar.add_argument('--reffilter', metavar='X', help='Use this filter to define the tweakreg refimage.',default='')
    refpar.add_argument('--refvisit', metavar='PID.vis', help='Use this PID.visit to define the tweakreg refimage [e.g. 12099.A1]',default='')

    imfindpar = parser.add_argument_group( "(4a) Settings for tweakreg.imagefind source detection")
    imfindpar.add_argument('--threshold', metavar='5', type=float, help='Detection threshold in sigmas for tweakreg object detection.',default=5)
    imfindpar.add_argument('--peakmin', metavar='X', type=float, help='Require peak flux above this value for tweakreg object detection.',default=None)
    imfindpar.add_argument('--peakmax', metavar='X', type=float, help='Require peak flux below this value for tweakreg object detection.',default=None)
    # imfindpar.add_argument('--fluxmin', metavar='X', type=float, help='Require total flux above this value for tweakreg object detection.',default=0)
    # imfindpar.add_argument('--fluxmax', metavar='X', type=float, help='Require total flux below this value for tweakreg object detection.',default=0)


    regpar = parser.add_argument_group( "(4b) Settings for tweakreg WCS registration stage")
    regpar.add_argument('--interactive', action='store_true', help='Run tweakreg interactively (showing plots)',default=False)
    regpar.add_argument('--intravisitreg', action='store_true', help='Run tweakreg before first drizzle stage to do intra-visit registration.',default=False)
    regpar.add_argument('--searchrad', metavar='X', type=float, help='Search radius in arcsec for tweakreg catalog matching.',default=1.5)
    regpar.add_argument('--minobj', metavar='N', type=int, help='Minimum number matched objects for tweakreg registration.',default=10)
    regpar.add_argument('--refcat', metavar='X.cat', help='Existing source catalog for limiting tweakreg matches.',default='')
    regpar.add_argument('--rfluxmin', metavar='X', type=float, help='Limit the tweakreg reference catalog to objects brighter than this magnitude.',default=None)
    regpar.add_argument('--rfluxmax', metavar='X', type=float, help='Limit the tweakreg reference catalog to objects fainter than this magnitude.',default=None)
    regpar.add_argument('--refnbright', metavar='N', type=int, help='Number of brightest objects to use from the tweakreg reference catalog.',default=None)
    regpar.add_argument('--shiftonly', action='store_true', help='Only allow a shift for image alignment. No rotation or scale.',default=False)
    regpar.add_argument('--nbright', metavar='N', type=int, help='Number of brightest objects to use from each single-exposure source catalog.',default=None)
    regpar.add_argument('--nclip', metavar='3', type=int, help='Number of sigma-clipping iterations for catalog matching.',default=3)
    regpar.add_argument('--sigmaclip', metavar='3.0', type=float, help='Clipping limit in sigmas, for catalog matching',default=3.0)

    drizpar = parser.add_argument_group( "(5) Settings for final astrodrizzle stage" )
    drizpar.add_argument('--drizcr', type=int, default=1, choices=[-1,0,1,2],
                         help='Astrodrizzle cosmic ray rejection stage: '
                         "[-1] remove CR flags and don't add any more; "
                         "[0] Keep existing CR flags and don't do any new CR rejection; "
                         '[1] Remove CR flags and run CR rejection only within the visit (the default); '
                         '[2] Re-run CR flagging at the multi-visit drizzle and stack stages.')
    drizpar.add_argument('--ra', metavar='X', type=float, help='R.A. for center of output image', default=None)
    drizpar.add_argument('--dec', metavar='X', type=float, help='Decl. for center of output image', default=None)
    drizpar.add_argument('--rot', metavar='0', type=float, help='Rotation (deg E of N) for output image', default=0.0)
    drizpar.add_argument('--imsize', metavar='X', type=float, help='Size of output image [arcsec]', default=None)
    drizpar.add_argument('--pixscale', metavar='X', type=float, help='Pixel scale to use for astrodrizzle.', default=None)
    drizpar.add_argument('--pixfrac', metavar='X', type=float, help='Pixfrac to use for astrodrizzle.', default=None)
    drizpar.add_argument('--wht_type', type=str, help='Type of the weight image.', choices=['IVM','EXP'], default='IVM')
    drizpar.add_argument('--singlesci', action='store_true', help='Make individual-exposure _single_sci.fits images. (also set by --singlesubs)', default=False )

    diffpar = parser.add_argument_group( "(5) Settings for subtraction stage")
    diffpar.add_argument('--singlesubs', action='store_true', help='Make diff images from the individual-exposure _single_sci.fits images. Also sets --singlesci.', default=False )
    diffpar.add_argument('--tempepoch', metavar='0', type=int, help='Template epoch.', default=0 )
    diffpar.add_argument('--tempfilters', metavar='X,Y', type=str, help='Make a composite template by combining images in these filters.', default=None )

    stackpar = parser.add_argument_group( "(5) Settings for multi-epoch stack stage")
    stackpar.add_argument('--stacktemplate', action='store_true', help='Include the template epoch in the multi-epoch stack.')
    stackpar.add_argument('--stackpixscale', metavar='X', type=float, default=None, help='Set the pixel scale for the multi-epoch stack.', )
    stackpar.add_argument('--stackpixfrac', metavar='X', type=float, default=None, help='Set the pixfrac for the multi-epoch stack.')
    stackpar.add_argument('--stackepochs', metavar='X,Y,Z', type=str, default=None, help='Specify the epochs to combine for the multi-epoch stack.')

    return parser


def main() :
    parser = mkparser()
    argv = parser.parse_args()

    if argv.dotest :
        import testpipe
        testpipe.colfaxtest( getflts=True, runpipeline=True )
        return 0

    # Run the pipeline :
    runpipe(argv.rootname, onlyfilters=(argv.filters or []),
             onlyepochs=(argv.epochs or []),
             doall=argv.doall,
             dosetup=argv.dosetup, dorefim=argv.dorefim,
             dodriz1=argv.dodriz1, doreg=argv.doreg,
             dodriz2=argv.dodriz2, dodiff=argv.dodiff, dostack=argv.dostack,
             drizcr=argv.drizcr, intravisitreg=argv.intravisitreg,
             refim=argv.refimage, refepoch=argv.refepoch,
             refvisit=argv.refvisit, reffilter=argv.reffilter,
             tempepoch=argv.tempepoch, tempfilters=argv.tempfilters,
             refcat=argv.refcat, interactive=argv.interactive,
             peakmin=argv.peakmin, peakmax=argv.peakmax,
             # fluxmin=argv.fluxmin, fluxmax=argv.fluxmax,
             rfluxmax=argv.rfluxmin, rfluxmin=argv.rfluxmax,
             refnbright=argv.refnbright, nbright=argv.nbright,
             searchrad=argv.searchrad, threshold=argv.threshold,
             nclip=argv.nclip, sigmaclip=argv.sigmaclip,
             minobj=argv.minobj, shiftonly=argv.shiftonly,
             singlestar=argv.singlestar,
             mjdmin=argv.mjdmin, mjdmax=argv.mjdmax,
             epochspan=argv.epochspan,
             ra=argv.ra, dec=argv.dec, rot=argv.rot,
             imsize_arcsec=argv.imsize,
             pixscale=argv.pixscale, pixfrac=argv.pixfrac,
             wht_type=argv.wht_type, clean=argv.clean,
             singlesubs=argv.singlesubs,
             singlesci=(argv.singlesci or argv.singlesubs),
             stackepochs=argv.stackepochs, # stacktemplate=argv.stacktemplate,
             stackpixscale=argv.stackpixscale, stackpixfrac=argv.stackpixfrac,
             clobber=argv.clobber, verbose=argv.verbose, debug=argv.debug)
    return 0

if __name__ == "__main__":
    main()
