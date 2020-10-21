"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Desc here
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
    Iterable
        Type:
            <type 'NoneType'>
        Description:
    ChunkCount
        Type:
            <type 'NoneType'>
        Description:
    ChunkLength
        Type:
            <type 'NoneType'>
        Description:
RETURNS:
    Result
        Type:
        Description:
"""
import Library_Round
def Main(
    Iterable= None,
    ChunkCount= None,
    ChunkLength= None,
    ForceExactChunkCount = None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if ForceExactChunkCount is not None:
        raise Exception('TODO: implement `ForceExactChunkCount` ')

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    ItemCount = len(Iterable)

    if ChunkLength is None and ChunkCount is not None:
        TrueChunkLength = ItemCount / ChunkCount

        #Remainder = ItemCount % ChunkCount
        #print ('Remainder', Remainder)
        #RoundDirection = None
        #if Remainder > 0:
        #    RoundDirection = 'Up'
        #else:
        #    RoundDirection = None

        ChunkLength = Library_Round.Main(
            Number= TrueChunkLength,
            Method= 'DecimalCount',
            DigitCount= 0,
            Direction= 'Up',
            #Direction= 'Down',
            #Direction = RoundDirection,
            PrintExtra = False,
            )
        ChunkLength = int(ChunkLength)

    #print ('ChunkLength', ChunkLength)


    Chunks = []
    for i in range(0, ItemCount, ChunkLength):
        Chunk = Iterable[i:i + ChunkLength]
        Chunks.append(Chunk)

    Result = Chunks
    return Result










 
