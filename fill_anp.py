import multiprocessing
import sys
import os
import datetime
from datetime import date, timedelta, datetime
import time_functions

outdir_logs = sys.argv[1]
outdir_files = sys.argv[2]

dates = []
current_date = date(2000,11,7)
end_date = date(2004,8,20)
while current_date <= end_date:
    crawl_date = str(current_date.day) + "-" + str(current_date.month) + "-" + str(current_date.year)
    write_date = str(current_date.year) + "-" + str(current_date.month) + "-" + str(current_date.day)
    dates.append((crawl_date,write_date))
    current_date += timedelta(days=1)

for date in dates:
    print date
    os.system("wget -w 0.5 -v --user=f.kunneman@let.ru.nl --password=crawl2014 -i http://portal.anp.nl/rss/indexer.do?action=importview\&sourceId=1\&day=" + date[0] + " -o " + outdir_logs + date[1] + " -O " + outdir_files + date[1])
