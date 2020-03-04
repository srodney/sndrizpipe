

#GOAL: Make this based on the sndrizpipe folder in the github.
#   We want this dockerfile to work when inside the repo for sndrizpipe
#   this file, needs to be located at filepath (no extension): 
#   .../sndrizpipe/Dockerfile

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6-dev
#python3.6 -m pip already installed via python
pip install numpy
pip install --upgrade setuptools
pip install astropy
pip install --user stsci.tools


git clone https://github.com/srodney/drizzlepac.git
cd /home/developer0/CodeHome/drizzlepac
python setup.py install --user
cd /home/developer0/CodeHome/
git clone https://github.com/srodney/sndrizpipe.git
cd /home/developer0/CodeHome/sndrizpipe
python setup.py install --user
cd /home/developer0/CodeHome/


#make the path for the command:
alias sndrizpipe="/home/developer0/anaconda3/bin/sndrizpipe"


cd /home/developer0/CodeHome/sndrizpipe/sndrizpipe
tar -zxvf colfax_test.tgz

sndrizpipe --filters F160W  --doall --mjdmin 56010 --mjdmax 56300 --ra 189.156538 --dec 62.309147  --refcat 'goodsn_mosaic.cat' colfax
