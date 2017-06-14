"""
Crop an image to a given ra,dec range, or to match
the ra,dec range of another image.
"""


def getbounds( fitsfile ):
    """
    Determine the ra,dec bounds of the given fits image.
    """
    from astropy.io import fits as pyfits
    import pywcs
    hdulist = pyfits.open(fitsfile)
    header = pyfits.getheader(fitsfile)
    x1,y1 = header['NAXIS1'],header['NAXIS2']
    try :
        wcs = pywcs.WCS(header, hdulist)
        ralim,declim = wcs.wcs_pix2sky([0,x1], [0,y1], 0)
    except AssertionError :
        wcs = pywcs.WCS( header )
        ralim,declim = wcs.wcs_pix2sky([0,x1], [0,y1], 0)
    return(ralim, declim)

def cropimage( fitsfile, ralim, declim ):
    from astropy.io import fits as pyfits
    import pywcs
    hdulist = pyfits.open(fitsfile)
    header = pyfits.getheader(fitsfile)
    x1,y1 = header['NAXIS1'],header['NAXIS2']
    try :
        wcs = pywcs.WCS(header, hdulist)
        xlim,ylim = wcs.wcs_sky2pix( ralim, declim, 0)
    except AssertionError :
        wcs = pywcs.WCS(header)
        xlim,ylim = wcs.wcs_sky2pix( ralim, declim, 0)
    return(xlim, ylim)

def cropimage_to_match(fitsfile1, fitsfile2):
    """  Crop fitsfile1 so that it matches fitsfile2
    :param fitsfile1:
    :param fitsfile2:
    :return:
    """
    ralim, declim = getbounds( fitsfile2 )
    xlim, ylim = cropimage( fitsfile1, ralim, declim)
    return( xlim, ylim )