./sndrizpipe.py --filters "F105w" --epochs 0 --mjdmin 55480 --mjdmax 55795 --ra 53.158222 --dec -27.777415 --dosetup primo
# ./sndrizpipe.py --filters "F105w" --epochs 0 --mjdmin 55480 --mjdmax 55795 --ra 53.158222 --dec -27.777415 --dorefim primo
./sndrizpipe.py --filters "F105w" --epochs 0 --mjdmin 55480 --mjdmax 55795 --ra 53.158222 --dec -27.777415 --dodriz1 primo
./sndrizpipe.py --filters "F105w" --epochs 0 --mjdmin 55480 --mjdmax 55795 --ra 53.158222 --dec -27.777415 --doreg primo 2>&1 | tee primo_F105w_reg.log
./sndrizpipe.py --filters "F105w" --epochs 0 --mjdmin 55480 --mjdmax 55795 --ra 53.158222 --dec -27.777415 --clobber --dodriz2 primo
rm primo_epochs.txt
grep -A 3 "WARNING" primo_F105w_reg.log
# ds9 -scale mode zscale primo.e00/primo_f105w_e00_reg_drz_sci.fits