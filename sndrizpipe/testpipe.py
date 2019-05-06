__author__ = 'srodney'

# TODO : add a test that uses the command-line interface
# command-line test :
# sndrizzle --filters F160W  --doall --mjdmin 56010 --mjdmax 56300 --ra 189.156538 --dec 62.309147  --refcat 'goodsn_mosaic.cat' colfax

def colfaxtest( getflts=True, username=None, password=None, runpipeline=True):
    """ Test the pipeline using images of SN Colfax from CANDELS,

    getflts : fetch the example FLT files from the CADC HST archive.
        You must provide your MAST/CADC username and passoword.
    ! NOT CURRENTLY WORKING.  MAYBE WHEN THE CADC REBOOT FINISHES !
    !  FOR NOW WE JUST USE A TAR BUNDLE INCLUDED IN THE GIT REPO !

    runpipeline :  run all the pipeline steps

    """
    from . import sndrizpipe
    import urllib.request, urllib.error, urllib.parse
    import os
    import sys
    import time

    start = time.time()

    thisfile = sys.argv[0]
    if 'ipython' in thisfile :
        thisfile = __file__
    thisdir = os.path.dirname( os.path.abspath( thisfile ) )

    if getflts :
        tgzfile = os.path.join( thisdir, 'colfax_test.tgz' )
        os.system( 'tar -xvzf %s'%tgzfile )

    if False :
        # Preferred method for getting the flt files for the colfax test suite.
        # This is not yet working.  Maybe due to the CADC reboot.
        # TODO : check if flt downloads work after April, 2014

        # create a password manager
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        # Add the username and password.
        # If we knew the realm, we could use it instead of None.
        top_level_url = "HTTP://WWW.CADC-CCDA.HIA-IHA.NRC-CNRC.GC.CA/DATA/PUB/HSTCA/"
        password_mgr.add_password(None, top_level_url, username, password)

        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

        # create "opener" (OpenerDirector instance)
        opener = urllib.request.build_opener(handler)

        # Install the opener.
        # Now all calls to urllib2.urlopen use our opener.
        urllib.request.install_opener(opener)

        # Go and fetch all the flt files:
        fltlist = ['IBTM7MLDQ_FLT','IBTM7MLGQ_FLT','IBTMADMJQ_FLT',
                   'IBTMADMNQ_FLT','IBOEABOSQ_FLT','IBOEABOWQ_FLT',
                   'IBWJCBD3Q_FLT','IBWJCBDBQ_FLT','IBOE3CJHQ_FLT',
                   'IBOE3CJKQ_FLT','IBOE3CJOQ_FLT','IBOE3CJRQ_FLT',
                   ]

        for fltroot in fltlist :
            url = 'HTTP://WWW.CADC-CCDA.HIA-IHA.NRC-CNRC.GC.CA/DATA/PUB/HSTCA/'
            flt = urllib.request.urlopen(url+fltroot)


    if runpipeline :
        sndrizpipe.runpipe( 'colfax', onlyfilters=['F160W'], onlyepochs=[0,1,2],
                            doall=True, refcat='goodsn_mosaic.cat',
                            refepoch=1, reffilter='F160W',
                            mjdmin=56010, mjdmax=56300, epochspan=5,
                            ra=189.156538, dec=62.309147,
                            clobber=False, verbose=True, debug=False )

    end = time.time()
    print(( "SNDRIZPIPE : colfax test completed in %.2f min"%((end-start)/60.) ))
    return 0

