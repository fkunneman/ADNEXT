from __future__ import division
import sys
import matplotlib.pyplot as plt
from pylab import *
from numpy import arange

plottype = sys.argv[1]
lw = int(sys.argv[2])
outplot = sys.argv[3]
xlabel = sys.argv[4]
ylabel = sys.argv[5]
plotfiles = sys.argv[6:]

if plottype[:4] == "line":
    linestyles = ["-","--","-.",":"]
    half = int(len(plotfiles)/2)
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
        if plottype[4:] == "range":
            x = range(len(x))
        plt.plot(x,y,linestyle=linestyles[i],linewidth=lw)
    legend = plotfiles[half:]
    plt.legend(legend,loc = "upper right",ncol = 2,bbox_to_anchor=(1.1, 1.2))

elif plottype == "hist":
    pf_open = open(plotfiles[0])
    y = []
    for entry in pf_open.readlines():
        # generate coordinates
        tokens = entry.strip().split("\t")
        ytoken = float(tokens[0])
        y.append(ytoken)
    d = (max(y) - min(y)) / 6
    b = arange(min(y),max(y) + d,d)
    print b
    plt.hist(y,bins=b)
    plt.ylim(0,20)

plt.ylabel(ylabel)
plt.xlabel(xlabel)
# plt.ylabel("Absolute estimation error (in days)")
# plt.xlabel("Time-to-event in hours")
    #plt.title("\'Micro-f1 score at\' as event time nears")
plt.savefig(outplot,bbox_inches="tight")
