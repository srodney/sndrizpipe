
"""
SOURCE:

DESCRIPTION:
    Reads the contents of a file into a string
ARGS:
    Filepath
        The filepath of which to read as text

RETURNS:
    Contents
        The contents of the file

"""
import os
#    Directory = os.path.realpath(Directory)
def Main(filepath):
    filepath = os.path.realpath(filepath)
    File = open(filepath, 'r')
    contents = File.read()
    File.close()
    return contents




