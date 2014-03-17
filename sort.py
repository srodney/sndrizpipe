# S.Rodney 2014.03.04
# Sorting flt files into epochs by date and filter
# for registration and drizzling
import exceptions

def intoEpochs( explist, mjdmin=0, mjdmax=0, epochspan=5, 
                makedirs=False, verbose=True, clobber=False ):
    """ 
    sort a list of flts into epochs.  Anything with MJD<mjdmin goes
    into the first epoch, anything with MJD>mjdmax goes into the last
    epoch.  All other epochs are made of exposures taken within
    epochspan days of eachother.

    Set makedirs=True to copy the flt files into separate epoch
    directories for drizzling
    """
    import os
    import shutil
    import numpy as np

    if type(explist)==str : 
        explist = getExpList( explist )

    mjdlist = np.array( [ exp.mjd for exp in explist ] )
    visitlist = np.array( [ exp.visit for exp in explist ] )
    filterlist = np.array( [ exp.filter for exp in explist ] )
    epochlist = np.zeros( len(mjdlist) )

    thisepochmjd0 = mjdlist.min()
    thisepoch = 0
    for imjd in mjdlist.argsort() : 
        thismjd = mjdlist[imjd]
        if (mjdmin>0) and (thismjd < mjdmin) : thisepoch=0
        elif (mjdmax>0) and (thismjd > mjdmax) : thisepoch=-1
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
            if not os.path.isdir( exp.epochdir ): 
                os.makedirs( exp.epochdir )
            if verbose : print("%s ==> %s"%(exp.filename, exp.epochdir) )
            shutil.copy( exp.filepath, exp.epochdir )

    return( explist, np.unique(epochlist) )


def getExpList( fltlist='*fl?.fits', outroot='TARGNAME' ):
    """ make a list of Exposure objects for each flt file"""
    from stsci import tools
    if type(fltlist)==str :
        fltlist=tools.parseinput.parseinput(fltlist)[0]
    return( [ Exposure( fltfile, outroot=outroot ) for fltfile in fltlist ] )



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

        try: 
            h=pyfits.getheader( self.filepath )
        except exceptions.Exception as e: 
            raise exceptions.RuntimeError("Unable to open file %s."%filepath)

        if outroot=='TARGNAME' : outroot = h['TARGNAME']
        self.outroot = outroot

        if 'flt.fits' in self.filename : 
            self.fltsuffix = 'flt'
            self.drzsuffix = 'drz'
        elif 'flc.fits' in self.filename : 
            self.fltsuffix = 'flc'
            self.drzsuffix = 'drc'

        self.mjd = round( h['EXPSTART'], 2 )
        try : 
            filtername = h['FILTER']
        except : 
            filtername = h['FILTER1']
            if filtername.startswith('CLEAR') : 
                filtername = h['FILTER2']
        self.filtername = filtername[:5].lower()
        self.filter = self.filtername

        self.camera = h['INSTRUME']+'-'+h['DETECTOR']

        self.pid = h['PROPOSID']
        self.linenum = h['LINENUM']
        self.target = h['TARGNAME']

        # Visit name and exposure number (in the orbit sequence), 
        # as defined in APT
        self.visit = self.linenum.split('.')[0]
        self.expnum = int( self.linenum.split('.')[1] )

        if h['PATTERN1'] == 'NONE' :
            self.dither = ceil( self.expnum / 2. )
        else : 
            self.dither = h['PATTSTEP']

        self.crsplit = 0
        if 'CRSPLIT' in h.keys(): 
            if h['CRSPLIT'] == 2 :
                if h['SHUTRPOS'] == 'A' : 
                    self.crsplit = 1
                elif h['SHUTRPOS'] == 'B' : 
                    self.crsplit = 2

        self.rootname = h['ROOTNAME']


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
