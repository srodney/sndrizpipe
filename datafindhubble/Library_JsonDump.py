"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    A generic wrapper to json
    fixes stupid things 
    which should be native to python
    like numpy arrays
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
    NestedObject
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import base64
import json
import numpy as np
print (' type( json.JSONEncoder)',  type( json.JSONEncoder) )
#-------------------------------------------------------------------------------
def Main(
    NestedObject= None,
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

    class NumpyEncoder(json.JSONEncoder):

        def default(self, obj):
            """If input object is an ndarray it will be converted into a dict 
            holding dtype, shape and the data, base64 encoded.
            """
            if isinstance(obj, np.ndarray):
                if obj.flags['C_CONTIGUOUS']:
                    obj_data = obj.data
                else:
                    cont_obj = np.ascontiguousarray(obj)
                    assert(cont_obj.flags['C_CONTIGUOUS'])
                    obj_data = cont_obj.data
                data_b64 = base64.b64encode(obj_data)
                return dict(__ndarray__=data_b64,
                            dtype=str(obj.dtype),
                            shape=obj.shape)
            # Let the base class default method raise the TypeError
            super(NumpyEncoder, self).default(obj)


    #def json_numpy_obj_hook(dct):
    #    """Decodes a previously encoded numpy ndarray with proper shape and dtype.
    #
    #    :param dct: (dict) json encoded ndarray
    #    :return: (ndarray) if input was an encoded ndarray
    #    """
    #    if isinstance(dct, dict) and '__ndarray__' in dct:
    #        data = base64.b64decode(dct['__ndarray__'])
    #        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    #    return dct

    Result = json.dumps(NestedObject, cls=NumpyEncoder, indent=4)
    return Result 
