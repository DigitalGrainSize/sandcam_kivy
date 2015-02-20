
hca = 327.286
nav_e = 0.0
nav_n = 0.0
nav_z = 0.0

with open('C:\Users\User\Desktop\capture.txt') as f:
   last = f.readline().split('\r')[-2]
   
f.close()
print last

last = last.split('99=')[1]

if ~last.startswith('     -1'):
   sd = float(last.split(';')[0].lstrip())/1000
   ha = 0.0009*float(last.split(';')[1].lstrip())/10
   va = 0.0009*float(last.split(';')[2].lstrip())/10

ha = (ha - hca) % 360

from math import cos, sin

Za = va*0.0174532925

n = nav_n + sd * sin(Za) * cos(ha*0.0174532925)

z = nav_z + sd * cos(Za)

e = nav_e + sd * sin(Za) * sin(ha*0.0174532925)








