import os
import platform
import sys

if platform.system() == 'Windows':
    sys.path.append(os.path.abspath("H:/twitterAnalyzer/CrawlingModule"))
elif platform.system() == 'Linux':
    sys.path.insert(0, os.path.abspath(".."))
    sys.path.append(os.path.abspath("~/twitterAnalyzer/CrawlingModule"))