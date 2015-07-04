# Daniel Buscombe, Oct 24 2014
# convert xlsx sandcam spreadsheet into re-formatted csv
import xlrd
import numpy as np
import csv

xlsxfile = 'SandCam_photoinfo_edited_db.xlsx'
book = xlrd.open_workbook(xlsxfile)

# get the first worksheet
first_sheet = book.sheet_by_index(0) 

# read first row , parse to variable 'headers'
headers = first_sheet.row_values(0)

# create container D to hold all data 
D = [[] for x in xrange(len(headers))]

# dump each column into array 'cells'
# then dump all values as numpy array into D
counter = 0
for v in range(len(headers)):
   cells = first_sheet.col_slice(colx=v)
   cells = cells[1:] # remove header value
   d = []
   for cell in cells:
      d.append(str(cell.value))
   D.append(np.asarray(d))
   counter +=1

# remove any empty cells in list D
D = [x for x in D if x != []]

# get dictionary object of headers
v = dict((header,0) for header in headers)

# so this ugly bit of code is needed to fill dict with correct order of values
# assigns value to correct spreadsheet header
counter = 0
a = v.keys()
for k in a:
   for vv in headers:
      if vv==k:
         v[k] = D[counter]
         try:
            v[k] = np.asarray(v[k],dtype=np.float)
         except:
            pass
         counter = 0
         break
      else:
         counter=counter+1

# get unique sites - 1 line per site
Sites = np.unique(v['RM'])

csvout = xlsxfile+'.csv'
#create csv file and append headers
f_csv = open(csvout, 'ab')
csvwriter = csv.writer(f_csv, delimiter=',')
csvwriter.writerow(['RM','SandCam','Site Name','Plot No',\
                       'Plot', 'image_1', 'image_2',\
                       'image_3','image_4','image_5','image_6'])

for k in range(len(Sites)):
   rows = np.where(v['RM'] == Sites[k])[0]
   plots = np.unique(v['Plot'][rows])

   for i in range(len(plots)):
      v['Photo #'][rows[np.where(v['Plot'][rows]==plots[i])[0]]]

      # allow up to 6 images
      images = np.zeros(6)*np.nan
      im_nos = np.where(v['Plot'][rows]==plots[i])[0]
      images[:len(im_nos)] = v['Photo #'][rows[im_nos]]
      # RM, sandcam, site name, plot number, plot, photos 
      tmp = [Sites[k], v['SandCam'][rows[np.where(v['Plot'][rows]==plots[i])[0]]][0], v['Site Name'][rows[np.where(v['Plot'][rows]==plots[i])[0]]][0], v['Plot_No'][rows[np.where(v['Plot'][rows]==plots[i])[0]]][0], plots[i], images[0],images[1],images[2],images[3],images[4],images[5]]
      # write line to csv file
      csvwriter.writerow(tmp)

f_csv.close()




