
from pynmea import nmea
import matplotlib.pyplot as plt
import serial, time, sys, datetime, shutil
import thread #threading, 
import numpy as np
import os

######Global Variables#####################################################
# you must declare the variables as 'global' in the fxn before using#
ser = 0
lat = 0
long = 0
pos_x = 0
pos_y = 0
alt = 0
i = 0 #x units for altitude measurment

#adjust these values based on your location and map, lat and long are in decimal degrees
TRX = -111.60475 #-105.1621          #top right longitude
TRY = 35.228303 #40.0868            #top right latitude
BLX = -111.633978 #-105.2898          #bottom left longitude
BLY = 35.204275 #40.001             #bottom left latitude
BAUDRATE = 9600
lat_input = 0            #latitude of home marker
long_input = 0           #longitude of home marker

#=========================
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
def get_nmea():
    gotpos = 0; counter = 0
    
    while (gotpos==0) &(counter<5):
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
            if gprmc_parts:
                if gpgsa_parts:
                    if gpvtg_parts:
                        if gpgsv_parts:
                            gpgga_parts = gpgga_parts[-1]; gpgsa_parts = gpgsa_parts[-1]
                            gprmc_parts = gprmc_parts[-1]; gpvtg_parts = gpvtg_parts[-1] 
                            gpgsv_parts = gpgsv_parts[-1]
                            gotpos=1
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

#=========================    
def show_nmea(ThreadName,delay):
    count = 0
    while count < 10:
        try:
            time.sleep(delay)
            count += 1
            gpgga_parts, gpgsa_parts, gprmc_parts, gpvtg_parts, gpgsv_parts = get_nmea()
            dat = parse_nmea(gpgga_parts, gpgsa_parts, gprmc_parts, gpvtg_parts, gpgsv_parts)

            print "======================="
            print "latitude: %s" % (dat['lat_1'])
            print "longitude: %s" % (dat['lon_1'])
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
            
        except:
            time.sleep(delay)
            count += 1
            print "No position"
        
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
    ser.timeout = 1
    ser.open()
    ser.isOpen()

#=========================
def user_input():
    #runs in main loop looking for user commands
    print 'hit e to exit'
    tester = raw_input()
    if tester == 'e':
	sys.exit()
		
########START#####################################################################################
init_serial()

thread.start_new_thread(show_nmea, ("Thread 1: ",0.01) )

#main program loop
while 1:
	user_input() # the main program waits for user input the entire time
ser.close()


##im = plt.imread('C:\Users\dbuscombe\Desktop\gps_tracker\map.png')
##implot = plt.imshow(im,extent=[BLX, TRX, BLY, TRY])

##thread1 = threading.Thread(target = show_gpgga())

##def stream_serial():
##    #stream data directly from the serial port
##    line = ser.readline()
##    return str(line)

##def thread():
##    #threads - run idependent of main loop
##    thread1 = threading.Thread(target = show_gpgga())
##    #thread2 = threading.Thread(target = user_input) #optional second thread
##    thread1.start()
##    #thread2.start()
