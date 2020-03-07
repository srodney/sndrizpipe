Required steps to run on south carolina cluster:


I ran these steps:

  439  pip install astropy
  440  sudo apt-get install pip
  441  I just want astropy
  442  python Example_DataFindHubbleSuperNova.py
  443  which python
  444  modulelist
  445  module list
  446  module avail
  447  module load python3/anaconda/2019.03
  448  pip -version
  449  pip --version
  450  pip install astropy --user
  451  python Example_DataFindHubbleSuperNova.py
  452  pip install astroquery --user
  453  python Example_DataFindHubbleSuperNova.py
  454  clear
  455  python Example_DataFindHubbleSuperNova.py
  456  python
  457  python Example_DataFindHubbleSuperNova.py
  458  history 20



I believe the only useful commands are:

  446  module avail
  447  module load python3/anaconda/2019.03
  450  pip install astropy --user
  452  pip install astroquery --user
  453  python Example_DataFindHubbleSuperNova.py



Now some data should be located in "/work/da2/DataHome"


Main files will be:
    "Example_DataFindHubbleSuperNova",
    "Process_DataFindHubbleSuperNova",
    "Example_SymlinkMountHubbleSuperNova",
    "Process_SymlinkMountHubbleSuperNova",


The processes should replace the examples eventually, 
    and they should have more bells and whistles 
    such as having try catch blocks in useful places
    and perhaps other things to help the batch slurm manager deal with stuff

    The point is that more work should be done to make the code more reliable as a "process" 
    isntead of some script that has been hacked together and run from the terminal one time

    We want elements of the code to be run on a nightly basis. 
    Especially code with a bottleneck of download time.  (network latency)














