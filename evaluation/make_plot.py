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
yrange_lowest = int(sys.argv[6])
yrange_highest = int(sys.argv[7])
sort = sys.argv[8]
legend = int(sys.argv[9])
plotfiles = sys.argv[10:]

if plottype[:4] == "line":
    linestyles = ["-","--","-.",":"]
    d = 1
    if legend:
        d = 2
    half = int(len(plotfiles)/d)
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
        if plottype[4:] == "range":
            x = range(len(x))
        plt.plot(x,y,linestyle=linestyles[i],linewidth=lw)
        if sort == "nosort":
            plt.gca().invert_xaxis()
#pos = np.arange(len(x))
        #    plt.xticks(xpos,x)
    plt.ylim((yrange_lowest,yrange_highest))
    if legend:
        legend = plotfiles[half:]
        plt.legend(legend,loc = "lower right")
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off') # labels along the bottom edge are off
    #plt.ylim(top=1)

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
    #plt.ylim(0,20)

elif plottype == "bar":
    pf_open = open(plotfiles[0])
    x = []
    y = []
    for line in pf_open.readlines():
        tokens = line.strip().split("\t")
        x.append(tokens[0])
        y.append(float(tokens[1]))
    x_pos = np.arange(len(x))
    plt.bar(x_pos,y,align="center")
    plt.xticks(x_pos, x)

plt.ylabel(ylabel)
plt.xlabel(xlabel)
# plt.ylabel("Absolute estimation error (in days)")
# plt.xlabel("Time-to-event in hours")
    #plt.title("\'Micro-f1 score at\' as event time nears")
plt.savefig(outplot,bbox_inches="tight")
