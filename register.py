#! /usr/bin/env python
# S.Rodney 2014.02.27

import os
import pyfits
# import exceptions

from stsci import tools
from drizzlepac import tweakreg
import stwcs
import exposures
import exceptions


def RunTweakReg( files='*fl?.fits', refcat=None, refim=None,
                 wcsname='SNDRIZPIPE', refnbright=None,
                 rfluxmax=None, rfluxmin=None, searchrad=1.0,
                 # fluxmax=None, fluxmin=None,
                 peakmin=None, peakmax=None, threshold=4.0,
                 minobj=10, nbright=None, fitgeometry='rscale',
                 interactive=False, clean=False, clobber=False,
                 verbose=False, debug=False ):
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
        raise exceptions.RuntimeError(
            "List of input files has no real files: %s"%str(files))

    # pre-clean any existing WCS header info
    # clearAltWCS( filelist )

    hdr1 = pyfits.getheader( filelist[0] )
    conv_width = getconvwidth(filelist[0])

    if (nbright and nbright<3) or minobj<3:
        use2dhist=False
    else :
        use2dhist=True

    # check first if the WCS wcsname already exists in the first image
    wcsnamelist = [ hdr1[k] for k in hdr1.keys() if k.startswith('WCSNAME') ]
    if wcsname in wcsnamelist and not clobber :
        print(
            "WCSNAME %s already exists in %s"%(wcsname,filelist[0]) +
            "so I'm skipping over this tweakreg step." +
            "Re-run with clobber=True if you really want it done." )
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

    if interactive : 
        while True :
            if nbright :
                # make source catalogs for each SCI extension
                srcCatListFile = mkSourceCatList(
                    filelist, filelist[0].split('_')[0]+'_cat.list',
                    threshold=threshold, peakmin=peakmin, peakmax=peakmax )
                if verbose :
                    print( "Generated a list of source catalogs : %s"%srcCatListFile)
                xcol, ycol, fluxcol = 1,2,3
            else :
                srcCatListFile=None
                nbright=None
                xcol, ycol, fluxcol = 1,2,None

            print( "sndrizzle.register:  Running a tweakreg loop interactively.")
            tweakreg.TweakReg(files, updatehdr=False, wcsname='TWEAK',
                              use2dhist=use2dhist,
                              see2dplot=True, residplot='both',
                              fitgeometry=fitgeometry, refcat=refcat,
                              refimage=refim, refxcol=1, refycol=2,
                              refxyunits='degrees', rfluxcol=rfluxcol,
                              rfluxunits=rfluxunits, refnbright=refnbright,
                              rfluxmax=rfluxmax, rfluxmin=rfluxmin,
                              # fluxmax=fluxmax, fluxmin=fluxmin,
                              peakmax=peakmax, peakmin=peakmin,
                              searchrad=searchrad, conv_width=conv_width,
                              threshold=threshold, separation=0,
                              tolerance=1.0, minobj=minobj,
                              catfile=srcCatListFile, nbright=nbright,
                              xcol=xcol, ycol=ycol,
                              fluxcol=fluxcol, fluxunits='cps',
                              clean=(clean and not nbright),
                              writecat=(not nbright) )
            print( "==============================\n sndrizzle.register:\n")
            userin = raw_input("Adopt these tweakreg settings? y/[n]").lower()
            if userin.startswith('y'): 
                print("OK. Proceeding to update headers.")
                break
            print("Current tweakreg/imagefind parameters:")
            printfloat("   refnbright = %i  # number of brightest refcat sources to use", refnbright)
            printfloat("   rfluxmin = %.1f  # min flux for refcat sources", rfluxmin)
            printfloat("   rfluxmax = %.1f  # max flux for refcat sources", rfluxmax)
            printfloat("   searchrad  = %.1f  # matching search radius (arcsec)", searchrad )
            printfloat("   peakmin    = %.1f  # min peak flux for detected sources", peakmin )
            printfloat("   peakmax    = %.1f  # max peak flux for detected sources", peakmax )
            # printfloat("   fluxmin    = %.1f  # min total flux for detected sources", fluxmin )
            # printfloat("   fluxmax    = %.1f  # max total flux for detected sources", fluxmax )
            printfloat("   threshold  = %.1f  # detection threshold in sigma ", threshold )
            printfloat("   fitgeometry= %s  # fitting geometry [shift,rscale] ", fitgeometry )
            print('Adjust parameters using "parname = value" syntax.') 
            print('Enter "run" to re-run tweakreg with new parameters.') 
            while True : 
                userin = raw_input("   ").lower()
                if userin.startswith('run') : break
                try : 
                    parname = userin.split('=')[0].strip()
                    value = userin.split('=')[1].strip()
                except : 
                    print('Must use the "parname = value" syntax. Try again') 
                    continue
                if parname=='refnbright' : refnbright=int( value )
                elif parname=='rfluxmin' : rfluxmin=float( value )
                elif parname=='rfluxmax' : rfluxmax=float( value )
                elif parname=='searchrad' : searchrad=float( value )
                elif parname=='peakmin' : peakmin=float( value )
                elif parname=='peakmax' : peakmax=float( value )
                # elif parname=='fluxmax' : fluxmax=float( value )
                # elif parname=='fluxmin' : fluxmin=float( value )
                elif parname=='threshold' : threshold=float( value )
                elif parname=='fitgeometry' : fitgeometry=value

    print( "==============================\n sndrizzle.register:\n")
    print( "  Final tweakreg run for updating headers.")

    if nbright :
        # make source catalogs for each SCI extension
        srcCatListFile = mkSourceCatList(
            filelist, filelist[0].split('_')[0]+'_cat.list',
            threshold=threshold, peakmin=peakmin, peakmax=peakmax )
        if verbose :
            print( "Generated a list of source catalogs : %s"%srcCatListFile)
        xcol, ycol, fluxcol = 1,2,3
    else :
        srcCatListFile=None
        nbright=None
        xcol, ycol, fluxcol = 1,2,None

    print( 'fitgeometry = %s'%fitgeometry )
    tweakreg.TweakReg(files, updatehdr=True, wcsname=wcsname,
                      use2dhist=use2dhist,
                      see2dplot=False, residplot='No plot',
                      fitgeometry=fitgeometry, refcat=refcat, refimage=refim,
                      refxcol=1, refycol=2, refxyunits='degrees', 
                      refnbright=refnbright, rfluxcol=rfluxcol, rfluxunits=rfluxunits,
                      rfluxmax=rfluxmax, rfluxmin=rfluxmin,
                      # fluxmax=fluxmax, fluxmin=fluxmin,
                      peakmax=peakmax, peakmin=peakmin,
                      searchrad=searchrad, conv_width=conv_width, threshold=threshold,
                      catfile=srcCatListFile, nbright=nbright,
                      xcol=xcol, ycol=ycol, fluxcol=fluxcol, fluxunits='cps',
                      separation=0, tolerance=1.0, minobj=minobj,
                      clean=clean, writecat=not nbright )
    return( wcsname )


# noinspection PyUnreachableCode
def SingleStarReg( imfile, refimfile, xy=[], xyref=[], wcsname='SINGLESTAR',
                   computesig=True, skysigma=0,
                   threshold=4.0, peakmin=None, peakmax=None,
                   nsigma=1.5, fluxmin=None, fluxmax=None, sciext=None,
                   verbose=True, clobber=True ):
    """ Update the WCS of imfile so that it matches the WCS of the refimfile,
    using a single star to define the necessary shift.
    If xy or xyref are provided, then assume the star is located within
    searchrad pixels of that position in the imfile or the refimfile, respectively.
    If either of those pixel coordinates are not provided, then use the
    brightest star in the image.
    """
    from astropy.io import ascii
    from drizzlepac.updatehdr import updatewcs_with_shift

    topdir = os.path.abspath( '.' )
    if not xy :
        # locate stars in imfile, pick out the brightest one
        imfiledir = os.path.dirname( imfile )
        imfilebase = os.path.basename( imfile )
        os.chdir( imfiledir )
        xycatfile = mkSourceCatalog(
            imfilebase, computesig=computesig, skysigma=skysigma, nsigma=nsigma,
            threshold=threshold, peakmin=peakmin, peakmax=peakmax,
            fluxmin=fluxmin, fluxmax= fluxmax  )[0]
        xycat = ascii.read( xycatfile )
        ibrightest = xycat['col3'].argmax()
        xy = [ xycat['col1'][ibrightest], xycat['col2'][ibrightest] ]
        os.chdir( topdir )
    if not xyref :
        # locate stars in refimfile, pick out the brightest one
        refimfiledir = os.path.dirname( refimfile )
        refimfilebase = os.path.basename( refimfile )
        os.chdir( refimfiledir )
        xyrefcatfile = mkSourceCatalog(
            refimfilebase, computesig=computesig, skysigma=skysigma, nsigma=nsigma,
            threshold=threshold, peakmin=peakmin, peakmax=peakmax,
            fluxmin=fluxmin, fluxmax= fluxmax  )[0]
        xyrefcat = ascii.read( xyrefcatfile )
        ibrightest = xyrefcat['col3'].argmax()
        xyref = [ xyrefcat['col1'][ibrightest], xyrefcat['col2'][ibrightest] ]
        os.chdir( topdir )

    #return( np.array([xy]), np.array([xyref]) )
    # compute the pixel shift from xy to xyref
    xshift = xyref[0] - xy[0]
    yshift = xyref[1] - xy[1]

    # update imfile with the WCS shift
    if not sciext :
        image = pyfits.open( imfile )
        extnamelist = [ ext.name.upper() for ext in image ]
        if 'SCI' in extnamelist :
            sciext='SCI'
        elif 'PRIMARY' in extnamelist :
            sciext='PRIMARY'
        else :
            raise exceptions.RuntimeError(
                "For the image %s you must provide the sciext keyword."%(
                    imfile ) )

    updatewcs_with_shift(imfile, refimfile, wcsname=wcsname,
                         rot=0.0, scale=1.0, xsh=xshift, ysh=yshift,
                         fit=None, xrms=None, yrms=None, verbose=verbose,
                         force=clobber, sciext=sciext )


def clearAltWCS( fltlist ) : 
    """ pre-clean any alternate wcs solutions from flt headers"""
    from drizzlepac import wcs_functions
    from drizzlepac.imageObject import imageObject

    for fltfile in fltlist : 
        hdulist = pyfits.open( fltfile, mode='update' )
        extlist = range( len(hdulist) )
        extlist = []
        for ext in range( len(hdulist) ) : 
            if 'WCSNAME' in hdulist[ext].header : extlist.append( ext )
            stwcs.wcsutil.restoreWCS( hdulist, ext, wcskey='O' )
        if len(extlist) : 
            wcs_functions.removeAllAltWCS(hdulist, extlist)
        hdulist.flush()
        hdulist.close()


def printfloat( fmtstr, value ):
    """ Print a float value using the given format string, handling
    None and NaN values appropriately
    """
    try :
        print( fmtstr % value ) 
    except : 
        pct = fmtstr.find('%')
        f = pct + fmtstr[pct:].find('f') + 1
        if value == None : 
            print( fmtstr[:pct] + ' None ' + fmtstr[f:] )
        elif value == float('nan') :
            print( fmtstr[:pct] + ' NaN ' + fmtstr[f:] )
        else : 
            print( fmtstr[:pct] + ' ??? ' + fmtstr[f:] )


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
        print >> fout, '%s %s'%( imfile, '  '.join(catlist) )
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
            wcs, mode='automatic',catalog=None, computesig=computesig,
            skysigma=skysigma, threshold=threshold, conv_width=conv_width,
            peakmin=peakmin, peakmax=peakmax,
            fluxmin=fluxmin, fluxmax= fluxmax,
            nsigma=nsigma, )
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

def getpixscale( fitsfile, returntuple=False ):
    """ compute the pixel scale of the reference pixel in arcsec/pix in
    each direction from the fits header cd matrix.
    With returntuple=True, return the two pixel scale values along the x and y
    axes.  For returntuple=False, return the average of the two.
    """
    from math import sqrt
    import pyfits

    if isinstance(fitsfile, basestring) :
        fitsfile = pyfits.open( fitsfile )
    if isinstance( fitsfile, pyfits.header.Header ) :
        hdr = fitsfile
    elif isinstance( fitsfile, pyfits.hdu.hdulist.HDUList ) :
        if 'sci' in [ hdu.name.lower() for hdu in fitsfile ] :
            hdr = fitsfile['SCI'].header
        else :
            hdr = fitsfile[0].header
    elif isinstance( fitsfile, pyfits.hdu.image.PrimaryHDU ) :
        hdr = fitsfile.header
    else :
        raise exceptions.RuntimeError( 'input object type %s is unrecognized')

    # if plate scale is already defined,
    # (as in the fits standard) just return it
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
    elif 'CDELT1' in hdr.keys() and (hdr['CDELT1']!=1 and hdr['CDELT2']!=1) :
        cdelt1 = hdr['CDELT1']
        cdelt2 = hdr['CDELT2']

    cdelt1 = cdelt1  * 3600.
    cdelt2 = cdelt2  * 3600.

    if returntuple :
        return( cdelt1, cdelt2 )
    else :
        return( (abs(cdelt1)+abs(cdelt2)) / 2. )

