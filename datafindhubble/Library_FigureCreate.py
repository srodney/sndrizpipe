"""
SOURCE:
    https://stackoverflow.com/questions/5525782/adjust-label-positioning-in-axes3d-of-matplotlib
DESCRIPTION:
    Creates and returns a figure using matplotlib 
    uses with a bunch of default settings that are logical,
    and consistent with the physics community.
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
    DimensionCount
        Type:
            <class 'NoneType'>
        Description:
            None
    DimensionLabels
        Type:
            <class 'NoneType'>
        Description:
            None
    PlotTitle
        Type:
            <class 'NoneType'>
        Description:
            None
    LimitBoxMinimum
        Type:
            <class 'NoneType'>
        Description:
            None
    LimitBoxMaximum
        Type:
            <class 'NoneType'>
        Description:
            None
    FontSize
        Type:
            <class 'NoneType'>
        Description:
            None
    ShowGrid
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import numpy
import matplotlib
import matplotlib.pyplot
import matplotlib.cm
import mpl_toolkits
import mpl_toolkits.mplot3d
import matplotlib.font_manager
import Library_DataGetMonitorSize
#-------------------------------------------------------------------------------
def Main(
    DimensionCount= None,
    DimensionLabels= None,
    LimitBoxMinimum= None,
    LimitBoxMaximum= None,

    PlotTitle= None,
    FontSize= None,
    ShowGrid= None,

    ExistingFigure = None,

    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    #if DimensionCount is None:
    #    DimensionCount = 2

    if FontSize is None:
        FontSize = 24

    if ShowGrid is None:
        ShowGrid = True

    if PlotTitle is None:
        PlotTitle = 'UNSET PLOT TITLE'

    if DimensionLabels is None and DimensionCount is not None:
        DimensionLabels = []
        for DimensionNumber in range(DimensionCount):
            DimensionLabels.append( 'UNSET DIMENSION LABEL' + str(DimensionNumber) )
        if PrintExtra: print ('DimensionLabels', DimensionLabels)
    

    if (CheckArguments):
        ArgumentErrorMessage = ""

        #if DimensionCount is None:
        #    ArgumentErrorMessage += 'DimensionCount is None\n'

        #We cannot check dimension matching: color maps can be 3d plots on 2d render
        if False: 
            if DimensionLabels is not None:
                if len(DimensionLabels) != DimensionCount:
                    ArgumentErrorMessage += 'len(DimensionLabels) != DimensionCount\n'
            if LimitBoxMinimum is not None:
                if len(LimitBoxMinimum) != DimensionCount:
                    ArgumentErrorMessage += 'len(LimitBoxMinimum) != DimensionCount\n'
            if LimitBoxMaximum is not None:
                if len(LimitBoxMaximum) != DimensionCount:
                    ArgumentErrorMessage += 'len(LimitBoxMaximum) != DimensionCount\n'


        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #Force a backend
    #matplotlib.use('TKAgg',warn=False, force=True)
    #Fix the size the figure to standard monitor size (1920pixels by 1080 pixels)
    MonitorSize = Library_DataGetMonitorSize.Main(    )


    #Change all the fonts to bold:
    #   Close any extra figure created by changing fonts... how annoying
    AllFiguresInMemoryBeforeFontChange = matplotlib.pyplot.get_fignums()
    font = {
        'weight' : 'bold',
        'size'   : FontSize 
        }
    matplotlib.rc('font', **font)
    matplotlib.pyplot.tick_params(labelsize=FontSize)
    matplotlib.font_manager.FontProperties()
    AllFiguresInMemoryAfterFontChange = matplotlib.pyplot.get_fignums()
    ExtraFiguresCreated = list(set(AllFiguresInMemoryAfterFontChange) - set(AllFiguresInMemoryBeforeFontChange))
    for ExtraFigureCreated in ExtraFiguresCreated:
        matplotlib.pyplot.figure( ExtraFigureCreated )
        matplotlib.pyplot.close() #<---OK CLOSE


    #AllFiguresInMemoryAfterClose = matplotlib.pyplot.get_fignums()
    if PrintExtra:
        print ('AllFiguresInMemoryBeforeFontChange', AllFiguresInMemoryBeforeFontChange)
        print ('AllFiguresInMemoryAfterFontChange', AllFiguresInMemoryAfterFontChange)
        print ('ExtraFiguresCreated', ExtraFiguresCreated)
        print ('AllFiguresInMemoryAfterClose', AllFiguresInMemoryAfterClose)


    #Set the font and make things bold in matplotlib global properties (WORK AROUND):
    fig = None
    if ExistingFigure is None:
        if False:
            #Create a dummy figure (we have to create a dummmy for the font to change) 
            figdummy = matplotlib.pyplot.figure(figsize=MonitorSize) 
            #Destroy the dummy figure ( now the font will apply on the next figures)
            matplotlib.pyplot.close(fig=figdummy)

        #Actually create the figure 
        fig = matplotlib.pyplot.figure(figsize=MonitorSize) 
        if PrintExtra:
            print ('fig.axes', fig.axes)
            print ('DimensionCount', DimensionCount)
    else:
        fig = ExistingFigure
        currentfigurenumber = matplotlib.pyplot.gcf().number
        matplotlib.pyplot.figure(num=currentfigurenumber, figsize=MonitorSize)


    #Based on how many dimensions there are, create a subplot
    subplot = None
    if (DimensionCount is None):
        pass
    elif (DimensionCount == 2):
        subplot = fig.add_subplot(111)
    elif (DimensionCount == 3):
        subplot = fig.add_subplot(111, projection='3d')


    if PrintExtra: print ('fig.axes', fig.axes)

    #Based on how many dimensions there are set the limits on each axis
    if PrintExtra:
        print ('LimitBoxMinimum', LimitBoxMinimum)
        print ('LimitBoxMaximum', LimitBoxMaximum)


    if PrintExtra: print ('fig.axes', fig.axes)

    if (LimitBoxMinimum is not None) and (LimitBoxMaximum is not None):
        if not (None in [LimitBoxMinimum[0], LimitBoxMaximum[0] ]):
            subplot.set_xlim( LimitBoxMinimum[0] , LimitBoxMaximum[0] )
        if not (None in [LimitBoxMinimum[1], LimitBoxMaximum[1] ]):
            subplot.set_ylim( LimitBoxMinimum[1] , LimitBoxMaximum[1] )
        if (DimensionCount is not None) and (DimensionCount == 3) and ( not (None in [LimitBoxMinimum[2], LimitBoxMaximum[2] ]) ):
            subplot.set_zlim(LimitBoxMinimum[2], LimitBoxMaximum[2])

        #Code below came from `Library_GraphOneDimensionalFunction`:
        """
        plt.axis(  [DomainMinimumPoint, DomainMaximumPoint, RangeMinimum, RangeMaximum]  ) 
        ax = plt.gca()
        ax.set_autoscale_on(False)    
        """

    if PrintExtra: print ('fig.axes', fig.axes)


    #Add the legend object to the figure ---> NOT WORK
    #    annoyingly -> cannot add legend before data
    #matplotlib.pyplot.legend(loc = 'best', numpoints=1)

    #Add the plot title object to the figure
    if (PlotTitle is not None):
        #matplotlib.pyplot.title(PlotTitle)
        fig.suptitle( PlotTitle )

    if PrintExtra: print ('fig.axes', fig.axes)
    #Add the axis labels:
    if DimensionCount is None:
        pass
    elif (DimensionCount == 2):
        subplot.set_xlabel(DimensionLabels[0], fontsize = FontSize)
        subplot.set_ylabel(DimensionLabels[1], fontsize = FontSize)

    elif (DimensionCount == 3):
        subplot.set_xlabel('\n\n\n'     + DimensionLabels[0], fontsize = FontSize)
        subplot.set_ylabel('\n\n\n'     + DimensionLabels[1], fontsize = FontSize)
        subplot.set_zlabel('\n\n\n\n'   + DimensionLabels[2], fontsize = FontSize)
    if PrintExtra: print ('fig.axes', fig.axes)

    Result = fig
    if DimensionCount is not None:
        Result.onlysubplot = subplot

    if PrintExtra: print ('fig.axes', fig.axes)

    return Result 






























