import matplotlib.pyplot as plt
import csv

t = []
x = []
y = []

with open('res.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for row in plots:
        t.append(int(row[0]))
        x.append(float(row[1]))
        y.append(float(row[2]))

axes = plt.gca()
axes.set_xlim([t[0],t[-1]])
axes.set_ylim([min(min(x),min(y))*1.1,max(max(x),max(y))*1.1])
plt.plot(t,x, label='VoltageDAC')
plt.plot(t,y, label='VoltageADC')
plt.xlabel('Time(ms)')
plt.ylabel('Voltage(V/Vin')
plt.title('Current, voltage vs time')
plt.legend()
plt.show()
