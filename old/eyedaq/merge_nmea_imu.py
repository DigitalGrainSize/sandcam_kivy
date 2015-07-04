from scipy.io import loadmat
from tkFileDialog import askopenfilename 
import matplotlib.pylab as plt
from PIL import Image

import sys, os
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk


# main
# open mat file gps
tk.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
gpsfile = askopenfilename(filetypes=[("GPS file","*.mat")], multiple=False)

gps = loadmat(gpsfile)

# open mat file imu
tk.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
imufile = askopenfilename(filetypes=[("IMU file","*.mat")], multiple=False)

imu = loadmat(imufile)

# get two timestamps
imu_time = np.squeeze(imu['Epoch_local'])
gps_time = np.squeeze(gps['epoch_local'])

# intepolate lat,lon
lat = np.interp(imu_time,gps_time,np.squeeze(gps['lat_1']))
lon = np.interp(imu_time,gps_time,np.squeeze(gps['lon_1']))

# get low pass filtered heading
head = np.squeeze(imu['heading_lowpass'])


## map file
#tk.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
#mapfile = askopenfilename(filetypes=[("Map Image","*.GIF *.gif")], multiple=False)
#if os.name=='nt':
#   mapfile = mapfile.split(' ')

## coord file
#posfile = askopenfilename(filetypes=[("Map Coords","*.txt")], multiple=False)
#posfile = posfile.split(' ')
#pos = np.genfromtxt(posfile[0])

# open as a PIL image object
#pil_image = Image.open(mapfile)


# plot heading
fig = plt.figure()
ax = plt.subplot(1,1,1)
#plt.imshow(pil_image,extent=[pos[0],pos[2],pos[1],pos[3]])
plt.scatter(lon,lat,head,head)
y_formatter = plt.ScalarFormatter(useOffset=False)
ax.yaxis.set_major_formatter(y_formatter)
ax.xaxis.set_major_formatter(y_formatter) 
setp(plt.xticks()[1], rotation=30)
plt.colorbar()
plt.title('Heading (Deg. True North)')

plt.savefig('heading_loop_LM',bbox_inches='tight',dpi=400)

plt.close()
del fig

# get pitch
pitch = np.squeeze(imu['Pitch_(theta)'])
roll = np.squeeze(imu['Roll_(phi)'])

fig = plt.figure()
fig.subplots_adjust(wspace = 0.6)
ax = plt.subplot(1,2,1)
#plt.imshow(pil_image,extent=[pos[0],pos[2],pos[1],pos[3]])
plt.scatter(lon,lat,head,pitch)
y_formatter = plt.ScalarFormatter(useOffset=False)
ax.yaxis.set_major_formatter(y_formatter)
ax.xaxis.set_major_formatter(y_formatter) 
setp(plt.xticks()[1], rotation=30)
plt.colorbar()
plt.title('Pitch (Deg.)')

ax = plt.subplot(1,2,2)
#plt.imshow(pil_image,extent=[pos[0],pos[2],pos[1],pos[3]])
plt.scatter(lon,lat,head,roll)
y_formatter = plt.ScalarFormatter(useOffset=False)
ax.yaxis.set_major_formatter(y_formatter)
ax.xaxis.set_major_formatter(y_formatter) 
setp(plt.xticks()[1], rotation=30)
plt.colorbar()
plt.title('Roll (Deg.)')

plt.savefig('pitch_roll_loop_LM',bbox_inches='tight',dpi=400)

plt.close()
del fig






