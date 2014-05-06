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
              dodriz1=False, drizcr=False, intravisitreg=False,
              # Register to a given image or  epoch, visit and filter
              doreg=False, refim=None, refepoch=None, refvisit=None, reffilter=None, 
              # Drizzle registered flts by epoch and filter 
              dodriz2=False,
              # make diff images
              dodiff=False, tempepoch=0,
              refcat=None,
              interactive=False, threshold=4, fluxmin=None, fluxmax=None,
              rfluxmax=None, rfluxmin=None, refnbright=None,
              searchrad=1.5, minobj=10,
              mjdmin=0, mjdmax=0, epochspan=5,
              ra=None, dec=None, rot=0, imsize_arcsec=None, 
              pixscale=None, pixfrac=None, wht_type='ERR',
              clobber=False, verbose=True, debug=False ):
    """ 
    Primary pipeline function.  Executes all the intermediate steps: 
       register, sort, drizzle, subtract, mask
    """
    import pyfits
    import shutil
    if debug : import pdb; pdb.set_trace()
    from drizzlepac.tweakback import tweakback

    topdir = os.path.abspath( '.' )
    fltdir = outroot + '.flt' 

    if doall :
        dosetup=True
        dorefim=True
        dodriz1=True
        doreg=True
        dodriz2=True
        dodiff=True

    if onlyfilters : 
        if type(onlyfilters)==str : 
            onlyfilters = onlyfilters.lower().split(',')
        onlyfilters = [ filt[:5].lower() for filt in onlyfilters ]
    if type(onlyepochs) in [str,int,float] :
        onlyepochs = [ int(ep) for ep in str(onlyepochs).split(',') ]

    # STAGE 0 : (always runs)
    # get a list of exposures and epochs, sorting flt files into epochs
    fltlist = glob.glob( "%s/*fl?.fits"%fltdir )
    if not len( fltlist ) : 
        raise( exceptions.RuntimeError( "There are no flt/flc files in %s !!"%fltdir) )
    explist_all = exposures.get_explist( fltlist, outroot=outroot, targetradec=[ra,dec])
    
    if not epochlistfile :
        epochlistfile =  "%s_epochs.txt"%explist_all[0].outroot
    if os.path.exists( epochlistfile ) :
        print( "%s exists. Adopting existing epoch sorting."%epochlistfile )
        exposures.read_epochs( explist_all, epochlistfile )
        exposures.print_epochs( explist_all, outfile=None,
                                verbose=verbose, clobber=False,
                                onlyfilters=None, onlyepochs=None )
    else :
        exposures.define_epochs( explist_all, epochspan=epochspan,
                                 mjdmin=mjdmin, mjdmax=mjdmax )
        exposures.print_epochs( explist_all, outfile=epochlistfile,
                                verbose=verbose, clobber=False,
                                onlyfilters=None, onlyepochs=None )

    if refim and not os.path.exists( refim ) :
        raise exceptions.RuntimeError( 'Ref image %s does not exist.'%refim )
    if not refim :
        # No refimage has been specified, so set the default refimage name
        refdrzdir = '%s.refim'%outroot
        refimbasename = '%s_wcsref_sci.fits'%(outroot)
        refim = os.path.abspath( os.path.join( refdrzdir, refimbasename ) )

    # reduce the working exposure list to contain only those exposures
    # that we actually want to process
    explist = []
    for exp in explist_all:
        if exp.epoch==-1 or not exp.ontarget :
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
    if dorefim :
        if verbose :
            print("sndrizpipe : (2) REFIM : Constructing WCS ref image.")
        if os.path.exists( refim ) and clobber :
            os.remove( refim )
        if os.path.exists( refim ) :
            print("%s already exists.  Not clobbering."%refim)
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
            
            # if refvisit is not set, then find the maximum depth visit and use that
            if not refvisit :
                #visits, exp_times, visit_depth = np.array( ([], [], []) )
                explistRIvisfind = [ exp for exp in explist_all
                        if (exp.epoch==refepoch and exp.filter==reffilter) ]
                visits = [exp.visit for exp in explistRIvisfind ]
                exp_times = np.array([exp.exposure_time
                                      for exp in explistRIvisfind ])
                unique_visits = np.unique( visits )
                if len(unique_visits)==1:
                    refvisit = unique_visits[0]
                elif len(unique_visits)<1:
                    raise exceptions.RuntimeError(
                        "No visits satisfy the refimage requirements:\n"+\
                        "  filter = %s     epoch = %s"%(reffilter,refepoch) )
                else :
                    visindices = [ np.where(np.char.equal(visits,vis))[0]
                                   for vis in unique_visits ]
                    visit_depth = np.array( [ np.sum(exp_times[ivis])
                                              for ivis in visindices ] )
                    ideepest  = np.argmax( visit_depth )
                    refvisit = unique_visits[ideepest]
            refvisit = refvisit.upper()
            
            explistRI = sorted( [ exp for exp in explist_all if exp.epoch==refepoch
                                  and exp.filter==reffilter and exp.visit==refvisit ] )

            refdrzdir = os.path.dirname( refim )
            if not os.path.isdir( refdrzdir ) :
                os.makedirs( refdrzdir )
            for exp in explistRI :
                fltfile = os.path.basename( exp.filename )
                refsrcdir = os.path.abspath( fltdir )
                shutil.copy( os.path.join( refsrcdir, fltfile ), refdrzdir )
            fltlistRI = [ exp.filename for exp in explistRI ]
            refimroot = '%s_wcsref'%outroot
            os.chdir( refdrzdir )
            refimsci, refimwht = drizzle.secondDrizzle(
                fltlistRI, refimroot, refimage=None, ra=ra, dec=dec, rot=rot,
                imsize_arcsec=imsize_arcsec, wht_type=wht_type,
                pixscale=pixscale, pixfrac=pixfrac,
                clobber=clobber, verbose=verbose, debug=debug  )
            os.rename(refimsci,refim)
            os.chdir(topdir)
            

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
                register.intraVisit(
                    fltlistFEV, fluxmin=fluxmin, fluxmax=fluxmax, minobj=minobj,
                    threshold=threshold, interactive=interactive, debug=debug )
            drizzle.firstDrizzle(
                fltlistFEV, outrootFEV, driz_cr=drizcr,
                wcskey=((intravisitreg and 'INTRAVIS') or '') )

            # TODO : Update the WCS of the refim so that it matches the reference catalog
            #if refcat :
            #    if verbose : print( " Registering reference image %s  to ref catalog %s"%(refim,refcat))
            #    register.toCatalog( refim, refcat, refim, refnbright=refnbright, rfluxmax=rfluxmax, rfluxmin=rfluxmin,
            #                        searchrad=searchrad, fluxmin=fluxmin, fluxmax=fluxmax, threshold=threshold,
            #                        interactive=interactive, debug=debug )

            os.chdir( topdir )


    if doreg or dodriz2 :
        if not os.path.exists( refim ):
            raise exceptions.RuntimeError("No refim file %s!  Maybe you should re-run with dorefim=True."%refim)
        else :
            refim = os.path.abspath( refim )

        # Fix the output  ra and dec center point if not provided by the user.
        if not ra and not dec :
            ra = pyfits.getval( refim, "CRVAL1" )
            dec = pyfits.getval( refim, "CRVAL2" )    

    # STAGE 4 :
    # Run tweakreg to register all the single-visit drz images
    # to a common WCS defined by the refcat/refim, updating the drz file headers.
    # Then use tweakback to propagate that back into the flt files
    if doreg : 
        if verbose :
            print("sndrizpipe : (4) REG : running tweakreg.")
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

            refimpath = os.path.abspath(refim)
            if refcat : refcatpath = os.path.abspath(refcat)
            else : refcatpath = None

            os.chdir( epochdir )
            if not os.path.exists( outsciFEV ) :
                exceptions.RuntimeError( "Missing %s."%outsciFEV )

            # register to the ref image and ref catalog
            origwcs = pyfits.getval( outsciFEV,'WCSNAME').strip()
            wcsname = register.toRefim(
                outsciFEV, refim=refimpath, refcat=refcatpath,
                searchrad=searchrad, fluxmin=fluxmin, fluxmax=fluxmax,
                threshold=threshold, minobj=minobj,
                refnbright=refnbright, rfluxmin=rfluxmin, rfluxmax=rfluxmax,
                interactive=interactive, clobber=clobber, debug=debug )

            # Run tweakback to update the constituent flts
            tweakback( outsciFEV, input=fltlistFEV, origwcs=origwcs,
                       wcsname=wcsname, verbose=verbose, force=clobber )
            os.chdir(topdir)
              

    # STAGE 5
    # Second and final astrodrizzle pass, wherein we rerun
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

            outsciFE, outwhtFE = drizzle.secondDrizzle(
                fltlistFE, outrootFE, refimage=refim, ra=ra, dec=dec, rot=rot,
                imsize_arcsec=imsize_arcsec, wht_type=wht_type,
                pixscale=pixscale, pixfrac=pixfrac, driz_cr=(drizcr>1),
                clobber=clobber, verbose=verbose, debug=debug  )

            outbpxFE = outwhtFE.replace('_wht','_bpx')
            outbpxFE = badpix.zerowht2badpix(
                outwhtFE, outbpxFE, verbose=verbose, clobber=clobber )
            os.chdir( topdir )


    # STAGE 6
    # Define a template epoch for each filter and subtract it from the other epochs
    if dodiff :
        if verbose :
            print("sndrizpipe : (6) DIFF : subtracting template images.")
        for filter in filterlist :
            if onlyfilters and filter not in onlyfilters : continue
            template = None
            if tempepoch == None : 
                # User did not define a template epoch, so we default
                # to use the first available epoch
                for epoch in epochlist : 
                    explistFE = [ exp for exp in explist
                                  if exp.filter==filter and exp.epoch==epoch ]
                    if len(explistFE)==0: continue
                    drzsuffix = explistFE[0].drzsuffix
                    epochdir = explistFE[0].epochdir
                    FEgroup = explistFE[0].FEgroup
                    outrootFE = '%s_%s'%(outroot, FEgroup )
                    if os.path.isfile( os.path.join( epochdir, outrootFE+"_reg_%s_sci.fits"%drzsuffix )) : 
                        tempepoch = epoch
                        break
            else : 
                explistF = [ exp for exp in explist if exp.filter==filter ]
                drzsuffix = explistF[0].drzsuffix

            # now do the subtractions
            tempdir = outroot+'.e%02i'%tempepoch
            tempsci = os.path.join( os.path.abspath(tempdir), '%s_%s_e%02i_reg_%s_sci.fits'%(outroot,filter,tempepoch,drzsuffix))
            tempwht = tempsci.replace('sci.fits','wht.fits')
            tempbpx = tempsci.replace('sci.fits','bpx.fits')
            topdir = os.path.abspath( '.' )
            for epoch in epochlist :
                if onlyepochs and epoch not in onlyepochs : continue
                if epoch == tempepoch : continue
                explistFE = [ exp for exp in explist if exp.filter==filter and exp.epoch==epoch ]
                if len(explistFE)==0 : continue
                epochdirFE = explistFE[0].epochdir
                outrootFE =  "%s_%s"%(outroot,explistFE[0].FEgroup)
                drzsuffix = explistFE[0].drzsuffix
                thisregsci = "%s_reg_%s_sci.fits"%(outrootFE,drzsuffix)
                thisregwht = "%s_reg_%s_wht.fits"%(outrootFE,drzsuffix)
                thisregbpx = "%s_reg_%s_bpx.fits"%(outrootFE,drzsuffix)
                
                os.chdir( epochdirFE )
                if not os.path.isfile( thisregsci ) : 
                    os.chdir( topdir ) 
                    continue
                thisdiffim = outrootFE + "-e%02i_sub_sci.fits"%tempepoch

                if not os.path.isfile( tempsci ) or not os.path.isfile( thisregsci) :
                    print( "Can't create diff image %s"%thisdiffim )
                    print( "  missing either  %s"%tempsci )
                    print( "    or  %s"%thisregsci )
                    os.chdir( topdir )
                    continue

                diffim = imarith.imsubtract( tempsci, thisregsci, outfile=thisdiffim,
                                              clobber=clobber, verbose=verbose, debug=debug)
                diffwht = badpix.combine_ivm_maps( thisregwht, tempwht,
                                                   diffim.replace('sci.fits','wht.fits'),
                                                   clobber=clobber, verbose=verbose )
                diffbpx = badpix.unionmask( tempbpx, thisregbpx,
                                     diffim.replace('sci.fits','bpx.fits'),
                                     clobber=clobber, verbose=verbose)
                diffim_masked = badpix.applymask( diffim, diffbpx,
                                                 clobber=clobber, verbose=verbose)
                print("Created diff image %s, wht map %s, and bpx mask %s"%(
                    diffim_masked, diffwht, diffbpx ) )
                os.chdir( topdir )
    return 0

def mkparser():
    import argparse
    parser = argparse.ArgumentParser(
        description='Run astrodrizzle and tweakreg on a set of flt or flc' +
        'images, building single-epoch drizzled images and diff images.')

    # Required positional argument
    parser.add_argument('rootname', help='Root name for the input flt dir (<rootname>.flt), also used for the output _drz products. ')

    # optional arguments :
    parser.add_argument('--filters', metavar='X,Y,Z', help='Process only these filters (comma-seperated list)',default='')
    parser.add_argument('--epochs', metavar='X,Y,Z', help='Process only these epochs (comma-seperated list)',default='')
    parser.add_argument('--clobber', action='store_true', help='Turn on clobber mode. [False]', default=False)
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbosity. [default is ON]', default=True )
    parser.add_argument('--quiet', dest='verbose', action='store_false', help='Turn off verbosity. [default is ON]', default=True )
    parser.add_argument('--debug', action='store_true', help='Enter debug mode. [False]', default=False)
    parser.add_argument('--dotest', action='store_true', help='Process the SN Colfax test data (all other options ignored)', default=False)

    proc = parser.add_argument_group("Processing stages")
    proc.add_argument('--dosetup', action='store_true', help='(1) copy flt files into epoch subdirs', default=False)
    proc.add_argument('--dorefim', action='store_true', help='(2) build the WCS ref image', default=False)
    proc.add_argument('--dodriz1', action='store_true', help='(3) first astrodrizzle pass (pre-registration)', default=False)
    proc.add_argument('--doreg', action='store_true', help='(4) run tweakreg to align with refimage', default=False)
    proc.add_argument('--dodriz2', action='store_true', help='(5) second astrodrizzle pass (registered)', default=False)
    proc.add_argument('--dodiff', action='store_true', help='(6) subtract and mask to make diff images', default=False)
    proc.add_argument('--doall', action='store_true', help='Run all necessary processing stages', default=False)

    sortpar = parser.add_argument_group( "Settings for epoch sorting stage")
    sortpar.add_argument('--mjdmin', metavar='0', type=float, help='All observations prior to this date are put into epoch 0.',default=0)
    sortpar.add_argument('--mjdmax', metavar='inf', type=float, help='All observations after this date are put into the last epoch.',default=0)
    sortpar.add_argument('--epochspan', metavar='5', type=float, help='Max number of days spanning a single epoch.',default=5)

    regpar = parser.add_argument_group( "Settings for tweakreg WCS registration stage")
    regpar.add_argument('--interactive', action='store_true', help='Run tweakreg interactively (showing plots)',default=False)
    regpar.add_argument('--intravisitreg', action='store_true', help='Run tweakreg before first drizzle stage to do intra-visit registration.',default=False)
    regpar.add_argument('--refcat', metavar='X.cat', help='Existing source catalog for limiting tweakreg matches.',default='')
    regpar.add_argument('--searchrad', metavar='X', type=float, help='Search radius in arcsec for tweakreg catalog matching.',default=1.5)
    regpar.add_argument('--searchthresh', metavar='5', type=float, help='Detection threshold in sigmas for tweakreg object detection.',default=5)
    regpar.add_argument('--peakmin', metavar='X', type=float, help='Require peak flux above this value for tweakreg object detection.',default=0)
    regpar.add_argument('--peakmax', metavar='X', type=float, help='Require peak flux below this value for tweakreg object detection.',default=0)
    regpar.add_argument('--rfluxmin', metavar='X', type=float, help='Limit the tweakreg reference catalog to objects brighter than this magnitude.',default=0)
    regpar.add_argument('--rfluxmax', metavar='X', type=float, help='Limit the tweakreg reference catalog to objects fainter than this magnitude.',default=0)
    regpar.add_argument('--refnbright', metavar='X', type=float, help='Number of brightest objects to use from the tweakreg reference catalog.',default=0)
    regpar.add_argument('--refimage', metavar='Z.fits', help='Existing WCS reference image. Full path is required.',default='')
    regpar.add_argument('--refepoch', metavar='X', type=int, help='Use this epoch to define the refimage.',default=0)
    regpar.add_argument('--reffilter', metavar='X', help='Use this filter to define the refimage.',default='')
    regpar.add_argument('--refvisit', metavar='X', help='Use this visit to define the refimage.',default='')
    regpar.add_argument('--minobj', metavar='X', type=int, help='Minimum number matched objects for tweakreg registration.',default=10)

    drizpar = parser.add_argument_group( "Settings for astrodrizzle and subtraction stages")
    drizpar.add_argument('--drizcr', metavar='N', type=int,
                         help='Run a fresh CR rejection step to replace existing flt CR flags.'+\
                         '\nUse --drizcr 1 to run CR rejection only within the visit.'+\
                         '\nUse --drizcr 2 to also flag CRs at the multi-visit drizzle stage.', default=False )
    drizpar.add_argument('--ra', metavar='X', type=float, help='R.A. for center of output image', default=None)
    drizpar.add_argument('--dec', metavar='X', type=float, help='Decl. for center of output image', default=None)
    drizpar.add_argument('--rot', metavar='0', type=float, help='Rotation (deg E of N) for output image', default=0.0)
    drizpar.add_argument('--imsize', metavar='X', type=float, help='Size of output image [arcsec]', default=None)
    drizpar.add_argument('--pixscale', metavar='X', type=float, help='Pixel scale to use for astrodrizzle.', default=None)
    drizpar.add_argument('--pixfrac', metavar='X', type=float, help='Pixfrac to use for astrodrizzle.', default=None)
    drizpar.add_argument('--wht_type', metavar='ERR', type=str, help='Type of the weight image.', default='ERR')
    drizpar.add_argument('--tempepoch', metavar='0', type=int, help='Template epoch.', default=0 )

    return parser


def main() :
    parser = mkparser()
    argv = parser.parse_args()

    # TODO : check that the user has provided a sufficient but non-redundant set of parameters

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
             dodriz2=argv.dodriz2, dodiff=argv.dodiff,
             drizcr=argv.drizcr, intravisitreg=argv.intravisitreg,
             refim=argv.refimage, refepoch=argv.refepoch,
             refvisit=argv.refvisit, reffilter=argv.reffilter,
             tempepoch=argv.tempepoch,
             refcat=argv.refcat, interactive=argv.interactive,
             fluxmin=argv.peakmin, fluxmax=argv.peakmax,
             rfluxmax=argv.rfluxmin or None,
             rfluxmin=argv.rfluxmax or None,
             refnbright=argv.refnbright or None,
             searchrad=argv.searchrad, threshold=argv.searchthresh,
             minobj=argv.minobj,
             mjdmin=argv.mjdmin, mjdmax=argv.mjdmax,
             epochspan=argv.epochspan,
             ra=argv.ra, dec=argv.dec, rot=argv.rot,
             imsize_arcsec=argv.imsize,
             pixscale=argv.pixscale, pixfrac=argv.pixfrac,
             wht_type=argv.wht_type,
             clobber=argv.clobber, verbose=argv.verbose, debug=argv.debug)
    return 0

if __name__ == "__main__":
    main()
