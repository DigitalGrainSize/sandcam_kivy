Kivy-powered GUI for taking sediment images with site and sample annotations and processing them for grain size

Written by Daniel Buscombe, October 2013
while at
Grand Canyon Monitoring and Research Center, U.G. Geological Survey, Flagstaff, AZ 

Please contact:
dbuscombe@usgs.gov

to report bugs and discuss the code, algorithm, collaborations

For the latest code version please visit:
https://github.com/dbuscombe-usgs

There are 2 versions
1. sc_basic.py
which is a program to 
1) view and capture an image of sediment
2) get site and sample info from the user
3) save image to file with the site and sample in the file name
4) crop and make greyscale and save another file

2. sc_get_gs.py
which is a program to:
1) view and capture an image of sediment
2) get site and sample info from the user
3) save image to file with the site and sample in the file name
4) crop and make greyscale and save another file
5) calculate grain size distribution and save results to text file
6) write summary statistics of the distribution to text file

Requirements for running the basic version:
1. python
2. kivy (http://kivy.org/#home)
3. python imaging library (https://pypi.python.org/pypi/PIL)

Requirements for running the grain size processing version which uses parallel processing for speed:
1. python
2. kivy (http://kivy.org/#home)
3. python imaging library (https://pypi.python.org/pypi/PIL)
4. scipy (https://pypi.python.org/pypi/scipy)
5. numpy (https://pypi.python.org/pypi/numpy)
6. joblib (https://pypi.python.org/pypi/joblib)

