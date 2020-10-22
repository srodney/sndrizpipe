"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Wraps around the hstphot package written by steven rodney
ARGS:
    CheckArguments
        Type:
            python boolean
        Description:
            if true, checks the arguments with conditions written in the function
            if false, ignores those conditions
    PrintExtra
        Type:
            python integer
        Description:
            if greater than 0, prints addional information about the function
            if 0, function is expected to print nothing to console
            Additional Notes:
                The greater the number, the more output the function will print
                Most functions only use 0 or 1, but some can print more depending on the number
    SubMaskedFilePath
        Type:
            <class 'NoneType'>
        Description:
            None
    PsfFilePath
        Type:
            <class 'NoneType'>
        Description:
            None
    SaveFolderPath
        Type:
            <class 'NoneType'>
        Description:
            None

    Coodinates
        Type:
            <class 'NoneType'>
        Description:
            None
    CoodinatesType
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""

import hstphot
import hstphot.dophot
import hstphot.dophot
import hstphot.util
#-------------------------------------------------------------------------------
import os
import matplotlib
import matplotlib.pyplot
import numpy
import Library_SystemDirectoryCreateSafe
import Library_PickleAndSaveToFile
import Library_StringFilePathGetFileName
import Library_Round
import Library_PressTheAnyKey
import Library_ArrayOfStringFileNamesStripAllExtensions
import Library_FilePathExists
#-------------------------------------------------------------------------------
def Main(
    SubMaskedFilePath= None,
    PsfFilePath= None,
    Coodinates= None,
    CoodinatesType= None,
    ResultFormat = None,
    SaveFolderPath = None,
    MakeFigure = None,
    ShowFigure = None,
    ObjectId = None,
    OverWrite = None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if OverWrite is None:
        OverWrite = True

    #What is the file name of the thing we want to phot?
    SubMaskedFileName = Library_StringFilePathGetFileName.Main(  SubMaskedFilePath   )
    SubMaskedFileNoExt = Library_ArrayOfStringFileNamesStripAllExtensions.Main([SubMaskedFileName])[0]

    #Where are we going to save our work?
    SaveFilePath = None
    if SaveFolderPath is not None:
        Library_SystemDirectoryCreateSafe.Main(SaveFolderPath)
        SaveFileName = SubMaskedFileNoExt  + '_' + CoodinatesType + str(Coodinates) +'_phot.png'
        SaveFilePath = SaveFolderPath +  '/' + SaveFileName 

    SaveFilePathExists = Library_FilePathExists.Main( SaveFilePath )
    if OverWrite is False and SaveFilePathExists:
        print('file exists, skipping')
        return None


    if CoodinatesType is None:
        CoodinatesType = 'radec'  #Same as 'sky'

    if ResultFormat is None:
        ResultFormat = 'Dictionary' #ALL THE KINDS OF RESULTS

    if MakeFigure is None:  
        MakeFigure = False

    if ShowFigure is None:
        ShowFigure = False


    #What point spread function file should we use for photometry?
    if PsfFilePath is None:

        #What is the sub masked file pixscale?
        SubMaskedFilePixScale = hstphot.util.getpixscale(SubMaskedFilePath)
        SubMaskedFilePixScaleString = str(
            int(Library_Round.Main(
                Number= SubMaskedFilePixScale,
                Method= 'SignificantFigures',
                DigitCount= 1,
                Direction= None, #'Down',
                #PrintExtra = True,
                )*1000)
            )
        #print ('SubMaskedFilePixScale', SubMaskedFilePixScale)
        #print ('SubMaskedFilePixScaleString', SubMaskedFilePixScaleString)


        #what is the sub masked file band filter?
        SubMaskedFileBandFilter = SubMaskedFileName.split('_')[-4]
        #print ('SubMaskedFileBandFilter', SubMaskedFileBandFilter)


        #Go find the psf file which matches the properties of the submasked file
        PsfFolder = '/home/developer0/DataHome/PhotUtils/p330e.psf.images'
        ValidPsfFileNames = []
        PsfFileNames = os.listdir( PsfFolder )
        for PsfFileName in PsfFileNames:

            #print ('PsfFileName', PsfFileName)

            if 'psf_model' in PsfFileName:
                PsfFileBandFilter = PsfFileName.split('_')[1]
                #print ('PsfFileBandFilter', PsfFileBandFilter)
                PsfFilePixScale = PsfFileName.split('_')[2]
                #print ('PsfFilePixScale', PsfFilePixScale)

                if SubMaskedFileBandFilter in PsfFileBandFilter and SubMaskedFilePixScaleString in PsfFilePixScale:
                    #print ('PsfFileName', PsfFileName, 'found')
                    ValidPsfFileNames.append(PsfFileName)

                    #if '90' in PsfFileName:
                    #    PsfFilePath = PsfFolder + '/' + PsfFileName
                    #    print ('PsfFilePath', PsfFilePath)
        #print ('ValidPsfFileNames', ValidPsfFileNames)
        if len(ValidPsfFileNames) == 1:
            PsfFilePath = PsfFolder + '/' + ValidPsfFileNames[0]
        elif len(ValidPsfFileNames) < 1:
            print ('SubMaskedFileName', SubMaskedFileName)
            print ('SubMaskedFilePixScale', SubMaskedFilePixScale)
            print ('SubMaskedFilePixScaleString', SubMaskedFilePixScaleString)
            print ('SubMaskedFileBandFilter', SubMaskedFileBandFilter)

            raise Exception('no psf file found which matches the submasked iformation' )
        elif len(ValidPsfFileNames) > 1:
            print ('ValidPsfFileNames', ValidPsfFileNames)
            raise Exception('too many valid psf file names found. Ambiguous which one to use')

    print ('PsfFilePath', PsfFilePath)
    #Library_PressTheAnyKey.Main()

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    targetim = hstphot.dophot.doastropyphot(
        SubMaskedFilePath, 
        coordinates = Coodinates, 
        apradarcsec= numpy.arange(0.1,1.0,0.025),
        psfimfilename=PsfFilePath,
        coord_type = CoodinatesType,
        )
    print ('targetim.pixscale', targetim.pixscale)

    phot = targetim.phot_summary_table #This line was missing from the notebook...

    #print ('dir(phot)', dir(phot))
    print ('phot.keys()', phot.keys())
    #print ('press the any key...')
    #input()

    if MakeFigure:
        PlotTitle = 'ID:' + str(ObjectId) + '\n' 
        PlotTitle += '[ra,dec]==' + str(Coodinates)

        Inch_in_Pixels = 80.0
        MonitorWidthPixels = 1920.0
        MonitorHeightPixels = 1080.0
        MonitorSize = (MonitorWidthPixels / Inch_in_Pixels,MonitorHeightPixels/Inch_in_Pixels)

        fig = matplotlib.pyplot.figure(figsize=MonitorSize) 
        fig.suptitle( PlotTitle )
        #matplotlib.pyplot.plot(phot['APER'], phot['MAG'], 'ro', ls=' ')
        matplotlib.pyplot.plot(phot['APER'], phot['FLUX'], 'ro', c='blue', ls=' ')
        matplotlib.pyplot.errorbar(phot['APER'], phot['FLUX'] , phot['FLUXERR'], 
            elinewidth = 1,
            c = 'red',
            fmt = '.',
            capsize = 10,
            )
        print ("phot['FLUXERR']", phot['FLUXERR'])

        ax = matplotlib.pyplot.gca()
        ax.set_xlabel('APER')
        #ax.set_ylabel('MAG')
        ax.set_ylabel('FLUX')
        ax.set_xlim(-0.1, 1.1)

    if ResultFormat == 'Dictionary':
        Result = {
            'photimageobject':  targetim, #<-- Has the full phot_summary_table inside it
            'APER' :            phot['APER'],
            'FLUX' :            phot['FLUX'],
            'FLUXERR' :         phot['FLUXERR'], 
            }

    elif ResultFormat == 'photimageobject':
        Result = targetim

    elif ResultFormat == 'phot_summary_table': #<-- This will be the most common choice
        Result = targetim.phot_summary_table

    else:
        raise Exception('`ResultFormat` unrecog. Try again. Do not pass go. Do not collect 200 dollars')

    if SaveFolderPath is not None:
        if MakeFigure:

            matplotlib.pyplot.savefig( SaveFilePath )
        Library_PickleAndSaveToFile.Main(
            Object= Result,
            SaveFilePath=SaveFolderPath + '/' + SubMaskedFileNoExt + '.pkl'
            )

    if ShowFigure:
        matplotlib.pyplot.show()

    return Result 
















































