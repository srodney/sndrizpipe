__author__ = 'srodney'



# 3-stage command-line test :
# sndrizzle --filters F160W  --dosort --mjdmin 56010 --mjdmax 56300 --ra 189.156538 --dec 62.309147  --epochspan 5 colfax
# sndrizzle  --dorefim  --refepoch 1 --reffilter 'F160W'  --refcat 'goodsn_mosaic.cat' --rfluxmax 27 --rfluxmin 14 --searchrad 1.5 colfax
# sndrizzle  --pixscale 0.09 --pixfrac 1 --tempepoch 8 --dodriz1 --dodriz2 --dodiff colfax

def colfaxtest():
    """ Test the pipeline functions using images of SN Colfax from CANDELS,
    mimicking the command-line interface.
    """
    import pipeline

    pipeline.singlepipe( 'colfax', onlyfilters=['F160W'], onlyepochs=[0,1],
              doall=False, dodiff=True,
              refcat='goodsn_mosaic.cat', refepoch=1, reffilter='F160W',
              mjdmin=56010, mjdmax=56300, epochspan=5, ra=189.156538, dec=62.309147,
              clobber=False, verbose=True, debug=False )

