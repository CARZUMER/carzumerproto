# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 05:03:41 2015

@author: Dan


Protocol to upload to PythonAnywhere
------------------------------------

1. In origin machine, zip together the static and templates directories and
    the file Prototype_Main.py
    Name the zipped file "Prototype.zip" (replacing any prior such file)
2. Go to PythonAnywhere login page:  https://www.pythonanywhere.com/login/
    USERNAME = dshoham@carzumer.com  /  PASSWORD = carzumer
3. Click FILES (top left)
4. Upload the file "Prototype.zip" from the main directory
5. Press the "DASHBOARD" link (upper right)
6. Click CONSOLES
7. Kill all active consoles (under YOUR CONSOLES:)
8. Click Bash
     A console will open with a ~ $ prompt.
9. Type: "unzip Prototype.zip"
     A long series of "inflating: ... " lines will appear
     If you are asked "replace [something]? respond "A" (for All)
10. Type "python Prototype_Main.py"
    This will start the service and print out various SQL code
11. Click "DASHBOARD" (again)
12. Click WEB
13. Press the big green button "RELOAD".  This should do it!
14. Go to danshoham.pythonanywhere.com to see it live

Protocol to upload to GitHub
----------------------------

[TODO]

"""
