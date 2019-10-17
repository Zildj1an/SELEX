import matplotlib.pyplot as plt
import csv

t = []
t1 = []
t2 = []
x = []
x1 = []
x2 = []
y1 = []
y2 = []

with open('res.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    last = -1
    for row in plots:
        t.append(float(row[0]))
        x.append(float(row[1]))
        if(last == int(row[0])):
            continue
        if(int(row[0]) % 10 < 4 and int(row[0]) % 10 > 2):
            t1.append(int(row[0]))
            y1.append(1000*float(row[2]))
            x1.append(float(row[1]))
        elif(int(row[0]) % 10 < 8 and int(row[0]) % 10 > 6):
            t2.append(int(row[0]))
            y2.append(1000*float(row[2]))
            x2.append(float(row[1]))
        last = int(row[0])

y3 = [(a-b) for a,b in zip(y1,y2)]

#axes = plt.gca()
#axes.set_xlim([t1[0],t1[-1]])
#pmax = max(max(x),max(y1))
#pmin = min(min(x),min(y1))
#width = pmax - pmin
#axes.set_ylim([pmin - 0.1*width, pmax + 0.1*width])
plt.plot(x1,y1,'go',label='VoltageUp(mV)',ms=0.5)
plt.plot(x2,y2,'ro',label='VoltageDown(mV)',ms=0.5)
#plt.plot(t2[:len(y3)],y3,label='Difference(mV)')
#plt.plot(t,x,label='VoltageDAC(V)')
plt.plot(x2[:len(y3)],y3,'bo',label='Pato plz', ms=0.5)
plt.xlabel('Voltage')
plt.ylabel('Current diff')
plt.title('Current vs Voltage')
plt.legend()
plt.show()
