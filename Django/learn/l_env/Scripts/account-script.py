#!c:\mediaspider\django\learn\l_env\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'account==0.1.0','console_scripts','account'
__requires__ = 'account==0.1.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('account==0.1.0', 'console_scripts', 'account')()
    )
