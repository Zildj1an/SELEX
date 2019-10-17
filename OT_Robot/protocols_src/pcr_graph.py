import requests
from matplotlib import pyplot as plt
from time import sleep

def graph(url, type='pcr'):

    plot_l, plot_b, plot_z = [0], [0], [0]

    plt.ion()

    while True:

        response = requests.get(url)
        status = {k:v for k,v in [x.split('=') for x in response.text[23:-6].split('&')]}

        plt.cla()
        
        plt.axis([0, 100, 0, 150])

        if len(plot_b) > 99:
            if type == 'pcr':
                plot_l = plot_l[50:]
            plot_b = plot_b[50:]
            plot_z = plot_z[50:]

        
        if type == 'pcr':
            plot_l += [float(status['l'])]
        plot_b += [float(status['b'])]
        plot_z += [float(status['z'])]

        if type == 'pcr':
            plt.plot(plot_l, label='lid')
        plt.plot(plot_b, label='base')
        plt.plot(plot_z, label='sample')

        plt.xlabel(f'{status["s"]} - {status["p"] if "p" in status.keys() else ""} {"| Remaining time: " + status["r"] if "r" in status.keys() else ""}')

        plt.legend()
        
        plt.show()

        plt.pause(0.1)
        
        sleep(3)

        
