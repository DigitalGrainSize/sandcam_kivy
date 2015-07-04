# plot_eyeball.py
# Daniel Buscombe, April 2014
from pynmea import nmea
import os, time, csv
from tkFileDialog import askopenfilename 
from datetime import datetime
from dateutil import tz
import calendar
from scipy.io import loadmat, savemat
from PIL import Image
import matplotlib.pylab as plt
import numpy as np
import tkMessageBox as msg

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk

# csv file
tk.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
csvfile = askopenfilename(filetypes=[("Eyeball file","*.csv")], multiple=False)

# map file
tk.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
mapfile = askopenfilename(filetypes=[("Map Image","*.GIF *.gif")], multiple=False)
if type(mapfile)==unicode:
   mapfile = str(mapfile)

print mapfile

# coord file
posfile = askopenfilename(filetypes=[("Map Coords","*.txt")], multiple=False)
#posfile = posfile.split(' ')
if type(posfile)==unicode:
   posfile = str(posfile)
   pos = np.genfromtxt(posfile)
       
print posfile       
pos = np.genfromtxt(posfile)

lat = []; lon = []; image = []; t = [];
code = []; stat = []; d = []
with open(csvfile, 'rb') as f:
    mycsv = csv.reader(f)
    for row in mycsv:
        if int(mycsv.line_num)>1:
           image.append(row[0])
           stat.append(row[1])
           lat.append(row[8])
           lon.append(row[9])   
           t.append(row[5])
           code.append(row[7])
           d.append(row[4])
  
f.close()    

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

epoch_local =[]; epoch_utc = []

d = '2014'+' '+d[0][2:4]+' '+d[0][:2]

for k in t:
   #utc = datetime.strptime(k[:10]+' '+str(k[11:-5]),'%Y-%m-%d %H:%M:%S')
   utc = datetime.strptime(d+' '+k[:2]+':'+k[2:4]+':'+k[4:],'%Y %m %d %H:%M:%S.%f')
   utc = utc.replace(tzinfo=from_zone)
   local = utc.astimezone(to_zone)
   epoch_utc.append(calendar.timegm(utc.timetuple()))
   epoch_local.append(calendar.timegm(local.timetuple()))

code = np.asarray(code,'float'); t = np.asarray(t)
lat = np.asarray(lat,'float'); lon = np.asarray(lon,'float')
code[np.where(np.isnan(code))] = 1
      
# open as a PIL image object
pil_image = Image.open(mapfile)

result = msg.askquestion("Plot Option", "Plot by sediment type? (No will plot by time)?", icon='question')
if result == 'yes':
   fig = plt.figure()
   ax = plt.subplot(1,1,1)
   plt.imshow(pil_image,extent=[pos[0],pos[2],pos[1],pos[3]])
   y_formatter = plt.ScalarFormatter(useOffset=False)
   ax.yaxis.set_major_formatter(y_formatter)
   ax.xaxis.set_major_formatter(y_formatter) 
   plt.scatter(lon,lat,s=code*100,c=code)
   plt.axis('tight')
   plt.show()
else:
   fig = plt.figure()
   ax = plt.subplot(1,1,1)
   plt.imshow(pil_image,extent=[pos[0],pos[2],pos[1],pos[3]])
   y_formatter = plt.ScalarFormatter(useOffset=False)
   ax.yaxis.set_major_formatter(y_formatter)
   ax.xaxis.set_major_formatter(y_formatter) 
   secs = epoch_local - np.min(epoch_local)
   plt.scatter(lon,lat,s=secs,c=secs)
   plt.axis('tight')
   plt.show()



