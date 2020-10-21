"""
SOURCE:
    Mind of Douglas Adams
    https://stackoverflow.com/questions/19935445/cross-hairs-in-python-animation
DESCRIPTION:
    When plotting very few points but very important points 
    It is nice to have cross hairs instead of dots of different colors
    For consistency we will use the same notation as graphscatterplot library
    This will perform similar to the functionality of the corner plot library


    ALWAYS needs an existing figure is floating in memory

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
    NumpyTwoDimensionalDatasets
        Type:
            <class 'NoneType'>
        Description:
            None
    DatasetLabels
        Type:
            <class 'NoneType'>
        Description:
            None
    DatasetColors
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
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
#-------------------------------------------------------------------------------
def Main(
    NumpyTwoDimensionalDatasets= None,
    DatasetLabels= None,
    DatasetColors= None,
    #ExistingFigure = None,
    LegendSize = None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None


    if (CheckArguments):
        ArgumentErrorMessage = ""

        #if ExistingFigure is None:
        #    ArgumentErrorMessage += 'ExistingFigure is None \n'


        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #fig = ExistingFigure
    #subplot = fig.onlysubplot

    #Lifted right from stack overflow:
    def cross_hair(x, y, ax=None, **kwargs):
        if ax is None:
            ax = plt.gca()

        horiz = ax.axhline(y,  **kwargs)
        vert = ax.axvline(x, **kwargs)
        return horiz, vert

    #Get the current axes
    ax = plt.gca()

    #Get the prev legends on the plot:
    #prev_legends = [c for c in ax.get_children() if isinstance(c, matplotlib.legend.Legend)]

    #handles.append(Patch(facecolor='orange', edgecolor='r'))
    #labels.append("Color Patch")

    #Create a legend of colors:
    #LegendPatchHandles = []


    #Get the handles from the current legend on the plot:
    handles, labels = ax.get_legend_handles_labels()


    if LegendSize is None:
        if len(handles) > 0:
            firsthandle = handles[0]
            LegendSize = firsthandle.__sizeof__()
            #print ('sizes', sizes)
            #LegendSize = sizes[0]
        else:
            LegendSize = 30    
    #print ('LegendSize', LegendSize)

    for DatasetLabel, DatasetColor in zip(DatasetLabels, DatasetColors):
        newpatch= mpatches.Patch(color=DatasetColor, label=DatasetLabel)
        handles.append(newpatch) 
    ax.legend(handles=handles, prop={'size': LegendSize})

    #Re-add the previous legends:
    #for legend in prev_legends:
    #    ax.add_artist(legend)


    #Add cross hairs one at a time
    for Dataset, DatasetColor in zip(NumpyTwoDimensionalDatasets, DatasetColors):
        x = Dataset[0][0]
        y = Dataset[0][1]
        cross_hair(x, y, color=DatasetColor )



    #Return true on success, which is NOT the figure object
    Result = True
    return Result 




















