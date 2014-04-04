import multiprocessing
import sys
import os
import datetime
from datetime import date, timedelta, datetime
import time_functions

datefile = open(sys.argv[1])
outdir_logs = sys.argv[2]
outdir_files = sys.argv[3]

datelines = datefile.readlines()
begin_date = time_functions.return_datetime(datelines[0].strip())
end_date = begin_date + timedelta(days=230)
datefile.close()

dates = []
current_date = begin_date
while current_date <= end_date:
    crawl_date = str(current_date.day) + "-" + str(current_date.month) + "-" + str(current_date.year)
    write_date = str(current_date.year) + "-" + str(current_date.month) + "-" + str(current_date.day)
    dates.append((crawl_date,write_date))
    current_date += timedelta(days=1)
date_out = open(sys.argv[1],"w")
new_date = end_date + timedelta(days=1)
datewrites = []
for i,st in enumerate([new_date.day,new_date.month]):
    if len(str(st)) == 1:
        datewrites.append("0" + str(st))
    else:
        datewrites.append(str(st))
date_out.write(datewrites[0] + "-" + datewrites[1] + "-" + str(new_date.year))
date_out.close()

for date in dates:
    os.system("wget -w 0.5 -v --user=f.kunneman@let.ru.nl --password=crawl2014 -i http://portal.anp.nl/rss/indexer.do?action=importview\&sourceId=1\&day=" + date[0] + " -o " + outdir_logs + date[1] + " -O " + outdir_files + date[1])
