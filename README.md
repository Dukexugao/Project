# Gui Project

Gui Application Project\
Functions:
1. Real-time operational dashboard for debt collection performance  (Code Uploaded)
2. Search engine for one specific account or placement (Code Uploaded)
3. Debt portfolio pricing including legal filtering, status scrubs, cost structuring, payer prediction and liquidation estimate        (Code Not Uploaded)



Pyinstaller(3.2.1) bugs fix:\
  1.No module named 'pandas.__libs.tslibs.timedeltas'\
    (1)Locate PyInstaller folder..\hooks\
    (2)Create file hook-pandas.py with contents : hiddenimports = ['pandas.__libs.tslibs.timedeltas'] 

  2.'Could not find QtWebEngineProcess.exe.' Error \
    https://github.com/pyinstaller/pyinstaller/pull/2514/files#diff-254d289fadd12387346b09de164c9321R26
