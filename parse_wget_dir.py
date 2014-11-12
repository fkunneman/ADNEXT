
from HTMLParser import HTMLParser
import sys
import codecs
import re

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    #def handle_starttag(self, tag, attrs):
    #    print "tag"
    #def handle_endtag(self, tag):
    #    print "tag"
    def handle_data(self, data):
        if not re.match(r"[ \n\t]+",data):
            print data.replace("\n","")

infile = open(sys.argv[1])

# instantiate the parser and fed it some HTML
parser = MyHTMLParser()
parser.feed(infile.read())