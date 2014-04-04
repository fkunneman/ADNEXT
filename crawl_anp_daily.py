import multiprocessing
import sys
import os
import datetime
from datetime import date, timedelta, datetime

outdir_logs = sys.argv[1]
outdir_files = sys.argv[2]

t = date.today()
cur = "-".join([str(t.day),str(t.month),str(t.year)])
cur_out = str(t.year) + "-" + str(t.month) + "-" + str(t.day)

os.system("wget -v --user=f.kunneman@let.ru.nl --password=crawl2014 -w 0.1 -i http://portal.anp.nl/rss/indexer.do?action=importview\&sourceId=1\&day=" + cur + " -o " + outdir_logs + cur_out + " -O " + outdir_files + cur_out)