# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 05:57:56 2015

@author: Dan
"""

import sqlite3 # This is the SQL engine in use.
import cfg
from StringClean import isNull, fixNull, fixZero, float0, strRound

class byZIP (object):
    # Reads, from a database, various tables by ZIP5
    # There is only one member of this class (MyZip)
    # MyZip is initialized once (at startup), and is then used many times
    # Each table is turned into a dictionary, with the ZIP as the key
    # and the look-up value as the value.
    # After initialization, calling MyZip.TableName[ZipCode] will return
    # the table look-up for that zip code.
    # For example:  MyZip.ST2['92024'] will return 'CA' (the US state)
    # The tables are:
    #   Income  -- median income
    #   ST2     -- 2 letter US state
    #   ST2Offset--The number of FICO points that state is above (or below,
    #              when negative) above the modeled number for its median
    #              income.  (Used to calculate FICO guess from income)
    #   FICO3   -- The modeled FICO guess for the Zip (used for FICO guess)
    #   Latitude, Longitude -- Geodesic coordinates of the zip code (used to
    #                          compute distances from dealers to consumers)
    #   TaxRate -- Sales tax rate in effect
    #   TradeInTaxCredit -- 1 for states that give Sales Tax Credit for Trade-
    #                       In's, 0 for states that do not
    def __init__(self):
        MyDB = sqlite3.connect(cfg.FnameDB)
        cur = MyDB.cursor()
        MyScript = """SELECT ZIP, Income, state, ST2Offset, FICO3,
                          Latitude, Longitude, SalesTax, TradeInTaxCredit
                      FROM ZipLatLon;"""
        cur.execute(MyScript)
        Results = cur.fetchall()
        MyDB.commit()
        MyDB.close()
        self.Income = {}
        self.ST2 = {}
        self.ST2offset = {}
        self.FICO3 = {}
        self.Latitude = {}
        self.Longitude = {}
        self.TaxRate = {}
        self.TradeInTaxCredit = {}
        for row in Results:
            self.Income.update({row[0]: float0(row[1])/12})
            self.ST2.update({row[0]: row[2]})
            self.ST2offset.update({row[0]: float0(row[3])})
            self.FICO3.update({row[0]: row[4]})
            self.Latitude.update({row[0]: row[5]})
            self.Longitude.update({row[0]: row[6]})
            self.TaxRate.update({row[0]: row[7]})
            self.TradeInTaxCredit.update({row[0]: row[8]})


MyZip = byZIP()
