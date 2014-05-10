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
                 fluxmin=None, fluxmax=None, threshold=4.0,
                 minobj=10, fitgeometry='rscale',
                 interactive=False, clobber=False, debug=False ):
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
    instrument = hdr1['INSTRUME']
    detector   = hdr1['DETECTOR']
    camera = instrument + '-' + detector
    pixscale = getpixscale( filelist[0] )
    if camera == 'ACS-WFC' :
        conv_width = 3.5 * 0.05 / pixscale
    elif camera == 'WFC3-UVIS' : 
        conv_width = 3.5 * 0.04 / pixscale
    elif camera == 'WFC3-IR' : 
        conv_width = 2.5 * 0.13 / pixscale
    else : 
        conv_width = 2.5

    # check first if the WCS wcsname already exists in the first image
    wcsnamelist = [ hdr1[k] for k in hdr1.keys() if k.startswith('WCSNAME') ]
    if wcsname in wcsnamelist and not clobber :
        print(
            "WCSNAME %s already exists in %s"%(wcsname,filelist[0]) +
            "so I'm skipping over this tweakreg step." +
            "Re-run with clobber=True if you really want it done." )
        return( wcsname )

    if refcat :
        refCatalog = ascii.read( refcat )
        rfluxcol, rfluxunits = None, None
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
            print( "sndrizzle.register:  Running a tweakreg loop interactively.")
            tweakreg.TweakReg(files, updatehdr=False, wcsname='TWEAK',
                              see2dplot=True, residplot='both', 
                              fitgeometry=fitgeometry, refcat=refcat,
                              refimage=refim, refxcol=1, refycol=2,
                              refxyunits='degrees', rfluxcol=rfluxcol,
                              rfluxunits=rfluxunits, refnbright=refnbright,
                              rfluxmax=rfluxmax, rfluxmin=rfluxmin,
                              searchrad=searchrad, conv_width=conv_width,
                              threshold=threshold, separation=0,
                              tolerance=searchrad, minobj=minobj,
                              clean=(not (interactive or debug) ),
                              writecat=(interactive or debug) )
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
            printfloat("   fluxmin    = %.1f  # min total flux for detected sources", fluxmin )
            printfloat("   fluxmax    = %.1f  # max total flux for detected sources", fluxmax )
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
                elif parname=='fluxmin' : fluxmin=float( value )
                elif parname=='fluxmax' : fluxmax=float( value )
                elif parname=='threshold' : threshold=float( value )
                elif parname=='fitgeometry' : fitgeometry=value

    print( "==============================\n sndrizzle.register:\n")
    print( "  Final tweakreg run for updating headers.")
    tweakreg.TweakReg(files, updatehdr=True, wcsname=wcsname,
                      see2dplot=False, residplot='No plot', 
                      fitgeometry=fitgeometry, refcat=refcat, refimage=refim,
                      refxcol=1, refycol=2, refxyunits='degrees', 
                      refnbright=refnbright, rfluxcol=rfluxcol, rfluxunits=rfluxunits,
                      rfluxmax=rfluxmax, rfluxmin=rfluxmin,
                      searchrad=searchrad, conv_width=conv_width, threshold=threshold, 
                      separation=0, tolerance=searchrad, minobj=minobj,
                      clean=(not debug) )
    return( wcsname )



def intraVisit( fltlist, fluxmin=None, fluxmax=None, threshold=4.0,
                minobj=10, interactive=False, clobber=False, debug=False ):
    """ 
    Run tweakreg on a list of flt images belonging to the same visit, 
    updating their WCS for alignment with the WCS of the first in the list. 

    When interactive is True, the user will be presented with the
    tweakreg plots (2d histogram, residuals, etc) to review, and will
    be given the opportunity to adjust the tweakreg parameters and
    re-run.
    """
    if debug : import pdb; pdb.set_trace() 
    wcsname = RunTweakReg(
        fltlist, refcat=None, wcsname='INTRAVIS', searchrad=1.0,
        fluxmin=fluxmin, fluxmax=fluxmax, fitgeometry='shift', minobj=minobj,
        threshold=threshold, interactive=interactive,  clobber=clobber )
    return( wcsname )


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


def mkSourceCatalog( imfile, computesig=True, skysigma=0,
                     threshold=4.0, fluxmin=None, fluxmax=None ) :
    """NOT FUNCTIONAL"""
    import pywcs
    from drizzlepac import catalogs

    image = pyfits.open( imfile )
    hdr = image[0].header
    data = image[0].data

    instrument = hdr['INSTRUME']
    detector   = hdr['DETECTOR']
    camera = instrument + '-' + detector
    if camera == 'ACS-WFC' : 
        conv_width = 3.5
    elif camera == 'WFC3-UVIS' : 
        conv_width = 3.5
    elif camera == 'WFC3-IR' : 
        conv_width = 2.5
    else : 
        conv_width = 2.5


    # PROBLEM :
    err = """
AttributeError: 'WCS' object has no attribute 'extname'
> /usr/local/Ureka/python/lib/python2.7/site-packages/drizzlepac/catalogs.py(268)__init__()
    267         Catalog.__init__(self,wcs,catalog_source,**kwargs)
--> 268         if self.wcs.extname == ('',None): self.wcs.extname = (0)
    269         self.source = pyfits.getdata(self.wcs.filename,ext=self.wcs.extname)
    """

    wcs = pywcs.WCS( hdr )
    wcs = pywcs.WCS( header=hdr, fobj=image )

    imcat = catalogs.generateCatalog(
        wcs, mode='automatic',catalog=None,
        computesig=computesig, skysigma=skysigma, threshold=threshold,
        fluxmin=fluxmin, fluxmax=fluxmax, conv_width=conv_width )
    return( imcat )


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

