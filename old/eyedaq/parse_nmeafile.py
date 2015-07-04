# parse_nmeafile.py
# Daniel Buscombe, April 2014
from pynmea import nmea
import os, time, pyproj, csv
from tkFileDialog import askopenfilename 
from datetime import datetime
from dateutil import tz
import calendar
from scipy.io import savemat

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk


# =========================================================
def ascol( arr ):
    '''
    reshapes row matrix to be a column matrix (N,1).
    '''
    if len( arr.shape ) == 1: arr = arr.reshape( ( arr.shape[0], 1 ) )
    return arr
# =========================================================


cs2cs_args = "epsg:26949"
# get the transformation matrix of desired output coordinates
try:
   trans =  pyproj.Proj(init=cs2cs_args)
except:
   trans =  pyproj.Proj(cs2cs_args)

tk.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
nmeafile = askopenfilename(filetypes=[("Nmea file","*.txt")], multiple=False)

f = open(nmeafile,'r')
raw = f.read()
f.close()

raw = raw.split('\r\n')

lat_1 = []; lon_1 = []; e_1 = []; n_1 = []
alt = []; t = []; qual = []; num_sats = []
ref_id = []; geo_sep = []
hdop = []; pdop = []; vdop = []; mode =[]; 
mode_type = []; sv_id01 = []; sv_id02 = []; 
sv_id03 = []; sv_id04 = []; sv_id05 = []; 
sv_id06 = []; sv_id07 = []; sv_id08 = [];
sv_id09 = []; sv_id10 = []; sv_id11 = []; sv_id12 = [];  
date = []; time_stamp = []; spd = []; true_course = [];
mag_var = []; mag_var_dir = []; lat_2 = []; lon_2 = [];
e_2 = []; n_2 = []; spd_grnd_kmh = []; spd_grnd_kts = [];
true_track = []; mag_track = []
az1 = []; az2 = []; elev_deg1 = []; elev_deg2 = []
num_sv = []; snr1 = []; snr2 = []; sv_prn1 = []; sv_prn2 = []

for k in xrange(len(raw)):
   gpgga = nmea.GPGGA(); gpgsa = nmea.GPGSA()
   gprmc = nmea.GPRMC(); gpvtg = nmea.GPVTG(); gpgsv = nmea.GPGSV()

   if raw[k].startswith('$GPGGA'):
      gpgga.parse(raw[k])

      lats = gpgga.latitude
      longs= gpgga.longitude
					
      #convert degrees,decimal minutes to decimal degrees 
      lat1 = (float(lats[2]+lats[3]+lats[4]+lats[5]+lats[6]+lats[7]+lats[8]))/60
      lat = (float(lats[0]+lats[1])+lat1)
      long1 = (float(longs[3]+longs[4]+longs[5]+longs[6]+longs[7]+longs[8]+longs[9]))/60
      long = (float(longs[0]+longs[1]+longs[2])+long1)
					
      #calc position
      lat_1.append(lat); lon_1.append(-long)
      #convert to az central state plane east/north
      e,n = trans(-long,lat)
      e_1.append(e); n_1.append(n)
        
      alt.append(gpgga.antenna_altitude)
      t.append(gpgga.timestamp); qual.append(gpgga.gps_qual)
      num_sats.append(gpgga.num_sats)
      ref_id.append(str(gpgga.ref_station_id)); geo_sep.append(gpgga.geo_sep)

   elif raw[k].startswith('$GPGSA'):
      gpgsa.parse(raw[k])

      hdop.append(gpgsa.hdop); pdop.append(gpgsa.pdop); 
      vdop.append(gpgsa.vdop); mode.append(gpgsa.mode); 
      mode_type.append(gpgsa.mode_fix_type)
      sv_id01.append(gpgsa.sv_id01); sv_id02.append(gpgsa.sv_id02)
      sv_id03.append(gpgsa.sv_id03); sv_id04.append(gpgsa.sv_id04)
      sv_id05.append(gpgsa.sv_id05); sv_id06.append(gpgsa.sv_id06)
      sv_id07.append(gpgsa.sv_id07); sv_id08.append(gpgsa.sv_id08)
      sv_id09.append(gpgsa.sv_id09); sv_id10.append(gpgsa.sv_id10)
      sv_id11.append(gpgsa.sv_id11); sv_id12.append(gpgsa.sv_id12)   

   elif raw[k].startswith('$GPRMC'):
      gprmc.parse(raw[k])

      date.append(gprmc.datestamp)
      time_stamp.append(gprmc.timestamp)
      spd.append(gprmc.spd_over_grnd)
      true_course.append(gprmc.true_course)
      mag_var.append(gprmc.mag_variation)
      mag_var_dir.append(gprmc.mag_var_dir)
            
      lats = gprmc.lat; longs= gprmc.lon
					
      #convert degrees,decimal minutes to decimal degrees 
      lat1 = (float(lats[2]+lats[3]+lats[4]+lats[5]+lats[6]+lats[7]+lats[8]))/60
      lat = (float(lats[0]+lats[1])+lat1)
      long1 = (float(longs[3]+longs[4]+longs[5]+longs[6]+longs[7]+longs[8]+longs[9]))/60
      long = (float(longs[0]+longs[1]+longs[2])+long1)
					
      #calc position
      lat_2.append(lat); lon_2.append(-long)

      #convert to az central state plane east/north
      e,n = trans(-long,lat)
      e_2.append(e); n_2.append(n)

   elif raw[k].startswith('$GPVTG'):
      gpvtg.parse(raw[k])

      true_track.append(gpvtg.true_track)
      spd_grnd_kmh.append(gpvtg.spd_over_grnd_kmph)
      spd_grnd_kts.append(gpvtg.spd_over_grnd_kts)
      mag_track.append(gpvtg.mag_track)

   elif raw[k].startswith('$GPGSV'):
      gpgsv.parse(raw[k])

      az1.append(gpgsv.azimuth_1)
      az2.append(gpgsv.azimuth_2)
      elev_deg1.append(gpgsv.elevation_deg_1)
      elev_deg2.append(gpgsv.elevation_deg_2)
      num_sv.append(gpgsv.num_sv_in_view)
      snr1.append(gpgsv.snr_1)
      snr2.append(gpgsv.snr_2)
      sv_prn1.append(gpgsv.sv_prn_num_1)
      sv_prn2.append(gpgsv.sv_prn_num_2)



from_zone = tz.tzutc()
to_zone = tz.tzlocal()

epoch_local =[]; epoch_utc = []

for k in xrange(len(date)):
   utc = datetime.strptime(date[k][:2]+' '+date[k][2:4]+' 20'+date[k][4:]+' '+time_stamp[k][:6], '%d %m %Y %H%M%S')
   utc = utc.replace(tzinfo=from_zone)
   local = utc.astimezone(to_zone)
   epoch_utc.append(calendar.timegm(utc.timetuple()))
   epoch_local.append(calendar.timegm(local.timetuple()))

csvfilename = nmeafile.split('.txt')[0]+'.csv'
f_csv = open(csvfilename, 'ab')
csvwriter = csv.writer(f_csv, delimiter=',')

csvwriter.writerow(['t','date','time_stamp','epoch_utc','epoch_local',\
                       'lat_1', 'lon_1','lat_2','lon_2',\
                       'e_1','n_1','e_2','n_2',\
                       'alt','hdop','pdop','vdop','qual','num_sats',\
                       'num_sv','snr1','snr2','sv_prn1','sv_prn2',\
                       'ref_id','geo_sep','mode','mode_type',\
                       'sv_id1','sv_id2','sv_id3','sv_id4',\
                       'sv_id5','sv_id6','sv_id7','sv_id8',\
                       'sv_id9','sv_id10','sv_id11','sv_id12',\
                       'az1','az2','elev_deg1','elev_deg2',\
                       'spd','spd_grnd_kts','spd_grnd_kmh','true_course',\
                       'mag_var','mag_var_dir','true_track','mag_track']) 

rows = zip(t,date,time_stamp,epoch_utc,epoch_local,lat_1, lon_1, lat_2, lon_2, e_1, n_1, e_2, n_2,\
           alt, hdop, pdop, vdop, qual, num_sats, num_sv, snr1, snr2, sv_prn1, sv_prn2,\
           ref_id, geo_sep, mode, mode_type, sv_id01, sv_id02, sv_id03, sv_id04,\
           sv_id05, sv_id06, sv_id07, sv_id08, sv_id09, sv_id10, sv_id11, sv_id12,\
           az1, az2, elev_deg1, elev_deg2, spd, spd_grnd_kts, spd_grnd_kmh, true_course,\
           mag_var, mag_var_dir, true_track, mag_track)
for row in rows:
    csvwriter.writerow(row)
f_csv.close()
   
# write to dictionary and save as .mat file
v = {}
for i in ('t','date','time_stamp','epoch_utc','epoch_local',\
                       'lat_1', 'lon_1','lat_2','lon_2',\
                       'e_1','n_1','e_2','n_2',\
                       'alt','hdop','pdop','vdop','qual','num_sats',\
                       'num_sv','snr1','snr2','sv_prn1','sv_prn2',\
                       'ref_id','geo_sep','mode','mode_type',\
                       'sv_id01','sv_id02','sv_id03','sv_id04',\
                       'sv_id05','sv_id06','sv_id07','sv_id08',\
                       'sv_id09','sv_id10','sv_id11','sv_id12',\
                       'az1','az2','elev_deg1','elev_deg2',\
                       'spd','spd_grnd_kts','spd_grnd_kmh','true_course',\
                       'mag_var','mag_var_dir','true_track','mag_track'):
    v[i] = locals()[i]

savemat(csvfilename.split('.csv')[0]+'_nmea.mat',v)



