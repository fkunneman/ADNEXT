import sys
import matplotlib.pyplot as plt
from pylab import *

outplot = sys.argv[1]
xlabel = sys.argv[2]
ylabel = sys.argv[3]
plotfiles = sys.argv[5:]

linestyles = ['-.', '-', '--', ':']
half = len(plotfiles)/2
for i,pf in enumerate(plotfiles[:half]):
    pf_open = open(pf)
    x = []
    y = []
    for entry in pf_open.readlines():
        # generate coordinates
        tokens = entry.strip().split("\t")
        x.append(int(tokens[0]))
        if tokens[1] == "NaN":
            ytoken = NaN
        else:
            ytoken = float(tokens[1])
        y.append(ytoken)
    print x
    print y
    plt.plot(x,y,linestyle=linestyles[i])
legend = plotfiles[half:]
plt.legend(legend,loc = "upper right",ncol = 2)
plt.ylabel(ylabel)
plt.xlabel(xlabel)
# plt.ylabel("Absolute estimation error (in days)")
# plt.xlabel("Time-to-event in hours")
    #plt.title("\'Micro-f1 score at\' as event time nears")
plt.savefig(outplot)
