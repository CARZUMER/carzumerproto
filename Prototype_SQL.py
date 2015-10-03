# -*- coding: utf-8 -*-
"""
Created on Sun Sep 06 23:00:36 2015

@author: Dan

This code is for working with SQLite

"""
import sqlite3
import csv
from numpy import loadtxt


def ShowTable(TableName, cur):
    # Show table count, columns, and top 5 rows
    print "*** " + TableName + " ***"
    cur.execute("SELECT COUNT(*) FROM " + TableName)
    c = cur.fetchone()
    cur.execute("SELECT * FROM " + TableName + " LIMIT 5;")
    all = cur.fetchall()
    names = [description[0] for description in cur.description]
    print c, names
    for row in all:
        print(row)


def CSV_to_DB(DBName, TableName, FileName, delim=","):
    # Will open/create a database DBName
    # Will create/overwrite a table TableName
    # Will populate TableName with records found in FileName
    # First row of FileName contains all field names
    # All fields are strings
    TableIn = loadtxt(FileName, delimiter=delim, dtype=str,
                      comments = "loNg and unliKely stRing")
    FieldNames = TableIn[0]
    InsertString = FieldNames[0]
    CreateString = FieldNames[0] + " TEXT"
    for F in FieldNames[1:]:
        InsertString = InsertString + ", " + F
        CreateString = CreateString + ", " + F + " TEXT"
    QString = "?" + ", ?" * (len(FieldNames)-1)

    to_db = [tuple(row) for row in TableIn[1:]]

    MyDB = sqlite3.connect(DBName)
    cur = MyDB.cursor()

    cur.execute("DROP TABLE IF EXISTS " + TableName + ";")
    cur.execute("CREATE TABLE " + TableName + " (" + CreateString + ");")
    cur.executemany("INSERT INTO " + TableName +
        " (" + InsertString + ") VALUES (" + QString + ");", to_db)

    ShowTable(TableName, cur)
    """
    cur.execute("SELECT COUNT(*) FROM " + TableName)
    c = cur.fetchone()
    cur.execute("SELECT * FROM " + TableName)
    res = cur.fetchone()
    print(c, res)
    """
    MyDB.commit()
    MyDB.close()


def GoodPrice(x):
    if (x == "") or (x is None):
        return 0
    try:
        i = abs(int(x))
        return i
    except:
        return 0


def SQL_FindPrice(sSellingPrice, sMSRP, sBookValue, sInvoice,
                  sInternet_Price, sMisc_Price1, sMisc_Price2, sMisc_Price3):
    # From the 8 pricing fields, try to surmise the actual selling price
    # Any price that is blank, zero, or none-numeric is considered "bad."
    # If both Internet_Price and SellingPrice are good, use the lower of the 2
    # Otherwise, use the first good price in the following order:
    # Internet, Selling, MSRP, Book, Invoice, Misc1, Misc2, Misc3
    # Return 0 if none are good
    Internet_Price = GoodPrice(sInternet_Price)
    SellingPrice = GoodPrice(sSellingPrice)
    if (Internet_Price > 0) and (SellingPrice > 0):
        return min(Internet_Price, SellingPrice)
    if (Internet_Price > 0):
        return Internet_Price
    if (SellingPrice > 0):
        return SellingPrice
    MSRP = GoodPrice(sMSRP)
    if (MSRP > 0):
        return MSRP
    BookValue = GoodPrice(sBookValue)
    if (BookValue > 0):
        return BookValue
    Invoice = GoodPrice(sInvoice)
    if (Invoice > 0):
        return Invoice
    Misc_Price = GoodPrice(sMisc_Price1)
    if (Misc_Price > 0):
        return Misc_Price
    Misc_Price = GoodPrice(sMisc_Price2)
    if (Misc_Price > 0):
        return Misc_Price
    Misc_Price = GoodPrice(sMisc_Price3)
    if (Misc_Price > 0):
        return Misc_Price
    return 0


def SQL_FindInvoice(sSellingPrice, sMSRP, sBookValue, sInvoice,
                  sInternet_Price, sMisc_Price1, sMisc_Price2, sMisc_Price3):
    # From the 8 pricing fields, try to surmise the actual invoice price
    # Any price that is blank, zero, or none-numeric is considered "bad."
    # If Invoice is good, use it;
    # Else, if Book Value is good, use it;
    # Otherwise, use the lowest good price of the rest
    # Return 0 if none are good
    Invoice = GoodPrice(sInvoice)
    if (Invoice > 0):
        return Invoice
    BookValue = GoodPrice(sBookValue)
    if (BookValue > 0):
        return BookValue

    Internet_Price = GoodPrice(sInternet_Price)
    SellingPrice = GoodPrice(sSellingPrice)
    MSRP = GoodPrice(sMSRP)
    Misc_Price1 = GoodPrice(sMisc_Price1)
    Misc_Price2 = GoodPrice(sMisc_Price2)
    Misc_Price3 = GoodPrice(sMisc_Price3)

    MaxPrice = max (Internet_Price, SellingPrice, MSRP,
                    Misc_Price1, Misc_Price2, Misc_Price3)
    if Internet_Price == 0:
        Internet_Price = MaxPrice
    if SellingPrice == 0:
        SellingPrice = MaxPrice
    if MSRP == 0:
        MSRP = MaxPrice
    if Misc_Price1 == 0:
        Misc_Price1 = MaxPrice
    if Misc_Price2 == 0:
        Misc_Price2 = MaxPrice
    if Misc_Price3 == 0:
        Misc_Price3 = MaxPrice
    return min (Internet_Price, SellingPrice, MSRP,
                Misc_Price1, Misc_Price2, Misc_Price3)


DBFile = "static/PrototypeDB.db"
MyDB = sqlite3.connect(DBFile)
cur = MyDB.cursor()
TableName = "inventory"
MyDB.create_function("SQL_FindPrice", 8, SQL_FindPrice)
MyDB.create_function("SQL_FindInvoice", 8, SQL_FindInvoice)


# The next piece of code reads a long inventory table and transcribes it
# into two sample files tab-delimited files
if False:
    FileName = "Inventory/Inventory.txt"
    TestLong = "Inventory/InventoryLong100.txt"
    TestShort = "Inventory/InventoryShort100.txt"

    ExcludeFields = ['Description',
                     'Options',
                     'Categorized Options',
                     'Special Field 1',
                     'Special Field 2',
                     'Special Field 3',
                     'Special Field 4',
                     'ImageList']

    InFile = open(FileName)

    """
    if os.path.exists(TestLong):
        os.remove(TestLong)
    LongFile = open(TestLong, 'w')

    if os.path.exists(TestShort):
        os.remove(TestShort)
    ShortFile = open(TestShort, 'w')
    """

    FieldNames = InFile.readline().replace("\n","").split('|')
    nFields = len(FieldNames)
    LongHeader = '\t'.join(FieldNames)
    ExcludeIndexes = []
    for i in range(nFields):
        if FieldNames[i] in ExcludeFields:
            ExcludeIndexes.append(i)
    print LongHeader
    print ExcludeIndexes
    # LongFile.write(LongHeader)
    # ShortFile.write(LongHeader)

    CreateString = " ('" + "' TEXT, '".join(FieldNames) + "');\n"
    InsertString = " ('" + "' ,'".join(FieldNames) +"') VALUES "
    print "CreateString = ", CreateString
    print "InsertString = ", InsertString

    cur.execute("DROP TABLE IF EXISTS " + TableName + ";")
    cur.execute("CREATE TABLE " + TableName + CreateString)

    k = 0

    for line in InFile:
        Values = line.replace("\'", "").split('|')
        k += 1
        nValues = len(Values)
        if nValues == nFields:
            if k % 10 == 0:
                LongValues = '\t'.join(Values)
                # LongFile.write(LongValues)
            for j in ExcludeIndexes:
                Values[j] = "X"
            ShortValues = '\t'.join(Values) + '\n'
            ValueString = "( \'" + "\', \'".join(Values) + "\' ); \n"
            SQL_INSERT = "INSERT INTO " + TableName + InsertString + ValueString
            print SQL_INSERT
            cur.execute(SQL_INSERT)
            # ShortFile.write(ShortValues)
        if k>= 3: break
    InFile.close()
    # LongFile.close()
    # ShortFile.close()

    ShowTable(TableName, cur)

if False:
    # This creates the various SQL tables from CSV files
    CSV_to_DB(DBFile, "Year_Dict", "CSVs/Year_Dict.csv")
    CSV_to_DB(DBFile, "Make_Dict", "CSVs/Make_Dict.csv")
    CSV_to_DB(DBFile, "Model_Dict", "CSVs/Model_Dict.csv")
    CSV_to_DB(DBFile, "Trim_Dict", "CSVs/Trim_Dict.csv")
    CSV_to_DB(DBFile, "Option_Dict", "CSVs/Option_Dict.csv")
    CSV_to_DB(DBFile, "inventory", "CSVs/Inventory.csv")
    CSV_to_DB(DBFile, "ZipLatLon", "CSVs/ZipTables.csv")
    CSV_to_DB(DBFile, "APR", "CSVs/APR.csv")
    CSV_to_DB(DBFile, "Trim_Top", "CSVs/Trim_Top.csv")

# CSV_to_DB(DBFile, "inventory", "Inventory/InventoryShort100.txt", delim="\t")


""" Code copied from Prototype_Main to show which fields are used
       DROP TABLE IF EXISTS Inventory_Filtered1;
       CREATE TABLE Inventory_Filtered1 AS
       SELECT VIN, YEAR, MAKE, Model, Trim,
           Ext_Color_Generic AS Color,
           SellingPrice, DealerZip, Latitude, Longitude,
           Invoice, Make_STD, Model_STD,"""


if False:
    # This cleans up the Inventory file by mapping raw versions of various
    # filtered fields into clean versions (with _STD suffix)
    cur.executescript('''DROP TABLE IF EXISTS Inventory_STD;
                         CREATE TABLE Inventory_STD AS
                         SELECT *,
                         SQL_FindPrice(SellingPrice, MSRP, BookValue,
                                       Invoice, Internet_Price,
                                       Misc_Price1, Misc_Price2, Misc_Price3)
                                       AS GoodPrice,
                         SQL_FindInvoice(SellingPrice, MSRP, BookValue,
                                       Invoice, Internet_Price,
                                       Misc_Price1, Misc_Price2, Misc_Price3)
                                       AS GoodInvoice
                         FROM inventory AS I
                         LEFT JOIN Year_Dict AS Y
                             ON I.YEAR = Y.Year_Raw
                         LEFT JOIN Make_Dict AS Ma
                             ON I.Make = Ma.Make_Raw
                         LEFT JOIN Model_Dict AS Mo
                             ON I.Model = Mo.Model_Raw
                         LEFT JOIN Trim_Dict AS T
                             ON I.Trim = T.Trim_Raw
                         LEFT JOIN ZipLatLon AS Z
                             ON I.DealerZip = Z.Zip;''')

    ShowTable("Inventory_STD", cur)



if False:
    TableName = "Inventory_STD"
    print "*** " + TableName + " ***"
    cur.execute("SELECT COUNT(*) FROM " + TableName)
    c = cur.fetchone()
    print c

if False:
    # Will showcase all tables
    ShowTable("Year_Filter", cur)
    ShowTable("Make_Filter", cur)
    ShowTable("Model_Filter", cur)
    ShowTable("Trim_Filter", cur)
    ShowTable("Color_Filter", cur)
    ShowTable("ZipLatLon", cur)
    ShowTable("Inventory_STD", cur)
    ShowTable("Inventory_Filtered", cur)
    ShowTable("APR", cur)


MyDB.commit()
MyDB.close()

