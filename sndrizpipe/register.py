#! /usr/bin/env python
# S.Rodney 2014.02.27

import os
from astropy.io import fits as pyfits
from stsci import tools
from drizzlepac import tweakreg
import stwcs
from .util import extname_bug_cleanup


def RunTweakReg(files='*fl?.fits', refcat=None, refim=None,
                wcsname='SNDRIZPIPE', refnbright=None,
                rmaxflux=None, rminflux=None, searchrad=1.0,
                # fluxmax=None, fluxmin=None,
                 nclip=3, sigmaclip=3.0, computesig=False,
                peakmin=None, peakmax=None, threshold=4.0,
                minobj=10, nbright=None, fitgeometry='rscale',
                interactive=False, clean=False, clobber=False,
                verbose=False, debug=False):
    """Run tweakreg on a set of flt files or drz files."""
    if debug : import pdb; pdb.set_trace()
    from astropy.io import ascii

    #convert the input list into a useable list of images for astrodrizzle
    if type( files ) == str :
        filelist=tools.parseinput.parseinput(files)[0]
    else :
        filelist = files
        files = ','.join( filelist ).strip(',')
    if len(filelist)==0 :
        raise RuntimeError(
            "List of input files has no real files: %s"%str(files))

    # pre-clean any existing WCS header info
    if clobber :
        clearAltWCS( filelist )

    hdr1 = pyfits.getheader( filelist[0] )
    conv_width = getconvwidth(filelist[0])
    if computesig==False :
        skysigma = getskysigma( filelist )
    else :
        skysigma=0.0

    if (nbright and nbright<3) or minobj<3:
        use2dhist=False
    else :
        use2dhist=True

    # check first if the WCS wcsname already exists in the first image
    wcsnamelist = [ hdr1[k] for k in list(hdr1.keys()) if k.startswith('WCSNAME') ]
    if wcsname in wcsnamelist and not clobber :
        print((
            "WCSNAME %s already exists in %s"%(wcsname,filelist[0]) +
            "so I'm skipping over this tweakreg step." +
            "Re-run with clobber=True if you really want it done." ))
        return( wcsname )

    rfluxcol, rfluxunits = None, None
    if refcat :
        refCatalog = ascii.read( refcat )
        if len(refCatalog.columns)>2 :
            for icol in range(len(refCatalog.columns)) :
                if 'flux' in refCatalog.colnames[icol].lower():
                    rfluxcol = icol+1
                    rfluxunits = 'flux'
                elif 'mag' in refCatalog.colnames[icol].lower():
                    rfluxcol = icol+1
                    rfluxunits = 'mag'
        if not refim :
            refim = filelist[0]

    if interactive :
        while True :
            if nbright :
                # make source catalogs for each SCI extension
                srcCatListFile = mkSourceCatList(
                    filelist, filelist[0].split('_')[0]+'_cat.list',
                    threshold=threshold, peakmin=peakmin, peakmax=peakmax )
                if verbose :
                    print(( "Generated a list of source catalogs : %s"%srcCatListFile))
                xcol, ycol, fluxcol = 1,2,3
            else :
                srcCatListFile=None
                nbright=None
                xcol, ycol, fluxcol = 1,2,None

            print( "sndrizzle.register:  Running a tweakreg loop interactively.")
            tweakreg.TweakReg(files, updatehdr=False, wcsname='TWEAK',
                              use2dhist=use2dhist,
                              see2dplot=True, residplot='both',
                              fitgeometry=fitgeometry, nclip=nclip,
                              computesig=computesig, skysigma=skysigma,
                              sigma=sigmaclip, refcat=refcat,
                              refimage=refim, refxcol=1, refycol=2,
                              refxyunits='degrees', rfluxcol=rfluxcol,
                              rfluxunits=rfluxunits, refnbright=refnbright,
                              rmaxflux=rmaxflux, rminflux=rminflux,
                              # fluxmax=fluxmax, fluxmin=fluxmin,
                              peakmax=peakmax, peakmin=peakmin,
                              searchrad=searchrad, conv_width=conv_width,
                              threshold=threshold, separation=0,
                              tolerance=1.0, minobj=minobj,
                              catfile=srcCatListFile, nbright=nbright,
                              xcol=xcol, ycol=ycol,
                              fluxcol=fluxcol, fluxunits='cps',
                              clean=(clean and not nbright),
                              writecat=(not nbright))
            print( "==============================\n sndrizzle.register:\n")
            userin = input("Adopt these tweakreg settings? y/[n]").lower()
            if userin.startswith('y'): 
                print("OK. Proceeding to update headers.")
                break
            print("Current tweakreg/imagefind parameters:")
            printfloat("   refnbright = %i  # number of brightest refcat sources to use", refnbright)
            printfloat("   rminflux = %.1f  # min flux for refcat sources", rminflux)
            printfloat("   rminflux = %.1f  # max flux for refcat sources", rmaxflux)
            printfloat("   searchrad  = %.1f  # matching search radius (arcsec)", searchrad )
            printfloat("   peakmin    = %.1f  # min peak flux for detected sources", peakmin )
            printfloat("   peakmax    = %.1f  # max peak flux for detected sources", peakmax )
            # printfloat("   fluxmin    = %.1f  # min total flux for detected sources", fluxmin )
            # printfloat("   fluxmax    = %.1f  # max total flux for detected sources", fluxmax )
            printfloat("   threshold  = %.1f  # detection threshold in sigma ", threshold )
            printfloat("   fitgeometry= %s  # fitting geometry [shift,rscale] ", fitgeometry )
            printfloat("   nclip      = %i  # Number of sigma-clipping iterations", nclip )
            printfloat("   sigmaclip  = %.1f  # Clipping limit in sigmas ", sigmaclip )
            print('Adjust parameters using "parname = value" syntax.')

            print('Enter "run" to re-run tweakreg with new parameters.') 
            while True : 
                userin = input("   ").lower()
                if userin.startswith('run') : break
                try : 
                    parname = userin.split('=')[0].strip()
                    value = userin.split('=')[1].strip()
                except : 
                    print('Must use the "parname = value" syntax. Try again') 
                    continue
                if parname=='refnbright' : refnbright=int( value )
                elif parname=='rminflux' : rminflux=float(value)
                elif parname=='rmaxflux' : rmaxflux=float(value)
                elif parname=='searchrad' : searchrad=float( value )
                elif parname=='peakmin' : peakmin=float( value )
                elif parname=='peakmax' : peakmax=float( value )
                # elif parname=='fluxmax' : fluxmax=float( value )
                # elif parname=='fluxmin' : fluxmin=float( value )
                elif parname=='threshold' : threshold=float( value )
                elif parname=='fitgeometry' : fitgeometry=value
                elif parname=='nclip' : nclip=int(value)
                elif parname=='sigmaclip' : sigmaclip=float(value)

    print( "==============================\n sndrizzle.register:\n")
    print( "  Final tweakreg run for updating headers.")

    if nbright :
        # make source catalogs for each SCI extension
        srcCatListFile = mkSourceCatList(
            filelist, filelist[0].split('_')[0]+'_cat.list',
            threshold=threshold, peakmin=peakmin, peakmax=peakmax )
        if verbose :
            print(( "Generated a list of source catalogs : %s"%srcCatListFile))
        xcol, ycol, fluxcol = 1,2,3
    else :
        srcCatListFile=None
        nbright=None
        xcol, ycol, fluxcol = 1,2,None

    print(( 'fitgeometry = %s'%fitgeometry ))

    extname_bug_cleanup(files)  # clean up any buggy headers
    tweakreg.TweakReg(files, updatehdr=True, wcsname=wcsname,
                      use2dhist=use2dhist,
                      see2dplot=False, residplot='No plot',
                      computesig=computesig, skysigma=skysigma,
                      fitgeometry=fitgeometry, nclip=nclip, sigma=sigmaclip,
                      refcat=refcat, refimage=refim,
                      refxcol=1, refycol=2, refxyunits='degrees',
                      refnbright=refnbright, rfluxcol=rfluxcol, rfluxunits=rfluxunits,
                      rmaxflux=rmaxflux, rminflux=rminflux,
                      # fluxmax=fluxmax, fluxmin=fluxmin,
                      peakmax=peakmax, peakmin=peakmin,
                      searchrad=searchrad, conv_width=conv_width, threshold=threshold,
                      catfile=srcCatListFile, nbright=nbright,
                      xcol=xcol, ycol=ycol, fluxcol=fluxcol, fluxunits='cps',
                      separation=0, tolerance=1.0, minobj=minobj,
                      clean=clean, writecat=not nbright)
    return( wcsname )


def SingleStarReg( imfile, ra, dec, wcsname='SINGLESTAR',
                   computesig=False, refim=None,
                   threshmin=0.5, peakmin=None, peakmax=None, searchrad=5.0,
                   nsigma=1.5, fluxmin=None, fluxmax=None,
                   verbose=True, clobber=True ):
    """ Update the WCS of imfile so that it matches the WCS of the refimfile,
    using a single star to define the necessary shift.
    If xy or xyref are provided, then assume the star is located within
    searchrad arcsec of that position in the imfile or the refimfile,
    respectively. If either of those pixel coordinates are not provided, then
    use the brightest star in the image.
    """
    # noinspection PyUnresolvedReferences
    from numpy import deg2rad, sqrt, cos, where, median
    from astropy.io import ascii
    from drizzlepac.updatehdr import updatewcs_with_shift
    from numpy import unique

    if refim is None : refim = imfile
    if computesig==False :
        skysigma = getskysigma( imfile )
        if verbose : print(("sndrizipipe.register.SingleStarReg: "
                           " Manually computed sky sigma for %s as %.5e"%(imfile,skysigma)))
    else :
        skysigma=0.0

    # locate stars in imfile, pick out the brightest one
    topdir = os.path.abspath( '.' )
    imfiledir = os.path.dirname( os.path.abspath(imfile) )
    imfilebase = os.path.basename( imfile )
    os.chdir( imfiledir )

    # Iterate the source-finding algorithm with progressively smaller threshold
    # values.  This helps to ensure that we correctly locate the single bright
    # source in the image
    xycatfile = None
    threshold = 200.
    while threshold >= threshmin :
        try :
            xycatfile = mkSourceCatalog(
                imfilebase, computesig=computesig, skysigma=skysigma, nsigma=nsigma,
                threshold=threshold, peakmin=peakmin, peakmax=peakmax,
                fluxmin=fluxmin, fluxmax= fluxmax  )[0]
            # The source finder succeeded!
            radeccatfile = xycatfile.replace('xy.coo','radec.coo')
            break
        except NameError :
            # the source finder failed, try again with a lower threshold
            threshold /= 2.
            continue
    if xycatfile is None :
        print(( "Failed to generate a clean source catalog for %s"%imfile + \
            " using threshmin = %.3f"%threshmin ))
        import pdb; pdb.set_trace()
        raise RuntimeError(
            "Failed to generate a clean source catalog for %s"%imfile + \
            " using threshmin = %.3f"%threshmin )

    xycat = ascii.read( xycatfile )
    radeccat = ascii.read( radeccatfile )
    if verbose :
        print(("Located %i sources with threshold=%.1f sigma"%(len(xycat),threshold)))

    os.chdir( topdir )

    # compute the approximate separation in arcsec from the target ra,dec
    # to each of the detected sources, then limit to those within searchrad
    rasrc, decsrc = radeccat['col1'], radeccat['col2']
    darcsec = sqrt( ((rasrc-ra)*cos(deg2rad(dec)))**2 + (decsrc-dec)**2 ) * 3600.
    inear = where( darcsec <= searchrad )[0]

    if verbose :
        print(("   %i of these sources are within %.1f arcsec of the target"%(len(inear),searchrad)))

    # identify the brightest source within searchrad arcsec of the target
    ibrightest = inear[ xycat['col3'][inear].argmax() ]
    xfnd,yfnd = [ xycat['col1'][ibrightest], xycat['col2'][ibrightest] ]

    if verbose :
        brightratio = xycat['col3'][ibrightest] / median(xycat['col3'][inear])
        print(("   The brightest of these sources is %.1fx brighter than the median."%brightratio))

    # The TweakReg imagefind algorithm sometimes misses the true center
    # catastrophically. Here we use a centroiding algorithm to re-center the
    # position on the star, checking for a large offset.
    # Note that we are using numpy arrays, so the origin is (0,0) and we need
    #  to correct the cntrd output to the (1,1) origin used by pyfits and drizzlepac.
    imdat = pyfits.getdata( imfile )
    fwhmpix = getfwhmpix( imfile )
    xcntrd, ycntrd = cntrd( imdat, xfnd, yfnd, fwhmpix )
    if xcntrd==-1 :
        if verbose : print('Recentering within a 5-pixel box')
        xcntrd, ycntrd = cntrd( imdat, xfnd, yfnd, fwhmpix, extendbox=5 )
    assert  ((xcntrd>0) & (ycntrd>0)), "Centroid recentering failed for %s"%imfile
    xcntrd += 1
    ycntrd += 1
    dxcntrd = xfnd-xcntrd
    dycntrd = yfnd-ycntrd
    if verbose >9 :
        # plot the centroid shift and save a .png image
        from matplotlib import pylab as pl
        from matplotlib import cm
        pl.clf()
        vmin = imdat[ycntrd-10:ycntrd+10,xcntrd-10:xcntrd+10].min()
        vmax = imdat[ycntrd-10:ycntrd+10,xcntrd-10:xcntrd+10].max()
        pl.imshow( imdat, cmap=cm.Greys, vmin=vmin, vmax=vmax)
        pl.plot( xfnd-1, yfnd-1, 'r+', ms=12, mew=1.5,
                 label='drizzlepac.ndfind source position: %.3f, %.3f'%(xfnd,yfnd) )
        pl.plot( xcntrd-1, ycntrd-1, 'gx', ms=12, mew=1.5,
                 label='register.cntrd recentered position: %.3f, %.3f'%(xcntrd,ycntrd) )
        pl.title( "Centroiding shift :  dx = %.3f   dy = %.3f"%(dxcntrd,dycntrd) )
        ax = pl.gca()
        ax.set_xlim( xcntrd-10, xcntrd+10 )
        ax.set_ylim( ycntrd-10, ycntrd+10 )
        pl.colorbar()
        ax.set_xlabel('X (pixels)')
        ax.set_ylabel('Y (pixels)')
        ax.legend( loc='upper right', numpoints=1, frameon=False )
        pl.draw()
        outpng = imfile.replace('.fits','_recenter.png')
        pl.savefig(outpng)
        print(("Saved a recentering image as " + outpng ))

    # locate the appropriate extensions for updating
    hdulist = pyfits.open( imfile )
    sciextlist = [ hdu.name for hdu in hdulist if 'WCSAXES' in hdu.header ]
    # convert the target position from ra,dec to x,y
    if len(sciextlist)>0:
        imwcs = stwcs.wcsutil.HSTWCS( hdulist, ext=(sciextlist[0],1) )
    else:
        sciextlist = ['PRIMARY']
        imwcs = stwcs.wcsutil.HSTWCS( hdulist, ext=None )
    xref, yref = imwcs.wcs_world2pix( ra, dec , 1)

    # If the new centroid position differs substantially from the original
    # ndfind position, then update the found source position
    # (i.e. in cases of catastrophic ndfind failure)
    if (abs(dxcntrd)>0.5) or (abs(dycntrd)>0.5) :
        xfnd = xcntrd
        yfnd = ycntrd

    # compute the pixel shift from the xy position found in the image
    # to the reference (target) xy position
    xshift = xfnd - xref
    yshift = yfnd - yref

    # apply that shift to the image wcs
    for sciext in unique(sciextlist):
        print(("Updating %s ext %s with xshift,yshift = %.5f %.5f"%(
            imfile,sciext, xshift, yshift )))
        updatewcs_with_shift(imfile, refim, wcsname=wcsname,
                             rot=0.0, scale=1.0, xsh=xshift, ysh=yshift,
                             fit=None, xrms=None, yrms=None, verbose=verbose,
                             force=clobber, sciext=sciext )
    hdulist.close()
    return( wcsname )


def clearAltWCS(fltlist):
    """ pre-clean any alternate wcs solutions from flt headers"""
    from drizzlepac import wcs_functions

    for fltfile in fltlist:
        hdulist = pyfits.open(fltfile, mode='update')
        extlist = []
        for ext in range(len(hdulist)):
            if 'WCSNAME' in hdulist[ext].header:
                extlist.append(ext)
            stwcs.wcsutil.restoreWCS(hdulist, ext, wcskey='O')
        if len(extlist):
            wcs_functions.removeAllAltWCS(hdulist, extlist)
        hdulist.flush()
        hdulist.close()


def printfloat( fmtstr, value ):
    """ Print a float value using the given format string, handling
    None and NaN values appropriately
    """
    try :
        print(( fmtstr % value )) 
    except : 
        pct = fmtstr.find('%')
        f = pct + fmtstr[pct:].find('f') + 1
        if value == None : 
            print(( fmtstr[:pct] + ' None ' + fmtstr[f:] ))
        elif value == float('nan') :
            print(( fmtstr[:pct] + ' NaN ' + fmtstr[f:] ))
        else : 
            print(( fmtstr[:pct] + ' ??? ' + fmtstr[f:] ))


def mkSourceCatList( imfilelist, listfilename, computesig=True, skysigma=0,
                     threshold=4.0, peakmin=None, peakmax=None,
                     nsigma=1.5, fluxmin=None, fluxmax=None ) :
    """Generate source catalogs for every image file in imfilelist.
    Then make a .list file that lists each file and its corresponding xy
    coo file (suitable for passing to TweakReg)
    """
    fout = open( listfilename, mode='w')
    for imfile in imfilelist :
        catlist = mkSourceCatalog(
            imfile, computesig=computesig, skysigma=skysigma,
            threshold=threshold, peakmin=peakmin, peakmax=peakmax,
            nsigma=nsigma, fluxmin=fluxmin, fluxmax=fluxmax )
        print('%s %s'%( imfile, '  '.join(catlist) ), file=fout)
    fout.close()
    return( listfilename )


def mkSourceCatalog( imfile, computesig=True, skysigma=0,
                     threshold=4.0, peakmin=None, peakmax=None,
                     nsigma=1.5, fluxmin=None, fluxmax=None ) :
    """Detect sources in the image and generate a catalog of source
    x,y positions and fluxes.

    Uses the same imagefind algorithm as tweakreg.

    Generates a separate xy catalog file for each SCI extension.
    """
    from drizzlepac import catalogs
    from drizzlepac.util import wcsutil

    conv_width = getconvwidth( imfile )
    image = pyfits.open( imfile )
    catfilelist = []
    extnamelist = [ ext.name.upper() for ext in image ]
    if 'SCI' in extnamelist :
        iextlist = [ iext for iext in range(len(extnamelist))
                     if extnamelist[iext]=='SCI' ]
    else :
        iextlist = [ 0 ]
    for iext in iextlist:
        wcs = wcsutil.HSTWCS( image, ext=iext)
        imcat = catalogs.generateCatalog(
            wcs, mode='automatic', catalog=imfile+'[%i]' % iext,
            computesig=computesig,
            skysigma=skysigma, threshold=threshold, conv_width=conv_width,
            peakmin=peakmin, peakmax=peakmax,
            fluxmin=fluxmin, fluxmax=fluxmax,
            nsigma=nsigma, sharplo=0.2, sharphi=1, roundlo=-1, roundhi=1,
            ratio=1, theta=0, use_sharp_round=True)
        imcat.buildCatalogs()
        xycatfile = imfile.replace('.fits','_%i_xy.coo'%iext )
        imcat.writeXYCatalog(xycatfile)
        radeccatfile = imfile.replace('.fits','_%i_radec.coo'%iext )
        writeRADecCatalog(imcat, radeccatfile )
        catfilelist.append( xycatfile )
    return( catfilelist )



def writeRADecCatalog(cat,filename):
    """ Write out the RA,Dec positions from a drizzlepac Catalog
    object into a text file.
    Fills in a missing method from drizzlepac.catalogs.
    """
    if cat.radec is None:
        cat.buildCatalogs()
    if cat.radec is None:
        warnstr = 'WARNING: \n    No RA,Dec source catalog to write to file. '
        print(warnstr)
        return

    f = open(filename,'w')
    f.write("# Source catalog derived for %s\n"%cat.wcs.filename)
    f.write("# Columns: \n")
    f.write('#    RA     Dec         Flux       ID\n')
    f.write('#   (deg)   (deg)      (cps)\n')
    for row in range(len(cat.radec[0])):
        for i in range(len(cat.xypos)):
            if i< len(cat.radec) :
                f.write("%.8f  "%(cat.radec[i][row]))
            else :
                f.write("%g  "%(cat.xypos[i][row]))
        f.write("\n")
    f.close()

def getconvwidth( fitsfile ):
    """ determine the appropriate convolution kernel
    width for finding (point) sources in the image
    :rtype : float
    """
    image = pyfits.open( fitsfile )
    hdr = image[0].header
    instrument = hdr['INSTRUME']
    detector   = hdr['DETECTOR']
    camera = instrument + '-' + detector
    pixscale = getpixscale( fitsfile, returntuple=False )
    if camera == 'ACS-WFC' :
        conv_width = 3.5 * 0.05 / pixscale
    elif camera == 'WFC3-UVIS' :
        conv_width = 3.5 * 0.04 / pixscale
    elif camera == 'WFC3-IR' :
        conv_width = 2.5 * 0.13 / pixscale
    else :
        conv_width = 2.5
    return( conv_width )

def getskysigma( filelist, usemode=False, nclip=3 ):
    """ Compute the median sky noise for the given image or list of images.
    The default uses the skysigma algorithm as stated in the drizzlepac manual (v1.0, 2012)
    instead of the one implemented in drizzlepac/catalogs.py.  That is, we
    use 1.5 times the sigma-clipped standard deviation of the image.  With usemode
    set to True, we instead use the square root of twice the mode.
    """
    from stsci import imagestats
    from numpy import median, sqrt, abs
    if isinstance( filelist, str ):
        filelist = [ filelist ]

    modelist, stddevlist = [], []
    for file in filelist :
        hdulist = pyfits.open( file )

        extnamelist = [ ext.name.upper() for ext in hdulist ]
        if 'SCI' in extnamelist :
            iextlist = [ iext for iext in range(len(extnamelist))
                         if extnamelist[iext]=='SCI' ]
        else :
            iextlist = [ 0 ]
        for iext in iextlist:
            ext = hdulist[ iext ]
            istats = imagestats.ImageStats(
                ext.data, nclip=nclip, fields='mode,stddev', binwidth=0.01 )
            stddevlist.append( istats.stddev )
            modelist.append( abs( istats.mode ))
    if usemode :
        return( sqrt( 2.0 * median( modelist ) ))
    return( 1.5 * median( stddevlist ) )

def getpixscale( fitsfile, returntuple=False ):
    """ compute the pixel scale of the reference pixel in arcsec/pix in
    each direction from the fits header cd matrix.
    With returntuple=True, return the two pixel scale values along the x and y
    axes.  For returntuple=False, return the average of the two.
    """
    from math import sqrt

    if isinstance(fitsfile, str) :
        fitsfile = pyfits.open( fitsfile )
    if isinstance( fitsfile, pyfits.header.Header ) :
        hdr = fitsfile
    elif isinstance( fitsfile, pyfits.hdu.hdulist.HDUList ) :
        extnamelist = [ hdu.name.lower() for hdu in fitsfile ]
        if 'sci' in extnamelist :
            isci = extnamelist.index('sci')
            hdr = fitsfile[isci].header
        else :
            hdr = fitsfile[0].header
    elif isinstance( fitsfile, pyfits.hdu.image.PrimaryHDU ) :
        hdr = fitsfile.header
    else :
        raise RuntimeError( 'input object type %s is unrecognized')

    if 'CD1_1' in hdr :
        cd11 = hdr['CD1_1']
        cd12 = hdr['CD1_2']
        cd21 = hdr['CD2_1']
        cd22 = hdr['CD2_2']

        # define the sign based on determinant
        det = cd11*cd22 - cd12*cd21
        if det<0 : sgn = -1
        else : sgn = 1

        if cd12==0 and cd21==0 :
            # no rotation: x=RA, y=Dec
            cdelt1 = cd11
            cdelt2 = cd22
        else :
            cdelt1 = sgn*sqrt(cd11**2 + cd12**2)
            cdelt2 = sqrt(cd22**2 + cd21**2)
    elif 'CDELT1' in list(hdr.keys()) and (hdr['CDELT1']!=1 and hdr['CDELT2']!=1) :
        cdelt1 = hdr['CDELT1']
        cdelt2 = hdr['CDELT2']

    cdelt1 = cdelt1  * 3600.
    cdelt2 = cdelt2  * 3600.

    if returntuple :
        return( cdelt1, cdelt2 )
    else :
        return( (abs(cdelt1)+abs(cdelt2)) / 2. )

def getfwhmpix( imfile ):
    """ Return the FWHM in pixels for this image (designed for HST images)
    """
    hdr = pyfits.getheader( imfile )
    instrument, detector = '',''
    if 'CAMERA' in hdr :
        instrument = hdr['CAMERA']
        detector = ''
    elif 'INSTRUME' in hdr :
        instrument = hdr['INSTRUME']
    if 'DETECTOR' in hdr :
        detector = hdr['DETECTOR']
    if 'TELESCOP' in hdr :
        telescope = hdr['TELESCOP']
    camera = '-'.join([instrument,detector]).rstrip('-')
    if camera == 'ACS-WFC' :
        fwhmarcsec = 0.13
    elif camera == 'WFC3-UVIS' :
        fwhmarcsec = 0.07
    elif camera == 'WFC3-IR' :
        fwhmarcsec = 0.14
    elif telescope=='HST' :
        fwhmarcsec = 0.1
    else :
        print(("WARNING : no instrument, detector or telescope identified for %s"%imfile))
        print("  so we are arbitrarily setting the FWHM to 2.5 pixels for centroiding")
        return( 2.5 )
    pixscale = getpixscale( imfile )
    fwhmpix = fwhmarcsec / pixscale
    return( fwhmpix )


def cntrd(img, x, y, fwhm, silent=False, debug=False, extendbox = False, keepcenter = False):
    """
    This function is from the IDL Astronomy Users Library
    converted to python by David O. Jones - 2/13/14

    ;+
    ;  NAME:
    ;       CNTRD
    ;  PURPOSE:
    ;       Compute the centroid  of a star using a derivative search
    ; EXPLANATION:
    ;       CNTRD uses an early DAOPHOT "FIND" centroid algorithm by locating the
    ;       position where the X and Y derivatives go to zero.   This is usually a
    ;       more "robust"  determination than a "center of mass" or fitting a 2d
    ;       Gaussian  if the wings in one direction are affected by the presence
    ;       of a neighboring star.
    ;
    ;  CALLING SEQUENCE:
    ;       CNTRD, img, x, y, xcen, ycen, [ fwhm , /KEEPCENTER, /SILENT, /DEBUG
    ;                                       EXTENDBOX = ]
    ;
    ;  INPUTS:
    ;       IMG - Two dimensional image array
    ;       X,Y - Scalar or vector integers giving approximate integer stellar
    ;             center
    ;
    ;  OPTIONAL INPUT:
    ;       FWHM - floating scalar; Centroid is computed using a box of half
    ;               width equal to 1.5 sigma = 0.637* FWHM.  CNTRD will prompt
    ;               for FWHM if not supplied
    ;
    ;  OUTPUTS:
    ;       XCEN - the computed X centroid position, same number of points as X
    ;       YCEN - computed Y centroid position, same number of points as Y,
    ;              floating point
    ;
    ;       Values for XCEN and YCEN will not be computed if the computed
    ;       centroid falls outside of the box, or if the computed derivatives
    ;       are non-decreasing.   If the centroid cannot be computed, then a
    ;       message is displayed and XCEN and YCEN are set to -1.
    ;
    ;  OPTIONAL OUTPUT KEYWORDS:
    ;       /SILENT - Normally CNTRD prints an error message if it is unable
    ;               to compute the centroid.   Set /SILENT to suppress this.
    ;       /DEBUG - If this keyword is set, then CNTRD will display the subarray
    ;               it is using to compute the centroid.
    ;       EXTENDBOX = {non-negative positive integer}.   CNTRD searches a box with
    ;              a half width equal to 1.5 sigma  = 0.637* FWHM to find the
    ;              maximum pixel.    To search a larger area, set EXTENDBOX to
    ;              the number of pixels to enlarge the half-width of the box.
    ;              Default is 0; prior to June 2004, the default was EXTENDBOX= 3
    ;       /KeepCenter = By default, CNTRD finds the maximum pixel in a box
    ;              centered on the input X,Y coordinates, and then extracts a new
    ;              box about this maximum pixel.   Set the /KeepCenter keyword
    ;              to skip then step of finding the maximum pixel, and instead use
    ;              a box centered on the input X,Y coordinates.
    ;  PROCEDURE:
    ;       Maximum pixel within distance from input pixel X, Y  determined
    ;       from FHWM is found and used as the center of a square, within
    ;       which the centroid is computed as the value (XCEN,YCEN) at which
    ;       the derivatives of the partial sums of the input image over (y,x)
    ;       with respect to (x,y) = 0.    In order to minimize contamination from
    ;       neighboring stars stars, a weighting factor W is defined as unity in
    ;       center, 0.5 at end, and linear in between
    ;
    ;  RESTRICTIONS:
    ;       (1) Does not recognize (bad) pixels.   Use the procedure GCNTRD.PRO
    ;           in this situation.
    ;       (2) DAOPHOT now uses a newer algorithm (implemented in GCNTRD.PRO) in
    ;           which centroids are determined by fitting 1-d Gaussians to the
    ;           marginal distributions in the X and Y directions.
    ;       (3) The default behavior of CNTRD changed in June 2004 (from EXTENDBOX=3
    ;           to EXTENDBOX = 0).
    ;       (4) Stone (1989, AJ, 97, 1227) concludes that the derivative search
    ;           algorithm in CNTRD is not as effective (though faster) as a
    ;            Gaussian fit (used in GCNTRD.PRO).
    ;  MODIFICATION HISTORY:
    ;       Written 2/25/86, by J. K. Hill, S.A.S.C., following
    ;       algorithm used by P. Stetson in DAOPHOT.
    ;       Allowed input vectors        G. Hennessy       April,  1992
    ;       Fixed to prevent wrong answer if floating pt. X & Y supplied
    ;               W. Landsman        March, 1993
    ;       Convert byte, integer subimages to float  W. Landsman  May 1995
    ;       Converted to IDL V5.0   W. Landsman   September 1997
    ;       Better checking of edge of frame David Hogg October 2000
    ;       Avoid integer wraparound for unsigned arrays W.Landsman January 2001
    ;       Handle case where more than 1 pixel has maximum value W.L. July 2002
    ;       Added /KEEPCENTER, EXTENDBOX (with default = 0) keywords WL June 2004
    ;       Some errrors were returning X,Y = NaN rather than -1,-1  WL Aug 2010
    ;-      """
    import numpy as np

    sz_image = np.shape(img)

    xsize = sz_image[1]
    ysize = sz_image[0]
    # dtype = sz_image[3]              ;Datatype

    #   Compute size of box needed to compute centroid

    if not extendbox: extendbox = 0
    nhalf =  int(0.637*fwhm)
    if nhalf < 2: nhalf = 2
    nbox = 2*nhalf+1             #Width of box to be used to compute centroid
    nhalfbig = nhalf + extendbox
    nbig = nbox + extendbox*2        #Extend box 3 pixels on each side to search for max pixel value
    if not np.iterable(x) : npts = 1
    else: npts = len(x)
    if npts == 1:
        xcen = float(x)
        ycen = float(y)
    else:
        xcen = x.astype(float)
        ycen = y.astype(float)
    ix = np.round( x )          #Central X pixel        ;Added 3/93
    iy = np.round( y )          #Central Y pixel

    if npts == 1:
        x,y,ix,iy,xcen,ycen = [x],[y],[ix],[iy],[xcen],[ycen]
    for i in range(npts):        #Loop over X,Y vector
        pos = str(x[i]) + ' ' + str(y[i])
        if not keepcenter:
            if ( (ix[i] < nhalfbig) or ((ix[i] + nhalfbig) > xsize-1) or \
                     (iy[i] < nhalfbig) or ((iy[i] + nhalfbig) > ysize-1) ):
                if not silent:
                    print(('Position '+ pos + ' too near edge of image'))
                    xcen[i] = -1   ; ycen[i] = -1
                    continue

            bigbox = img[int(iy[i]-nhalfbig) : int(iy[i]+nhalfbig+1), int(ix[i]-nhalfbig) : int(ix[i]+nhalfbig+1)]

            #  Locate maximum pixel in 'NBIG' sized subimage
            goodrow = np.where(bigbox == bigbox)
            mx = np.max( bigbox[goodrow])     #Maximum pixel value in BIGBOX
            mx_pos = np.where(bigbox.reshape(np.shape(bigbox)[0]*np.shape(bigbox)[1]) == mx)[0] #How many pixels have maximum value?
            Nmax = len(mx_pos)
            idx = mx_pos % nbig          #X coordinate of Max pixel
            idy = mx_pos / nbig            #Y coordinate of Max pixel
            if Nmax > 1:                 #More than 1 pixel at maximum?
                idx = np.round(np.sum(idx)/Nmax)
                idy = np.round(np.sum(idy)/Nmax)
            else:
                idx = idx[0]
                idy = idy[0]

            xmax = ix[i] - (nhalf+extendbox) + idx  #X coordinate in original image array
            ymax = iy[i] - (nhalf+extendbox) + idy  #Y coordinate in original image array
        else:
            xmax = ix[i]
            ymax = iy[i]

#; ---------------------------------------------------------------------
#; check *new* center location for range
#; added by Hogg

        if ( (xmax < nhalf) or ((xmax + nhalf) > xsize-1) or \
                 (ymax < nhalf) or ((ymax + nhalf) > ysize-1) ):
            if not silent:
                print(('Position '+ pos + ' moved too near edge of image'))
                xcen[i] = -1 ; ycen[i] = -1
                continue
#; ---------------------------------------------------------------------
#
#;  Extract smaller 'STRBOX' sized subimage centered on maximum pixel

        strbox = img[int(ymax-nhalf) : int(ymax+nhalf+1), int(xmax-nhalf) : int(xmax+nhalf+1)]
# if (dtype NE 4) and (dtype NE 5) then strbox = float(strbox)

        if debug:
            print('Subarray used to compute centroid:')
            print(strbox)

        ir = (nhalf-1)
        if ir < 1: ir = 1
        dd = np.arange(nbox-1).astype(int) + 0.5 - nhalf
    # Weighting factor W unity in center, 0.5 at end, and linear in between
        w = 1. - 0.5*(np.abs(dd)-0.5)/(nhalf-0.5)
        sumc   = np.sum(w)

    #; Find X centroid
        deriv = np.roll(strbox,-1,axis=1) - strbox    #;Shift in X & subtract to get derivative
        deriv = deriv[nhalf-ir:nhalf+ir+1,0:nbox-1] #;Don't want edges of the array
        deriv = np.sum( deriv, 0 )                    #    ;Sum X derivatives over Y direction
        sumd   = np.sum( w*deriv )
        sumxd  = np.sum( w*dd*deriv )
        sumxsq = np.sum( w*dd**2 )

        if sumxd >= 0:    # ;Reject if X derivative not decreasing

            if not silent:
                print(('Unable to compute X centroid around position '+ pos))
                xcen[i]=-1 ; ycen[i]=-1
                continue

        dx = sumxsq*sumd/(sumc*sumxd)
        if ( np.abs(dx) > nhalf ):    #Reject if centroid outside box
            if not silent:
                print(('Computed X centroid for position '+ pos + ' out of range'))
                xcen[i]=-1 ; ycen[i]=-1
                continue

        xcen[i] = xmax - dx    #X centroid in original array

#  Find Y Centroid

        deriv = np.roll(strbox,-1,axis=0) - strbox    #;Shift in X & subtract to get derivative
        deriv = deriv[0:nbox-1,nhalf-ir:nhalf+ir+1]
        deriv = np.sum( deriv,1 )
        sumd =   np.sum( w*deriv )
        sumxd =  np.sum( w*deriv*dd )
        sumxsq = np.sum( w*dd**2 )

        if (sumxd >= 0):  #;Reject if Y derivative not decreasing
            if not silent:
                print(('Unable to compute Y centroid around position '+ pos))
                xcen[i] = -1 ; ycen[i] = -1
                continue

        dy = sumxsq*sumd/(sumc*sumxd)
        if (np.abs(dy) > nhalf):  #Reject if computed Y centroid outside box
            if not silent:
                print(('Computed X centroid for position '+ pos + ' out of centering box.'))
                xcen[i]=-1 ; ycen[i]=-1
                continue

        ycen[i] = ymax-dy

    if npts == 1: xcen,ycen = xcen[0],ycen[0]
    return(xcen,ycen)
