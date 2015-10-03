# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 06:12:54 2015

@author: Dan
"""

import sqlite3 # This is the SQL engine in use.
import cfg
from StringClean import isNull, fixNull, fixZero, float0, strRound


class TrimTop (object):
    # Reads, from a database, The list of all Make-Model-Trim combinations
    # There is only one member of this class (MMList)
    # MMList is initialized once (at startup), and is then used many times
    # A global setting cfg.TrimTopPct (80%) determines which combination will
    #   be incorporated into the menus (all others will fall under "others")
    #   This is to prevent the menues from being cluttered with rare choices
    # In the database, field "CUM_PCT_NEW" provides the prevalence of each
    #   Make-Model-Trim combination.  If it is <= 80%, the combination is
    #   sufficiently common to generate menue choices for the consumer
    # The class generates two dictionaries: MakesDict and ModelsDict
    # The MakesDict dictionary provides a mapping from the Make to an array of
    #   Models.  Only Makes common enough to meet the threshold have entries,
    #   and only common-enough Models are represented in the array.
    #   For example: MMList.MakesDict['HYUNDAI'] returns ['ACCENT', 'AZERA' , 'ELANTRA', 'SONATA']
    # Likewise, the ModelsDict dictionary provides a mapping from each
    #   represented Make-Model combination (represented as MAKE(MODEL) ) to an
    #   array of represented Trims.
    #   For example: MMList.ModelsDict['HYUNDAI(ELANTRA)'] returns ['', 'GLS PZEV', 'LIM PZEV']
    def __init__(self):

        MyDB = sqlite3.connect(cfg.FnameDB)
        cur = MyDB.cursor()
        MyScript = """SELECT NUMBER, STD_MAKE, STD_MODEL, STD_TRIM,
                          COUNT_NEW, COUNT_ALL, PCT_NEW, CUM_PCT_NEW
                      FROM Trim_Top;"""
        cur.execute(MyScript)
        Results = cur.fetchall()
        MyDB.commit()
        MyDB.close()

        self.MakesDict = {}
        self.ModelsDict = {}

        for TrimRow in Results:
            try:
                Number = str(TrimRow[0])
                STD_Make = str(TrimRow[1])
                STD_Model = str(TrimRow[2])
                STD_Trim = str(TrimRow[3])
                Count_New = str(TrimRow[4])
                Count_All = str(TrimRow[5])
                Pct_New = str(TrimRow[6])
                sPct_Cum = str(TrimRow[7])
                MakeMod = STD_Make + "(" + STD_Model +")"
                Pct_Cum = float(sPct_Cum)
            except ValueError:
                Pct_Cum = 2
            except:
                print "Unexpected error in TrimTop:"
                print "Number = " + Number
                print "STD_Make = " + STD_Make
                print "STD_Model = " + STD_Model
                print "STD_Trim = " + STD_Trim
                print "Count_New = " + Count_New
                print "Count_All = " + Count_All
                print "Pct_New = " + Pct_New
                print "sPct_Cum = " + sPct_Cum
                print "MakeMod = " + MakeMod
                raise

            if Pct_Cum <= cfg.TrimTopPct:
                if STD_Make not in self.MakesDict:
                    self.MakesDict[STD_Make] = []
                if STD_Model not in self.MakesDict[STD_Make]:
                    self.MakesDict[STD_Make].append(STD_Model)
                if MakeMod not in self.ModelsDict:
                    self.ModelsDict[MakeMod] = []
                if STD_Trim not in self.ModelsDict[MakeMod]:
                    self.ModelsDict[MakeMod].append(STD_Trim)


MyMMT = TrimTop()

