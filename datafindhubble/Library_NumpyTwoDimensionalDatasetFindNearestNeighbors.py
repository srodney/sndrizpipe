"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Find the nearest neighbors from a given coordinate. 
    Either we want to find the k nearest ones,
    or we want to find all the ones that exist within a radius.
    We can use whatever algorithms are fastest at our disposal. 
    This problem is fast in low D using kdtrees 
    In high dimensions, this is an unsolved problem
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
            <class 'NoneType'>
        Description:
            None
    Coordinate
        Type:
            <class 'NoneType'>
        Description:
            None
    NumberNeighbors
        Type:
            <class 'NoneType'>
        Description:
            None
    Radius
        Type:
            <class 'NoneType'>
        Description:
            None

    Method
        Type:
            <class 'NoneType'>
        Description:
            defaults to 'kdtree'

RETURNS:
    Result
        Type:
        Description:
"""
import numpy
import scipy
import scipy.spatial
#-------------------------------------------------------------------------------
def Main(
    NumpyTwoDimensionalDataset= None,
    Coordinate= None,
    Coordinates = None,
    NumberNeighbors= None,
    Radius= None,
    Method = None,
    ResultFormat = None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if Method is None:
        Method = 'kdtree' 

    if ResultFormat is None:
        ResultFormat = 'Dictionary'

    if Coordinate is not None and Coordinates is None:
        Coordinates = numpy.atleast_2d ( numpy.array(Coordinate) )
    Coordinates = numpy.array(Coordinates)

    #print ('Coordinates', Coordinates)


    if (CheckArguments):
        ArgumentErrorMessage = ""

        if NumpyTwoDimensionalDataset.shape[1] !=  Coordinates.shape[1]:
            ArgumentErrorMessage != 'NumpyTwoDimensionalDataset.shape' + str(NumpyTwoDimensionalDataset.shape) + '\n'
            ArgumentErrorMessage != 'Coordinate.shape' + str(Coordinate.shape) + '\n'
            ArgumentErrorMessage != '`NumpyTwoDimensionalDataset` dimm count not match `Coordinate` dimm count \n'

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #SampleSize = SamplesLocations.shape[0]
    #if PrintExtra: 
    #    print ('--Starting a search for nearest neighbor distances')    
    #    print ('--RandomSubsetSize = ', RandomSubsetSize)
    #    print ('--SampleSize       = ', SampleSize)

    if PrintExtra: print (Library_DateStringNowGMT.Main(), 'Making KDTree')
    NeighborTree = scipy.spatial.cKDTree( NumpyTwoDimensionalDataset )
    #NumberNeighbors = 1
    Distances = None


    #What coordinates do we want the nearest neighbors?
    #if PrintExtra: print (Library_DateStringNowGMT.Main(), 'Selecting Samples To Get Distances')
    #if RandomSubsetSize is not None and RandomSubsetSize < SampleSize:
    #    SamplesRandomSubsetIndexes = numpy.random.choice(range(SampleSize), RandomSubsetSize )
    #    QueryLocations = SamplesLocations[SamplesRandomSubsetIndexes]
    #
    #else:
    #    QueryLocations = SamplesLocations
    #QueryLocations = Coordinates

    if PrintExtra: print (Library_DateStringNowGMT.Main(), 'Querying the tree')

    if NumberNeighbors is not None and Radius is None:
        NeighborDistances, NeighborIndices = NeighborTree.query(Coordinates, 1+NumberNeighbors) #[0][:,1:]#.query() returns ('Distances', 'Neighbors') 
        NeighborIndices = list( numpy.array(NeighborIndices).flatten() )
        #NeighborIndices = list(set(list( numpy.array(NeighborIndices).flatten() )))
        #print ('NeighborIndices', NeighborIndices)
        NeighborCoordinates = NumpyTwoDimensionalDataset[NeighborIndices]

    elif  NumberNeighbors is None and Radius is not None:
        NeighborIndices = NeighborTree.query_ball_point(Coordinates, Radius) #[0][:,1:]#.query() returns ('Distances', 'Neighbors') 
        NeighborIndices = list( numpy.array(list(NeighborIndices)).flatten() )
        NeighborDistances = None
        NeighborCoordinates = NumpyTwoDimensionalDataset[   NeighborIndices     ]
    else:
        raise Exception('Conflicting Args. Need exactly one of [`NumberNeighbors`, `Radius`] ')

    if PrintExtra: print (Library_DateStringNowGMT.Main(), 'Finished Querying the tree')

    #Distances = DistancesToNeighbors.T[0]
    #Result = Distances

    if ResultFormat == 'Dictionary':

        Result = {
            'NeighborDistances'     : NeighborDistances,
            'NeighborIndices'       : NeighborIndices,
            'NeighborCoordinates'   : NeighborCoordinates,
            }
    elif ResultFormat == 'NeighborCoordinates':
        Result = NeighborCoordinates


    return Result 















