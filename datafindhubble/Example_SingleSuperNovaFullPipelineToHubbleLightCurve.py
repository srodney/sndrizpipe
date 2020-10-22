import Library_SystemGetLocalHomeDirectory
import Library_SystemGetLocalDataDirectory
import Library_SingleSuperNovaFullPipelineToHubbleLightCurve
import Library_DataFileCsvReadAsAstropyTable
#-------------------------------------------------------------------------------


#Directory Management:
HomeDirectory = Library_SystemGetLocalHomeDirectory.Main()
DataDirectory = Library_SystemGetLocalDataDirectory.Main()

SuperNovaCatalogsDataDirectory  = DataDirectory + '/AstronomySuperNovaData/SuperNovaCatalogs/'
SuperNovaImageDownloadDirectory = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleImages/'
SuperNovaMetaDataDirectory      = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleMetaData/'


#-------------------------------------------------------------------------------
#Load the colfax supernova data from the pantheon catalog:
#   #SN CID CIDint IDSURVEY TYPE FIELD CUTFLAG_SNANA zCMB zCMBERR zHD zHDERR VPEC VPEC_ERR HOST_LOGMASS HOST_LOGMASS_ERR SNRMAX1 SNRMAX2 SNRMAX3 PKMJD PKMJDERR x1 x1ERR c cERR mB mBERR x0 x0ERR COV_x1_c COV_x1_x0 COV_c_x0 NDOF FITCHI2 FITPROB RA DECL TGAPMAX TrestMIN TrestMAX MWEBV MU MUMODEL MUERR MUERR_RAW MURES MUPULL ERRCODE biasCor_mu biasCorErr_mu biasCor_mB biasCor_x1 biasCor_c biasScale_muCOV IDSAMPLE  
#   SN: colfax 9 106 -9 NULL 1 2.26000 0.02000 2.26000 0.02000 0 0 10 99 10.4868 8.3572 7.9355 56078.227 1.121 1.86741e-02 0.9076 0.1275 0.1327 26.8086 5.60957e-02 3.39286e-07 1.75296e-08 1.59068e-02 -6.76292e-09 1.36618e-11 13 10.1621 0.7502 189.156586 62.309174 11.5330 -1.20303e+00 32.1810 1.20000e-02  46.2366 46.2813  0.2567  0.5177  0.070  0.272 0 -0.591  0.028 -0.060 -0.050  0.142  0.235 4 

pantheon = Library_DataFileCsvReadAsAstropyTable.Main(
    Filepath= SuperNovaCatalogsDataDirectory + 'pantheon.dat',
    ColumnNamesExisting= ['CID','zCMB','RA','DECL', 'PKMJD'],
    ColumnNamesNew= ['ID','z','ra','dec', 'mjd'],
    ColumnNamesRestrict = ['TYPE'],
    ColumnValuesRestrict = [0],
    )

ColfaxSuperNova = None
for SingleSuperNova in pantheon: 
    #print ('SingleSuperNova', SingleSuperNova)
    if SingleSuperNova['ID'] == 'colfax':
        ColfaxSuperNova = SingleSuperNova
        break

print ('ColfaxSuperNova', ColfaxSuperNova)


Result = Library_SingleSuperNovaFullPipelineToHubbleLightCurve.Main(
    SingleSuperNovaCatalogName = 'pantheon',
    SingleSuperNovaId= ColfaxSuperNova['ID'],
    SingleSuperNovaRa= ColfaxSuperNova['ra'],
    SingleSuperNovaDec= ColfaxSuperNova['dec'],
    SingleSuperNovaMjd= ColfaxSuperNova['mjd'],
    SingleSuperNovaMjdRange= [
        ColfaxSuperNova['mjd'] - 50, 
        ColfaxSuperNova['mjd'] + 100
        ],

    #What stuff will we do/skip? (default is do everything)
    DoAstroquerySearch = False,
    DoAstroqueryDownload = False,
    DoSymlinkMount = False,
    DoDrizzleDiffs = False,
    DoDrizzleDiffFileCopy = False,
    DoCenterFind = False,
    DoPhotometry = False,
    DoLightCurve = True,
    )

print( Result ) 

















































