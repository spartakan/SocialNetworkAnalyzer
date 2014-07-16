import os
import platform
import sys

if platform.system() == 'Windows':
    sys.path.append(os.path.abspath("H:/twitterAnalyzer/CrawlingModule"))
elif platform.system() == 'Linux':
    sys.path.append(os.path.abspath("~/twitterAnalyzer/CrawlingModule"))