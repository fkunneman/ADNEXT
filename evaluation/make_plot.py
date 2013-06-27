import sys
import matplotlib.pyplot as plt

outplot = sys.argv[1]
plotfiles = sys.argv[2:]

linestyles = ['-.', '-', '--', ':']
half = len(plotfiles)/2
for i,pf in enumerate(plotfiles[:half]):
    pf_open = open(pf)
    x = []
    y = []
    for entry in pf_open.readlines():
        # generate coordinates
        tokens = entry.strip().split("\t")
        x.append(tokens[0])
        y.append(tokens[1])
    plt.plot(x,y,linestyle = linestyles[i])
legend = plotfiles[half:]
plt.legend(legend,loc = "upper right",ncol = 2)
plt.ylabel("Absolute estimation error (in days)")
plt.xlabel("Time-to-event in hours")
    #plt.title("\'Micro-f1 score at\' as event time nears")
plt.savefig(outplot)
