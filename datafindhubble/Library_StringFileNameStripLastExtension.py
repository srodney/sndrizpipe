def Main(FileName):

    FileNamePieces = FileName.split(".")
    NumFileNamePieces = len(FileNamePieces)
    Result = FileNamePieces[-1]
    if (len(FileNamePieces) > 1):
        FileNamePiecesWithoutLastOne = FileNamePieces[:-1]
        Result = '.'.join( FileNamePiecesWithoutLastOne )

    return Result


