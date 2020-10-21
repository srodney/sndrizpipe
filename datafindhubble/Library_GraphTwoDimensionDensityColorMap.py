"""
SOURCE:
    Mind of Douglas Adams
    Meshgrid exmaple on the kde scipy page:
        http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html

DESCRIPTION:
    Graph an arbitrary function of 2 variables
    3d graph tends to be difficult to view because of angle
    2d heat map is likely to be a better choice


    Matplotlib Compatability:
        This function does not play nice with other graphs:
        Does not allow for graphing additional things on the same plot:
            fig = matplotlib.pyplot.figure() 
                Included in this method
            matplotlib.pyplot.draw() 
                Included in this method
        Can still be called amist other programs without a delay, because matplotlib.pyplot.show() is not invoked


ARGS (9 Count):
    Function:
        python function which has ARGS (1 count):
            Point:
                numpy array of two values
                point looks like [x_coord, y_coord]

        GraphTwoDimensionalDensityColorMap is designed to graph on 3 dimmensional coordinates
        Point == [x,y]
        F( Point )  => returns z

 
    DomainMinimumPoint:
        used for plot boundaries
        numpy array of two values:
            [x_min, y_min]

    DomainMaximumPoint:
        used for plot boundaries
        numpy array of two values:
            [x_max, y_max]

    ObservedDataset:
        Type_NumpyTwoDimensionalDataset
            [point, point, ...,  point]
        Used for scatter presentation

    PlotThreeDimensional:
        The plot generated will be a heat map regardless of choice with color correpsonding to density
        This can be two values:
            True
                Show visual third dimension and look at the surface from a fixed point
                Cannot plot contours
            False
                2D plot
                Will show contours

    Xlabel: ...
    Ylabel: ...
    Zlabel: ...


RETURNS:
    None

"""

import matplotlib
import matplotlib.cm
import matplotlib.pyplot
import numpy
import multiprocessing_on_dill
#------------------------------------------------------------------------------
import Library_FigureCreate
import Library_ParallelLoop
import Type_NumpyTwoDimensionalDataset
import Library_DatasetGetMinimumDatapoint
import Library_DatasetGetMaximumDatapoint
import Library_LazyPickleDump
import Library_IterableSplitIntoChunks
#------------------------------------------------------------------------------
def Main( 
    Function = None, 
    #Functions = None,
    DomainMinimumPoint = None, 
    DomainMaximumPoint = None, 

    ObservedDataset = None, 
    Markersize = None,

    PlotThreeDimensional = False, 
    ShowContours = False, 
    ShowContourLabels = False,
    SurfaceType = None,
    PluginPointCount = None,
    PluginSimultaneous = None,

    Xlabel = "X", 
    Ylabel = "Y", 
    Zlabel = "Z",
    PlotTitle = None,
    LogX = False,
    LogY = False, 
    LogZ = False,
    Zorder = None,
    ScaleRange = None,
    ColorMap = None,

    CheckArguments = True,  
    SaveFigureFilePath = None,

    HideProgressBar = None,
    Parallelize = None,
    BatchCount = None,
    BatchSize = None,

    ResultFormat = None,
    PickleResult = None,
    ExistingFigure = None,
    PrintExtra = False,
    ):
    Result = None

    #---------------------------------------------------------------------------
    #ARG CHECKING:
    if (CheckArguments): 
        ArgumentErrorMessage = ""

        #Make sure we have enough information for a domain box:
        if ObservedDataset is None:    
            if DomainMinimumPoint is None or DomainMaximumPoint is None:
                ArgumentErrorMessage += 'Need a dataset or a domain box for graphing a density map\n'

        #Make sure that the format of the observed ataset is correct:
        elif ObservedDataset is not None:    
            if (Type_NumpyTwoDimensionalDataset.Main(ObservedDataset) != True ):
                ArgumentErrorMessage += "(Type_NumpyTwoDimensionalDataset.Main(ObservedDataset) != True)\n"

        if (len(ArgumentErrorMessage) > 0 ):
            if (PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #---------------------------------------------------------------------------
    #ARG FORMATTING / FIXING /
    #Figure out parallel processing loop settings:
    if HideProgressBar is None:
        HideProgressBar = False

    if BatchCount is None and BatchSize is None:
        BatchCount = 100

    if Parallelize is None:
        Parallelize = False

    LoopAlgorithm = None
    if Parallelize:
        LoopAlgorithm = 'multiprocessing'
    else:
        LoopAlgorithm = 'loop'

    #Figure out how many dimensions matplotlib needs to render
    PlotDimensionCount = None
    if PlotThreeDimensional:
        PlotDimensionCount = 3
    else:
        PlotDimensionCount = 2

    #Fill in any none values to defaults:
    if Markersize is None:
        Markersize = 1

    #Extract all the observations in X, Y coordinates:
    if (ObservedDataset is not None):
        ObservedPointsCount = len(ObservedDataset)
        ObservedX = ObservedDataset.T[0]
        ObservedY = ObservedDataset.T[1]
    else:
        ObservedPointsCount = 0
        ObservedX = numpy.array([])
        ObservedY = numpy.array([])

    #Infer the plot domain minimums and maximums from the dataset if omited
    if (DomainMinimumPoint  is None):
        DomainMinimumPoint = numpy.nanmin(ObservedDataset, axis = 0)
    if (DomainMaximumPoint  is None):
        DomainMaximumPoint = numpy.nanmax(ObservedDataset, axis = 0) 

    #Further format the domain box information to smaller variables:
    DomainMinimumPoint = numpy.array(DomainMinimumPoint)
    DomainMaximumPoint = numpy.array(DomainMaximumPoint)
    xmin, ymin = DomainMinimumPoint
    xmax, ymax = DomainMaximumPoint
    xrng, yrng = DomainMaximumPoint - DomainMinimumPoint
    if PrintExtra:
        print('DomainMinimumPoint', DomainMinimumPoint)
        print('DomainMaximumPoint', DomainMaximumPoint)

    #Plugin options:
    if PluginPointCount is None:
        PluginPointCount = 10**5

    if PluginSimultaneous is None:
        PluginSimultaneous = False

    #misc formating options:
    if ResultFormat is None:
        ResultFormat = 'fig'

    if ScaleRange is None:
        ScaleRange = 1.

    if PickleResult is None:    
        PickleResult = False

    if Zorder is None:
        Zorder = 0 #Not using... causes more trouble than its worth

    if SurfaceType is None:
        SurfaceType = 'solid'
    
    if ColorMap is None:
        #ColorMap = matplotlib.pyplot.cm.gist_earth_r
        ColorMap = matplotlib.pyplot.cm.viridis #This is the built in default
    elif ColorMap in ['grey' , 'gray']:
        ColorMap = matplotlib.pyplot.cm.gray


    #---------------------------------------------------------------------------
    #CREATE FIGURE OBJECT:
    fig = None
    subplot = None
    if ExistingFigure is None:
        fig = Library_FigureCreate.Main(
            DimensionCount= PlotDimensionCount,
            DimensionLabels= [Xlabel, Ylabel, Zlabel],
            PlotTitle= PlotTitle,
            LimitBoxMinimum= DomainMinimumPoint.tolist() + [None],
            LimitBoxMaximum= DomainMaximumPoint.tolist() + [None],
            FontSize= None,
            ShowGrid= None
            )
        subplot = fig.onlysubplot
        
    else:
        fig = ExistingFigure
        subplot = fig.onlysubplot

    #---------------------------------------------------------------------------
    #BEGIN BUILDING COLOR MAP:
    #Make meshgrid of points from minimum and maximum (plugged into the function)

    PluginPointCountX = int(numpy.sqrt(PluginPointCount))
    PluginPointCountY = int(numpy.sqrt(PluginPointCount))


    #FIXME: (NOTE) 
    #   mgrid == meshgrid.T
    #       1) http://louistiao.me/posts/numpy-mgrid-vs-meshgrid/
    #   This problem showed up when teaching the SC python minicourse in 2020 summer
    #       1) https://github.com/uofscphysics/STEM_Python_Course/tree/Summer2020/02_Week2/00_Probability_Theory
    #       2) Test_DensityColorPlot
    X, Y = numpy.mgrid[xmin:xmax:complex(PluginPointCountX), ymin:ymax:complex(PluginPointCountY)] #1000 x 1000 -> 1 million points

    PointsToPlugIn = numpy.vstack([X.ravel(), Y.ravel()])
    PointsToPlugInDataset = PointsToPlugIn.T
    PlugInPointsCount = len(PointsToPlugInDataset)
    if PrintExtra:
        print ('X.shape, Y.shape', X.shape, Y.shape)
        print('PlugInPointsCount', PlugInPointsCount)
        print('PointsToPlugInDataset.shape', PointsToPlugInDataset.shape)
        print('PointsToPlugInDataset[0]', PointsToPlugInDataset[0])


    #Plug meshgrid points into function (store values as numpy.float datatype )
    if PrintExtra: print ('LoopAlgorithm', LoopAlgorithm)
    FunctionResultValuesForGrid = None
    if PluginSimultaneous:
        #If the function can handle simulatneous points with numpy broadcasting...
        #   ... then the best optimziation is to throw equal chunks at the func for each core:
        CPU_count = multiprocessing_on_dill.cpu_count()
        PointsToPlugInDatasetChunks = Library_IterableSplitIntoChunks.Main(
            Iterable= PointsToPlugInDataset,
            ChunkCount= CPU_count,
            )
        FunctionResultValuesForGrid = numpy.vstack( Library_ParallelLoop.Main(
            Function        = Function,
            ListOfArgSets   = PointsToPlugInDatasetChunks,
            Algorithm       = LoopAlgorithm,
            #BatchCount      = 100, 
            BatchCount      = BatchCount,
            BatchSize       = BatchSize,
            HideProgressBar = HideProgressBar,
            PrintExtra      = PrintExtra,
            ) )
    else:
        #If the function can only handle one point at a time...
        #   the best optimization is just to throw all the points into a big queue:
        FunctionResultValuesForGrid = Library_ParallelLoop.Main(
            Function        = Function,
            ListOfArgSets   = PointsToPlugInDataset,
            Algorithm       = LoopAlgorithm,
            #BatchCount      = 100, 
            BatchCount      = BatchCount,
            BatchSize       = BatchSize,
            HideProgressBar = HideProgressBar,
            PrintExtra      = PrintExtra,
            )

    FunctionResultValuesForGrid = numpy.array( FunctionResultValuesForGrid, dtype=numpy.float)  
    if LogZ: FunctionResultValuesForGrid = numpy.log(FunctionResultValuesForGrid)     #TODO: scale the image axes without changing the function values


    Z = numpy.reshape(FunctionResultValuesForGrid, X.shape) 
    zmin = numpy.nanmin(Z)
    zmax = numpy.nanmax(Z)
    zrng = zmax - zmin
    if PrintExtra: #>0:
        print('Z.shape', Z.shape)
        print ('zmin, zmax, zrng', zmin, zmax, zrng)
        if PrintExtra > 1: print ('FunctionResultValuesForGrid', FunctionResultValuesForGrid)


    #Design the plot with the coordinate values (this could be done in it's own function)
    if (PlotThreeDimensional == True):

        #Plot the surface:
        if SurfaceType == 'solid':
            surface = subplot.plot_surface(X, Y, Z, 
                rstride=1, 
                cstride=1, 
                cmap= ColorMap, 
                #zorder=Zorder,
                antialiased=False,
                vmin = zmin,
                vmax = zmax,
                )
        elif SurfaceType == 'wireframe':
            subplot.plot_wireframe(X, Y, Z, rstride=1, cstride=1)        


        #Plot the observed dataset:
        if ObservedDataset is not None:

            #Get Z-values for the data based on the function:
            ObservedZ = []
            for PointToPlugIn in ObservedDataset:
                FunctionValueForPointToPlugIn = 0.0
                try:
                    FunctionValueForPointToPlugIn = Function(PointToPlugIn)
                except:
                    print('Function(' , PointToPlugIn, ')', ' failed... skipping')
                    pass
                ObservedZ.append( FunctionValueForPointToPlugIn )
            ObservedZ = numpy.array(ObservedZ).flatten()
            if PrintExtra:
                print ('ObservedX.shape',ObservedX.shape )
                print ('ObservedY.shape',ObservedY.shape )
                print ('ObservedZ.shape',ObservedZ.shape )

            #Draw litle verticle bars going up to each point:
            #https://towardsdatascience.com/an-easy-introduction-to-3d-plotting-with-matplotlib-801561999725
            subplot.bar3d(
                ObservedX, 
                ObservedY, 
                ObservedZ - zrng / 100, 
                #numpy.zeros(ObservedPointsCount),
                numpy.ones(ObservedPointsCount) * xrng / 100, 
                numpy.ones(ObservedPointsCount) * yrng / 100, 
                numpy.ones(ObservedPointsCount) * 2* zrng / 100, 
                #numpy.ones(ObservedPointsCount)*ObservedZ + 2* zrng / 100
                #color='aqua'
                #zorder=Zorder,
                )

    else:

        #Plot the colormap of the function:
        heatmap = subplot.imshow( 
            numpy.rot90(Z), 
            cmap=ColorMap, 
            extent=[xmin, xmax, ymin, ymax] ,
            aspect = 'auto' ,
            interpolation = None,
            #norm=LogNorm(vmin=0.01, vmax=1)
            #zorder=Zorder,
            )  

        #Add color bar (showing Z-axis sense of scale)
        cbar = matplotlib.pyplot.colorbar( heatmap, label = Zlabel )

        #Add the observations:
        if (ObservedDataset is not None):
            matplotlib.pyplot.plot(
                ObservedX, 
                ObservedY, 
                color='red', marker = 'o', linestyle = 'None', markersize=Markersize, 
                #zorder=Zorder,
                )

        #Plot Countours: ( From http://matplotlib.org/examples/pylab_examples/contour_demo.html )
        if ShowContours :
            CS = matplotlib.pyplot.contour(X, Y, Z, 
                5,          # number of contours
                colors='k', # negative contours will be dashed by default
                )
            if ShowContourLabels:
                matplotlib.pyplot.clabel(CS, fontsize=9, inline=1)

    #Save the final figure:
    if (SaveFigureFilePath is not None):
        matplotlib.pyplot.savefig( SaveFigureFilePath )

    #Craft the final result object:
    if ResultFormat == 'fig':
        Result = fig
    elif ResultFormat == 'Dictionary': 
        Result = {}
        Result['fig'] = fig
        Result['PointsToPlugInDataset'] = PointsToPlugInDataset
        Result['FunctionResultValuesForGrid'] = FunctionResultValuesForGrid

    #Should we store the points we plugged into the function to file?
    if PickleResult:
        Library_LazyPickleDump.Main(PointsToPlugInDataset)
        Library_LazyPickleDump.Main(FunctionResultValuesForGrid)
        Library_LazyPickleDump.Main(Result)


    return Result





























