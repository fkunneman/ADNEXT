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
end_date = begin_date + timedelta(days=10)
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
date_out.write(str(new_date.day) + "-" + str(new_date.month) + "-" + str(new_date.year))

for date in dates:
    os.system("wget -w 0.1 -v --user=f.kunneman@let.ru.nl --password=crawl2013 -i http://portal.anp.nl/rss/indexer.do?action=importview\&sourceId=1\&day=" + date[0] + " -o " + outdir_logs + date[1] + " -O " + outdir_files + date[1])
