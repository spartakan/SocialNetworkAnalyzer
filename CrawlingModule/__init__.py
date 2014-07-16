import os
import platform
import sys

if platform.system() == 'Windows':
    sys.path.append(os.path.abspath("H:/twitterAnalyzer"))
elif platform.system() == 'Linux':
    sys.path.insert(0,os.path.abspath("/home/sd/twitterAnalyzer"))
    print "SYS PATH : ",sys.path
    #sys.path.append(os.path.abspath("~/twitterAnalyzer"))
