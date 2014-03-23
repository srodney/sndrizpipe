#! /usr/bin/env python
# S.Rodney 2014.02.25

import os
import pyfits
import exceptions

from stsci import tools
from drizzlepac import tweakreg, astrodrizzle

          
def firstDrizzle( fltlist, outroot, wcskey='', driz_cr=True, clean=True, 
                    clobber=False, verbose=True, debug=False ):
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

    # define the default astrodrizzle parameters for this camera
    instrument = hdr['INSTRUME']
    detector = hdr['DETECTOR']
    drizpar = getdrizpar( instrument, detector, nexposures=len(fltlist))
    astrodrizzle.AstroDrizzle( 
        fltlist, output=outroot, runfile=outroot+'_astrodriz.log',
        updatewcs=False, wcskey=wcskey, build=False, resetbits=int(driz_cr and 4096),
        restore=True, preserve=True, overwrite=False, clean=True, 
        driz_sep_bits=drizpar['drizbits'], final_bits=drizpar['drizbits'], 
        driz_sep_pixfrac=drizpar['pixfrac'], final_pixfrac=drizpar['pixfrac'], 
        driz_sep_scale=drizpar['pixscale'], final_scale=drizpar['pixscale'], 
        driz_sep_rot='INDEF',  final_rot='INDEF'  )
    if fltlist[0].find('_flc.fits')>0  : drzsfx = '_drc'
    else: drzsfx = '_drz'    
    outscifile = outroot+drzsfx+'_sci.fits'
    outwhtfile = outroot+drzsfx+'_wht.fits'
    scrubnans( outscifile ) 
    scrubnans( outwhtfile )
    return( ( outscifile, outwhtfile ) )


def secondDrizzle( fltlist='*fl?.fits', outroot='final', refimage='', 
                     ra=None, dec=None, rot=0, imsize_arcsec=None, 
                     pixscale=None, pixfrac=None, wht_type='ERR',
                     clobber=False, verbose=True, debug=False  ) : 
    """ 
    Run astrodrizzle on a pile of flt images.
    
    If the user does not specify pixscale, pixfrac, or imsize_arcsec
    then these are set to reasonable defaults for the camera.

    Returns the names of the output sci and wht.fits images.
    """
    if debug : import pdb; pdb.set_trace()

    #convert the input list into a useable list of images for astrodrizzle
    if type( fltlist ) == str : 
        fltlist=tools.parseinput.parseinput(fltlist)[0]

    hdulist=pyfits.open(fltlist[0])
    hdr=hdulist[0].header
    hdulist.close()

    # define the default astrodrizzle parameters for this camera
    instrument = hdr['INSTRUME']
    detector = hdr['DETECTOR']
    drizpar = getdrizpar( instrument, detector) 

    if not pixscale : pixscale = drizpar['pixscale']
    if not pixfrac : pixfrac = drizpar['pixfrac']
    if not imsize_arcsec : imsize_arcsec = drizpar['imsize_arcsec']

    # the ra and the dec are the desired ra and dec for the center of the frame
    if ra==None and dec==None and refimage=='' :
        if verbose : print("WARNING: No ra,dec or refimage provided. Using target coordinates of first image.")
        #grab the target ra and dec from the header of the first file
        ra,dec = hdr['RA_TARG'],hdr['DEC_TARG']

    imsize_pix = imsize_arcsec/pixscale                     
    astrodrizzle.AstroDrizzle( 
        fltlist, output=outroot, updatewcs=False, resetbits=0,
        restore=False, preserve=True, overwrite=True, clean=True, 
        driz_sep_wcs=True, driz_sep_pixfrac=1.0, driz_sep_scale=pixscale, 
        driz_sep_ra=ra, driz_sep_dec=dec, driz_sep_rot=rot,
        driz_sep_outnx=imsize_pix, driz_sep_outny=imsize_pix, 
        final_wcs=True, final_pixfrac=pixfrac, final_scale=pixscale,
        final_ra=ra, final_dec=dec, final_rot=rot, 
        final_outnx=imsize_pix, final_outny=imsize_pix, 
        final_wht_type=wht_type )
                    
    if fltlist[0].find('_flc.fits')>0  : drzsfx = '_drc'
    else: drzsfx = '_drz'    
    outscifile = outroot+drzsfx+'_sci.fits'
    outwhtfile = outroot+drzsfx+'_wht.fits'

    if (not os.path.isfile( outscifile )) or  (not os.path.isfile( outwhtfile ) ) :
        raise exceptions.RuntimeError( "astrodriz.py says : Astrodrizzle did not produce the expected output files %s and %s"%(outscifile,outwhtfile) )

    scrubnans( outscifile ) 
    scrubnans( outwhtfile )

    return( ( outscifile, outwhtfile ) )



def getdrizpar( instrument, detector, nexposures=None ) :
    """
    return a dict with defaults for a few key astrodrizzle parameters,
    based on the instrument and detector 

    # TODO : adjust parameters based on number of dithers
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
            return( {'pixscale':pixscale, 'pixfrac':1.0, 'imsize_arcsec':200,
                     'drizbits':'8192,512,64'} )
        elif detector.startswith('UV'):
            if nexposures == 1 :
                pixscale=0.04
            elif nexposures >= 2 :
                pixscale=0.03
            return( {'pixscale':pixscale, 'pixfrac':1.0, 'imsize_arcsec':230,
                     'drizbits':'64,32' } )
    elif instrument=='ACS': 
        if detector.startswith('WFC'):
            if nexposures == 1 :
                pixscale=0.05
            elif nexposures == 2 :
                pixscale=0.04
            elif nexposures >= 3 :
                pixscale=0.03
            return( {'pixscale':pixscale, 'pixfrac':1.0, 'imsize_arcsec':300,
                     'drizbits':'64,32'} )
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

    parser = argparse.ArgumentParser(description='Run astrodrizzle on a set of flt or flc images.')
    parser.add_argument('outroot', metavar='outroot',help='Root name for the output _drz products.')
    parser.add_argument('fltlist', metavar='fltlist',nargs = '?',help='List of input flt/flc.fits files. Wildcards are allowed (e.g. "*fl?.fits").', default="*fl?.fits")
    parser.add_argument('--refimage', metavar='refimage', help='WCS reference image. The flt files will be registered to this image. Full path is required.',default='')
    parser.add_argument('--ra', metavar='ra', type=float, help='R.A. for center of output image (in lieu of a refimage)', default=None)
    parser.add_argument('--dec', metavar='dec', type=float, help='Decl. for center of output image (in lieu of a refimage)', default=None)
    parser.add_argument('--rot', metavar='rot', type=float, help='Rotation (deg E of N) for output image (in lieu of a refimage)', default=0.0)
    parser.add_argument('--imsize', metavar='imsize', type=float, help='Image size [arcsec] of output image (in lieu of a refimage)', default=None)
    parser.add_argument('--pixscale', metavar='pixscale', type=float, help='Pixel scale to use for astrodrizzle.', default=None)
    parser.add_argument('--pixfrac', metavar='pixfrac', type=float, help='Pixfrac to use for astrodrizzle.', default=None)
    parser.add_argument('--wht_type', metavar='wht_type', type=str, help='Type of the weight image.', default='ERR')

    # parser.add_argument('--refdir', metavar='refdir', help='Directory containing HST reference files. The final slash is required.', default='./')

    # parser.add_argument('--drizcr', action='store_true', help='Run the CR rejection stage in astrodrizzle.', default=False)

    parser.add_argument('--clobber', action='store_true', help='Turn on clobber mode. [False]', default=False)
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbosity. [default is ON]')
    parser.add_argument('--quiet', dest='verbose', action='store_false', help='Turn off verbosity. [default is ON]')
    parser.add_argument('--debug', action='store_true', help='Enter debug mode. [False]', default=False)

    args = parser.parse_args()

    # TODO : insert firstdrizzle or seconddrizzle function calls here

