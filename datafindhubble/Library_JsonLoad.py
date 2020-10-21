"""
SOURCE:
    http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python/6633651#6633651
    https://stackoverflow.com/questions/27909658/json-encoder-and-decoder-for-complex-numpy-arrays
DESCRIPTION:
    Loads a json into a python object
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
    JsonString
        Type:
            <type 'NoneType'>
        Description:
    ForceAscii
        Type:
            <type 'NoneType'>
        Description:
    ForceUnicode
        Type:
            <type 'NoneType'>
        Description:
RETURNS:
    Result
        Type:
        Description:
"""
import base64
import json
import numpy as np

def Main(
    JsonString= None,
    ForceAscii= False,
    ForceUnicode= False,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None


    if ForceAscii is None:
        ForceAscii= False
    if ForceUnicode is None:
        ForceUnicode= False
    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    """
    s = JsonString


    def byteify(input):
        if isinstance(input, dict):
            return {byteify(key): byteify(value)
                    for key, value in input.items()}
        elif isinstance(input, list):
            return [byteify(element) for element in input]
        elif isinstance(input, str):
            return input.encode('utf-8')
        else:
            return input

    def deunicodify_hook(pairs):
        new_pairs = []
        for key, value in pairs:
            if isinstance(value, str):
                value = value.encode('utf-8')
            if isinstance(key, str):
                key = key.encode('utf-8')
            new_pairs.append((key, value))
        return dict(new_pairs)

    def _decode_list(data):
        rv = []
        for item in data:
            if isinstance(item, str):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = _decode_list(item)
            elif isinstance(item, dict):
                item = _decode_dict(item)
            rv.append(item)
        return rv

    def _decode_dict(data):
        rv = {}
        for key, value in data.items():
            if isinstance(key, str):
                key = key.encode('utf-8')
            if isinstance(value, str):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = _decode_list(value)
            elif isinstance(value, dict):
                value = _decode_dict(value)
            rv[key] = value
        return rv

    def ascii_encode_dict(data):
        ascii_encode = lambda x: x.encode('ascii')
        return dict(map(ascii_encode, pair) for pair in data.items())

    if ForceAscii is False and ForceUnicode is False:
        ErrorMessage = 'Arg error: need either ForceAscii or ForceUnicode to not be `False`'
        raise Exception(ErrorMessage)
    elif ForceAscii is True and ForceUnicode is False:
        #TODO: Understand if this changed from python2 to 3.
        #   Regular old json.loads seems to work as expected now. 

        #do the ascii
        #print 'Forcing ascii'
        #obj = json.loads(s, object_hook=_decode_dict)

        obj = json.loads(s) 
        #obj = json.loads(s, object_hook=_decode_dict)

        #print 'obj', obj
        #obj = json.loads(s, object_hook=deunicodify_hook)
    elif ForceAscii is False and ForceUnicode is True:
        obj = json.loads(s)#by default the json loads method makes unicode things
    elif ForceAscii is True and ForceUnicode is True:
        ErrorMessage = 'Arg error: both ForceAscii ForceUnicode are not none- solution ambiguous'
        raise Exception(ErrorMessage)
    """


    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            """
            if input object is a ndarray it will be converted into a dict holding dtype, shape and the data base64 encoded
            """
            if isinstance(obj, np.ndarray):
                data_b64 = base64.b64encode(obj.data)
                return dict(__ndarray__=data_b64,
                            dtype=str(obj.dtype),
                            shape=obj.shape)
            # Let the base class default method raise the TypeError
            return json.JSONEncoder(self, obj)


    def json_numpy_obj_hook(dct):
        """
        Decodes a previously encoded numpy ndarray
        with proper shape and dtype
        :param dct: (dict) json encoded ndarray
        :return: (ndarray) if input was an encoded ndarray
        """
        if isinstance(dct, dict) and '__ndarray__' in dct:
            data = base64.b64decode(dct['__ndarray__'])
            return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
        return dct

    # Overload dump/load to default use this behavior.
    def dumps(*args, **kwargs):
        kwargs.setdefault('cls', NumpyEncoder)
        return json.dumps(*args, **kwargs)

    def loads(*args, **kwargs):
        kwargs.setdefault('object_hook', json_numpy_obj_hook)    
        return json.loads(*args, **kwargs)

    def dump(*args, **kwargs):
        kwargs.setdefault('cls', NumpyEncoder)
        return json.dump(*args, **kwargs)

    def load(*args, **kwargs):
        kwargs.setdefault('object_hook', json_numpy_obj_hook)
        return json.load(*args, **kwargs)

    """
    if __name__ == '__main__':

        data = np.arange(3, dtype=np.complex)

        one_level = {'level1': data, 'foo':'bar'}
        two_level = {'level2': one_level}

        dumped = dumps(two_level)
        result = loads(dumped)

        print '\noriginal data', data
        print '\nnested dict of dict complex array', two_level
        print '\ndecoded nested data', result
    """

    Result = loads(JsonString)
    return Result 
