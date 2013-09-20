#!/usr/bin/env python

import codecs
import re
import time_functions
import datetime

def ibt(metalines,outdir,args):
    
    future=re.compile(r"(straks|zometeen|vanmiddag|vanavond|vannacht|vandaag|morgen|morgenavond|morgenmiddag|morgenochtend|overmorgen|weekend|maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag|maandagavond|dinsdagavond|woensdagavond|donderdagavond|vrijdagavond|zaterdagavond|zondagavond|januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december|nog.+(dagen|slapen))")       
    today=re.compile(r"(straks|zometeen|vanmiddag|vanavond|vannacht|vandaag)")
    tomorrow=re.compile(r"morgen(avond|middag|ochtend)?")
    day_after_t=re.compile(r"overmorgen")
    weekend=re.compile(r"\b(weekend)\b")
    weekday=re.compile(r"(maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)(avond|middag|ochtend)?")
    weekdays=["maandag","dinsdag","woensdag","donderdag","vrijdag","zaterdag","zondag"]
    month=re.compile(r"(\d{1,2}) (januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)")
    months=["januari","februari","maart","april","mei","juni","juli","augustus","september","oktober","november","december"]
    nog=re.compile(r"nog(.+) (dagen|slapen)")
    num=re.compile(r"\b(twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achttien|negentien|twintig|eenentwintig|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21)\b")
    wordnums=["twee","drie","vier","vijf","zes","zeven","acht","negen","tien","elf","twaalf","dertien","veertien","vijftien","zestien","zeventien","achttien","negentien","twintig","eenentwintig"]
    
    estimations=[]
    meta_out = codecs.open(outdir + "meta.txt","w","utf-8")
    for i in metalines:
        meta_out.write(i)
        tokens=i.split("\t")
        text=tokens[-1]
        date=tokens[int(args[0])]
        text=text.strip()
        if future.search(text):
            if today.search(text):
                estimations.append("0")
            elif tomorrow.search(text):
                estimations.append("-1")
            elif day_after_t.search(text):
                estimations.append("-2")
            else:
                if args[1] == "dummy":
                    estimations.append("nt")
                else:
                    tweet_date=time_functions.return_datetime(date,setting="vs")
                    if weekend.search(text) or weekday.search(text):
                        tweet_weekday=tweet_date.weekday()
                        if weekend.search(text):
                            ref_weekday=weekdays.index("zaterdag")
                        elif weekday.search(text):
                            ref_weekday=weekdays.index(weekday.search(text).groups()[0])
                        if ref_weekday == tweet_weekday:
                            estimations.append("0")
                        else:
                            if tweet_weekday < ref_weekday:
                                dif=ref_weekday - tweet_weekday
                            else:
                                dif=ref_weekday + (7-tweet_weekday)
                            estimation=str(dif * -1)
                            estimations.append(estimation)
                    elif month.search(text):
                        ref=month.search(text).groups()
                        day=int(ref[0])
                        mth=months.index(ref[1]) + 1
                        tweet_month=tweet_date.month
                        tweet_year=tweet_date.year
                        if mth >= tweet_month:
                            year=tweet_year
                        else:
                            year=tweet_year + 1
                        try:
                            ref_date=datetime.datetime(year,mth,day,0,0,0)
                            tte=str(time_functions.timerel(ref_date,tweet_date,"day") * -1)
                            if int(tte) < -21:
                                tte="early"
                            estimations.append(tte)
                        except ValueError:
                            continue
                    elif nog.search(text):
                        in_between=nog.search(text).groups()[0]
                        numbers=num.findall(in_between)
                        if len(numbers) == 1:
                            number=numbers[0]
                            if re.search(r"[a-z]",number):
                                number=wordnums.index(number) + 2
                            number=str(int(number) * -1)
                            if int(number) < -21:
                                number="early"
                            estimations.append(number)
                        else:
                            estimations.append("nt")
                    else:
                        estimations.append("nt")
        else:
            estimations.append("nt")
    meta_out.close()
    if args[1] == "dummy":
        baseline_out=codecs.open(outdir + "baseline_dummy.txt","w","utf-8")
    else: 
        baseline_out=codecs.open(outdir + "baseline.txt","w","utf-8")
    baseline_out.write(" ".join(estimations))
    baseline_out.close()
