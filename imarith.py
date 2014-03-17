"""
S.Rodney 2014.02.26

Functions for combining and modifying science images.

"""

def immultiply( image, scalefactor, outfile=None, clobber=False, verbose=False):
    """
    Multiply the image by scalefactor.  If a string is provided for outfile,
    then the resulting scaled image file is written to that file name.  Otherwise, 
    the scaled image data array is returned. 
    """
    import os
    import pyfits
    from numpy import ndarray
    import exceptions

    # read in the image
    if isinstance( image, str ):
        if not os.path.isfile( image ) :
            raise exceptions.RuntimeError(
                "The image file %s is not valid."%image )
        im1head = pyfits.getheader( image )
        im1data = pyfits.getdata( image )
        im1head.update("FLXSCALE",scalefactor,"Flux scaling factor")
    elif instance( image, ndarray ):
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
    import pyfits
    from numpy import ndarray
    import exceptions

    # read in the images
    if isinstance( image1, str ):
        if not os.path.isfile( image1 ) :
            raise exceptions.RuntimeError(
                "The image file %s is not valid."%image1 )
        im1head = pyfits.getheader( image1 )
        im1data = pyfits.getdata( image1 )
        im1head.update("SRCIM1",image1,"First source image  for imsum")
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
        im1head.update("SRCIM2",image2,"Second source image for imsum")
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
    import pyfits
    from numpy import ndarray
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
        im2head.update("SRCIM1",image1,"First source image = template for subtraction")
        im2head.update("SRCIM2",image2,"Second source image = search epoch image")
        outdir = os.path.split( outfile )[0]
        if outdir and not os.path.isdir(outdir): 
            os.makedirs( outdir )
        pyfits.writeto( outfile, diffim, 
                        header=im2head,
                        clobber=clobber )
        return( outfile )
