from astropy.io import fits
from stsci import tools
from numpy import where, isfinite


def scrubnans( filename, fillval=0 ):
    """Locate any pixels in the given fits file that have values of NaN,
    indef, or inf. Replace them all with the given fillval.
    """
    hdulist = fits.open( filename, mode='update' )
    imdata = hdulist[0].data
    ybad, xbad  = where( 1-isfinite( imdata ) )
    imdata[ybad, xbad] = fillval
    hdulist.flush()
    hdulist.close()
    return()


def extname_bug_cleanup(files):
    """Check for a buggy header that contains an incompatible pair of
    header keywords, and fix it if present.
    If a fits header has the EXTVER keyword set, but no EXTNAME, then
    this does not make sense with the FITS standard. We expect EXTVER
    to be present only for distinguishing between extensions
    that have the same EXTNAME, so if there is no EXTNAME, there should
    be no EXTVER.  We delete EXTVER in this situation.

    Note: this function only fixes the primary header.

    See https://github.com/spacetelescope/drizzlepac/issues/590

    INPUTS
      files - str or list ;  the files to check and fix

    OUTPUTS
       None
    """
    #convert the input list into a useable list of images for astrodrizzle
    if type( files ) == str :
        filelist=tools.parseinput.parseinput(files)[0]
    else :
        filelist = files
        files = ','.join( filelist ).strip(',')
    if len(filelist)==0 :
        raise RuntimeError(
            "List of input files has no real files: %s"%str(files))

    # Find the bug and fix it, modifying files in place
    for file in filelist:
        hdulist = fits.open(file, mode='update')
        changemade = False
        for hdu in hdulist:
            if (('EXTVER' in hdu.header) and
                    ('EXTNAME' not in hdu.header)):
                hdu.header.remove('EXTVER')
                changemade=True
        if changemade:
            hdulist.flush()
    return
