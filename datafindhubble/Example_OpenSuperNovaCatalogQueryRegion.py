import Library_OpenSuperNovaCatalogQueryRegion
import Library_PrettyPrintNestedObject
#-------------------------------------------------------------------------------


#Example:
# https://api.astrocats.space/catalog?ra=21:23:32.16&dec=-53:01:36.08&radius=2

Result = Library_OpenSuperNovaCatalogQueryRegion.Main(
    RightAscension= 150.468643,
    Declination=  2.164106,
    Radius= 2,
    )
print( list(Result.keys()) ) 



Library_PrettyPrintNestedObject.Main( NestedObject= Result ) 













































