"""
SOURCE:
    Mind of Douglas Adams

    Might want to use wireframe capabilities:
        https://www.oreilly.com/learning/three-dimensional-plotting-in-matplotlib

DESCRIPTION:
    https://stackoverflow.com/questions/44881885/python-draw-parallelepiped/49766400
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
    ExistingFigure
        Type:
            <class 'NoneType'>
        Description:
            None
    CubeCenter
        Type:
            <class 'NoneType'>
        Description:
            None
    CubeSideLength
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
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
#-------------------------------------------------------------------------------
import Library_OuterProduct
#-------------------------------------------------------------------------------
def Main(
    ExistingFigure= None,
    CubeCenter= None,
    CubeSideLength= None,
    color = None,
    alpha = None,
    markersize = None,
    PlotVertices = None,
    PlotCenter = None,
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

    #ARG FIXING:
    if PlotCenter is None:
        PlotCenter = False

    if PlotVertices is None:
        PlotVertices = False

    if color is None:
        ColorBlue = [ 0.4,  0.7,  0.99]
        ColorRed = [ 1,  0.1,  0.1]
        #color = numpy.random.rand( 3)  
        color = ColorRed
        #print('Generated Color', color)

    if alpha is None:
        alpha = 0.5

    if markersize is None:
        markersize = 7

    CubeCenter = numpy.array(CubeCenter)
    DimensionCount = len(CubeCenter) #Always 3... might be able to take this out


    #Create the figure:
    fig = None
    if ExistingFigure is None:
        #size the graph
        #   Default to common monitor size:  
        #   1920pixels by 1080 pixels
        Inch_in_Pixels = 80.0
        MonitorSize = (1920.0/Inch_in_Pixels,1080.0/Inch_in_Pixels)
        #Create a new figure because one did not already exist to add stuff upon:
        fig = matplotlib.pyplot.figure(figsize=MonitorSize) #figsize=MonitorSize
        #Add the 3d subplot to the NEW figure
        subplot = fig.add_subplot(111, projection='3d')

    else:
        #There already exists a figure. 
        #We assume it already is 3D and has the appropriate subplot
        fig = ExistingFigure

    #Get the subplot of the active figure
    allaxes = fig.get_axes()
    subplot = allaxes[0]


    #Draw the center of the cube:
    if PlotCenter:
        CenterX = CubeCenter[0]
        CenterY = CubeCenter[1]
        CenterZ = CubeCenter[2]
        matplotlib.pyplot.plot(
            [CenterX], 
            [CenterY],
            [CenterZ],  
            c=color, 
            markersize=markersize, 
            marker='o',
            linestyle = 'None',
            alpha=alpha,
            #**kwargs,
            )


    #Construct list of possible vertices using an outer product: (8 for cube)
    SingleDimensionTranslationPossibilities = [ CubeSideLength/2, -CubeSideLength/2]
    List1 = SingleDimensionTranslationPossibilities
    List2 = SingleDimensionTranslationPossibilities
    List3 = SingleDimensionTranslationPossibilities
    ListOfLists = [List1, List2, List3]
    TranslationsToVertices = Library_OuterProduct.Main(
        ListOfLists= ListOfLists
        )
    VertexCoordinates = []
    for Translation in TranslationsToVertices:
        VertexCoodinate = CubeCenter + numpy.array(Translation)
        VertexCoordinates.append(VertexCoodinate)
    VertexCoordinates = numpy.array(VertexCoordinates)
    if PrintExtra:
        print ('VertexCoordinates')
        print (VertexCoordinates)

    if PlotVertices:
        PlottableVertexCoordinates = VertexCoordinates.T
        #print ('PlottableVertexCoordinates')
        #print (PlottableVertexCoordinates)
        matplotlib.pyplot.plot(
            PlottableVertexCoordinates[0], 
            PlottableVertexCoordinates[1],
            PlottableVertexCoordinates[2],  
            c=color, 
            markersize=markersize, 
            marker='o',
            linestyle = 'None',
            alpha=alpha,
            #**kwargs,
            )

    #Given all the vertices, find pairs which only differ on 1 coordinate: (12 edges for cube)
    EdgeCount = 0
    AllEdgesVertexPairs = []
    AllEdgesVertexPairsStringified = []
    for Vertex1 in VertexCoordinates:
        for Vertex2 in VertexCoordinates:

            #Check if we have an edge:
            VertexDiff = Vertex1 - Vertex2
            ZeroCount = DimensionCount - numpy.count_nonzero( VertexDiff )
            if ZeroCount == 2:

                #Check if the edge is new:
                VertexPair = [Vertex1, Vertex2]
                VertexPairReverseStringified = str( [Vertex2, Vertex1] )
                if not (VertexPairReverseStringified in AllEdgesVertexPairsStringified):

                    #We actually found a new cube edge so store it:
                    AllEdgesVertexPairs.append(VertexPair)
                    AllEdgesVertexPairsStringified.append(str(VertexPair))
                    EdgeCount += 1

    if PrintExtra:
        print ('EdgeCount', EdgeCount) #Need 12 edges for a cube

    #Plot a line segment for each edge pair:
    for SingleEdgeVertexPair in AllEdgesVertexPairs:
        Vertex1 = SingleEdgeVertexPair[0]
        Vertex2 = SingleEdgeVertexPair[1]

        EdgeXvals = [Vertex1[0], Vertex2[0] ]
        EdgeYvals = [Vertex1[1], Vertex2[1] ]
        EdgeZvals = [Vertex1[2], Vertex2[2] ]

        matplotlib.pyplot.plot(
            EdgeXvals, 
            EdgeYvals,
            EdgeZvals,  
            c=color, 
            marker=None,
            linestyle = '-',
            linewidth = 0.2,
            )

    #DO NOT ADD ANY LABELS HERE.
    #This library will be trigged many many times to modify existing figures. 



    Result = fig
    return Result 



















