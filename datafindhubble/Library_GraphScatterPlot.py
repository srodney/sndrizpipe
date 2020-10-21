"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Graph a scatter plot in 2d or 3d -> depending on the dataset dimensions:
    Takes a Type_NumpyTwoDimensionalDataset -> 
    If it has 3 columns -> 3d
    If it has 2 columns -> 2d
    Then it creates the points
    MarkerColors are by defualt black, and labels can be added outside the method
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
    NumpyTwoDimensionalDataset
        Type:
            <type 'NoneType'>
        Description:
RETURNS:
    Result
        Type:
        Description:
"""

import numpy
import matplotlib
import matplotlib.pyplot
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
#------------------------------------------------------------------------------
import Type_NumpyTwoDimensionalDataset
import Library_GraphCube
import Library_IterableTakeSubsetOnCondition
import Library_FigureCreate
import Library_PythonZipLengthCheck
#------------------------------------------------------------------------------

def Main(
    NumpyTwoDimensionalDataset= None,
    NumpyTwoDimensionalDatasets = None,
    DatasetsErrorBars = None,
    DatasetLabels = None,
    ExistingFigure = None,
    Zorders = None,
    Xlabel = "X", 
    Ylabel = "Y", 
    Zlabel = "Z",
    PlotTitle = None,
    SaveFigureFilePath = None,

    #Style:
    MarkerSize = None,
    MarkerSizes = None,
    MarkerStyle = None,
    MarkerStyles = None,
    DatasetColors = None,
    DatasetsAlphas = None,
    MarkerColors = None,

    ConnectPoints = False,
    LogDomain = False, 
    LogRange = False,
    ScaleRange = None,

    alpha = None,
    PlotCubes = None,
    CubeSideLength = None,

    ForceScaling3D = None,
    ForceScaling2D = None,
    HorizontalMin = None,
    HorizontalMax = None,
    VerticleDisplacement = None,

    xmin = None,
    ymin = None,
    zmin = None,
    xmax = None,
    ymax = None,
    zmax = None,

    DatapointConditionFunction = None,

    AddPointLocationLabels = None,
    LocationLabelShift = None,
    LegendLocation = None,


    #Depricated args:
    colors = None,
    markerstyle = None,
    markersize = None,


    #std args:
    CheckArguments = True,
    PrintExtra = False,
    #**kwargs,
    ):

    Result = None


    #ARG FORMATTING / FIXING:
    #Make sure the numpy two dimensional datasets passed in have good shapes
    if (NumpyTwoDimensionalDatasets is not None):
        FirstDataset = NumpyTwoDimensionalDatasets[0]
        for Dataset in NumpyTwoDimensionalDatasets:
            if (Type_NumpyTwoDimensionalDataset.Main(Dataset) != True ):
                raise Exception('"(Type_NumpyTwoDimensionalDataset.Main(NumpyTwoDimensionalDataset) != True)\n"')
            if Dataset.shape[1] != FirstDataset.shape[1]:
                print('Dataset.shape', Dataset.shape)
                print('FirstDataset.shape', FirstDataset.shape)
                raise Exception('All Datasets must have same number of columns')
    else:
        if NumpyTwoDimensionalDataset is not None:
            NumpyTwoDimensionalDatasets = [NumpyTwoDimensionalDataset]
            MarkerColors = [c]
        else:
            raise Exception('Arg fail, needs at least one of [NumpyTwoDimensionalDataset, NumpyTwoDimensionalDatasets]')
    DatasetCount = len(NumpyTwoDimensionalDatasets)

    #Figure out the dimensionality of the plot:
    DimensionCount = NumpyTwoDimensionalDatasets[0].shape[1]


    #Create the none args
    if LegendLocation is None:
        LegendLocation = 'best'



    if Zorders is None:
        Zorders = [0]*DatasetCount
    if alpha is None:
        alpha = 1.0
    if DatasetsAlphas is None:
        DatasetsAlphas = [None]*DatasetCount 
    if DatasetLabels is None:
        DatasetLabels = [None]*DatasetCount
    if DatasetsErrorBars is None:
        DatasetsErrorBars = [None]*DatasetCount
    if DatasetColors is not None and MarkerColors is None:
        MarkerColors = DatasetColors
    if MarkerColors is None:
        MarkerColors = numpy.random.rand(DatasetCount, 3)  
        if PrintExtra: print('Generated MarkerColors', MarkerColors)



    if MarkerSize is None:
        MarkerSize = 7
    if MarkerSizes is None:
        MarkerSizes = [MarkerSize]*DatasetCount
    if MarkerStyle is None:
        MarkerStyle = 'o'
    if MarkerStyles is None:
        MarkerStyles = [MarkerStyle]*DatasetCount
    if PlotCubes is None:
        PlotCubes = False
    if ForceScaling3D is None:
        ForceScaling3D = False
    if ForceScaling2D is None:
        ForceScaling2D = False
    if VerticleDisplacement is None:
        VerticleDisplacement = 0             
    if ScaleRange is None:
        ScaleRange = 1


    #Figure out the minimum and maximum values on the first column of data
    if HorizontalMin is None:
        AllDataConcat = numpy.concatenate( NumpyTwoDimensionalDatasets )
        HorizontalMin = numpy.min( AllDataConcat[:, 0] )
        #print ('HorizontalMin', HorizontalMin)
        HorizontalMax = numpy.max( AllDataConcat[:, 0] )
        #print ('HorizontalMax', HorizontalMax)


    #Fix the datasets to have at least 2 columns. 
    #   If only one column exists, then set the second column to zero's
    NumpyTwoDimensionalDatasetsFixed = []
    for NumpyTwoDimensionalDataset in NumpyTwoDimensionalDatasets:
        NumpyTwoDimensionalDatasetFixed = NumpyTwoDimensionalDataset
        #If the dataset has shape n,1 then add an extra column of zeros
        if NumpyTwoDimensionalDataset.shape[1] == 1:
            NumpyTwoDimensionalDatasetFixed = numpy.hstack( [
                NumpyTwoDimensionalDataset,
                numpy.zeros(shape=NumpyTwoDimensionalDataset.shape)
                 ] )
        NumpyTwoDimensionalDatasetsFixed.append(NumpyTwoDimensionalDatasetFixed)
    NumpyTwoDimensionalDatasets = NumpyTwoDimensionalDatasetsFixed


    #Deal force scaling options:
    if ForceScaling2D and ForceScaling3D:
        if DimensionCount is 2:
            ForceScaling2D = True
            ForceScaling3D = False
        elif DimensionCount is 3:
            ForceScaling2D = False
            ForceScaling3D = True

    if ForceScaling2D or ForceScaling3D:
        MonitorWidthPixels = 1920.0
        MonitorHeightPixels = 1080.0
        FigureVertToHorizontalScaling = MonitorHeightPixels / MonitorWidthPixels
        VerticleMin = HorizontalMin * FigureVertToHorizontalScaling
        VerticleMax = HorizontalMax * FigureVertToHorizontalScaling

    if ForceScaling2D:
        xmin = HorizontalMin
        xmax = HorizontalMax
        ymin = HorizontalMin/ FigureVertToHorizontalScaling
        ymax = HorizontalMax/ FigureVertToHorizontalScaling

    if ForceScaling3D:
        xmin = HorizontalMin
        xmax = HorizontalMax
        ymin = HorizontalMin
        ymax = HorizontalMax
        zmin = VerticleMin + VerticleDisplacement
        zmax = VerticleMax + VerticleDisplacement


    #Check args:
    if (CheckArguments):
        ArgumentErrorMessage = ""

        if  (PlotCubes is True ) and (CubeSideLength is None):
            ArgumentErrorMessage += '`CubeSideLength` is None'

        if (ForceScaling3D is True) and (None in [HorizontalMin, HorizontalMax] ):
            ArgumentErrorMessage += 'None in [`HorizontalMin`, `HorizontalMax`]'

        if not isinstance(MarkerStyles[0], str):
            ArgumentErrorMessage += 'not isinstance(MarkerStyles[0], str)'

        if (colors is not None):
            ArgumentErrorMessage += '`colors` is depricated. replaced by `Colors`'

        if (markerstyle is not None):
            ArgumentErrorMessage += '`markerstyle` is depricated. replaced by `MarkerStyle`'

        if (markersize is not None):
            ArgumentErrorMessage += '`markersize` is depricated. replaced by `MarkerSize`'

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #Get or create the figure object:
    fig = None
    subplot = None
    if ExistingFigure is None:
        fig = Library_FigureCreate.Main(
            DimensionCount= DimensionCount,
            DimensionLabels= [Xlabel, Ylabel, Zlabel],
            PlotTitle= PlotTitle,
            LimitBoxMinimum= [xmin, ymin, zmin],
            LimitBoxMaximum= [xmax, ymax, zmax],
            FontSize= None,
            ShowGrid= None
            )
        subplot = fig.onlysubplot
        
    else:
        fig = ExistingFigure
        subplot = fig.onlysubplot
#------------------------------------------------------------------------------


    #Loop through each dataset and plot each set of points
    #   with the desired set of properties for that dataset
    #   (points of different shapes and sizes must be in different datasets)
    ZipLengthCheck = Library_PythonZipLengthCheck.Main(
        ListOfLists= [
            NumpyTwoDimensionalDatasets, 
            DatasetLabels, 
            MarkerColors, 
            DatasetsAlphas, 
            MarkerStyles, 
            MarkerSizes,
            Zorders
            ],
        RaiseException = True,        )
    for \
            NumpyTwoDimensionalDataset, \
            DatasetLabel, \
            Color, \
            DatasetAlphas, \
            MarkerStyle, \
            MarkerSize, \
            Zorder, \
            DatasetErrorBars \
        in zip(
            NumpyTwoDimensionalDatasets, 
            DatasetLabels, 
            MarkerColors, 
            DatasetsAlphas, 
            MarkerStyles, 
            MarkerSizes,
            Zorders,
            DatasetsErrorBars,
        ):

        #Fix the alphas formatting to match dimensionality
        if isinstance( DatasetAlphas , (float, int)  ):
            DatasetAlphas = [DatasetAlphas]*len(NumpyTwoDimensionalDataset)

        #Take a subset of the data points:
        if DatapointConditionFunction is not None:
            NumpyTwoDimensionalDataset = Library_IterableTakeSubsetOnCondition.Main(
                Iterable= NumpyTwoDimensionalDataset,
                ConditionFunction= DatapointConditionFunction
                )
            NumpyTwoDimensionalDataset = numpy.array(NumpyTwoDimensionalDataset)

        #Get meta data about the dataset
        RowCount = NumpyTwoDimensionalDataset.shape[0]
        ColCount = NumpyTwoDimensionalDataset.shape[1]
        if not (ColCount in [2,3]):
            raise Exception('Col count not manageable')
        NumpyTwoDimensionalDatasetTranspose = NumpyTwoDimensionalDataset.T


        #If we are making a 2D plot:
        if (ColCount == 2):
            Xvals = NumpyTwoDimensionalDatasetTranspose[0]
            Yvals = NumpyTwoDimensionalDatasetTranspose[1]*ScaleRange

            if (LogDomain):
                pass
            if (LogRange):
                Yvals = numpy.log(Yvals)

            matplotlib.pyplot.scatter(
                Xvals, 
                Yvals,
                c= numpy.atleast_2d( Color ),  #<- color needs to be 2D array
                label = DatasetLabel,
                s=MarkerSize, 
                alpha=alpha,
                marker = MarkerStyle,
                zorder = Zorder,
                )

            if not (DatasetErrorBars is None):
                matplotlib.pyplot.errorbar(Xvals, Yvals, DatasetErrorBars, 
                    elinewidth = 1,
                    #c = 'red',
                    c =  Color ,
                    fmt = '.',
                    capsize = 10,
                    )         


            if ConnectPoints:
                matplotlib.pyplot.plot(
                    Xvals, 
                    Yvals,
                    c=Color, 
                    alpha=alpha)

        #If we are making a 3D plot:
        elif (ColCount == 3):
            Xvals = NumpyTwoDimensionalDatasetTranspose[0]
            Yvals = NumpyTwoDimensionalDatasetTranspose[1]
            Zvals = NumpyTwoDimensionalDatasetTranspose[2]*ScaleRange

            if PlotCubes:
                for SingleCubeCenter in NumpyTwoDimensionalDataset:
                    #Add a cube to the figure at each point
                    fig = Library_GraphCube.Main(
                        ExistingFigure = fig,
                        CubeCenter= SingleCubeCenter,
                        CubeSideLength= CubeSideLength,
                        color =  [0, 0, 0],
                        )

            elif (PlotCubes == False) and (DatasetAlphas is None):
                matplotlib.pyplot.plot(
                    Xvals, 
                    Yvals,
                    Zvals,  
                    c=Color, 
                    label = DatasetLabel,
                    MarkerSize=MarkerSize, 
                    marker= MarkerStyle,#'o', 
                    linestyle = 'None',
                    alpha=alpha,
                    )

            elif (PlotCubes == False) and (DatasetAlphas is not None):

                ValueNumber = 0
                for Zval in Zvals:
                    SingleAlpha = DatasetAlphas[ValueNumber]
                    if PrintExtra > 2:
                        print ('SingleAlpha', SingleAlpha)
                        print (Xvals[ValueNumber])
                        print (Yvals[ValueNumber])
                        print (Zvals[ValueNumber])

                    matplotlib.pyplot.plot(
                        [Xvals[ValueNumber]], 
                        [Yvals[ValueNumber]],
                        [Zvals[ValueNumber]],  
                        c=Color, 
                        label = DatasetLabel,
                        marker= MarkerStyle,#'o', 
                        MarkerSize = MarkerSize,
                        linestyle = 'None',
                        alpha=float(SingleAlpha),
                        )
                    ValueNumber += 1
        else:
            raise Exception('ColCount not logical')


        #Regardless of the dimensionality of the dataset
        #   Add location labels:
        if AddPointLocationLabels :
            if DimensionCount == 3:
                #TODO: https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
                raise Exception('TODO')
            if LocationLabelShift is None:
                LocationLabelShift = 2*numpy.ones(DimensionCount)
            for DataPoint in NumpyTwoDimensionalDataset:
                PointLabel = str(list(DataPoint) )
                #print ('DataPoint', DataPoint)
                #print ('LocationLabelShift', LocationLabelShift)
                matplotlib.pyplot.annotate( PointLabel, DataPoint + LocationLabelShift   )



    #Add legend (we have to add the legend at the end. cannot be created in advance):
    if (not None in DatasetLabels):
        from collections import OrderedDict
        import matplotlib.pyplot as plt
        #plt.legend(loc = 'best', numpoints=1)
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc = LegendLocation)


    #Save the file:
    if (SaveFigureFilePath is not None):
        plt.savefig( SaveFigureFilePath, bbox_inches='tight' )
    

    #Return the figure object in case you want to add to it later:
    Result = fig
    return Result 












