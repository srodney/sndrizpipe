#! /usr/bin/env python
# S.Rodney 2014.02.25

import os
from astropy.io import fits as pyfits
import exceptions

from stsci import tools
from drizzlepac import tweakreg, astrodrizzle

def hotpixPostargClean( flt1, flt2, verbose=False ):
    """
    Remove all CR flags from a pair of WFC3-IR flt DQ arrays except those that
    are most likely unflagged hot pixels, identified by getting a 4096 flag in
    both exposures.

    :param fltlist: a list of WFC3 IR flt files from a single dither sequence
       that already have 4096 CR flags in their DQ arrays from astrodrizzle
    :return:
    """
    import numpy as np
    im1 = pyfits.open( flt1, mode='update' )
    im2 = pyfits.open( flt2, mode='update' )

    dq1 = im1[3].data
    dq2 = im2[3].data

    crflags1 = dq1 & 4096
    crflags2 = dq2 & 4096
    hotpixflags = ( ( crflags1 & crflags2 ) / 4096 ) * 16

    icrflags1 = np.where( crflags1 )
    icrflags2 = np.where( crflags2 )

    im1[3].data[ icrflags1 ] -= 4096
    im2[3].data[ icrflags2 ] -= 4096

    im1[3].data += hotpixflags
    im2[3].data += hotpixflags

    if verbose :
        ncr1 = len( np.where( np.ravel(crflags1) )[0] )
        ncr2 = len( np.where( np.ravel(crflags2) )[0] )
        nhotpix = len( np.where( np.ravel(hotpixflags) )[0] )
        print( "Removed (%i,%i) CR flags, and re-flagged %i as hot pixels"%(ncr1,ncr2,nhotpix) )

    im1.flush()
    im1.close()
    im2.flush()
    im2.close()


def firstDrizzle( fltlist, outroot, wcskey='', driz_cr=True, clean=True, 
                  driz_cr_snr='5.0 4.5', clobber=False, verbose=True, debug=False ):
    """Run astrodrizzle with almost-default parameters to make a
    native-scale unrotated drz_sci.fits image.
    
    Use the keyword wcskey to specify an alternate WCS solution from
    the headers (e.g. if tweakreg has been run)

    Returns the names of the output sci and wht.fits images.

    """
    if debug : import pdb; pdb.set_trace()

    #convert the input list into a useable list of images for astrodrizzle
    if type( fltlist ) == str : 
        fltlist=tools.parseinput.parseinput(fltlist)[0]

    hdulist=pyfits.open(fltlist[0])
    hdr=hdulist[0].header
    hdulist.close()

    # If we only have one image, skip the median,blot,and driz_cr steps
    docombine=True
    if len(fltlist)==1:
        docombine=False

    # For image sets with fewer than 5 images :
    # if the exposure time in the image set varies by more than a factor of 10
    # then disable CR rejection and wipe out existing CR flags, because the
    # drizzlepac driz_cr step will flag sky noise as CRs.
    if len(fltlist) < 5 :
        etimelist = [ pyfits.getval(flt,'EXPTIME') for flt in fltlist ]
        if len(etimelist)>1:
            if max( etimelist ) / min( etimelist ) > 10 :
                driz_cr = -1

    # define the default astrodrizzle parameters for this camera
    instrument = hdr['INSTRUME']
    detector = hdr['DETECTOR']
    drizpar = getdrizpar( instrument, detector, nexposures=len(fltlist))
    if verbose : print("Drizzling %i flts to make %s."%(len(fltlist),outroot))
    if driz_cr<0 or (driz_cr and docombine):
        resetbits = 0
    else:
        resetbits = 4096
    astrodrizzle.AstroDrizzle(
        fltlist, output=outroot, runfile=outroot+'_astrodriz.log',
        updatewcs=False, wcskey=wcskey, build=False,
        resetbits=resetbits,
        restore=(not clobber), preserve=True, overwrite=clobber, clean=clean,
        median=docombine, blot=(driz_cr>0 and docombine),
        driz_cr=(driz_cr>0 and docombine),
        combine_type='iminmed', driz_cr_snr=driz_cr_snr,
        driz_sep_bits=drizpar['drizbits'], final_bits=drizpar['drizbits'], 
        driz_sep_pixfrac=drizpar['pixfrac'], final_pixfrac=drizpar['pixfrac'], 
        driz_sep_scale=drizpar['pixscale'], final_scale=drizpar['pixscale'])
        # driz_sep_rot='INDEF',  final_rot='INDEF'  )

    if fltlist[0].find('_flc.fits') > 0:
        drzsfx = '_drc'
    elif fltlist[0].find('_flm.fits') > 0:
        drzsfx = '_drc'
    else:
        drzsfx = '_drz'
    outscifile = outroot+drzsfx+'_sci.fits'
    outwhtfile = outroot+drzsfx+'_wht.fits'

    if (not os.path.isfile(outscifile)) or (not os.path.isfile(outwhtfile)):
        if os.path.isfile(outscifile.replace('drc','drz')):
            os.rename(outscifile.replace('drc','drz'), outscifile)
        if os.path.isfile(outwhtfile.replace('drc','drz')):
            os.rename(outwhtfile.replace('drc','drz'), outwhtfile)

    if (not os.path.isfile(outscifile)) or (not os.path.isfile(outwhtfile)):
        raise exceptions.RuntimeError( "astrodriz.py says : Astrodrizzle did not produce the expected output files %s and %s"%(outscifile,outwhtfile) )

    scrubnans( outscifile )
    scrubnans( outwhtfile )

    if clean :
        ctxfile = outscifile.replace( '_sci.fits','_ctx.fits')
        if os.path.isfile( ctxfile ) :
            os.remove( ctxfile )

    return( ( outscifile, outwhtfile ) )


def secondDrizzle( fltlist='*fl?.fits', outroot='final', refimage='',
                   ra=None, dec=None, rot=0, imsize_arcsec=None,
                   naxis12=None, driz_cr=False,  driz_cr_snr='5.0 4.5',
                   singlesci=False, pixscale=None, pixfrac=None,
                   wht_type='IVM', combine_type='iminmed',
                   clean=True, clobber=False, verbose=True, debug=False ) :
    """ 
    Run astrodrizzle on a pile of flt images.
    
    If the user does not specify pixscale, pixfrac, or imsize_arcsec
    then these are set to reasonable defaults for the camera.

    Returns the names of the output sci and wht.fits images.
    """
    if debug : import pdb; pdb.set_trace()
    import badpix

    #convert the input list into a useable list of images for astrodrizzle
    if type( fltlist ) == str : 
        fltlist=tools.parseinput.parseinput(fltlist)[0]

    hdulist=pyfits.open(fltlist[0])
    hdr=hdulist[0].header
    hdulist.close()

    # For image sets with fewer than 5 images :
    # if the exposure time in the image set varies by more than a factor of 10
    # then disable CR rejection and wipe out existing CR flags, because the
    # drizzlepac driz_cr step will flag sky noise as CRs.
    if len(fltlist) < 5 :
        etimelist = [ pyfits.getval(flt,'EXPTIME') for flt in fltlist ]
        if max( etimelist ) / min( etimelist ) > 10 :
            driz_cr = -1

    # define the default astrodrizzle parameters for this camera
    # Note that we fake the number of exposures to be 2, so that we get
    # consistent default pixel scales across all epochs, regardless of the
    # varying number of exposures per epoch.  This can of course be
    # over-ridden by the user specifying pixscale and pixfrac.
    instrument = hdr['INSTRUME']
    detector = hdr['DETECTOR']
    camera = instrument + '-' + detector
    drizpar = getdrizpar( instrument, detector, nexposures=2 )

    if not pixscale : pixscale = drizpar['pixscale']
    if not pixfrac : pixfrac = drizpar['pixfrac']

    # the ra and the dec are the desired ra and dec for the center of the frame
    if ra==None and dec==None and refimage=='' :
        if verbose : print("WARNING: No ra,dec or refimage provided. Using target coordinates of first image.")
        #grab the target ra and dec from the header of the first file
        ra,dec = hdr['RA_TARG'],hdr['DEC_TARG']

    # If we only have one image, skip the median,blot,and driz_cr steps
    docombine=True
    if len(fltlist)==1:
        docombine=False
    combine_nhigh = 0
    if combine_type in ['median', 'imedian'] :
        nflt = len(fltlist)
        if nflt <= 3 :
            combine_nhigh=0
        elif camera=='WFC3-IR' :
            # For WFC3-IR set combine_nhigh to 1 or 2 for CRs that slip through
            # the up-the-ramp sampling
            combine_nhigh= (nflt>5) + (nflt>9)
        else :
            # For ACS and UVIS set combine_nhigh to 1, 2, 3, or 4, keeping
            # an odd number of pixels for the median each time
            combine_nhigh =  (1 + nflt%2)*( 1 + 2*(nflt>7)*(1-nflt%2) + (nflt>11)*(nflt%2))

    if imsize_arcsec is None and naxis12 is None :
        imsize_arcsec = drizpar['imsize_arcsec']
    if naxis12 is not None :
        naxis1 = int(naxis12.split(',')[0])
        naxis2 = int(naxis12.split(',')[1])
    else :
        naxis1 = imsize_arcsec/pixscale
        naxis2 = imsize_arcsec/pixscale
    if driz_cr:
        resetbits = 4096
    else:
        resetbits = 0
    astrodrizzle.AstroDrizzle(
        fltlist, output=outroot, runfile=outroot+'_astrodriz.log',
        updatewcs=False, build=False, resetbits=resetbits,
        restore=False, preserve=True, overwrite=True, clean=clean,
        median=docombine, blot=docombine,
        driz_cr=(driz_cr>0 and docombine),  driz_cr_snr=driz_cr_snr,
        combine_type=combine_type, combine_nhigh=combine_nhigh,
        driz_sep_wcs=True, driz_sep_pixfrac=1.0, driz_sep_scale=pixscale,
        driz_sep_ra=ra, driz_sep_dec=dec, driz_sep_rot=rot,
        driz_sep_bits=drizpar['drizbits'],
        driz_sep_outnx=naxis1, driz_sep_outny=naxis2,
        final_wcs=True, final_pixfrac=pixfrac, final_scale=pixscale,
        final_bits=drizpar['drizbits'],
        final_ra=ra, final_dec=dec, final_rot=rot,
        final_outnx=naxis1, final_outny=naxis2,
        final_wht_type=wht_type)
                    
    if fltlist[0].find('_flc.fits') > 0:
        drzsfx = '_drc'
    elif fltlist[0].find('_flm.fits') > 0:
        drzsfx = '_drc'
    else:
        drzsfx = '_drz'
    outscifile = outroot+drzsfx+'_sci.fits'
    outwhtfile = outroot+drzsfx+'_wht.fits'

    if (not os.path.isfile(outscifile)) or (not os.path.isfile(outwhtfile)):
        if os.path.isfile(outscifile.replace('drc','drz')):
            os.rename(outscifile.replace('drc','drz'), outscifile)
        if os.path.isfile(outwhtfile.replace('drc','drz')):
            os.rename(outwhtfile.replace('drc','drz'), outwhtfile)

    if (not os.path.isfile(outscifile)) or (not os.path.isfile(outwhtfile)):
        raise exceptions.RuntimeError( "astrodriz.py says : Astrodrizzle did not produce the expected output files %s and %s"%(outscifile,outwhtfile) )

    scrubnans( outscifile ) 
    scrubnans( outwhtfile )

    scilist = [ outscifile ]
    whtlist = [ outwhtfile ]
    if singlesci :
        astrodrizzle.AstroDrizzle(
            fltlist, output=outroot, updatewcs=False, resetbits=0,
            restore=False, preserve=False, overwrite=False, clean=False,
            driz_separate=True,
            median=False, blot=False, driz_cr=False, driz_combine=False,
            driz_sep_wcs=True, driz_sep_pixfrac=1.0, driz_sep_scale=pixscale,
            driz_sep_ra=ra, driz_sep_dec=dec, driz_sep_rot=rot,
            driz_sep_bits=drizpar['drizbits'],
            driz_sep_outnx=naxis1, driz_sep_outny=naxis2 )
        # give the output single_sci.fits files some more helpful names
        for fltfile in fltlist :
            if fltfile.endswith('_flc.fits') :
                fltsfx = '_flc.fits'
            elif fltfile.endswith('_flm.fits') :
                fltsfx = '_flm.fits'
            else :
                fltsfx = '_flt.fits'
            scifile0 = fltfile.replace(fltsfx,'_single_sci.fits')
            scifile1 = outroot + '_' + scifile0
            if not os.path.isfile( scifile0 ) :
                raise exceptions.RuntimeError('Missing _single_sci.fits file %s'%scifile0)
            os.rename( scifile0, scifile1 )
            whtfile0 = scifile0.replace( '_sci.fits','_wht.fits')
            whtfile1 = scifile1.replace( '_sci.fits','_wht.fits')
            os.rename( whtfile0, whtfile1 )
            scilist.append( scifile1 )
            whtlist.append( whtfile1 )
            if clean :
                maskfile1 = scifile0.replace( '_single_sci.fits','_sci1_single_mask.fits')
                if os.path.isfile( maskfile1 ) : os.remove( maskfile1 )
                maskfile2 = scifile0.replace( '_single_sci.fits','_sci2_single_mask.fits')
                if os.path.isfile( maskfile2 ) : os.remove( maskfile2 )

    bpxlist = []
    for whtfile in whtlist :
        bpxfile = whtfile.replace('_wht','_bpx')
        bpxfile = badpix.zerowht2badpix(
            whtfile, bpxfile, verbose=verbose, clobber=clobber )
        bpxlist.append( bpxfile )

    if clean :
        for scifile in scilist :
            ctxfile = scifile.replace( '_sci.fits','_ctx.fits')
            if os.path.isfile( ctxfile ) :
                os.remove( ctxfile )

    return( scilist, whtlist, bpxlist )



def getdrizpar( instrument, detector, nexposures=None ) :
    """
    return a dict with defaults for a few key astrodrizzle parameters,
    based on the instrument and detector 
    """
    if nexposures is None :
        nexposures = 2 # set a middle-of-the-road pixscale as the default

    if instrument=='WFC3':
        if detector.startswith('IR'): 
            if nexposures == 1 :
                pixscale=0.13
            elif nexposures == 2 :
                pixscale=0.09
            elif nexposures >= 3 :
                pixscale=0.06
            # drizbits DQ flags allowed as OK :
            # 8192 = up-the-ramp CR; 512 = bad flat (blobs); 64 = warm pixel
            return( {'pixscale':pixscale, 'pixfrac':1.0, 'imsize_arcsec':30,
                     'drizbits':'8192,512'} )
        elif detector.startswith('UV'):
            if nexposures == 1 :
                pixscale=0.04
            elif nexposures >= 2 :
                pixscale=0.03
            # drizbits DQ flags allowed as OK :
            # 64 = warm pixel; 32 = hot pix CTE tail
            return( {'pixscale':pixscale, 'pixfrac':1.0, 'imsize_arcsec':30,
                     'drizbits':'32' } )
    elif instrument=='ACS': 
        if detector.startswith('WFC'):
            if nexposures == 1 :
                pixscale=0.05
            elif nexposures == 2 :
                pixscale=0.04
            elif nexposures >= 3 :
                pixscale=0.03
            # drizbits DQ flags allowed as OK :
            # 64 = warm pixel; 32 = hot pix CTE tail
            return( {'pixscale':pixscale, 'pixfrac':1.0, 'imsize_arcsec':30,
                     'drizbits':'32'} )
    else :
        raise exceptions.RuntimeError('Unknown instrument+detector:  %s %s'%(instrument, detector ) )


def scrubnans( filename, fillval=0 ):
    """Locate any pixels in the given fits file that have values of NaN,
    indef, or inf. Replace them all with the given fillval.
    """
    from numpy import where, isfinite

    hdulist = pyfits.open( filename, mode='update' )
    imdata = hdulist[0].data
    ybad, xbad  = where( 1-isfinite( imdata ) )
    imdata[ybad, xbad] = fillval
    hdulist.flush()
    hdulist.close()
    return()

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Run astrodrizzle on a set of flt, flc, or flm images.')
    parser.add_argument('outroot', metavar='outroot',help='Root name for the output _drz products.')
    parser.add_argument('fltlist', metavar='fltlist',nargs = '?',help='List of input flt/flc.fits files. Wildcards are allowed (e.g. "*fl?.fits").', default="*fl?.fits")
    parser.add_argument('--refimage', metavar='refimage', help='WCS reference image. The flt files will be registered to this image. Full path is required.',default='')
    parser.add_argument('--ra', metavar='ra', type=float, help='R.A. for center of output image (in lieu of a refimage)', default=None)
    parser.add_argument('--dec', metavar='dec', type=float, help='Decl. for center of output image (in lieu of a refimage)', default=None)
    parser.add_argument('--rot', metavar='rot', type=float, help='Rotation (deg E of N) for output image (in lieu of a refimage)', default=0.0)
    parser.add_argument('--imsize', metavar='imsize', type=float, help='Image size [arcsec] of output image (in lieu of a refimage)', default=None)
    parser.add_argument('--pixscale', metavar='pixscale', type=float, help='Pixel scale to use for astrodrizzle.', default=None)
    parser.add_argument('--pixfrac', metavar='pixfrac', type=float, help='Pixfrac to use for astrodrizzle.', default=None)
    parser.add_argument('--wht_type', metavar='wht_type', type=str, help='Type of the weight image.', default='IVM')

    # parser.add_argument('--refdir', metavar='refdir', help='Directory containing HST reference files. The final slash is required.', default='./')

    # parser.add_argument('--drizcr', action='store_true', help='Run the CR rejection stage in astrodrizzle.', default=False)

    parser.add_argument('--clobber', action='store_true', help='Turn on clobber mode. [False]', default=False)
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbosity. [default is ON]')
    parser.add_argument('--quiet', dest='verbose', action='store_false', help='Turn off verbosity. [default is ON]')
    parser.add_argument('--debug', action='store_true', help='Enter debug mode. [False]', default=False)

    args = parser.parse_args()

    # TODO : insert firstdrizzle or seconddrizzle function calls here

