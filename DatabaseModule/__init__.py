import os
import platform
import sys

if platform.system() == 'Windows':
    sys.path.append(os.path.abspath("H:/SocialNetworkAnalyzer/DatabaseModule"))
elif platform.system() == 'Linux':
    sys.path.append(os.path.abspath("~/SocialNetworkAnalyzer/DatabaseModule"))