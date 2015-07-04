# parse_eyeballcsv.py
# written by Daniel Buscombe, May 2014
# while at
# Grand Canyon Monitoring and Research Center, U.G. Geological Survey, Flagstaff, AZ 
# please contact:
# dbuscombe@usgs.gov
# program to convert raw 'eyedaq.py' csv output file
# into a csv file with values one row per station

# import libraries
from tkFileDialog import askopenfilename 
import sys, csv
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
from collections import Counter

# function to calculate mode value per station
def station_mode(st,d,index):
   out = []
   for j in st:
      tmp = []
      for k in j:
         tmp.append(d[index][k])
      tmp2 = Counter(tmp)
      out.append(tmp2.most_common(1)[0][0])
   return out

# function to calculate mean value per station
def station_average(st,d,index):
   out = []
   for j in st:
      tmp = []
      for k in j:
         tmp.append(d[index][k])
      out.append(reduce(lambda x, y: x + y, tmp) / len(tmp))
   return out
   
# this does all the work
def parser(csvfile):

   try:
      # open csv and get only headers (1st row)
      with open(csvfile, 'rb') as f:
         mycsv = csv.reader(f)
         v = mycsv.next()
      f.close()

      # these will be field names - replace spaces with underscores
      vnew = [];
      for k in xrange(len(v)):
         vnew.append(v[k].replace(' ','_'))
   
      # create a new list the length of vnew
      del v
      d = [[] for x in xrange(len(vnew)+1)]

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

      # find column of station
      index = [i for i, s in enumerate(vnew) if 'station' in s][0]
      uniq_st = list(sorted(set(d[index]))) # find unique values of station

      counter=0
      # find rows associated with each station
      st = [[] for x in xrange(len(uniq_st))]
      for k in d[index]:
         for j in xrange(len(uniq_st)):
            if k==uniq_st[j]:
               st[j].append(counter)
               counter = counter+1

      #date
      index = [i for i, s in enumerate(vnew) if 'date' in s][0]
      dates = station_average(st,d,index)

      #times
      index = [i for i, s in enumerate(vnew) if 'time' in s][1]
      times = station_average(st,d,index)

      #lats
      index = [i for i, s in enumerate(vnew) if 'latitude_1' in s][0]
      lats = station_average(st,d,index)
      if len(str(lats[0]))<10:
         index = [i for i, s in enumerate(vnew) if 'latitude_2' in s][0]
      lats = station_average(st,d,index)

      #lons
      index = [i for i, s in enumerate(vnew) if 'longitude_1' in s][0]
      lons = station_average(st,d,index)

      #e
      index = [i for i, s in enumerate(vnew) if 'easting_1' in s][0]
      e = station_average(st,d,index)

      #n
      index = [i for i, s in enumerate(vnew) if 'northing_1' in s][0]
      n = station_average(st,d,index)

      #alt
      index = [i for i, s in enumerate(vnew) if 'altitude' in s][0]
      alt = station_average(st,d,index)

      #dep
      index = [i for i, s in enumerate(vnew) if 'depth_(m)' in s][0]
      dep = station_average(st,d,index)

      # early versions of eyedaq had a mistake in how wrote to file
      # the following bit of code corrects this
      if lats[0]<0:
         lats, lons = lons, lats
         #e
         index = [i for i, s in enumerate(vnew) if 'easting_1' in s][0]+1
         e = station_average(st,d,index)
         #n
         index = [i for i, s in enumerate(vnew) if 'northing_1' in s][0]+1
         n = station_average(st,d,index)
         #alt
         index = [i for i, s in enumerate(vnew) if 'altitude' in s][0]+1
         alt = station_average(st,d,index)
         #dep
         index = [i for i, s in enumerate(vnew) if 'depth_(m)' in s][0]+1
         dep = station_average(st,d,index)

      #bed code
      index = [i for i, s in enumerate(vnew) if 'bed_code' in s][0]
      code = station_mode(st,d,index)

      #index for images
      index = [i for i, s in enumerate(vnew) if 'Image' in s][0]

      # output file name
      csvout = csvfile.split('.csv')[0]+'_site_av.csv'
      #create csv file and append headers
      f_csv = open(csvout, 'ab')
      csvwriter = csv.writer(f_csv, delimiter=',')
      csvwriter.writerow(['station','date','time','bed code',\
                       'latitude', 'longitude','easting 1','northing 1',\
                       'altitude','depth_m','image_1', 'image_2',\
                       'image_3','image_4','image_5','image_6',\
                       'image_7','image_8','image_9','image_10'])
                       
      #cycle through each station
      for k in xrange(len(st)):
         tmp = [int(uniq_st[k]),int(dates[k]),int(times[k]),int(code[k]),\
                       lats[k],lons[k],e[k],n[k],alt[k],dep[k]]
         for j in xrange(len(st[k])):
            tmp.append(d[index][j])
         csvwriter.writerow(tmp)

      f_csv.close()   
      print "data parsed to %s" % (csvout)      
   except:
      print "no data in %s" % (csvfile)
         
# start program
if __name__ == '__main__':   
   
   # open csv file
   tk.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
   csvfiles = askopenfilename(filetypes=[("IMU file","*.csv")], multiple=True)

   for csvfile in csvfiles:
      parser(csvfile)






