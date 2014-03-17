"""
S.Rodney 2014.02.26

Functions for making, combining and applying bad pixel masks
that are constructed from HST weight maps.

"""


def zerowht2badpix( whtfile, badpixfile,  
                    verbose=False, clobber=False, debug=False ):
    """ Convert a weight file produced by astrodrizzle
    into a bad pixel map.  This version defines bad pixels as only 
    those that have a value of zero in the weight image

    Returns : the name of the output bad pixel file.
    """
    import pyfits
    import numpy as np
    import os
    import exceptions
    if verbose : print("Converting %s into bad pixel mask %s"%(whtfile,badpixfile))

    if debug: import pdb; pdb.set_trace()

    if os.path.isfile( badpixfile ) : 
        if clobber : 
            if verbose: print( "  %s exists. Clobbering."%badpixfile )
            os.remove( badpixfile ) 
        else : 
            if verbose: print( "  %s exists. Not clobbering."%badpixfile )
            return( badpixfile ) 

    # read in the WHT data 
    wht = pyfits.open(whtfile)    
    whtdat = wht[0].data
    bpthresh = 0

    # write out a badpix file. 
    bpdata = wht[0].data
    xbad, ybad = np.where( bpdata <= bpthresh )
    xgood, ygood = np.where( bpdata > bpthresh )
    bpdata[ xbad, ybad ] = 1
    bpdata[ xgood, ygood ] = 0

    bpdata = bpdata.astype( np.uint8 ) 
    wht[0].header['BITPIX'] = 8
    wht[0].data = bpdata 
   
    Npix = bpdata.shape[0]*bpdata.shape[1]
    Ngood = len(xgood) # = bpdata.sum()
    Nbad = len(xbad)   #
    if verbose : 
        print("   %i pixels have no useful data (%.2f pct)"%(Nbad,100*float(Nbad)/Npix) )

    # write out the badpix mask
    wht.writeto( badpixfile )
    wht.close()    
    return( badpixfile )


def applymask( scifile, badpixfile, outfile=None,
               verbose=False, clobber=False ):
    """ apply the badpix mask to the given scifile, setting all bad
    pixels to zero. If outfile is not provided then it defaults to
    replacing _sci.fits from with _masked.fits.

    Returns : name of the output masked sci.fits file.

    """
    import os
    import pyfits
    from numpy import where

    if not outfile : 
        if scifile.endswith('sci.fits') : 
            outfile = scifile.replace( 'sci.fits','masked.fits')
        else : 
            outfile = scifile.replace( '.fits','_masked.fits')

    if os.path.isfile( outfile ) :
        if clobber : 
            if outfile == scifile : 
                print('badpixmask.applymask error : outfile must be different from infile')
                import sys
                sys.exit(1)
            print( "%s exists. Clobbering"%outfile)
            os.remove( outfile )
        else : 
            print( "%s exists. Not clobbering"%outfile)
            return( outfile )

    # TODO : update header to indicate masking
    sci = pyfits.open( scifile )
    bpdata = pyfits.getdata( badpixfile ) 
    if verbose : 
        print('Setting %i bad pixels in %s to get %s'%(
                bpdata.sum(), scifile, outfile ) )

    sci[0].data *= 1-bpdata
    sci.writeto( outfile )
    sci.close()
    return( outfile )

    

def unionmask( imfile1, imfile2, outfile, clobber=False, verbose=False):
    """
    construct the union of image1 and image2 badpix masks
    Returns the name of the output union bad pixel mask file.
    """
    import os
    import pyfits
    import exceptions
    from numpy import array, uint8

    # read in the images
    im1head = pyfits.getheader( imfile1 )
    imdat1 = pyfits.getdata( imfile1 )
    imdat2 = pyfits.getdata( imfile2 )

    if os.path.exists( outfile ) :
        if not clobber :
            print( "%s exists. Not clobbering."%outfile)
            return( outfile )
        else :
            os.remove( outfile )
    
    uniondat = array(imdat1,dtype=uint8) | array(imdat2,dtype=uint8)
    
    # TODO : make a useful header
    im1head.update("SRCIM1",imfile1,"First source image  for badpixunion")
    im1head.update("SRCIM2",imfile2,"Second source image for badpixunion")
    outdir = os.path.split( outfile )[0]
    if outdir : 
        if not os.path.isdir(outdir): 
            os.makedirs( outdir )
    pyfits.writeto( outfile, uniondat, header=im1head,clobber=clobber,
                    output_verify='fix')
    return( outfile )



def applyUnionMask( scifile, badpixfile1, badpixfile2, outfile=None,
                    verbose=False, clobber=False ):
    """Apply the union of badpix masks 1 and 2 to the given scifile,
    setting all bad pixels to zero. 

    WARNING : If outfile is not provided then this function defaults
    to updating the scifile in place.

    Returns : name of the output masked sci.fits file.

    """
    import os
    import pyfits
    from numpy import where
    import exceptions
    from numpy import array, uint8

    # read in the badpix images
    bpxhead1 = pyfits.getheader( badpixfile1 )
    bpxdat1 = pyfits.getdata( badpixfile1 )
    bpxdat2 = pyfits.getdata( badpixfile2 )
    uniondat = array(bpxdat1,dtype=uint8) | array(bpxdat2,dtype=uint8)

    if not outfile : 
        outfile = scifile
    if outfile == scifile : 
        print('WARNING : updating %s with badpix masking in place.'%scifile)
    elif os.path.isfile( outfile ) : 
        if clobber : 
            print( "%s exists. Clobbering"%outfile)
            os.remove( outfile )
        else :
            print( "%s exists. Not clobbering"%outfile)
            return( outfile )

    # TODO : update header to indicate masking
    if verbose : 
        print('Setting %i bad pixels to 0 in %s to get %s'%(
                uniondat.sum(), scifile, outfile ) )

    sci = pyfits.open( scifile, mode='update' )
    sci[0].data *= 1-uniondat
    sci.flush()
    sci.close()
    return( outfile )

    
