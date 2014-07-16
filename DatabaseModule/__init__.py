import os
import platform
import sys

if platform.system() == 'Windows':
    sys.path.append(os.path.abspath("H:/twitterAnalyzer/DatabaseModule"))
elif platform.system() == 'Linux':
    sys.path.append(os.path.abspath("~/twitterAnalyzer/DatabaseModule"))