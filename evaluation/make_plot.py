import sys
import matplotlib.pyplot as plt
from pylab import *

plottype = sys.argv[1]
outplot = sys.argv[2]
xlabel = sys.argv[3]
ylabel = sys.argv[4]
plotfiles = sys.argv[5:]

if plottype == "line":
    linestyles = ["-","--","-.",":"]
    half = len(plotfiles)/2
    for i,pf in enumerate(plotfiles[:half]):
        pf_open = open(pf)
        x = []
        y = []
        for entry in pf_open.readlines():
            # generate coordinates
            tokens = entry.strip().split("\t")
            x.append(float(tokens[0]))
            if tokens[1] == "NaN":
                ytoken = NaN
            else:
                ytoken = float(tokens[1])
            y.append(ytoken)
        print x
        print y
        plt.plot(x,y,linestyle=linestyles[i],linewidth=4,)
    legend = plotfiles[half:]
    plt.legend(legend,loc = "upper right",ncol = 2,bbox_to_anchor=(1.1, 1.2))

elif plottype == "hist":
    pf_open = open(plotfiles[0])
    y = []
    for entry in pf_open.readlines():
        # generate coordinates
        tokens = entry.strip().split("\t")
        ytoken = float(tokens[1])
        y.append(ytoken)
    bins = range(min(y),max(y),5)
    plt.hist(y,bins)

plt.ylabel(ylabel)
plt.xlabel(xlabel)
# plt.ylabel("Absolute estimation error (in days)")
# plt.xlabel("Time-to-event in hours")
    #plt.title("\'Micro-f1 score at\' as event time nears")
plt.savefig(outplot,bbox_inches="tight")
