# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 07:18:56 2015

@author: Dan
"""


import sqlite3 # This is the SQL engine in use.
import math # needed for trigonometric computations in geo-distance functions
import cfg
from StringClean import isNull, fixNull, fixZero, float0, strRound
from APR import MyAPR
#from ConsumerClass import SessionConsumer
#from FilterClass import SessionFilterArray


class OneVehicle(object):
    # A member of this class is a vehicle available for sale
    # FieldNames is an ordered list of Fields describing the Vehicle
    # Properties is a dictionary from each FieldName to it's value
    def __init__(self, FieldNames, FieldValues):
        self.Properties = {}
        for i in range(len(FieldNames)):
            self.Properties.update({FieldNames[i]: FieldValues[i]})
        self.FieldNames = FieldNames

    def __repr__(self):
        Outstring = "[* "
        for Property in self.FieldNames:
            Outstring = Outstring + Property + ": " + \
                        str(self.Properties[Property]) + " "
        return Outstring + "*]"


class VehicleArray(object):
    # This is an array of all Vehciles that passed the filter

    def __init__(self, FilterArray, SessionConsumer, MyAPR):
        HardArray, SoftArray = \
            FetchFilteredInventory(FilterArray, SessionConsumer, MyAPR)
        FieldNames = GetFieldsNames("Inventory_Hard")
        self.HardVehicles = []
        for FetchedVehicle in HardArray:
            self.HardVehicles.append(OneVehicle(FieldNames, FetchedVehicle))
        self.SoftVehicles = []
        for FetchedVehicle in SoftArray:
            self.SoftVehicles.append(OneVehicle(FieldNames, FetchedVehicle))

    def __repr__(self):
        Outstring = "Hard Filtered Vehicles:\n"
        for HardVehicle in self.HardVehicles:
            Outstring = Outstring + str(HardVehicle) + "\n"
        Outstring = Outstring + "Soft Filtered Vehicles:\n"
        for SoftVehicle in self.SoftVehicles:
            Outstring = Outstring + str(SoftVehicle) + "\n"
        return Outstring


def GetFieldsNames(TableName):
        MyDB = sqlite3.connect(cfg.FnameDB)
        cur = MyDB.cursor()
        cur.execute("SELECT * FROM " + TableName + " LIMIT 1;")
        Results = [description[0] for description in cur.description]
        MyDB.commit()
        MyDB.close()
        return Results


def FetchFilteredInventory(FilterArray, SessionConsumer, MyAPR):
        # Code to serach the inventory database for matching entries
        MyDB = sqlite3.connect(cfg.FnameDB)
        cur = MyDB.cursor()
        MyDB.create_function("SQL_BestSellingPrice", 2, SQL_BestSellingPrice)
        MyDB.create_function("SQL_BestInvoicePrice", 3, SQL_BestInvoicePrice)
        MyDB.create_function("SQL_Distance", 4, SQL_Distance)
        MyDB.create_function("SQL_SalesTax", 4, SQL_SalesTax)
        MyDB.create_function("SQL_Transport", 1, SQL_Transport)
        MyDB.create_function("SQL_CashCost", 3, SQL_CashCost)
        MyDB.create_function("SQL_FindAPR", 8, SQL_FindAPR)
        MyDB.create_function("SQL_FindMonthly", 8, SQL_FindMonthly)
        MyDB.create_function("SQL_FindDown", 8, SQL_FindDown)

        MyScript1 = """
           DROP TABLE IF EXISTS Inventory_Filtered1;
           CREATE TABLE Inventory_Filtered1 AS
           SELECT I.*,
           CashCost AS Down0,
           0 AS Monthly0,
           DownWant AS Down1,
           SQL_FindMonthly(SellingPrice, Invoice, CashCost,
                                           TradeIn, Payoff,
                                           DownWant, Fico, TermWant) AS Monthly1,
           DownMax AS Down2,
           SQL_FindMonthly(SellingPrice, Invoice, CashCost,
                                           TradeIn, Payoff,
                                           DownMax, Fico, TermWant) AS Monthly2,
           SQL_FindDown(SellingPrice, Invoice, CashCost,
                                      TradeIn, Payoff,
                                      MonthlyWant, Fico, TermWant) AS Down3,
           MonthlyWant AS Monthly3,
           SQL_FindDown(SellingPrice, Invoice, CashCost,
                                          TradeIn, Payoff,
                                          MonthlyMax, Fico, TermWant) AS Down4,
           MonthlyMax AS Monthly4,
           0 as Down5,
           SQL_FindMonthly(SellingPrice, Invoice, CashCost,
                                           TradeIn, Payoff,
                                           '0', Fico, TermWant) AS Monthly5
           FROM
           (SELECT *,
           SQL_Transport(DistanceMiles) AS TransportCost,
           SQL_CashCost(BestSellingPrice, DistanceMiles, SalesTax) AS CashCost

           FROM
           (SELECT *,
           SQL_Distance(DealerLatitude, DealerLongitude,
                ConsumerLatitude, ConsumerLongitude) AS DistanceMiles,

           SQL_SalesTax(BestSellingPrice, TaxRate,
                TradeInValue, TradeInTaxCredit) AS SalesTax

           FROM
           (SELECT VIN, YEAR, MAKE, Model, Trim,
           Year_STD, Make_STD, Model_STD, Trim_STD,
           Ext_Color_Generic AS Color,
           SellingPrice, Invoice,
           CAST(ABS(RANDOM() % 10000) AS TEXT) AS RandomNumber,
           DealerZip,
           Latitude,
           Longitude,
           Latitude AS DealerLatitude,
           Longitude AS DealerLongitude,
           SQL_BestSellingPrice(SellingPrice, Invoice) AS BestSellingPrice,
           """ + \
           SessionConsumer.Latitude.Value + " AS ConsumerLatitude, \n" + \
           SessionConsumer.Longitude.Value + " AS ConsumerLongitude, \n" + \
           SessionConsumer.TaxRate.Value + " AS TaxRate, \n\'" + \
           SessionConsumer.TradeInValue.Value + "\' AS TradeInValue, \n" + \
           SessionConsumer.TradeInTaxCredit.Value + " AS TradeInTaxCredit, \n\'" + \
           SessionConsumer.Fico.Value + "\' AS Fico, \n" + \
           SessionConsumer.UpfrontWant.Value + " AS DownWant, \n" + \
           SessionConsumer.UpfrontMax.Value + " AS DownMax, \n" + \
           SessionConsumer.MonthlyWant.Value + " AS MonthlyWant, \n" + \
           SessionConsumer.MonthlyMax.Value + " AS MonthlyMax, \n\'" + \
           SessionConsumer.TermWant.Value + "\' AS TermWant, \n\'" + \
           SessionConsumer.TradeInValue.Value + "\' AS TradeIn, \n\'" + \
           SessionConsumer.TradeInPayoff.Value + """\' AS Payoff

           FROM Inventory_STD))) AS I\n """

        HardFilter =   MakeFilterSQLTable(cur, FilterArray,
                           "Year_Filter", "Year_In", "Year_STD", "1Year") + \
                       MakeFilterSQLTable(cur, FilterArray,
                           "Make_Filter", "Make_In", "Make_STD", "2Make") + \
                       MakeFilterSQLTable(cur, FilterArray,
                           "Model_Filter", "Model_In", "Model_STD", "3Model") + \
                       MakeFilterSQLTable(cur, FilterArray,
                           "Trim_Filter", "Trim_In", "Trim_STD", "4Trim") + \
                       MakeFilterSQLTable(cur, FilterArray,
                           "Color_Filter", "Color_In", "Color", "5Color") + \
                       " WHERE BestSellingPrice >= " + \
                        cfg.LowestValidSellingPrice + "\n"

        SoftFilter = " WHERE Down4 <= DownMax and BestSellingPrice >= " + \
                        cfg.LowestValidSellingPrice + "\n"

        HardOrder =   " \n ORDER BY CashCost ASC LIMIT 25; \n"

        SoftOrder =   " \n ORDER BY RandomNumber LIMIT 25; \n "

        HardDestination = """ DROP TABLE IF EXISTS Inventory_Hard;
                           CREATE TABLE Inventory_Hard AS """

        SoftDestination = """ DROP TABLE IF EXISTS Inventory_Soft;
                           CREATE TABLE Inventory_Soft AS """

        MyScript2 = """ SELECT *,
                           '' as APR0,
                           SQL_FindAPR(SellingPrice, Invoice, CashCost,
                                       TradeIn, Payoff, Down1, Fico, TermWant) AS APR1,
                           SQL_FindAPR(SellingPrice, Invoice, CashCost,
                                       TradeIn, Payoff, Down2, Fico, TermWant) AS APR2,
                           SQL_FindAPR(SellingPrice, Invoice, CashCost,
                                       TradeIn, Payoff, Down3, Fico, TermWant) AS APR3,
                           SQL_FindAPR(SellingPrice, Invoice, CashCost,
                                       TradeIn, Payoff, Down4, Fico, TermWant) AS APR4,
                           SQL_FindAPR(SellingPrice, Invoice, CashCost,
                                       TradeIn, Payoff, Down5, Fico, TermWant) AS APR5

                       FROM Inventory_Filtered1 """

        HardFilterScript = MyScript1 + HardFilter + HardOrder + \
                             HardDestination + MyScript2 + HardOrder

        SoftFilterScript = MyScript1 + SoftFilter + SoftOrder + \
                            SoftDestination + MyScript2 + SoftOrder

        print "HardFilterScript = "
        print HardFilterScript

        print "SoftFilterScript = "
        print SoftFilterScript

        cur.executescript(HardFilterScript)
        cur.execute("SELECT * FROM Inventory_Hard LIMIT " +
                    str(cfg.SelectionsShown))
        HardResults = cur.fetchall()


        cur.executescript(SoftFilterScript)
        cur.execute("SELECT * FROM Inventory_Soft LIMIT " +
                    str(cfg.SelectionsShown))
        SoftResults = cur.fetchall()

        MyDB.commit()
        MyDB.close()
        return HardResults, SoftResults


def MakeFilterSQLTable(cur, FilterArray,
                       TableName, FieldName, InventoryField, FilterName):
    # With an already opened SQL database (pointed to by cur),
    # Create a table with one field, listing all checked filter options
    cur.execute("DROP TABLE IF EXISTS " + TableName)
    cur.execute("CREATE TABLE " + TableName + "(" + FieldName + " TEXT);")
    AnyChecked = False
    for AvailableChoice in FilterArray.Filter[FilterName].Choices:
        AnyChecked = AnyChecked or \
                     FilterArray.Filter[FilterName].Choices[AvailableChoice]
    if AnyChecked:
        for AvailableChoice in FilterArray.Filter[FilterName].Choices:
            if FilterArray.Filter[FilterName].Choices[AvailableChoice]:
                cur.execute("INSERT INTO " + TableName + "(" + FieldName +
                            ") VALUES (\'" + AvailableChoice + "\');")
        Results = "INNER JOIN " + TableName + " ON I." + InventoryField +\
                  " = " + TableName + "." + FieldName + "\n"
    else:
        Results = ""
    return Results


def SQL_Distance(slat1, slon1, slat2, slon2):
    # Find the Geo-distance between two pairs of latitude and longitude coords
    # Logic: Great Circle formula on a spherical Earth
    if isNull(slat1) or isNull(slon1) or isNull(slat2) or isNull(slon2):
           return ""
    try:
        lat1 = float(slat1)
        lon1 = float(slon1)
        lat2 = float(slat2)
        lon2 = float(slon2)
        R = 3956 # Earth Radius in miles
        dLat = math.radians(lat2 - lat1) # Convert Degrees 2 Radians
        dLon = math.radians(lon2 - lon1)
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)
        a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        Results = R * c
        return str(int(round(Results)))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_Distance:"
        print "slat1 = " + str(slat1)
        print "slon1 = " + str(slon1)
        print "slat2 = " + str(slat2)
        print "slon2 = " + str(slon2)
        raise


def SQL_BestSellingPrice(sSellingPrice, sInvoice):
    # Data Cleaning process to ascertain the vehcile selling price
    # Logic: If SellingPrice is clean and >0, use it
    #       Else, if Invoice is clean, use it,
    #       Else, use "0" (for lack of a better alternative)
    try:
        Results = float(fixZero(sSellingPrice, fixZero(sInvoice, 0)))
        return int(round(Results))
    except ValueError:
        return 0
    except:
        print "Unexpected error in SQL_SalesTax:"
        print "sSellingPrice = " + str(sSellingPrice)
        print "sInvoice = " + str(sInvoice)
        raise


def SQL_BestInvoicePrice(sSellingPrice, sInvoice, iCashCost):
    # Data Cleaning process to ascertain the vehcile Invoice price
    # Logic: If Inmvoice is clean and >0, use it
    #       Else, if SellingPrice is clean, use it,
    #       Else, use CashCost (for lack of a better alternative)
    try:
        Results = float(fixZero(sInvoice, fixZero(sSellingPrice, iCashCost)))
        return str(int(round(Results)))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_SalesTax:"
        print "sSellingPrice = " + str(sSellingPrice)
        print "sInvoice = " + str(sInvoice)
        print "iCashCost = " + str(iCashCost)
        raise


def SQL_SalesTax(sBestSellingPrice, sTaxRate, sTradeIn, sTradeInCredit):
    # Find the actual ($ amount) of sales tax on a prospective transaction
    # In some states, the sales tax applies the the entire selling price,
    #   whereas in others, it only applies to the difference between the
    #   purchase price of the new vehicle and Trade-in value
    #   The parameter sTradeInCredit is 0 for the former and 1 for the latter
    # Logic: SalesTax = TaxRate * (SellingPrice - TradeIn * TradeInCredit)
    #           (SalesTax is never negative)
    try:
        Results = max( 0, float0(sTaxRate) * \
                  (float0(sBestSellingPrice) - \
                   float0(sTradeIn) * float0(sTradeInCredit) ) )
        return str(int(round(Results)))
    except ValueError:
        return "0"
    except:
        print "Unexpected error in SQL_SalesTax:"
        print "sBestSellingPrice = " + str(sBestSellingPrice)
        print "sTaxRate = " + str(sTaxRate)
        print "sTradeIn = " + str(sTradeIn)
        print "sTradeInCredit = " + str(sTradeInCredit)
        raise


def SQL_Transport(sDistance):
    # Find the cost of transporting a vehicle between two pairs of coords
    # Logic: Apply Transport Cost Model to find $ cost as function of distance
    #        Transport Cost Model uses two seperate straight-line fits:
    #        A short distance fit (under 600 miles) and a long distance one
    #        Global variables supply the intercept and slope for each fit
    try:
        Distance = float0(sDistance)
        if Distance < cfg.ShippingBreakPoint:
            Results = cfg.ShippingLowIntercept + cfg.ShippingLowSlope * Distance
        else:
            Results = cfg.ShippingHighIntercept + cfg.ShippingHighSlope * Distance
        return str(int(round(Results)))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_Transport:"
        print "sDistance = " + str(sDistance)
        raise


def SQL_CashCost(sBestSellingPrice, sDistance, sTax):
    # Find the Cash Cost of a vehicle
    # Logic: CashCost = SellingPrice + Transport + SalesTax
    #       Transport is computed using SQL_Transport() from coords
    #       SalesTax is computed using SQL_SalesTax() from price, tradeIn, Rate
    try:
        TransportCost = float0(fixZero(SQL_Transport(sDistance), cfg.ShippingMissing))
        SalesTax = float0(sTax)
        SellingPrice = float0(sBestSellingPrice)
        Results = SellingPrice + TransportCost + SalesTax
        return int(round(Results))
    except ValueError:
        return 0
    except:
        print "Unexpected error in SQL_CashCost:"
        print "sBestSellingPrice = " + str(sBestSellingPrice)
        print "sDistance = " + str(sDistance)
        print "sTax = " + str(sTax)
        raise


def SQL_FindAPR(sSellingPrice, sInvoice, iCashCost, sTradeIn, sPayoff, fDownCash, sFico, sTerm):
    # Find the APR for a given DownCash figure
    # Logic: LoanAmount = Price - [ DownCash + TradeIn - TradeInPayoff ]
    #        LTV = LoanAmount / Invoice
    #        Use LTV and FICO to find APR in the APR table
    global GlobalAPR
    try:
        Invoice = float(fixZero(sInvoice, fixZero(sSellingPrice, iCashCost)))
        if Invoice == 0:
            return "0"
        TradeInNet = float0(sTradeIn) - float0(sPayoff)
        DownPayment = float0(fDownCash) + TradeInNet
        LoanAmount = iCashCost - DownPayment
        LTV = LoanAmount / Invoice
        sFico = fixNull(sFico, str(cfg.LowestFicoAnywhere))
        Results = MyAPR.GetAPR(sFico, LTV, sTerm)
        return str(Results)
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_FindAPR:"
        print "sSellingPrice = " + str(sSellingPrice)
        print "sInvoice = " + str(sInvoice)
        print "iCashCost = " + str(iCashCost)
        print "sTradeIn = " + str(sTradeIn)
        print "sPayoff = " + str(sPayoff)
        print "fDownCash = " + str(fDownCash)
        print "sFico = " + str(sFico)
        print "sTerm = " + str(sTerm)
        raise


def SQL_FindMonthly(sSellingPrice, sInvoice, iCashCost, sTradeIn, sPayoff, fDownCash, sFico, sTerm):
    # Find required MonthlyPayments for a given DownCash figure
    # Logic: LoanAmount = Price - [ DownCash + TradeIn - TradeInPayoff ]
    #        LTV = LoanAmount / Invoice
    #        Use LTV and FICO to find [Monthly%] in the M72 table
    #        The M72 tables incorporates the active APR grid
    #        Monthly% is the Monthly payment as a % of LoanAmount
    #        MonthlyPayment = [Monthly%] * LoanAmount
    try:
        Invoice = float(fixZero(sInvoice, fixZero(sSellingPrice, iCashCost)))
        if Invoice == 0:
            return "0"
        TradeInNet = float0(sTradeIn) - float0(sPayoff)
        DownPayment = float0(fDownCash) + TradeInNet
        LoanAmount = iCashCost - DownPayment
        LTV = LoanAmount / Invoice
        sFico = fixNull(sFico, str(cfg.LowestFicoAnywhere))
        Results = MyAPR.GetMonthly(sFico, LTV, sTerm) * LoanAmount
        return int(round(Results))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_FindMonthly:"
        print "sSellingPrice = " + str(sSellingPrice)
        print "sInvoice = " + str(sInvoice)
        print "iCashCost = " + str(iCashCost)
        print "sTradeIn = " + str(sTradeIn)
        print "sPayoff = " + str(sPayoff)
        print "fDownCash = " + str(fDownCash)
        print "sFico = " + str(sFico)
        print "sTerm = " + str(sTerm)
        raise


def SQL_FindDown(sSellingPrice, sInvoice, iCashCost, sTradeIn, sPayoff, fMonthly, sFico, sTerm):
    # Find required DownCash for a given MonthlyPayment figure
    # This is the reverse of SQL_DealUpfront()
    # Note: This one is tricky, since APR computation requires knowing LTV,
    #       but LTV is driven by DownCash -- which is the solution we seek
    #       It is assumed that APR is monotone increasing with LTV
    #
    # Logic: Try each LTV granularity possibility starting with the lowest LTV
    #       The list length is the number of LTV granulations (=17)
    #       For each LTV in the list:
    #           Use FICO and LTV to find [Monthly%] in the M72 Table
    #           LoanAmount = MonthlyPayment / [%Monthly]
    #           ConsequentLTV = LoanAmount / Invoice
    #           If ConsequentLTV > LTV, not a solution; continue to next LTV
    #       If reached highest LTV, and still not a solution; use highest LTV
    #       Once a solution is found (or using highest):
    #           DownCash = Price - LoanAmount - [TradeIn - TradeInPayoff]
    try:
        Invoice = float(fixZero(sInvoice, fixZero(sSellingPrice, iCashCost)))
        if Invoice == 0:
            return "0"
        TradeInNet = float0(sTradeIn) - float0(sPayoff)
        Monthly = float0(fMonthly)
        sFico = fixNull(sFico, str(cfg.LowestFicoAnywhere))

        NeedSolution = True
        TryLTV = MyAPR.LowLTV
        while TryLTV <= MyAPR.HighLTV and NeedSolution:
            LoanAmount = Monthly / MyAPR.GetMonthly(sFico, TryLTV, sTerm)
            NeedSolution = (LoanAmount / Invoice) > TryLTV
            TryLTV += MyAPR.StepLTV

        Results = iCashCost - LoanAmount - TradeInNet
        return int(round(Results))
    except ValueError:
        return ""
    except:
        print "Unexpected error in SQL_FindDown:"
        print "sSellingPrice = " + str(sSellingPrice)
        print "sInvoice = " + str(sInvoice)
        print "iCashCost = " + str(iCashCost)
        print "sTradeIn = " + str(sTradeIn)
        print "sPayoff = " + str(sPayoff)
        print "fMonthly = " + str(fMonthly)
        print "sFico = " + str(sFico)
        raise


#MySelections = VehicleArray(SessionFilterArray, SessionConsumer, MyAPR)
#MySelections0 = MySelections