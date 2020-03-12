

def Main(integer, length):
	IntegerAsString = str(integer)
	
	while (len(IntegerAsString) < length):
		IntegerAsString = "0" + IntegerAsString

	return IntegerAsString
