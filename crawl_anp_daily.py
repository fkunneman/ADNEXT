import multiprocessing
import sys
import os
import datetime
from datetime import date, timedelta, datetime

outdir_logs = sys.argv[1]
outdir_files = sys.argv[2]

t = date.today()
cur = "-".join([str(t.day),str(t.month),str(t.year)])

os.system("wget -v --user=f.kunneman@let.ru.nl --password=crawl2013 -w 0.1 -i http://portal.anp.nl/rss/indexer.do?action=importview\&sourceId=1\&day=" + cur + " -o " + outdir_logs + cd + " -O " + outdir_files + cd)
