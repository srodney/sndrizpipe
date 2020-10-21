"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Assumes that the photometry is already done and sitting in a file somewhere
    What is the associated light curve for all the photometry of interest?
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
    SuperNovaIdPhotometryFolderPath
        Type:
            <class 'NoneType'>
        Description:
            None
    SuperNovaIdLightCurveFolderPath
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import matplotlib
import numpy
import glob
import Config_NumpyMatplotlibColors
import Library_GraphScatterPlot
import Library_LoadPickleFile
import Library_NumpyTwoDimensionalDatasetFindNearestNeighbors
#-------------------------------------------------------------------------------
def Main(
    SuperNovaId = None,
    SuperNovaIdPhotometryFolderPath= None,
    SuperNovaIdLightCurveFolderPath= None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    SupernovaPhotPicklePaths  = list(glob.iglob( SuperNovaIdPhotometryFolderPath + '/**/*sub_masked.pkl', recursive=True))

    EpochLabels = []
    LightCurveTimesFluxsErrors = []
    for SupernovaPhotPicklePath in SupernovaPhotPicklePaths:
        print ('    photpicklepath:', SupernovaPhotPicklePath)
    
        EpochLabel = SupernovaPhotPicklePath.split('_')[-4] + '_' + SupernovaPhotPicklePath.split('_')[-3]
        print ('EpochLabel', EpochLabel)
        EpochLabels.append(EpochLabel)

        SuperNovaPhotTable = Library_LoadPickleFile.Main( SupernovaPhotPicklePath )['photimageobject'].phot_summary_table
        Apers = SuperNovaPhotTable['APER']
        MJDs = SuperNovaPhotTable['MJD']
        Fluxs = SuperNovaPhotTable['FLUX']
        Fluxerrs = SuperNovaPhotTable['FLUXERR']

        #Find the nearest aper to 0.4
        NearestApersSearchResult = Library_NumpyTwoDimensionalDatasetFindNearestNeighbors.Main(
            NumpyTwoDimensionalDataset= numpy.array( [list(Apers)] ).T,
            Coordinate= [0.4],
            NumberNeighbors= 1,
            Radius= None,
            Method = None,
            )
        print (NearestApersSearchResult)
    
        NearestAperIndex = NearestApersSearchResult['NeighborIndices'][0]
        print ('NearestAperIndex', NearestAperIndex)


        Aper = Apers[NearestAperIndex]
        MJD = MJDs[NearestAperIndex]
        Flux = Fluxs[NearestAperIndex]
        Fluxerr = Fluxerrs[NearestAperIndex]

        print ('Aper', Aper)
        print ('MJD', MJD)
        print ('Flux', Flux)
        print ('Fluxerr', Fluxerr)

        LightCurveTimesFluxsErrors.append([MJD, Flux, Fluxerr])
    LightCurveTimesFluxsErrors = numpy.array(LightCurveTimesFluxsErrors)



    #Make the lightcurve at 0.4 aper exactly:
    print ('LightCurveTimesFluxsErrors')
    print (LightCurveTimesFluxsErrors)
    Library_GraphScatterPlot.Main(
        NumpyTwoDimensionalDatasets = [ LightCurveTimesFluxsErrors[:, [0,1] ] ],
        DatasetLabels = ['0.4 Aper Light Curve'],
        DatasetColors = [Config_NumpyMatplotlibColors.ColorBlue],
        MarkerSizes = [20],
        PlotTitle = "Supernova `" + str(SuperNovaId) + "` Light Curve",
        ConnectPoints = False,
        )
    matplotlib.pyplot.errorbar(
        LightCurveTimesFluxsErrors[:,0], #MJDs
        LightCurveTimesFluxsErrors[:,1], #Fluxes
        LightCurveTimesFluxsErrors[:,2], #Fluxerrs
        elinewidth = 1,
        c = 'red',
        fmt = '.',
        capsize = 10,
        )

    #Add some labels so we know what epochs we are talking about:
    LocationLabelShift = numpy.array([0,0]) #2*numpy.ones(2)
    for DataPoint, PointLabel in zip( LightCurveTimesFluxsErrors[:, [0,1] ], EpochLabels ):
        print ('PointLabel', PointLabel)
        print ('DataPoint', DataPoint)
        matplotlib.pyplot.annotate( PointLabel, DataPoint + LocationLabelShift   )

    #Save the figure:
    for ParentFolderPath in [SuperNovaIdPhotometryFolderPath, SuperNovaIdLightCurveFolderPath]:
        SaveFigureFilePath =  ParentFolderPath + '/' + str(SuperNovaId) + '_LightCurve.png'
        matplotlib.pyplot.savefig( SaveFigureFilePath, bbox_inches='tight' )

    matplotlib.pyplot.close('all')
    #print ('press the any key...')
    #input()



    return Result 












