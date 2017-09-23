#! /usr/bin/env python
"""
S.Rodney 2014.02.26

Functions for combining and modifying science images.

"""
from astropy.io import fits as pyfits


def immultiply( image, scalefactor, outfile=None, clobber=False, verbose=False):
    """
    Multiply the image by scalefactor.  If a string is provided for outfile,
    then the resulting scaled image file is written to that file name.  Otherwise, 
    the scaled image data array is returned. 
    """
    import os
    from numpy import ndarray
    import exceptions

    # read in the image
    if isinstance( image, str ):
        if not os.path.isfile( image ) :
            raise exceptions.RuntimeError(
                "The image file %s is not valid."%image )
        im1head = pyfits.getheader( image )
        im1data = pyfits.getdata( image )
        im1head["FLXSCALE"] = (scalefactor,"Flux scaling factor")
    elif isinstance( image, ndarray ):
        im1data = image
        im1head = None
    else : 
        raise  exceptions.RuntimeError("Provide a fits file name or numpy array for each image.")
    
    scaledim =  scalefactor * im1data
    
    if outfile :
        outdir = os.path.split( outfile )[0]
        if outdir : 
            if not os.path.isdir(outdir): 
                os.makedirs( outdir )
        pyfits.writeto( outfile, scaledim, header=im1head,clobber=clobber )
        return( outfile )
    else : 
        return( scaledim )




def imsum( image1, image2, outfile=None, clobber=False, verbose=False):
    """
    Add together image1 and image2.  If a string is provided for
    outfile, then the resulting summed image is written to that file
    name.  Otherwise, the summed image data array is returned.
    """
    import os
    from numpy import ndarray
    import exceptions

    # read in the images
    if isinstance( image1, str ):
        if not os.path.isfile( image1 ) :
            raise exceptions.RuntimeError(
                "The image file %s is not valid."%image1 )
        im1head = pyfits.getheader( image1 )
        im1data = pyfits.getdata( image1 )
        im1head["SRCIM1"] = (image1,"First source image  for imsum")
    elif isinstance( image1, ndarray ):
        im1data = image1
        im1head = None
    else : 
        raise  exceptions.RuntimeError(
            "Provide a fits file name or numpy array for each image.")
    
    if isinstance( image2, str ):
        if not os.path.isfile( image2 ) :
            raise exceptions.RuntimeError(
                "The image file %s is not valid."%image2 )
        im2data = pyfits.getdata( image2 )
        im1head["SRCIM2"] = (image2,"Second source image for imsum")
    elif isinstance( image2, ndarray ):
        im2data = image2
    else : 
        raise  exceptions.RuntimeError(
            "Provide a fits file name or numpy array for each image.")


    # sometimes multidrizzle drops a pixel. Unpredictable.
    nx2,ny2 = im2data.shape
    nx1,ny1 = im1data.shape
    if nx2>nx1 or ny2>ny1 : 
        im2data = im2data[:min(nx1,nx2),:min(ny1,ny2)]
        im1data = im1data[:min(nx1,nx2),:min(ny1,ny2)]
    elif nx2<nx1 or ny2<ny1 : 
        im1data = im1data[:min(nx1,nx2),:min(ny1,ny2)]
        im2data = im2data[:min(nx1,nx2),:min(ny1,ny2)]

    sumim =  im2data + im1data
    
    if outfile :
        # TODO : make a useful header
        outdir = os.path.split( outfile )[0]
        if outdir : 
            if not os.path.isdir(outdir): 
                os.makedirs( outdir )
        pyfits.writeto( outfile, sumim, 
                        header=im1head,
                        clobber=clobber )
        return( outfile )
    else : 
        return( sumim )


def imsubtract( image1, image2, outfile=None, 
                clobber=False, verbose=False, debug=False):
    """
    Construct a simple subtraction: image2 - image1.  Guards against
    different sized data arrays by assuming that the lower left pixel
    (0,0) is the anchor point.  (i.e. the second image will be
    trimmed or extended if needed.)  
    """
    import os
    import exceptions

    if debug  : import pdb; pdb.set_trace()

    if outfile : 
        if os.path.isfile( outfile ) and not clobber : 
            print("%s exists. Not clobbering."%outfile)
            return( outfile )

    # read in the images
    if not os.path.isfile( image1 ) :
        raise exceptions.RuntimeError(
            "The image file %s is not valid."%image1 )
    im1head = pyfits.getheader( image1 )
    im1data = pyfits.getdata( image1 )

    if not os.path.isfile( image2 ) :
        raise exceptions.RuntimeError(
            "The image file %s is not valid."%image2 )
    im2head = pyfits.getheader( image2 )
    im2data = pyfits.getdata( image2 )

    # sometimes multidrizzle drops a pixel. Unpredictable.
    nx2,ny2 = im2data.shape
    nx1,ny1 = im1data.shape
    if nx2>nx1 or ny2>ny1 : 
        im2data = im2data[:min(nx1,nx2),:min(ny1,ny2)]
        im1data = im1data[:min(nx1,nx2),:min(ny1,ny2)]
    elif nx2<nx1 or ny2<ny1 : 
        im1data = im1data[:min(nx1,nx2),:min(ny1,ny2)]
        im2data = im2data[:min(nx1,nx2),:min(ny1,ny2)]

    diffim =  im2data - im1data
    
    if not outfile :
        return( diffim )
    else : 
        im2head["SRCIM1"] = (image1,"First source image = template for subtraction")
        im2head["SRCIM2"] = (image2,"Second source image = search epoch image")
        outdir = os.path.split( outfile )[0]
        if outdir and not os.path.isdir(outdir): 
            os.makedirs( outdir )
        pyfits.writeto( outfile, diffim, 
                        header=im2head,
                        clobber=clobber )
        return( outfile )


def combine_ivm_maps( im1, im2, outfile, clobber=False, verbose=False):
    """
    Combine two inverse-variance weight maps ivm1 and ivm2.
    Returns the name of the output composite weight map.
    """
    import os
    from numpy import ma

    if os.path.exists( outfile ) :
        if not clobber :
            print( "%s exists. Not clobbering."%outfile)
            return( outfile )
        else :
            os.remove( outfile )

    # read in the images
    im1head = pyfits.getheader( im1 )
    im1dat = pyfits.getdata( im1 )
    im2dat = pyfits.getdata( im2 )
    var1 = ma.masked_array( 1./im1dat )
    var2 = ma.masked_array( 1./im2dat )

    ivm12 = 1./( var1 + var2 )
    ivm12.set_fill_value(0)
    ivm12out = ivm12.filled()

    # TODO : make a useful header
    im1head["SRCIM1"] = (im1,"First source image  for IVM sum")
    im1head["SRCIM2"]  = (im2,"Second source image for IVM sum")
    outdir = os.path.split( outfile )[0]
    if outdir :
        if not os.path.isdir(outdir):
            os.makedirs( outdir )
    pyfits.writeto( outfile, ivm12out, header=im1head,clobber=clobber,
                    output_verify='fix')
    return( outfile )


def imaverage( imagelist, outfile,
               clobber=False, verbose=False):
    """
     construct a simple average of all images in the list.
     Assumes all input images have identical dimensions
     Returns name of outfile
    """
    import os
    from numpy import where, ones, zeros, float32

    if os.path.exists(outfile)  :
        if clobber :
            os.unlink( outfile )
        else :
            print( "%s exists. Not clobbering."%outfile )
            return( outfile )

    # make empty arrays for components of the weighted average
    naxis1 = pyfits.getval( imagelist[0], 'NAXIS1')
    naxis2 = pyfits.getval( imagelist[0], 'NAXIS2')
    sumarray = zeros( [naxis2,naxis1], dtype=float32 )
    ncombinearray = zeros( [naxis2,naxis1], dtype=float32 )

    # construct the weighted average and update header keywords
    outhdr = pyfits.getheader( imagelist[0] )
    for imfilenum, imfile in zip(range(1, len(imagelist) + 1), imagelist):
        imdat = pyfits.getdata(imfile)
        sumarray += imdat
        ncombinearray += where( imdat != 0 , ones(imdat.shape), zeros(imdat.shape) )
        outhdr.update({"SRCIM%02i" % imfilenum: (
            imfile, "source im %i, used in avg" % imfilenum)})
    outscidat = where( ncombinearray > 0 , sumarray/ncombinearray, zeros(sumarray.shape) )

    outdir = os.path.dirname( outfile )
    if outdir :
        if not os.path.isdir(outdir):
            os.makedirs( outdir )
    pyfits.writeto( outfile, outscidat, header=outhdr )

    return( outfile )

def imweightedaverage( imagelist, whtlist, outfile, outwht,
                     clobber=False, verbose=False):
    """
     construct a weighted average :

     (weight1*image1 + weight2*image2 + ...) / (weight1+weight2+...)

     And a composite weight map :
       (weight1 + weight2 + ...) / Nweight

     Mean image is written to outfile.
     Assumes all input images have identical dimensions
     Returns name of outfile and whtfile
    """
    import os
    from numpy import where, ones, zeros, float32

    if os.path.exists(outfile)  :
        if clobber :
            os.unlink( outfile )
        else :
            print( "%s exists. Not clobbering."%outfile )
            return( outfile, outwht )

    if os.path.exists(outwht)  :
        if clobber :
            os.unlink( outwht )
        else :
            print( "%s exists. Not clobbering."%outwht )
            return( outfile, outwht )

    # make empty arrays for components of the weighted average
    naxis1 = pyfits.getval( imagelist[0], 'NAXIS1')
    naxis2 = pyfits.getval( imagelist[0], 'NAXIS2')
    sumarray = zeros( [naxis2,naxis1], dtype=float32 )
    ncombinearray = zeros( [naxis2,naxis1], dtype=float32 )
    whtarray = ones( [naxis2,naxis1], dtype=float32 )

    # construct the weighted average and update header keywords
    outhdr = pyfits.getheader( imagelist[0] )
    # import pdb; pdb.set_trace()
    for imfilenum, imfile, whtfile in zip(range(1, len(imagelist) + 1),
                                          imagelist, whtlist):
        imdat = pyfits.getdata(imfile)
        whtdat = pyfits.getdata(whtfile)
        sumarray += whtdat * imdat
        whtarray += whtdat
        ncombinearray += where(whtdat > 0, ones(whtdat.shape),
                               zeros(whtdat.shape))
        outhdr.update({"SRCIM%02i" % imfilenum: (
            imfile, "source im %i, used in whted avg" % imfilenum)})

    # outscidat = nan_to_num( sumarray / whtarray )
    # outscidat = sumarray / whtarray
    outscidat = where( ncombinearray > 0 , sumarray / whtarray, zeros(sumarray.shape) )
    outwhtdat = where( ncombinearray > 0 , whtarray/ncombinearray, zeros(whtarray.shape) )

    outdir = os.path.dirname( outfile )
    if outdir :
        if not os.path.isdir(outdir):
            os.makedirs( outdir )
    pyfits.writeto( outfile, outscidat, header=outhdr )
    pyfits.writeto( outwht,  outwhtdat, header=outhdr )

    return( outfile, outwht )


def mkparser():
    import argparse

    class SmartFormatter(argparse.HelpFormatter):
        def _split_lines(self, text, width):
            # this is the RawTextHelpFormatter._split_lines
            if text.startswith('R|'):
                return text[2:].splitlines()
            return argparse.HelpFormatter._split_lines(self, text, width)

    parser = argparse.ArgumentParser(
        description='Combine a list of images. Assumes they are the same '
                    'size, same pixel scale, and already registered.',
        formatter_class=SmartFormatter)

    # Required positional argument
    parser.add_argument('outfile',
                        help='Output filename for the combined image.')

    # optional arguments :
    parser.add_argument('--combinetype', type=str,
                        choices=['mean', 'sum', 'median'], default='mean',
                        help='Combination method.')
    parser.add_argument('--clobber', action='store_true',
                        help='Turn on clobber mode. [False]', default=False)
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Turn on verbosity. [default is OFF]',
                        default=False)
    parser.add_argument('--imagelist', nargs='+',
                        help='List of image files to combine.')

    return parser

def main():
    parser = mkparser()
    argv = parser.parse_args()

    if argv.combinetype == 'mean':
        outfile = imaverage(argv.imagelist, argv.outfile, clobber=argv.clobber,
                            verbose=argv.verbose)
        print('created %s'%outfile)


if __name__ == "__main__":
    main()
