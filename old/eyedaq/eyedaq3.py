# eyedaq3
# Written by Daniel Buscombe, April 2014
# while at
# Grand Canyon Monitoring and Research Center, U.G. Geological Survey, Flagstaff, AZ 
# please contact:
# dbuscombe@usgs.gov

# =============================================
# ============= LIBRARIES =================
# =============================================
import numpy as np
from multiprocessing import Process, Queue
#from Queue import Empty
import cv2, pyproj
from PIL import Image, ImageTk
import os, csv
from tkFileDialog import askopenfilename 

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk

#from time import *
import time, serial, sys
from pynmea import nmea

vidnum=0
global tk_image
w = 640
h = 500
width_og = 0
height_org = 0
ser = 0
ser2 = 0
lat = 0
long = 0
pos_x = 0
pos_y = 0
alt = 0
i = 0 #x units for altitude measurment
BAUDRATE = 9600
BAUDRATE2 = 4800

cs2cs_args = "epsg:26949"
# get the transformation matrix of desired output coordinates
try:
   trans =  pyproj.Proj(init=cs2cs_args)
except:
   trans =  pyproj.Proj(cs2cs_args)
 
# =============================================
# ============= GPS FUNCTIONS =================
# =============================================
def scan():
    #scan for available ports. return a list of tuples (num, name)
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.name))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available

#=========================
def init_serial():

    if os.name=='nt':
       #opens the serial port based on the COM number you choose
       print "Found Ports:"
       for n,s in scan():
          print "%s" % s
       print " "

       #enter your COM port number
       print "Choose a COM port #. Enter # only, then enter"
       temp = raw_input() #waits here for keyboard input
       if temp == 'e':
	   sys.exit()
       comnum = 'COM' + temp #concatenate COM and the port number to define serial port

    else:
       comnum='/dev/ttyUSB0'

    global ser, BAUDRATE
    ser = serial.Serial()
    ser.baudrate = BAUDRATE
    ser.port = comnum
    ser.timeout = 0.5
    ser.open()
    #ser.isOpen()
    
#=========================
def init_serial_depth():

    if os.name=='nt':
       #opens the serial port based on the COM number you choose
       print "Found Ports:"
       for n,s in scan():
          print "%s" % s
       print " "

       #enter your COM port number
       print "Choose a COM port #. Enter # only, then enter"
       temp = raw_input() #waits here for keyboard input
       if temp == 'e':
	   sys.exit()
       comnum2 = 'COM' + temp #concatenate COM and the port number to define serial port

    else:
       comnum2='/dev/ttyUSB0'

    global ser2, BAUDRATE2
    ser2 = serial.Serial()
    ser2.baudrate = BAUDRATE2
    ser2.port = comnum2
    ser2.timeout = 0.5
    ser2.open()
    ser2.isOpen()

#=========================
def get_nmea():
    gotpos = 0; counter = 0
    
    while (gotpos==0) &(counter<3):
        line = ser.read(1000) # read 1000 bytes
        parts = line.split('\r\n') # split by line return

        newparts = [] # create new variable which contains cleaned strings
        for k in range(len(parts)):
            if parts[k].startswith('$'): #select if starts with $
                if len(parts[k].split('*'))>1: #select if contains *
                    if parts[k].count('$')==1: # select if only contains 1 $
                        newparts.append(parts[k])

        gpgga_parts = []; gpgsa_parts = [];
        gprmc_parts = []; gpvtg_parts = []; gpgsv_parts = []
        for k in range(len(newparts)):
            if "GPGGA" in newparts[k]:
                gpgga_parts.append(newparts[k])
            elif "GPGSA" in newparts[k]:
                gpgsa_parts.append(newparts[k])                
            elif "GPRMC" in newparts[k]:
                gprmc_parts.append(newparts[k])          
            elif "GPVTG" in newparts[k]:
                gpvtg_parts.append(newparts[k])
            elif "GPGSV" in newparts[k]:
                gpgsv_parts.append(newparts[k])

        if gpgga_parts:
            gotpos=1
            gpgga_parts = gpgga_parts[-1]; 
        if gprmc_parts:
            gprmc_parts = gprmc_parts[-1]; 
        if gpgsa_parts:
            gpgsa_parts = gpgsa_parts[-1]
        if gpvtg_parts:
            gpvtg_parts = gpvtg_parts[-1]
        if gpgsv_parts:
            gpgsv_parts = gpgsv_parts[-1]
                            
        counter += 1
        
    return gpgga_parts, gpgsa_parts, gprmc_parts, gpvtg_parts, gpgsv_parts

#=========================
def parse_nmea(gpgga_parts, gpgsa_parts, gprmc_parts, gpvtg_parts, gpgsv_parts):
    gpgga = nmea.GPGGA(); gpgsa = nmea.GPGSA()
    gprmc = nmea.GPRMC(); gpvtg = nmea.GPVTG(); gpgsv = nmea.GPGSV()

    dat = {}     
    # GPGGA
    try:
        gpgga.parse(gpgga_parts)
        lats = gpgga.latitude
        longs= gpgga.longitude
					
        #convert degrees,decimal minutes to decimal degrees 
        lat1 = (float(lats[2]+lats[3]+lats[4]+lats[5]+lats[6]+lats[7]+lats[8]))/60
        lat = (float(lats[0]+lats[1])+lat1)
        long1 = (float(longs[3]+longs[4]+longs[5]+longs[6]+longs[7]+longs[8]+longs[9]))/60
        long = (float(longs[0]+longs[1]+longs[2])+long1)
					
        #calc position
        dat['lat_1'] = str(lat);
        dat['lon_1'] = str(-long)
        #convert to az central state plane east/north
        e,n = trans(-long,lat)
        dat['e_1'] = str(e); dat['n_1'] = str(n)
        
        dat['alt'] = str(gpgga.antenna_altitude)
        dat['t'] = str(gpgga.timestamp);
        dat['qual'] = str(gpgga.gps_qual)
        dat['num_sats'] = str(gpgga.num_sats)
        dat['ref_id'] = str(gpgga.ref_station_id)
        dat['geo_sep'] = str(gpgga.geo_sep)
    except:
        dat['lat_1'] = 'NaN'; dat['lon_1'] = 'NaN'
        dat['alt'] = 'NaN'; dat['t'] = 'NaN'
        dat['qual'] = 'NaN'; dat['num_sats'] = 'NaN'
        dat['ref_id'] = 'NaN'; dat['geo_sep'] = 'NaN'
  
    # GPGSA
    try:
        gpgsa.parse(gpgsa_parts)
        dat['hdop'] = str(gpgsa.hdop); dat['pdop'] = str(gpgsa.pdop); dat['vdop'] = str(gpgsa.vdop)
        dat['mode'] = str(gpgsa.mode); dat['mode_type'] = str(gpgsa.mode_fix_type)
        dat['sv_id01'] = str(gpgsa.sv_id01); dat['sv_id02'] = str(gpgsa.sv_id02)
        dat['sv_id03'] = str(gpgsa.sv_id03); dat['sv_id04'] = str(gpgsa.sv_id04)
        dat['sv_id05'] = str(gpgsa.sv_id05); dat['sv_id06'] = str(gpgsa.sv_id06)
        dat['sv_id07'] = str(gpgsa.sv_id07); dat['sv_id08'] = str(gpgsa.sv_id08)
        dat['sv_id09'] = str(gpgsa.sv_id09); dat['sv_id10'] = str(gpgsa.sv_id10)
        dat['sv_id11'] = str(gpgsa.sv_id11); dat['sv_id12'] = str(gpgsa.sv_id12)    
    except:
        dat['hdop'] = 'NaN'; dat['pdop'] = 'NaN'; dat['vdop'] = 'NaN'
        dat['mode'] = 'NaN'; dat['mode_type'] = 'NaN'
        dat['sv_id01'] = 'NaN'; dat['sv_id02'] = 'NaN'
        dat['sv_id03'] = 'NaN'; dat['sv_id04'] = 'NaN'
        dat['sv_id05'] = 'NaN'; dat['sv_id06'] = 'NaN'
        dat['sv_id07'] = 'NaN'; dat['sv_id08'] = 'NaN'
        dat['sv_id09'] = 'NaN'; dat['sv_id10'] = 'NaN'
        dat['sv_id11'] = 'NaN'; dat['sv_id12'] = 'NaN'
            
    # GPGSV
    try:
        gpgsv.parse(gpgsv_parts)
        dat['az1'] = str(gpgsv.azimuth_1)
        dat['az2'] = str(gpgsv.azimuth_2)
        dat['elev_deg1'] = str(gpgsv.elevation_deg_1)
        dat['elev_deg2'] = str(gpgsv.elevation_deg_2)
        dat['num_sv'] = str(gpgsv.num_sv_in_view)
        dat['snr1'] = str(gpgsv.snr_1)
        dat['snr2'] = str(gpgsv.snr_2)
        dat['sv_prn1'] = str(gpgsv.sv_prn_num_1)
        dat['sv_prn2'] = str(gpgsv.sv_prn_num_2)
    except:
        dat['az1'] = 'NaN'; dat['az2'] = 'NaN'
        dat['elev_deg1'] = 'NaN'; dat['elev_deg2'] = 'NaN'
        dat['num_sv'] = 'NaN'; dat['snr1'] = 'NaN'
        dat['snr2'] = 'NaN'; dat['sv_prn1'] = 'NaN'; dat['sv_prn2'] = 'NaN'
            
    # GPRMC
    try:
        gprmc.parse(gprmc_parts)
        dat['date'] = str(gprmc.datestamp)
        dat['time_stamp'] = str(gprmc.timestamp)
        dat['spd'] = str(gprmc.spd_over_grnd)
        dat['true_course'] = str(gprmc.true_course)
        dat['mag_var'] = str(gprmc.mag_variation)
        dat['mag_var_dir'] = str(gprmc.mag_var_dir)
            
        lats = gprmc.lat; longs= gprmc.lon
					
        #convert degrees,decimal minutes to decimal degrees 
        lat1 = (float(lats[2]+lats[3]+lats[4]+lats[5]+lats[6]+lats[7]+lats[8]))/60
        lat = (float(lats[0]+lats[1])+lat1)
        long1 = (float(longs[3]+longs[4]+longs[5]+longs[6]+longs[7]+longs[8]+longs[9]))/60
        long = (float(longs[0]+longs[1]+longs[2])+long1)
					
        #calc position
        dat['lat_2'] = str(lat); dat['lon_2'] = str(-long)

        #convert to az central state plane east/north
        e,n = trans(-long,lat)
        dat['e_2'] = str(e); dat['n_2'] = str(n)
        
    except:
        dat['date'] = 'NaN'; dat['time_stamp'] = 'NaN'
        dat['spd'] = 'NaN'; dat['true_course'] = 'NaN'
        dat['mag_var'] = 'NaN'; dat['mag_var_dir'] = 'NaN'
        dat['lat_2'] = 'NaN'; dat['lon_2'] = 'NaN'

    #GPVTG
    try:
        gpvtg.parse(gpvtg_parts)
        dat['true_track'] = str(gpvtg.true_track)
        dat['spd_grnd_kmh'] = str(gpvtg.spd_over_grnd_kmph)
        dat['spd_grnd_kts'] = str(gpvtg.spd_over_grnd_kts)
        dat['mag_track'] = str(gpvtg.mag_track)
    except:
        dat['true_track'] = 'NaN'; dat['spd_grnd_kmh'] = 'NaN'
        dat['spd_grnd_kts'] = 'NaN'; dat['mag_track'] = 'NaN'
        
    return dat

# =============================================
# ============= GUI FUNCTIONS =================
# =============================================

def quit_(root, process,ser,f_csv,bedf_csv):
   # get the last site visited and add 1, write to station file
   fsite = open(os.getcwd()+os.sep+'station_start.txt','w')
   fsite.write(str(int(site.get())+1))
   print "station_start.txt updated"
   # destroy video thread and close gui
   print "video stream released"
   process.terminate()
   print "video stream terminated"
   root.destroy()
   print "GUI destroyed"
   # close the csv results files
   f_csv.close()
   bedf_csv.close()
   print "output files closed"
   # close the serial port
   ser.close()
   ser2.close()
   print "serial port closed"
   sys.exit()
   

# =============================================
def cls():
   if os.name=='posix': # true if linux/mac or cygwin on windows
      os.system('clear') 
   else: # windows
      os.system('cls')

# =============================================
def show_sats(pil_image):

    gpgga_parts, gpgsa_parts, gprmc_parts, gpvtg_parts, gpgsv_parts = get_nmea()
    dat = parse_nmea(gpgga_parts, gpgsa_parts, gprmc_parts, gpvtg_parts, gpgsv_parts)

    tmp = ser2.readline()
    tmp = line.split('\r\n') # split by line return
    print tmp

    print "======================="
    print "latitude: %s" % (dat['lat_1'])
    print "longitude: %s" % (dat['lon_1'])
    print "easting (AZ Central): %s" % (dat['e_1'])
    print "northing (AZ Central): %s" % (dat['n_1'])    
    print "altitude: %s" % (dat['alt'])
    print "time: %s" % (dat['t'])
    print "date: %s" % (dat['date'])
    print "number of satellites: %s" % (dat['num_sats'])
    print "hdop: %s" % (dat['hdop'])
    print "pdop: %s" % (dat['pdop'])
    print "vdop: %s" % (dat['vdop'])
    print "speed: %s" % (dat['spd'])
    print "SNR 1: %s" % (dat['snr1'])
    print "SNR 2: %s" % (dat['snr2'])
    print "Speed-over-ground (km/h): %s" % (dat['spd_grnd_kmh'])
    print "Track: %s" % (dat['true_track'])
    print "======================="

    #update screen values
    latscreen.set(dat['lat_1'])
    lonscreen.set(dat['lon_1'])
    #elevscreen.set(dat['alt'])
    #depthscreen.set(dat['depth'])

    cent=[float(dat['lon_1']), float(dat['lat_1'])]

    offset1 = int(width_org/10)
    offset2 = int(height_org/10)
    
    factorx = 1-(cent[0]-pos[2])/(pos[0]-pos[2])
    factory = 1-(cent[1]-pos[3])/(pos[1]-pos[3])

    originX = max(int(factorx*width_org)-offset1,0)
    destX = min(int(factorx*width_org)+offset1,width_org)
    originY = max(int(factory*height_org)-offset2,0)
    destY = min(int(factory*height_org)+offset2,height_org)

    # left, upper, right, lower
    #pil_image = pil_image.crop((150, 150, width_org-150, height_org-150))
    pil_image = pil_image.crop((originX,originY,destX,destY))

    # set the resizing factor so the aspect ratio is retained
    factor = 1.1
    width = int(width_org * factor) #(width_org/width_now))  
    height = int(height_org * factor) #(height_org/height_now))
    pil_image2 = pil_image.resize((width, height), Image.BILINEAR) #Image.ANTIALIAS)

    # convert PIL image object to Tkinter PhotoImage object
    tk_image = ImageTk.PhotoImage(pil_image2)

    #w1.itemconfig(image_on_canvas, image = tk_image)

    w1.configure(image=tk_image, text='X', font=("Helvetica",18))
    w1.image = tk_image  # avoid garbage collection

    return dat

# =============================================
def update_(pil_image):
   cls()
   dat = show_sats(pil_image)

# =============================================
def snap_(queue,pil_image):
   frame = queue.get()
   im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
   timenow = time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())
   filename = os.getcwd()+os.sep+'sand_images'+os.sep+timenow+'_'+site.get()+".png"
   cv2.imwrite(filename,im)
   print "%s written to file" % (filename)

   cls()
   dat = show_sats(pil_image)
   #write to csv file
   csvwriter.writerow([filename,timenow,dat['t'],dat['date'],dat['time_stamp'],\
                       dat['lat_1'],dat['lon_1'],dat['lat_2'],dat['lon_2'],\
                       dat['e_1'],dat['n_1'],dat['e_2'],dat['n_2'],dat['alt'],\
                       dat['hdop'],dat['pdop'],dat['vdop'],dat['qual'],dat['num_sats'],\
                       dat['num_sv'],dat['snr1'],dat['snr2'],dat['sv_prn1'],dat['sv_prn2'],\
                       dat['ref_id'],dat['geo_sep'],dat['mode'],dat['mode_type'],\
                       dat['sv_id01'],dat['sv_id02'],dat['sv_id03'],dat['sv_id04'],\
                       dat['sv_id05'],dat['sv_id06'],dat['sv_id07'],dat['sv_id08'],\
                       dat['sv_id09'],dat['sv_id10'],dat['sv_id11'],dat['sv_id12'],\
                       dat['az1'],dat['az2'],dat['elev_deg1'],dat['elev_deg2'],\
                       dat['spd'],dat['spd_grnd_kts'],dat['spd_grnd_kmh'],dat['true_course'],\
                       dat['mag_var'],dat['mag_var_dir'],dat['true_track'],dat['mag_track'],\
                       ])   
        
# =============================================
def sand_(queue,pil_image):
   frame = queue.get()
   im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
   timenow = time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())
   filename = os.getcwd()+os.sep+'bed_images'+os.sep+timenow+'_'+site.get()+"_sand.png"
   cv2.imwrite(filename,im)
   print "%s written to file" % (filename)

   cls()
   dat = show_sats(pil_image)
   #write to csv file
   bedcsvwriter.writerow([filename,timenow,dat['t'],dat['date'],dat['time_stamp'],'sand','1',\
                       dat['lat_1'],dat['lon_1'],dat['lat_2'],dat['lon_2'],\
                       dat['e_1'],dat['n_1'],dat['e_2'],dat['n_2'],dat['alt'],\
                       dat['hdop'],dat['pdop'],dat['vdop'],dat['qual'],dat['num_sats'],\
                       dat['num_sv'],dat['snr1'],dat['snr2'],dat['sv_prn1'],dat['sv_prn2'],\
                       dat['ref_id'],dat['geo_sep'],dat['mode'],dat['mode_type'],\
                       dat['sv_id01'],dat['sv_id02'],dat['sv_id03'],dat['sv_id04'],\
                       dat['sv_id05'],dat['sv_id06'],dat['sv_id07'],dat['sv_id08'],\
                       dat['sv_id09'],dat['sv_id10'],dat['sv_id11'],dat['sv_id12'],\
                       dat['az1'],dat['az2'],dat['elev_deg1'],dat['elev_deg2'],\
                       dat['spd'],dat['spd_grnd_kts'],dat['spd_grnd_kmh'],dat['true_course'],\
                       dat['mag_var'],dat['mag_var_dir'],dat['true_track'],dat['mag_track'],\
                       ])
   
# =============================================
def sand_gravel_(queue,pil_image):
   frame = queue.get()
   im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
   timenow = time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())
   filename = os.getcwd()+os.sep+'bed_images'+os.sep+timenow+'_'+site.get()+"_sand_gravel.png"
   cv2.imwrite(filename,im)
   print "%s written to file" % (filename)

   cls()
   dat = show_sats(pil_image)
   #write to csv file
   bedcsvwriter.writerow([filename,timenow,dat['t'],dat['date'],dat['time_stamp'],'sand/gravel','2',\
                       dat['lat_1'],dat['lon_1'],dat['lat_2'],dat['lon_2'],\
                       dat['e_1'],dat['n_1'],dat['e_2'],dat['n_2'],dat['alt'],\
                       dat['hdop'],dat['pdop'],dat['vdop'],dat['qual'],dat['num_sats'],\
                       dat['num_sv'],dat['snr1'],dat['snr2'],dat['sv_prn1'],dat['sv_prn2'],\
                       dat['ref_id'],dat['geo_sep'],dat['mode'],dat['mode_type'],\
                       dat['sv_id01'],dat['sv_id02'],dat['sv_id03'],dat['sv_id04'],\
                       dat['sv_id05'],dat['sv_id06'],dat['sv_id07'],dat['sv_id08'],\
                       dat['sv_id09'],dat['sv_id10'],dat['sv_id11'],dat['sv_id12'],\
                       dat['az1'],dat['az2'],dat['elev_deg1'],dat['elev_deg2'],\
                       dat['spd'],dat['spd_grnd_kts'],dat['spd_grnd_kmh'],dat['true_course'],\
                       dat['mag_var'],dat['mag_var_dir'],dat['true_track'],dat['mag_track'],\
                       ])
   
# =============================================
def gravel_(queue,pil_image):
   frame = queue.get()
   im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
   timenow = time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())
   filename = os.getcwd()+os.sep+'bed_images'+os.sep+timenow+'_'+site.get()+"_gravel.png"
   cv2.imwrite(filename,im)
   print "%s written to file" % (filename)

   cls()
   dat = show_sats(pil_image)
   #write to csv file
   bedcsvwriter.writerow([filename,timenow,dat['t'],dat['date'],dat['time_stamp'],'gravel','3',\
                       dat['lat_1'],dat['lon_1'],dat['lat_2'],dat['lon_2'],\
                       dat['e_1'],dat['n_1'],dat['e_2'],dat['n_2'],dat['alt'],\
                       dat['hdop'],dat['pdop'],dat['vdop'],dat['qual'],dat['num_sats'],\
                       dat['num_sv'],dat['snr1'],dat['snr2'],dat['sv_prn1'],dat['sv_prn2'],\
                       dat['ref_id'],dat['geo_sep'],dat['mode'],dat['mode_type'],\
                       dat['sv_id01'],dat['sv_id02'],dat['sv_id03'],dat['sv_id04'],\
                       dat['sv_id05'],dat['sv_id06'],dat['sv_id07'],dat['sv_id08'],\
                       dat['sv_id09'],dat['sv_id10'],dat['sv_id11'],dat['sv_id12'],\
                       dat['az1'],dat['az2'],dat['elev_deg1'],dat['elev_deg2'],\
                       dat['spd'],dat['spd_grnd_kts'],dat['spd_grnd_kmh'],dat['true_course'],\
                       dat['mag_var'],dat['mag_var_dir'],dat['true_track'],dat['mag_track'],\
                       ])
                       
# =============================================
def cobble_(queue,pil_image):
   frame = queue.get()
   im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
   timenow = time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())
   filename = os.getcwd()+os.sep+'bed_images'+os.sep+timenow+'_'+site.get()+"_cobble.png"
   cv2.imwrite(filename,im)
   print "%s written to file" % (filename)

   cls()
   dat = show_sats(pil_image)
   #write to csv file
   bedcsvwriter.writerow([filename,timenow,dat['t'],dat['date'],dat['time_stamp'],'cobble','4',\
                       dat['lat_1'],dat['lon_1'],dat['lat_2'],dat['lon_2'],\
                       dat['e_1'],dat['n_1'],dat['e_2'],dat['n_2'],dat['alt'],\
                       dat['hdop'],dat['pdop'],dat['vdop'],dat['qual'],dat['num_sats'],\
                       dat['num_sv'],dat['snr1'],dat['snr2'],dat['sv_prn1'],dat['sv_prn2'],\
                       dat['ref_id'],dat['geo_sep'],dat['mode'],dat['mode_type'],\
                       dat['sv_id01'],dat['sv_id02'],dat['sv_id03'],dat['sv_id04'],\
                       dat['sv_id05'],dat['sv_id06'],dat['sv_id07'],dat['sv_id08'],\
                       dat['sv_id09'],dat['sv_id10'],dat['sv_id11'],dat['sv_id12'],\
                       dat['az1'],dat['az2'],dat['elev_deg1'],dat['elev_deg2'],\
                       dat['spd'],dat['spd_grnd_kts'],dat['spd_grnd_kmh'],dat['true_course'],\
                       dat['mag_var'],dat['mag_var_dir'],dat['true_track'],dat['mag_track'],\
                       ])
# =============================================
def sand_rock_(queue,pil_image):
   frame = queue.get()
   im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
   timenow = time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())
   filename = os.getcwd()+os.sep+'bed_images'+os.sep+timenow+'_'+site.get()+"_sand_rock.png"
   cv2.imwrite(filename,im)
   print "%s written to file" % (filename)

   cls()
   dat = show_sats(pil_image)
   #write to csv file
   bedcsvwriter.writerow([filename,timenow,dat['t'],dat['date'],dat['time_stamp'],'sand/rock','5',\
                       dat['lat_1'],dat['lon_1'],dat['lat_2'],dat['lon_2'],\
                       dat['e_1'],dat['n_1'],dat['e_2'],dat['n_2'],dat['alt'],\
                       dat['hdop'],dat['pdop'],dat['vdop'],dat['qual'],dat['num_sats'],\
                       dat['num_sv'],dat['snr1'],dat['snr2'],dat['sv_prn1'],dat['sv_prn2'],\
                       dat['ref_id'],dat['geo_sep'],dat['mode'],dat['mode_type'],\
                       dat['sv_id01'],dat['sv_id02'],dat['sv_id03'],dat['sv_id04'],\
                       dat['sv_id05'],dat['sv_id06'],dat['sv_id07'],dat['sv_id08'],\
                       dat['sv_id09'],dat['sv_id10'],dat['sv_id11'],dat['sv_id12'],\
                       dat['az1'],dat['az2'],dat['elev_deg1'],dat['elev_deg2'],\
                       dat['spd'],dat['spd_grnd_kts'],dat['spd_grnd_kmh'],dat['true_course'],\
                       dat['mag_var'],dat['mag_var_dir'],dat['true_track'],dat['mag_track'],\
                       ])
# =============================================
def rock_(queue,pil_image):
   frame = queue.get()
   im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
   timenow = time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())
   filename = os.getcwd()+os.sep+'bed_images'+os.sep+timenow+'_'+site.get()+"_rock.png"
   cv2.imwrite(filename,im)
   print "%s written to file" % (filename)

   cls()
   dat = show_sats(pil_image)
   #write to csv file
   bedcsvwriter.writerow([filename,timenow,dat['t'],dat['date'],dat['time_stamp'],'rock','6',\
                       dat['lat_1'],dat['lon_1'],dat['lat_2'],dat['lon_2'],\
                       dat['e_1'],dat['n_1'],dat['e_2'],dat['n_2'],dat['alt'],\
                       dat['hdop'],dat['pdop'],dat['vdop'],dat['qual'],dat['num_sats'],\
                       dat['num_sv'],dat['snr1'],dat['snr2'],dat['sv_prn1'],dat['sv_prn2'],\
                       dat['ref_id'],dat['geo_sep'],dat['mode'],dat['mode_type'],\
                       dat['sv_id01'],dat['sv_id02'],dat['sv_id03'],dat['sv_id04'],\
                       dat['sv_id05'],dat['sv_id06'],dat['sv_id07'],dat['sv_id08'],\
                       dat['sv_id09'],dat['sv_id10'],dat['sv_id11'],dat['sv_id12'],\
                       dat['az1'],dat['az2'],dat['elev_deg1'],dat['elev_deg2'],\
                       dat['spd'],dat['spd_grnd_kts'],dat['spd_grnd_kmh'],dat['true_course'],\
                       dat['mag_var'],dat['mag_var_dir'],dat['true_track'],dat['mag_track'],\
                       ])
   
# =============================================
def update_image(image_label, queue):
   frame = queue.get()
   im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
   a = Image.fromarray(im)
   b = ImageTk.PhotoImage(image=a)
   image_label.configure(image=b)
   image_label._image_cache = b  # avoid garbage collection
   root.update()

# =============================================
def update_all(root, image_label, queue):
   update_image(image_label, queue)
   root.after(0, func=lambda: update_all(root, image_label, queue))

# =============================================
# multiprocessing image processing functions
def image_capture(queue):
   vidFile = cv2.VideoCapture(vidnum)
   while True:
      try:
         flag, frame=vidFile.read()
         if flag==0:
            break
         queue.put(frame)
         cv2.waitKey(20)
      except:
         continue


# =============================================
# ============= MAIN PROGRAM ==================
# =============================================
if __name__ == '__main__':

   cls()
   print "==========================================="
   print "=============== EYEDAQ ===================="
   print "==========================================="
   print "======Eyeball Data Acquisition System======"
   print "==========================================="
   print "======A PROGRAM BY DANIEL BUSCOMBE========="
   print "========USGS, FLAGSTAFF, ARIZONA==========="
   print "=========REVISION 0.2, APR 2014============"
   print "=============== BETA  ====================="
   print "==========================================="

   # initialize serial port with gps data coming in
   init_serial()
   
   # initialize serial port with gps data coming in
   init_serial_depth()   

#   try:
#      vidFile = cv2.VideoCapture(vidnum)
#      vidFile.release()
#   except:
#      sys.exit("Video camera failed to initialize")

   # set up outputs for sand images
   if os.path.isdir(os.getcwd()+os.sep+'sand_images'):
       csvfilename = os.getcwd()+os.sep+'sand_images'+os.sep+'dat_'+time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())+'.csv'
   else:
       os.mkdir(os.getcwd()+os.sep+'sand_images')
       csvfilename = os.getcwd()+os.sep+'sand_images'+os.sep+'dat_'+time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())+'.csv'

   f_csv = open(csvfilename, 'ab') #append binary: the binary is required for windows stoopid excel to not put extra \r
   csvwriter = csv.writer(f_csv, delimiter=',')
   csvwriter.writerow(['Image', 'local time', 't','date','time',\
                       'latitude 1', 'longitude 1','latitude 2','longitude 2',\
                       'easting 1','northing 1','easting 2','northing 2',\
                       'altitude','hdop','pdop','vdop','gps quality','num_sats',\
                       'num_sv','snr1','snr2','sv_prn1','sv_prn2',\
                        'ref id','geo sep','mode','mode type',\
                        'sat id1','sat id2','sat id3','sat id4',\
                        'sat id5','sat id6','sat id7','sat id8',\
                        'sat id9','sat id10','sat id11','sat id12',\
                        'azimuth 1','azimuth 2','elev deg 1','elev deg 2',\
                        'speed','ground speed kts','ground speed kmh','true course',\
                        'mag variation','mag var direc','true track','mag track'])

   # set up outputs for 'bed' images
   if os.path.isdir(os.getcwd()+os.sep+'bed_images'):
       bedcsvfilename = os.getcwd()+os.sep+'bed_images'+os.sep+'dat_'+time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())+'.csv'
   else:
       os.mkdir(os.getcwd()+os.sep+'bed_images')
       bedcsvfilename = os.getcwd()+os.sep+'bed_images'+os.sep+'dat_'+time.strftime("%b_%d_%Y_%H_%M_%S", time.localtime())+'.csv'
       
   bedf_csv = open(bedcsvfilename, 'ab')
   bedcsvwriter = csv.writer(bedf_csv, delimiter=',')
   bedcsvwriter.writerow(['Image', 'local time', 't','date','time','bed class','bed code',\
                       'latitude 1', 'longitude 1','latitude 2','longitude 2',\
                       'easting 1','northing 1','easting 2','northing 2',\
                       'altitude','hdop','pdop','vdop','gps quality','num_sats',\
                       'num_sv','snr1','snr2','sv_prn1','sv_prn2',\
                        'ref id','geo sep','mode','mode type',\
                        'sat id1','sat id2','sat id3','sat id4',\
                        'sat id5','sat id6','sat id7','sat id8',\
                        'sat id9','sat id10','sat id11','sat id12',\
                        'azimuth 1','azimuth 2','elev deg 1','elev deg 2',\
                        'speed','ground speed kts','ground speed kmh','true course',\
                        'mag variation','mag var direc','true track','mag track'])                      
 
   tk.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
   mapfile = askopenfilename(filetypes=[("Map Image","*.GIF *.gif")], multiple=False)
   if os.name=='nt':
       #mapfile = mapfile.split(' ')
       if type(mapfile)==unicode:
          mapfile = str(mapfile)
          
   if os.name=='posix':
       posfile = mapfile[0].split('.gif')[0]+'.txt'
       pos = np.genfromtxt(posfile)
   else:
       posfile = askopenfilename(filetypes=[("Map Coords","*.txt")], multiple=False)
       #posfile = posfile.split(' ')
       if type(posfile)==unicode:
          posfile = str(posfile)
       pos = np.genfromtxt(posfile)

   # ===== start the queue for the gui image collection
   queue = Queue()
   print 'queue initialized...'
   root = tk.Toplevel() #Tk()
   print 'GUI initialized...'
   root.resizable(True, True)

   # ===== label for the video
   image_label = tk.Label(master=root)# label for the video frame
   image_label.grid(row=1, column=4)

   # pick an image file you have .bmp  .jpg  .gif.  .png
   # if not in the working directory, give full path
   try:
      img_file = mapfile[0]
      # open as a PIL image object
      pil_image = Image.open(img_file)
   except:
      img_file = mapfile
      print img_file
      pil_image = Image.open(img_file)

   # get the size of the original image
   width_org, height_org = pil_image.size

   cent=[pos[0]+((pos[2]-pos[0])/2), pos[1]+((pos[3]-pos[1])/2)]

   offset = int(width_org/10)
   factorx = (cent[0]-pos[2])/(pos[0]-pos[2])
   factory = (cent[1]-pos[3])/(pos[1]-pos[3])

   print factorx, factory
   originX = int(factorx*width_org)-offset #max(int(factorx*width_org)-offset,0)
   destX = int(factorx*width_org)+offset #min(int(factorx*width_org)+offset,width_org)
   originY = int(factory*height_org)-offset #max(int(factory*height_org)-offset,0)
   destY = int(factory*height_org)+offset #min(int(factory*height_org)+offset,height_org)

   #print (int(factorx*width_org),int(factory*height_org))
   print (originX,originY,destX,destY)
   # left, upper, right, lower
   #pil_image = pil_image.crop((150, 150, width_org-150, height_org-150))
   pil_image2 = pil_image.crop((originX,originY,destX,destY))

   # set the resizing factor so the aspect ratio is retained
   factor = 1.1
   width = int(width_org * factor) #(width_org/width_now))  
   height = int(height_org * factor) #(height_org/height_now))
   pil_image2 = pil_image2.resize((width, height), Image.BILINEAR) #Image.ANTIALIAS)   

   # convert PIL image object to Tkinter PhotoImage object
   tk_image = ImageTk.PhotoImage(pil_image2)

   w1 = tk.Label(master=root, width=w, height=h, image=tk_image, text='X', font=("Helvetica",18), compound=tk.CENTER)
   w1.grid(row=1, column=0, columnspan = 2)

   #w1 = tk.Canvas(master=root, width=w, height=h)   
   #w1.grid(row=1, column=0, columnspan = 2)
   #image_on_canvas = w1.create_image(0, 0, image = tk_image)

   print 'GUI image label initialized...'
   p = Process(target=image_capture, args=(queue,))
   p.start()
   print 'image capture process has started...'

   # ===== draw some buttons
   # update button
   update_button = tk.Button(master=root, text='Update', activebackground='red', command=lambda: update_(pil_image))
   update_button.grid(row=0, column=0)
   
   # quit button
   quit_button = tk.Button(master=root, text='Quit', activebackground='red', command=lambda: quit_(root, p, ser, f_csv, bedf_csv))
   quit_button.grid(row=2, column=0)

   # snap button
   snap_button = tk.Button(master=root,text="Snap",activebackground='blue', command=lambda: snap_(queue,pil_image))
   snap_button.grid(row=3, column=0)

   # sand button
   sand_button = tk.Button(master=root, text='Sand',activebackground='yellow', command=lambda: sand_(queue,pil_image))
   sand_button.grid(row=2, column=1)

   # gravel button
   gravel_button = tk.Button(master=root, text='Gravel',activebackground='green', command=lambda: gravel_(queue,pil_image))
   gravel_button.grid(row=3, column=1)

   # sand/gravel button
   sg_button = tk.Button(master=root, text='Sand/Gravel',activebackground='cyan', command=lambda: sand_gravel_(queue,pil_image))
   sg_button.grid(row=4, column=1)

   # cobble button
   cobble_button = tk.Button(master=root, text='Cobble',activebackground='magenta', command=lambda: cobble_(queue,pil_image))
   cobble_button.grid(row=2, column=2)

   # rock button
   rock_button = tk.Button(master=root, text='Rock',activebackground='red', command=lambda: rock_(queue,pil_image))
   rock_button.grid(row=3, column=2)

   # sand/rock button
   sr_button = tk.Button(master=root, text='Sand/Rock',activebackground='white', command=lambda: sand_rock_(queue,pil_image))
   sr_button.grid(row=4, column=2)

   # open and read a simple text file which contains the last site visited
   if os.path.isfile(os.getcwd()+os.sep+'station_start.txt'):
       fsite = open(os.getcwd()+os.sep+'station_start.txt')
       try:
           site_start = int(fsite.readline()); fsite.close()
       except:
           site_start=1
   else:
       site_start=1
   
   site = tk.Spinbox(master=root,from_=site_start, to=100000)
   site.grid(row = 4, column = 0)
   site.focus_set()   

   # field for lat 
   latscreen = tk.StringVar()
   lat_entry = tk.Entry(master=root, width = 10, textvariable = latscreen)
   lat_entry.grid(row = 5, column = 0)
   latscreen.set(u"Latitude")

   # field for lon
   lonscreen = tk.StringVar()
   lon_entry = tk.Entry(master=root, width = 10, textvariable = lonscreen)
   lon_entry.grid(row = 5, column = 1 )
   lonscreen.set(u"Longitude")

   # field for elev
   #elevscreen = tk.StringVar()
   #elev_entry = tk.Entry(master=root, width = 10, textvariable = elevscreen)
   #elev_entry.grid(row = 5, column = 2)
   #elevscreen.set(u"Elevation")
   
   # field for depth
   depthscreen = tk.StringVar()
   depth_entry = tk.Entry(master=root, width = 10, textvariable = depthscreen)
   depth_entry.grid(row = 5, column = 2)
   depthscreen.set(u"Depth")   

   print 'buttons initialized...'
   # setup the update callback
   root.after(0, func=lambda: update_all(root, image_label, queue))
   root.title('EyeDAq: Eyeball Data Acquisition System')

   print 'root.after was called...'
   root.mainloop()
   print 'mainloop exit'
   p.join()
   print 'image capture process exit'

   # ===== initiate some text fields
   # field for site 
   #site = tk.Entry(master=root)

    #'center' is default --> uses center of picture
    #at canvas coordinates x=250, y=250 (center of canvas)
    #w1.create_image(w//2, h//2, image=tk_image, anchor='center')

    #w1.itemconfigure(w1,image=tk_image) #canvas

      # 'nw' uses upper left corner of the image as anchor
   # image corner positions at canvas coordinates x=30, y=20
   #w1.create_image(300, 20, image=tk_image, anchor='nw')

   #'center' is default --> uses center of picture
   #at canvas coordinates x=250, y=250 (center of canvas)
   #w1.create_image(w//2, h//2, image=tk_image, anchor='center')
      # use one of these filter options to resize the image:
   # Image.NEAREST     use nearest neighbour
   # Image.BILINEAR    linear interpolation in a 2x2 environment
   # Image.BICUBIC     cubic spline interpolation in a 4x4 environment
   # Image.ANTIALIAS   best down-sizing filter

      #width_now, height_now = pil_image.size

#   loadbutton = tk.Button(master=root,text = u"Load Map",
#                                command = lambda: getmap(root))
#   loadbutton.grid(row=0, column=0)

#   try:
#      mapim = tk.PhotoImage(file=mapfile[0])
#   except:
#      # ===== a naff logo
#      mapim = tk.PhotoImage(file="logo.gif")
   
#   w = 640
#   h = 500

#   #im = tk.PhotoImage(file=os.getcwd()+os.sep+'maps'+os.sep+'flagstaff.gif')
#   w1 = tk.Label(master=root, image=mapim)
#   w1.grid(row=1, column=0, columnspan = 2)

   #w1 = tk.Canvas(master=root, width=w, height=h)
   #w1.grid(row=1, column=0, columnspan = 2)
   #w1.pack(side="top",fill='both', expand='yes')
