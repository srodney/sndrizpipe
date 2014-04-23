# S.Rodney 2014.03.04
# Reading exposure info from a pile of flt files,
# defining epochs by date and filter, and moving
# flt files into epoch subdirs for registration
# and drizzling.

def get_explist( fltlist='*fl?.fits', outroot='TARGNAME' ):
    """ make a list of Exposure objects for each flt file"""
    from stsci import tools
    if type(fltlist)==str :
        fltlist=tools.parseinput.parseinput(fltlist)[0]
    return( [ Exposure( fltfile, outroot=outroot ) for fltfile in fltlist ] )


def define_epochs( explist, epochspan=5, mjdmin=0, mjdmax=0 ):
    """
    Sort a list of flts into epochs.  Anything with MJD < mjdmin or
    MJD > mjdmax goes into epoch 00 (the template epoch).
    All other epochs are made of exposures taken within
    epochspan days of each other.

    Caution : calling this function actually updates the input explist.
    """
    import numpy as np

    if type(explist)==str :
        explist = get_explist( explist )

    mjdlist = np.array( [ exp.mjd for exp in explist ] )
    visitlist = np.array( [ exp.visit for exp in explist ] )
    epochlist = np.zeros( len(mjdlist) )

    thisepochmjd0 = mjdlist.min()
    thisepoch = 1
    for imjd in mjdlist.argsort() :
        thismjd = mjdlist[imjd]
        if (mjdmin>0) and (thismjd < mjdmin) : thisepoch=0
        elif (mjdmax>0) and (thismjd > mjdmax) : thisepoch=0
        elif thismjd > thisepochmjd0+epochspan :
            thisepoch += 1
            thisepochmjd0 = thismjd
        for ithisvis in np.where( visitlist == visitlist[imjd] )[0] :
            epochlist[ ithisvis ] = thisepoch
            explist[ ithisvis ].epoch = thisepoch
    # Sort the exposure list by epoch, then filter, then visit
    explist.sort( key=lambda exp: (exp.epoch, exp.filter, exp.visit) )
    return(explist)

def read_epochs( explist, epochlistfile, checkradec=None, onlyfilters=None ):
    """Read the epoch sorting scheme from epochlistfile, apply it to
    the Exposures in explist (i.e. update their .epoch parameters) and
    return the modified explist.

    Caution : calling this function actually updates the input explist.
    """
    from astropy.io import ascii
    epochtable = ascii.read( epochlistfile )
    rootnamelist = epochtable['rootname'].tolist()
    epochlist = epochtable['epoch']
    for exp in explist :
        if onlyfilters and exp.filter not in onlyfilters :
            continue
        if isinstance(checkradec,list) and len(checkradec)==2:
            if checkradec[0] and checkradec[1] :
                if not checkonimage(exp,checkradec,verbose=False) : continue
        try:
            iexp = rootnamelist.index(exp.rootname)
        except ValueError:
            continue
        exp.epoch = epochlist[iexp]
    # Sort the exposure list by epoch, then filter, then visit
    explist.sort( key=lambda exp: (exp.epoch, exp.filter, exp.visit) )
    return(explist)

def print_epochs( explist, outfile=None, verbose=True, clobber=False, checkradec=None, onlyfilters=None, onlyepochs=None ):
    """Print summary lines for each exposure, epoch by epoch, filter by
    filter, and visit by visit.  Everything is printed to stdout and
    to the given outfile, if provided.
    """
    import os

    if outfile :
        if os.path.exists( outfile ) :
            if clobber :
                os.remove( outfile )
            else :
                print("%s exists. Not clobbering."%outfile)
                return(outfile)
        fout = open( outfile, 'a' )

    # Sort the exposure list by epoch, then filter, then visit
    explist.sort( key=lambda exp: (exp.epoch, exp.filter, exp.visit) )

    header = '#%9s %5s %3s %3s %6s %5s %7s '%(
            'rootname','pid','vis','exp','filter','epoch','mjd' )

    if outfile:
        print >> fout, header
    if verbose :
        print(header)
    thisepoch = explist[0].epoch
    for exp in explist :
        if onlyfilters and exp.filter not in onlyfilters :
            continue
        if onlyepochs and exp.epoch not in onlyepochs :
            continue
        if isinstance(checkradec,list) and len(checkradec)==2:
            if checkradec[0] and checkradec[1] :
                if not checkonimage(exp,checkradec,verbose=verbose) : continue
        if exp.epoch!=thisepoch:
            print("")
            if outfile: print>>fout,""
            thisepoch = exp.epoch
        if outfile :
            print >>fout, exp.summaryline_short
        if verbose :
            print( exp.summaryline_short )
    if outfile :
        fout.close()

def copy_to_epochdirs( explist,  onlyfilters=[], onlyepochs=[],
                       checkradec=None, verbose=True, clobber=False ):
    """ Given a list of Exposure objects in explist, copy the flt files into
    separate epoch directories for drizzling -- limited to the Exposures that
    match the constraints in onlyfilters and onlyepochs.
    """
    import os
    import shutil

    if onlyfilters :
        if type(onlyfilters)==str :
            onlyfilters = onlyfilters.lower().split(',')
        onlyfilters = [ filt[:5].lower() for filt in onlyfilters ]
    if type(onlyepochs) in [str,int,float]  :
        onlyepochs = [ int(ep) for ep in str(onlyepochs).split(',') ]

    if clobber :
        if verbose:
            print( "Wiping away existing epoch dirs.")
        for exp in explist :
            if os.path.isdir( exp.epochdir ) :
                shutil.rmtree( exp.epochdir )

    for exp in explist :
        # only copy files for the given filter and epoch
        if onlyfilters and exp.filter not in onlyfilters :
            continue
        if onlyepochs and exp.epoch not in onlyepochs :
            continue
        # Check that the target is on the image before copying files
        if isinstance(checkradec,list) and len(checkradec)==2:
            if checkradec[0] and checkradec[1] :
                if not checkonimage(exp,checkradec,verbose=verbose) : continue
        if not os.path.isdir( exp.epochdir ):
            os.makedirs( exp.epochdir )
        if verbose : print("Copying %s ==> %s"%(exp.filename, exp.epochdir) )
        shutil.copy( exp.filepath, exp.epochdir )



def checkonimage(exp,checkradec,verbose=True):
    """Check if the given ra,dec falls anywhere within the
    science frame of the image that defines the given Exposure object.
    """
    import pyfits
    import pywcs
    ra,dec = checkradec
    onimage = False
    if exp.header['detector'] in ['WFC','UVIS'] : 
        hdulist = pyfits.open( exp.filepath )
    else : 
        hdulist = None
    for hdr in exp.headerlist :
        expwcs = pywcs.WCS( hdr, hdulist )
        ix,iy = expwcs.wcs_sky2pix( ra, dec, 0 )
        if ix<0 or ix>expwcs.naxis1 : continue
        if iy<0 or iy>expwcs.naxis2 : continue
        onimage=True
        break

    if verbose and not onimage :
        print("Target RA,Dec is off image %s"%(exp.filename))
    return( onimage )


class Exposure( object ): 
    """ A class for single exposure flt.fits files, used for sorting
    them into groups by epoch and band for astrodrizzling.
    """

    def __init__( self, filename, outroot='TARGNAME' ) : 
        import pyfits
        import os
        from math import ceil

        self.filename = os.path.basename( filename )
        self.filepath = os.path.abspath( filename )

        self.header = pyfits.getheader( self.filepath )
        hdulist = pyfits.open(self.filepath)
        self.headerlist = []
        for hdu in hdulist :
            if hdu.name!='SCI':continue
            self.headerlist.append( hdu.header )

        if outroot=='TARGNAME' : outroot = self.header['TARGNAME']
        self.outroot = outroot

        if 'flt.fits' in self.filename : 
            self.fltsuffix = 'flt'
            self.drzsuffix = 'drz'
        elif 'flc.fits' in self.filename : 
            self.fltsuffix = 'flc'
            self.drzsuffix = 'drc'

        self.mjd = round( self.header['EXPSTART'], 2 )
        try : 
            filtername = self.header['FILTER']
        except : 
            filtername = self.header['FILTER1']
            if filtername.startswith('CLEAR') : 
                filtername = self.header['FILTER2']
        self.filtername = filtername[:5].lower()
        self.filter = self.filtername

        self.camera = self.header['INSTRUME']+'-'+self.header['DETECTOR']

        self.pid = self.header['PROPOSID']
        self.linenum = self.header['LINENUM']
        self.target = self.header['TARGNAME']

        # Visit name and exposure number (in the orbit sequence), 
        # as defined in APT
        self.visit = self.linenum.split('.')[0]
        self.expnum = int( self.linenum.split('.')[1] )

        if self.header['PATTERN1'] == 'NONE' :
            self.dither = ceil( self.expnum / 2. )
        else : 
            self.dither = self.header['PATTSTEP']

        self.crsplit = 0
        if 'CRSPLIT' in self.header.keys():
            if self.header['CRSPLIT'] == 2 :
                if self.header['SHUTRPOS'] == 'A' :
                    self.crsplit = 1
                elif self.header['SHUTRPOS'] == 'B' :
                    self.crsplit = 2

        self.rootname = self.header['ROOTNAME']
        self.exposure_time = self.header['EXPTIME']


        # 2-digits uniquely identifying this visit and this exposure
        # within this orbit, from the HST filename
        self.viscode = self.rootname[4:6].upper()
        self.expid = self.rootname[-3:-1]

        # epoch to be defined later
        self.epoch  = 99

    @property
    def epochdir( self ):
        return( '%s.e%02i'%( self.outroot, self.epoch ) )

    @property
    def FEVgroup( self ):
        """each exposure belongs to a single 'FEV group', which comprises all
        the images from the same Filter, same Epoch, and same Visit;
        suitable for combination with astrodrizzle in the first
        (pre-registration) drizzle pass, possibly including the CR
        rejection step.
        """
        return( '%s_e%02i_v%s'%( self.filter, self.epoch, self.visit ) )

    @property
    def FEgroup( self ):
        """each exposure belongs to a single 'FE group', which comprises all
        the images from the same Filter and same Epoch; suitable for
        combination with astrodrizzle in the second (post-registration)
        drizzle pass.
        """
        return( '%s_e%02i'%( self.filter, self.epoch ) )
           
    @property
    def summaryline( self ) :
        import os
        return( '%s  PID %i  Visit %s Exp %s Filter %s : Epoch %02i MJD %.1f '%(
                os.path.basename(self.filename), self.pid,
                self.visit, self.expid, self.filter,
                self.epoch, self.mjd ) )

    @property
    def summaryline_short( self ) :
        return('%9s  %5i %3s %3s %6s    %02i %7.1f '%(
                self.rootname, self.pid, self.visit, self.expid, self.filter,
                self.epoch, self.mjd ) )
