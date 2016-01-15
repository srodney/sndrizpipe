#! /usr/bin/env python
# 2014.05.30
# S.Rodney
# Construct a template image comprising one or two template images,
# scaled to match the transmission curve of a different filter. 

import numpy as np
import os
import sys
import exceptions

def loadFilter( camfiltername, filtdir='HSTFILTERS' ):
    """ Read in a filter transmission curve.
    Returns two numpy arrays, wavelength in angstroms,
    and flux transmission. 

    The input value, camfiltername,  must be of the form 
    'INSTRUMENT-DETECTOR-FILTER'.  For instruments with
    only 1 filter set, the detector name may be omitted.  
    For example: 
        'ACS-WFC-F606W'
        'WFC3-IR-F105W'
        'NICMOS-NIC2-F110W'
        'WFPC2-F850LP'
    """
    thisfile = sys.argv[0]
    if 'ipython' in thisfile :
        thisfile = __file__
    thisdir = os.path.dirname( os.path.abspath( thisfile ) )
    if not os.path.isdir( filtdir ) :
        filtdir = os.path.join( thisdir, filtdir )
    filtdir = os.path.abspath(filtdir)
    if not os.path.isdir( filtdir ) :
        raise exceptions.RuntimeError("No such directory %s"%filtdir)

    camfiltername = camfiltername.upper()
    instrument = camfiltername.split('-')[0]
    detector = camfiltername.split('-')[1]
    filtername = camfiltername.split('-')[-1]
    if detector == filtername : 
        datfile = '%s_%s.dat'%(instrument, filtername)   
    else : 
        datfile = '%s_%s_%s.dat'%(instrument, detector, filtername)   

    datfile = os.path.join( filtdir, datfile )
    wavelength, transmission = np.loadtxt( datfile, unpack=True)

    return( wavelength, transmission)


def computeFilterScaling( target, source1, source2=None, filtdir='HSTFILTERS') :
    """Determine the flux scaling factor for matching image(s) taken 
    in the source filter(s) to an image in the target filter. 

    This returns the value that should be multiplied to the image in filter source1 
    (or multiplied to [source1+source2]) to match the throughput of the target filter.  

    This returns just a single number, effectively assuming the source
    SED is flat across the bandpass(es), so that we just need to
    correct for total throughput, not for the shape of the filter.

    The input values, target, source1 and source2 must be of the form 
    'INSTRUMENT-DETECTOR-FILTER'.   For example: 
        'ACS-WFC-F606W'
        'WFC3-IR-F105W'
        'NICMOS-NIC2-F110W'
    """
    from scipy import integrate as scint

    target = target.upper()
    source1 = source1.upper()

    wT, tT = loadFilter( target )
    intT = scint.simps( tT, wT )

    wS1, tS1 = loadFilter( source1, filtdir )
    intS1 = scint.simps( tS1, wS1 )

    if source2 != None:
        source2 = source2.upper()
        wS2, tS2 = loadFilter( source2, filtdir )
        intS2 = scint.simps( tS2, wS2 )
        denominator = (intS2 + intS1)
    else : 
        denominator = intS1

    return( intT / denominator )


def camfiltername(imfile):
    """ Read the camera (or instrument and detector) and filter names
    from the image header.
    Returns a string giving camera-filtername or instr-det-filter
    """
    import pyfits
    hdr = pyfits.getheader( imfile )

    namelist = []
    if 'CAMERA' in hdr :
        namelist.append(hdr['CAMERA'])
    else :
        if 'INSTRUME' in hdr :
            namelist.append(hdr['INSTRUME'])
        elif 'INSTRUMENT' in hdr :
            namelist.append(hdr['INSTRUMENT'])
        if 'DETECTOR' in hdr :
            namelist.append( hdr['DETECTOR'] )
    if 'FILTER1' in hdr :
        if not hdr['FILTER1'].startswith('CLEAR') :
            namelist.append( hdr['FILTER1'] )
        else :
            namelist.append( hdr['FILTER2'] )
    elif 'FILTER' in hdr :
        namelist.append( hdr['FILTER'] )
    else :
        raise exceptions.RuntimeError('No filter in %s header.'%imfile)

    filtername = '-'.join( namelist ).strip('-')
    return( filtername.upper() )

def mkscaledtemplate( targetfilter, imfile1, imfile2=None, outfile=None,
                      scalefactor=1, filtdir='HSTFILTERS', verbose=True,
                      clobber=False ):
    """ Combine and/or scale imfile1 (and imfile2) to match the
    filter transmission function for targetfilter (e.g. for making a
    template image for F814W from two images in F775W and F850LP).

    If an outfile is specified and the wht and bpx files associated with the
    input image files are available, then they will also be combined and
    written to appropriately named output files

    The argument targetfilter must have the form 'INSTRUMENT-DETECTOR-FILTER'.
    For example:  'ACS-WFC-F606W'

    Returns the names of all files generated (sci, wht, bpx)
    """
    import pyfits
    import imarith
    import shutil
    import badpix

    sourcefilter1 = camfiltername( imfile1 )
    if imfile2 :
        sourcefilter2 = camfiltername( imfile2 )
        if verbose :
            print('Scaling %s + %s to match %s'%(sourcefilter1,sourcefilter2,targetfilter))
    else :
        sourcefilter2 = None
        if verbose :
            print('Scaling %s to match %s'%(sourcefilter1,targetfilter))

    scalefactor = scalefactor * computeFilterScaling(
        targetfilter, sourcefilter1, source2=sourcefilter2, filtdir=filtdir)

    if imfile2 :
        imdat = imarith.imsum( imfile1, imfile2 )
    else :
        imdat = pyfits.getdata( imfile1 )

    imdatscaled = imdat * scalefactor

    outhdr = pyfits.getheader( imfile1 )
    outhdr['FILTER'] = '~' + targetfilter.split('-')[-1]
    if 'FILTER1' in outhdr : outhdr.remove('FILTER1')
    if 'FILTER2' in outhdr : outhdr.remove('FILTER2')

    if outfile is None :
        return( imdatscaled )

    outdir = os.path.split( outfile )[0]
    if outdir :
        if not os.path.isdir(outdir):
            os.makedirs( outdir )
    pyfits.writeto( outfile, imdatscaled, header=outhdr, clobber=clobber )

    if not outfile.endswith('sci.fits') or not imfile1.endswith('sci.fits'):
        return( outfile )

    outwht = outfile.replace('sci.fits','wht.fits')
    outbpx = outfile.replace('sci.fits','bpx.fits')

    inwht1 = imfile1.replace('sci.fits','wht.fits')
    inbpx1 = imfile1.replace('sci.fits','bpx.fits')

    if imfile2 is None :
        if os.path.isfile( inwht1 ) and os.path.isfile( inbpx1 ) :
            shutil.copy( inwht1, outwht )
            shutil.copy( inbpx1, outbpx )
            return( outfile, outwht, outbpx)
        else :
            return( outfile )

    inwht2 = imfile2.replace('sci.fits','wht.fits')
    inbpx2 = imfile2.replace('sci.fits','bpx.fits')
    if os.path.isfile( inwht2 ) :
        outwht = imarith.combine_ivm_maps( inwht1, inwht2, outwht,
                                           clobber=clobber, verbose=verbose )
    if os.path.isfile( inbpx2 ) :
        outbpx = badpix.unionmask( inbpx1, inbpx2, outbpx,
                                   clobber=clobber, verbose=verbose )

    assert os.path.isfile( outfile ), "Scaled template %s not created."%outfile
    assert os.path.isfile( outwht ), "Scaled weight image %s not created."%outwht
    assert os.path.isfile( outbpx ), "Scaled badpix image %s not created."%outbpx

    return( outfile, outwht, outbpx)


def doScaleSubMask( targname, targfilter, targepoch, tempfilter, tempepoch,
                    tempfilter2=None, tempepoch2=None, scalefactor=1,
                    filtdir='HSTFILTERS',
                    clean=True, verbose=True, clobber=False ):
    """ Primary function for making pseudo-filter diff images :
    * make a scaled template image, scaling the template filter to match the target filter
    * subtract scaled template from target filter+epoch
    * make a union badpix mask
    * apply the union badpix mask
    * make a composite weight mask
    """
    import os
    import imarith
    import badpix
    import pyfits

    targdir = '%s.e%02i'%(targname, targepoch)
    targsci = '%s_%s_e%02i_reg_drc_sci.fits'%(targname, targfilter, targepoch)
    targsci = os.path.join( targdir, targsci )
    if not os.path.isfile( targsci ) :
        targsci = targsci.replace('_drc','_drz')
    targwht = targsci.replace( '_sci.fits','_wht.fits')
    targbpx = targsci.replace( '_sci.fits','_bpx.fits')
    assert os.path.isfile( targsci )
    assert os.path.isfile( targwht )
    assert os.path.isfile( targbpx )

    hdr = pyfits.getheader( targsci )
    if 'CAMERA' in hdr :
        instrument = hdr['CAMERA']
        detector = ''
    elif 'INSTRUME' in hdr :
        instrument = hdr['INSTRUME']
    if 'DETECTOR' in hdr :
        detector = hdr['DETECTOR']
    targetcamfilter = '-'.join([instrument,detector,targfilter.upper()]).rstrip('-')
    if targetcamfilter.endswith('L') :
        targetcamfilter += 'P'

    tempdir = '%s.e%02i'%(targname, tempepoch)
    tempfile = '%s_%s_e%02i_reg_drc_sci.fits'%(targname, tempfilter, tempepoch)
    tempfile = os.path.join( tempdir, tempfile )
    if not os.path.isfile( tempfile ) :
        tempfile = tempfile.replace('_drc','_drz')
    assert os.path.isfile( tempfile )

    if tempfilter2 is None :
        tempfile2 = None
    else :
        if tempepoch2 is None :
            tempepoch2 = tempepoch
        tempdir2 = '%s.e%02i'%(targname, tempepoch2)
        tempfile2 = '%s_%s_e%02i_reg_drc_sci.fits'%(targname, tempfilter2, tempepoch2)
        tempfile2 = os.path.join( tempdir2, tempfile2 )
        if not os.path.isfile( tempfile2 ) :
            tempfile2 = tempfile2.replace('_drc','_drz')
        assert os.path.isfile( tempfile2 )

    outfile = os.path.join( tempdir, '%s_~%s_e%02i_reg_drc_sci.fits'%(targname, targfilter, tempepoch) )

    if os.path.exists( outfile ) and not clobber :
        print("Template file %s already exists, not clobbering."%outfile)
        tempsci = outfile
        tempwht = tempsci.replace('sci.fits','wht.fits')
        tempbpx = tempsci.replace('sci.fits','bpx.fits')
    else :
        tempsci, tempwht, tempbpx = mkscaledtemplate(
            targetcamfilter, tempfile, imfile2=tempfile2, outfile=outfile,
            scalefactor=scalefactor, filtdir=filtdir, verbose=verbose, clobber=clobber)

    subsci = '%s_%s_e%02i-e%02i_sub_sci.fits'%(targname, targfilter, targepoch, tempepoch)
    subsci = os.path.join( targdir, subsci )

    if verbose :  print( "Making pseudo diff image %s"%subsci )
    diffim = imarith.imsubtract( tempsci, targsci, outfile=subsci,
                                 clobber=clobber, verbose=verbose )
    diffwht = imarith.combine_ivm_maps( targwht, tempwht,
                                       diffim.replace('sci.fits','wht.fits'),
                                       clobber=clobber, verbose=verbose )
    diffbpx = badpix.unionmask( tempbpx, targbpx,
                         diffim.replace('sci.fits','bpx.fits'),
                         clobber=clobber, verbose=verbose)
    diffim_masked = badpix.applymask( diffim, diffbpx,
                                     clobber=clobber, verbose=verbose)
    if clean :
        # delete the sub_sci.fits, b/c it is superseded
        os.remove( diffim )
    if verbose :
        print("Created diff image %s, wht map %s, and bpx mask %s"%(
            diffim_masked, diffwht, diffbpx ) )
    return( diffim_masked, diffwht, diffbpx )

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Combine and/or scale an image or pair of images to match '
                    'the transmission function of a different filter, and then '
                    'subtract that pseudo-template to make a diff image. '
                    " \n EXAMPLE: making a pseudo-F845M template from epoch 00 "
                    " F814W images, and subtracting it from epoch 06 F845M images.\n "
                    'sndrizpipe/pseudodiff.py --clobber --verbose camille f845m 06 f814w\n\n'
    )

    # Required positional argument
    parser.add_argument('name', type=str, help="Name of the target (the prefix for drz image products)" )
    parser.add_argument('targetfilter', type=str, help="Filter of the target image, to be matched" )
    parser.add_argument('targetepoch', type=int, help="Epoch of the target image" )
    parser.add_argument('tempfilter', type=str, help="Filter of the template image, to be scaled." )
    parser.add_argument('tempfilter2', nargs='?', type=str, help="Optional second template filter, to be combined with the first and scaled." )
    parser.add_argument('--scalefactor', metavar=1, type=float, default=1, help="Specify an additional scale factor to apply to the template image after scaling input template image(s) to have total integrated filter transmission equal to the search epoch." )
    parser.add_argument('--tempepoch', metavar=0, type=int, default=0, help="Epoch of the template image" )
    parser.add_argument('--tempepoch2', metavar=0, type=int, default=None, help="Epoch of the 2nd template image. If not provided, we assume it is the same as the first." )
    parser.add_argument('--filtdir', metavar='HSTFILTERS', type=str,
                        help='Directory containing the filter transmission curves. Default is HSTFILTERS in the sndrizpipe installation dir.',
                        default='HSTFILTERS')
    parser.add_argument('--clobber', default=False, action='store_true',
                        help='Clobber existing reference catalog if it exists. [False]')
    parser.add_argument('--verbose', default=False, action='store_true',
                        help='Turn on verbose output. [False]')
    argv = parser.parse_args()

    if argv.tempfilter2 is None :
        tempfilter2 = None
    else :
        tempfilter2 = argv.tempfilter2.lower()[:5]
    doScaleSubMask( argv.name, argv.targetfilter.lower()[:5], argv.targetepoch,
                    argv.tempfilter.lower()[:5], argv.tempepoch,
                    tempfilter2=tempfilter2, tempepoch2=argv.tempepoch2,
                    scalefactor=argv.scalefactor,
                    filtdir=argv.filtdir, clean=True, verbose=argv.verbose, clobber=argv.clobber)



if __name__=='__main__' :
    main()
