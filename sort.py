# S.Rodney 2014.03.04
# Sorting flt files into epochs by date and filter
# for registration and drizzling
import exceptions

def intoEpochs( explist, epochlistfile=None, mjdmin=0, mjdmax=0, epochspan=5,
                makedirs=False, onlyfilters=[], onlyepochs=[], 
                checkradec=None, verbose=True, clobber=False ):
    """ 
    sort a list of flts into epochs.  Anything with MJD<mjdmin goes
    into the first epoch, anything with MJD>mjdmax goes into the last
    epoch.  All other epochs are made of exposures taken within
    epochspan days of eachother.

    Provide epochlistfile to specify a file to write the epochs to, or else
    this will default to <outroot>_epochs.txt using the output rootname
    of the first exposure.  If the outfile exists and clobbering is turned
    off, then we adopt the epoch listing in the existing epochlistfile.

    Set makedirs=True to copy the flt files into separate epoch
    directories for drizzling
    """
    import os
    import shutil
    import numpy as np

    if type(explist)==str : 
        explist = getExpList( explist )

    if not epochlistfile :
        epochlistfile =  "%s_epochs.txt"%explist[0].outroot
    if os.path.exists( epochlistfile ) and not clobber :
        print( "%s exists. Adopting existing epoch sorting."%epochlistfile )
        explist = read_epoch_list( explist, epochlistfile )
        epochlist = np.unique( [ exp.epoch for exp in explist ] )
        return( explist, epochlist )

    if onlyfilters :
        if type(onlyfilters)==str :
            onlyfilters = onlyfilters.lower().split(',')
        onlyfilters = [ filt[:5].lower() for filt in onlyfilters ]
    if type(onlyepochs) in [str,int,float]  :
        onlyepochs = [ int(ep) for ep in str(onlyepochs).split(',') ]

    mjdlist = np.array( [ exp.mjd for exp in explist ] )
    visitlist = np.array( [ exp.visit for exp in explist ] )
    filterlist = np.array( [ exp.filter for exp in explist ] )
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

    lastepoch = np.max( epochlist ) + 1
    for iexp in range(len(explist)) : 
        if explist[iexp].epoch == -1 : 
            explist[iexp].epoch = lastepoch
            epochlist[iexp] = lastepoch
            
    thisepoch = 0 
    for iexp in epochlist.argsort() : 
        if explist[iexp].epoch != thisepoch : 
            thisepoch = explist[iexp].epoch
            if verbose: print( "" )
        if verbose: print( explist[iexp].summaryline )

    if makedirs : 
        if clobber : 
            if verbose: print( "Wiping away existing epoch dirs.")
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
            if verbose : print("%s ==> %s"%(exp.filename, exp.epochdir) )
            shutil.copy( exp.filepath, exp.epochdir )

    write_epoch_list( explist, epochlistfile, clobber=clobber )
    return( explist, np.unique(epochlist) )


def read_epoch_list( explist, epochlistfile ):
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
        iexp = rootnamelist.index(exp.rootname)
        exp.epoch = epochlist[iexp]
    return( explist )


def write_epoch_list( explist, outfile, clobber=False ):
    """Write out a text file listing the Exposures in explist, sorted into
    epochs and grouped by visit and filter
    """
    import os
    from astropy.table import Table

    if os.path.exists( outfile ) :
        if clobber :
            os.path.remove( outfile )
        else :
            print("%s exists. Not clobbering."%outfile)
            return(outfile)

    # TODO : Make tabledata into sorted numpy arrays for formatted output.
    tabledata = { 'rootname':[exp.rootname for exp in explist],
                  'epoch':[exp.epoch for exp in explist],
                  'filter':[exp.filter for exp in explist],
                  'visit':[exp.visit for exp in explist],
                  'mjd':[exp.mjd for exp in explist]
                  }
    outtable = Table( tabledata  )
    outtable.write( outfile, format='ascii.commented_header')
    return( outtable )


def getExpList( fltlist='*fl?.fits', outroot='TARGNAME' ):
    """ make a list of Exposure objects for each flt file"""
    from stsci import tools
    if type(fltlist)==str :
        fltlist=tools.parseinput.parseinput(fltlist)[0]
    return( [ Exposure( fltfile, outroot=outroot ) for fltfile in fltlist ] )


def checkonimage(exp,checkradec,verbose=True):
    """Check if the given ra,dec falls anywhere within the
    science frame of the image that defines the given Exposure object.
    """
    import pywcs
    ra,dec = checkradec
    onimage = False
    for hdr in exp.headerlist :
        expwcs = pywcs.WCS(hdr)
        ix,iy = expwcs.wcs_sky2pix( ra, dec, 0 )
        if ix<0 or ix>expwcs.naxis1 : continue
        if iy<0 or iy>expwcs.naxis2 : continue
        onimage=True
        break

    if verbose and not onimage :
        print("Target RA,Dec is off image ."%())
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


        # 2-digits uniquely identifying this visit and this exposure
        # within this orbit, from the HST filename
        self.viscode = self.rootname[4:6].upper()
        self.expid = self.rootname[-3:-1]

        # epoch to be defined later
        self.epoch  = 99

    #@property
    #def drzsuffix( self ):
    #    if self.camera=='ACS-WFC' : 
    #        return( 'drc' )
    #    else :
    #        return( 'drz' )

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
