#parse_imu.py
# Daniel Buscombe, April 2014
# libraries
import csv, sys, time, os
from tkFileDialog import askopenfilename 
from scipy.io import savemat
from datetime import datetime
from dateutil import tz
import calendar
from scipy.signal import firwin, lfilter
import numpy as np

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk

# main
# open csv file
tk.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
csvfile = askopenfilename(filetypes=[("IMU file","*.csv")], multiple=False)

# open csv and get only headers (1st row)
with open(csvfile, 'rb') as f:
    mycsv = csv.reader(f)
    v = mycsv.next()
f.close()

# these will be field names
# replace spaces with underscores
vnew = [];
for k in xrange(len(v)):
   vnew.append(v[k].replace(' ','_'))
   
# create a new list the length of vnew
del v
d = [[] for x in xrange(len(vnew))]

# cycle through csvfile rows and assign values to dictionary
with open(csvfile, 'rb') as f: 
    mycsv = csv.reader(f)   
    for row in mycsv:
        if int(mycsv.line_num)>1:
           for k in xrange(len(row)):
              try:
                 d[k].append(float(row[k]))
              except:
                 d[k].append(row[k])
# close file
f.close()

# create dictionary filling keys with vnew and values with d
#v = dict((el,dd) for el in vnew for dd in d)

# dict makes order screweed up
v = dict((el,0) for el in vnew)

# so this ugly bit of code is needed to fill dict with correct order of values
counter = 0
a = v.keys()
for k in a:
   for vv in vnew:
      if vv==k:
         v[k] = d[counter]
         counter = 0
         break
      else:
         counter=counter+1

del vv,a,k,counter,vnew

# get date from file creation time
date = time.ctime(os.path.getmtime(csvfile))
date = datetime.strptime(date,'%a %b %d %H:%M:%S %Y')

# for conversions and creations of epoch time
to_zone = tz.tzutc()
from_zone = tz.tzlocal()

#local = []
#for k in v['Time_(s)']:
#   local.append(datetime.strptime(datetime.strftime(date,'%Y %m %d')+' '+k,'%Y %m %d %I:%M:%S.%f:%p'))

#v['Local_datetime'] = local

# get epoch times in local and utc
epoch_local =[]; epoch_utc = []
for k in v['Time_(s)']:
   local = datetime.strptime(datetime.strftime(date,'%Y %m %d')+' '+k,'%Y %m %d %I:%M:%S.%f:%p')
   epoch_local.append(calendar.timegm(local.timetuple()))
   local = local.replace(tzinfo=from_zone)
   utc = local.astimezone(to_zone)
   epoch_utc.append(calendar.timegm(utc.timetuple()))

v['Epoch_local'] = epoch_local
v['Epoch_utc'] = epoch_utc

#This finds a magnetic north bearing, correcting for board tilt and roll as measured by the accelerometer
#Roll Angle - about axis 0
#tan(roll angle) = gy/gz
#Use Atan2 so we have an output os (-180 - 180) degrees
rollAngle = np.arctan2(v['Processed_Y_Accel'], v['Processed_Z_Accel'])

#Pitch Angle - about axis 1
#tan(pitch angle) = -gx / (gy x sin(roll angle) x gz * cos(roll angle))
#Pitch angle range is (-90 - 90) degrees
pitchAngle = np.arctan(-np.asarray(v['Processed_X_Accel']) , ( (np.asarray(v['Processed_Y_Accel']) * np.sin(rollAngle)) + np.asarray(v['Processed_Y_Accel']) * np.cos(rollAngle)) )


#Yaw Angle - about axis 2 
#tan (yaw angle ) = (mZ x sin(roll) - mY x cos(roll)) /
#(mx x cos(pitch) + my x sin(pitch) x sin(roll) + mz x sin(pitch) x cos(roll))
#Use Atan2 to get our range in (-180 - 180)
#Yaw angle == 0 degrees when axis 0 is pointing at magnetic north
yawAngle = np.arctan2(\
		   (v['Processed_Z_Mag'] * np.sin(rollAngle)) - (v['Processed_Y_Mag'] * np.cos(rollAngle)),\
		   (v['Processed_X_Mag'] * np.cos(pitchAngle))+ (v['Processed_Y_Mag'] * np.sin(pitchAngle) * np.sin(rollAngle))+ (v['Processed_Z_Mag'] * np.sin(pitchAngle) * np.cos(rollAngle)) )

y = -yawAngle.copy()

# turn -180:180 into 0:260
ind1 = np.where(y>=0); ind2 = np.where(y<0)
y[ind1] = y[ind1]*(180/np.pi)
y[ind2] = 360-(y[ind2]*(-180/np.pi))

v['heading_raw'] = y

# low pass filter
h=firwin( numtaps=10, cutoff=0.5, nyq=16/2)
y = lfilter( h, 1.0, y)

v['heading_lowpass'] = y

savemat(csvfile.split('.csv')[0]+'.mat',v)

