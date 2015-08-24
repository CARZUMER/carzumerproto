# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 03:08:50 2015

@author: Dan

This file contains the Prototype Project

"""
from numpy import loadtxt
import web


# Designate global default values
G_DefaultZip = "90650"
G_SlopeFicoFromIncome = 0.00074811*12
G_InterceptFicoFromIncome = 657.7013707
G_LowestFicoFromIncome = 640
G_HighstFicoFromIncome = 800
G_FicoRound = 1
G_LowestIncomeFromFico = 2500
G_HighstIncomeFromFico = 7500
G_IncomeRound = 100
G_DebtPercentofIncome = 0.10
G_DebtRound = 25
G_TradeInIncomeMonths = 2.0
G_TradeInRound = 500
G_UpfrontWantedIncomeMonths = 1.0
G_LowestUpfrontWanted = 0.0
G_HighestUpfrontWanted = 5000.0
G_UpfrontMaxIncomeMonths = 2.0
G_LowestUpfrontMax = 2000.0
G_HighestUpfrontMax = 20000.0
G_UpfrontRound = 100
G_MonthlyWantedPercentofIncome = 0.08
G_LowestMonthlyWanted = 100.0
G_HighestMonthlyWanted = 2500.0
G_MonthlyMaxPercentofIncome = 0.18
G_LowestMonthlyMax = 200.0
G_HighestMonthlyMax = 5000.0
G_MonthlyRound = 10
G_TermWanted = 72


TablesDirectory = "c:\Users\Dan\Documents\CarZumer\Prototype\Python"
FnameZIP5toFICO3 = TablesDirectory + "\FICO3byZIP5_Model.csv"
TemplatesDirectory = TablesDirectory + "\Prototype\templates/"


def strRound(v, multiple=1):
    # Returns a string value of v rounded to nearest (integer) multiple
    return str(int(float(v)/multiple + 0.5) * multiple)


class byZIP (object):
    # Reads, from a file, various tables by ZIP5
    def __init__(self):
        TableIn = loadtxt(FnameZIP5toFICO3,
                          delimiter=",", dtype=str, skiprows=1)
        self.Income = {ZIP5: float(Income)/12 for
                    ZIP5, Income, FICO3byIncome, ST2, ST2offset, FICO3 in TableIn}
        self.ST2 = {ZIP5: ST2 for
                    ZIP5, Income, FICO3byIncome, ST2, ST2offset, FICO3 in TableIn}
        self.ST2offset = {ZIP5: float(ST2offset) for
                    ZIP5, Income, FICO3byIncome, ST2, ST2offset, FICO3 in TableIn}
        self.FICO3 = {ZIP5: FICO3 for
                    ZIP5, Income, FICO3byIncome, ST2, ST2offset, FICO3 in TableIn}


class UserField (object):
    # A user field has 2-elements: a value and a flag if it's a system guess
    Value = ""
    isGuess = True
    GuessBasis = "Default is Blank"

    def __init__(self, Label):
        self.Label = Label

    def __repr__(self):
        if self.isGuess:
            GuessText = "Guess - " + self.GuessBasis
        else:
            GuessText = "User Input"
        return "%s = %s [%s] " % (self.Label, self.Value, GuessText)

    def GetField(self):
        UserInput = raw_input(self)
        Updated = self
        if UserInput != "":
            Updated.Value = UserInput
            Updated.isGuess = False
        return Updated


class ConsumerInfo (object):
    # Create a class that holds the current values of user inputs
    DeliveryZip = UserField("Delivery Zip")
    Fico = UserField("FICO Score")
    Income = UserField("Monthly Gross Income")
    DebtService = UserField("Monthly Debt Service Excluding Auto")
    isHomeowner = UserField("Do You Owns Your Primary Residence Home?")
    isCosigner = UserField("Is There a Co-Signer?")
    Cosigner = UserField("FICO score of Co-Signer (if any)")
    isTradeIn = UserField("Is There a Trade-In?")
    TradeInValue = UserField("Value of Trade-In")
    TradeInPayoff = UserField("Loan Payoff for Trade-In")
    UpfrontWant = UserField("Upfront Cash Ideally")
    UpfrontMax = UserField("Maximum Available Upfront Cash")
    MonthlyWant = UserField("Monthly Payment Ideally")
    MonthlyMax = UserField("Maximum Available Monthly Payment")
    TermWant = UserField("Loan Term (months) Ideally")


    def __init__(self, OriginZip):
        self.Zip = UserField("Registration Zip")
        if OriginZip == "":
            self.Zip.Value = G_DefaultZip
            self.Zip.GuessBasis = "Global Default Zip"
        else:
            self.Zip.Value = OriginZip
            self.Zip.GuessBasis = "Origin Zip"

    def __repr__(self):
        return "%s\n"*16 % (
            self.Zip,
            self.DeliveryZip,
            self.Fico,
            self.Income,
            self.DebtService,
            self.isHomeowner,
            self.isCosigner,
            self.Cosigner,
            self.isTradeIn,
            self.TradeInValue,
            self.TradeInPayoff,
            self.UpfrontWant,
            self.UpfrontMax,
            self.MonthlyWant,
            self.MonthlyMax,
            self.TermWant
        )

    def GetInfo(self):
        # Will prompt user to update each ConsumerInfo Field
        self.Zip = self.Zip.GetField()
        self.DeliveryZip = self.DeliveryZip.GetField()
        self.Fico = self.Fico.GetField()
        self.Income = self.Income.GetField()
        self.DebtService = self.DebtService.GetField()
        self.isHomeowner = self.isHomeowner.GetField()
        self.isCosigner = self.isCosigner.GetField()
        self.Cosigner = self.Cosigner.GetField()
        self.isTradeIn = self.isTradeIn.GetField()
        self.TradeInValue = self.TradeInValue.GetField()
        self.TradeInPayoff = self.TradeInPayoff.GetField()
        self.UpfrontWant = self.UpfrontWant.GetField()
        self.UpfrontMax = self.UpfrontMax.GetField()
        self.MonthlyWant = self.MonthlyWant.GetField()
        self.MonthlyMax = self.MonthlyMax.GetField()
        self.TermWant = self.TermWant.GetField()

    def MakeGuesses(self, ZIPTable):
        # Will fill in the values for each isGuess=True field
        if self.Zip.isGuess and (not self.DeliveryZip.isGuess):
            self.Zip.Value = self.DeliveryZip.Value
            self.Zip.GuessBasis = "from ACTUAL Delivery Zip"

        if self.DeliveryZip.isGuess:
            self.DeliveryZip.Value = self.Zip.Value
            self.DeliveryZip.GuessBasis = "from Zip"

        if self.Fico.isGuess:
            if self.Income.isGuess:
                self.Fico.Value = strRound(
                                  ZIPTable.FICO3[self.Zip.Value],
                                  G_FicoRound)
                self.Fico.GuessBasis = "from Zip-based model"
            else:
                self.Fico.Value = strRound(
                                  max(G_LowestFicoFromIncome,
                                  min(G_HighstFicoFromIncome,
                                      G_SlopeFicoFromIncome *
                                      float(self.Income.Value) +
                                      G_InterceptFicoFromIncome +
                                      ZIPTable.ST2offset[self.Zip.Value])),
                                  G_FicoRound)
                self.Fico.GuessBasis = "from ACTUAL Income, offset by State"

        if self.Income.isGuess:
            if self.Fico.isGuess:
                self.Income.Value = strRound(ZIPTable.Income[self.Zip.Value],
                                             G_IncomeRound)
                self.Income.GuessBasis = "from Zip Median table"
            else:
                self.Income.Value = strRound(
                                    max(G_LowestIncomeFromFico,
                                    min(G_HighstIncomeFromFico,
                                        (float(self.Fico.Value) -
                                         ZIPTable.ST2offset[self.Zip.Value] -
                                         G_InterceptFicoFromIncome) /
                                        G_SlopeFicoFromIncome)),
                                    G_IncomeRound)
                self.Income.GuessBasis = "from ACTUAL FICO, offset by State"

        if self.DebtService.isGuess:
            self.DebtService.Value = strRound(
                                      float(self.Income.Value) *
                                      G_DebtPercentofIncome,
                                      G_DebtRound)
            self.DebtService.GuessBasis = "percent of Income"

        if self.isHomeowner.isGuess:
            self.isHomeowner.Value = "N"
            self.isHomeowner.GuessBasis = "Default is No"

        if self.isCosigner.isGuess:
            self.isCosigner.Value = "N"
            self.isCosigner.GuessBasis = "Default is No"

        if self.Cosigner.isGuess:
            if self.isCosigner.Value == "N":
                self.Cosigner.Value = ""
                self.Cosigner.GuessBasis = "There is no CoSigner"
            else:
                self.Cosigner.Value = strRound(
                                      ZIPTable.FICO3[self.Zip.Value],
                                      G_FicoRound)
                self.Cosigner.GuessBasis = "from Zip-based model"

        if self.isTradeIn.isGuess:
            if self.TradeInValue.isGuess or self.TradeInValue.Value == "":
                self.isTradeIn.Value = "N"
                self.isTradeIn.GuessBasis = "Default is No, will be updated"
            else:
                self.isTradeIn.Value = "Y"
                self.isTradeIn.GuessBasis = "An ACTUAL Trade-In Value exists"

        if self.TradeInValue.isGuess:
            if self.isTradeIn.Value == "N":
                self.TradeInValue.Value = ""
                self.TradeInValue.GuessBasis = "There is no Trade-In"
            else:
                self.TradeInValue.Value = strRound(
                                    float(self.Income.Value) *
                                    G_TradeInIncomeMonths,
                                    G_TradeInRound)
                self.TradeInValue.GuessBasis = "Months of Income"

        if self.TradeInPayoff.isGuess:
            if self.isTradeIn.Value == "N":
                self.TradeInPayoff.Value = ""
                self.TradeInPayoff.GuessBasis = "There is no Trade-In"
            else:
                self.TradeInPayoff.Value = "0"
                self.TradeInPayoff.GuessBasis = "Set to $0, will be updated"

        if self.UpfrontWant.isGuess:
            if self.UpfrontMax.isGuess:
                self.UpfrontWant.Value = strRound(
                                          max(G_LowestUpfrontWanted,
                                          min(G_HighestUpfrontWanted,
                                          float(self.Income.Value) *
                                          G_UpfrontWantedIncomeMonths)),
                                          G_UpfrontRound)
                self.UpfrontWant.GuessBasis = "Months of Income"
            else:
                self.UpfrontWant.Value = self.UpfrontMax.Value
                self.UpfrontWant.GuessBasis = "ACTUAL Upfront Maximum"

        if self.UpfrontMax.isGuess:
            if self.UpfrontWant.isGuess:
                self.UpfrontMax.Value = strRound(
                                          max(G_LowestUpfrontMax,
                                          min(G_HighestUpfrontMax,
                                          float(self.Income.Value) *
                                          G_UpfrontMaxIncomeMonths)),
                                          G_UpfrontRound)
                self.UpfrontMax.GuessBasis = "Months of Income"
            else:
                self.UpfrontMax.Value = self.UpfrontWant.Value
                self.UpfrontMax.GuessBasis = "ACTUAL Upfront Wanted"
        elif float(self.UpfrontMax.Value) <= float(self.UpfrontWant.Value):
            self.UpfrontMax.Value = self.UpfrontWant.Value
            self.UpfrontMax.isGuess = True
            self.UpfrontMax.GuessBasis = "OVER-WRITE Max to Equal Wanted"

        if self.MonthlyWant.isGuess:
            if self.MonthlyMax.isGuess:
                self.MonthlyWant.Value = strRound(
                                          max(G_LowestMonthlyWanted,
                                          min(G_HighestMonthlyWanted,
                                          float(self.Income.Value) *
                                          G_MonthlyWantedPercentofIncome)),
                                          G_MonthlyRound)
                self.MonthlyWant.GuessBasis = "Percent of Income"
            else:
                self.MonthlyWant.Value = self.MonthlyMax.Value
                self.MonthlyWant.GuessBasis = "ACTUAL Monthly Maximum"

        if self.MonthlyMax.isGuess:
            if self.MonthlyWant.isGuess:
                self.MonthlyMax.Value = strRound(
                                          max(G_LowestMonthlyMax,
                                          min(G_HighestMonthlyMax,
                                          float(self.Income.Value) *
                                          G_MonthlyMaxPercentofIncome)),
                                          G_MonthlyRound)
                self.MonthlyMax.GuessBasis = "Percent of Income"
            else:
                self.MonthlyMax.Value = self.MonthlyWant.Value
                self.MonthlyMax.GuessBasis = "ACTUAL Monthly Wanted"

        elif float(self.MonthlyMax.Value) <= float(self.MonthlyWant.Value):
            self.MonthlyMax.Value = self.MonthlyWant.Value
            self.MonthlyMax.isGuess = True
            self.MonthlyMax.GuessBasis = "OVER-WRITE Max to Equal Wanted"

        if self.TermWant.isGuess:
            self.TermWant.Value = G_TermWanted
            self.TermWant.GuessBasis = "Always defaults to 72"


class Index(object):
    def GET(self):
        return render.CarZumerBrowse(MyConsumer)

    def POST(self):
        form = web.input( V1="",  V2="",  V3="",  V4="",  V5="",
                          V6="",  V7="",  V8="",  V9="", V10="",
                         V11="", V12="", V13="", V14="", V15="",
                         V16="")
        MyConsumer.Zip.Value = form.V1
        MyConsumer.DeliveryZip.Value = form.V2
        MyConsumer.Fico.Value = form.V3
        MyConsumer.Income.Value = form.V4
        MyConsumer.DebtService.Value = form.V5
        MyConsumer.isHomeowner.Value = form.V6
        MyConsumer.isCosigner.Value = form.V7
        MyConsumer.Cosigner.Value = form.V8
        MyConsumer.isTradeIn.Value = form.V9
        MyConsumer.TradeInValue.Value = form.V10
        MyConsumer.TradeInPayoff.Value = form.V11
        MyConsumer.UpfrontWant.Value = form.V12
        MyConsumer.UpfrontMax.Value = form.V13
        MyConsumer.MonthlyWant.Value = form.V14
        MyConsumer.MonthlyMax.Value = form.V15
        MyConsumer.TermWant.Value = form.V16
        
        MyConsumer.Zip.isGuess = (MyConsumer.Zip.Value == "")
        MyConsumer.DeliveryZip.isGuess = (MyConsumer.DeliveryZip.Value == "")
        MyConsumer.Fico.isGuess = (MyConsumer.Fico.Value == "")
        MyConsumer.Income.isGuess = (MyConsumer.Income.Value == "")
        MyConsumer.DebtService.isGuess = (MyConsumer.DebtService.Value == "")
        MyConsumer.isHomeowner.isGuess = (MyConsumer.isHomeowner.Value == "")
        MyConsumer.isCosigner.isGuess = (MyConsumer.isCosigner.Value == "")
        MyConsumer.isCosigner.isGuess = (MyConsumer.isCosigner.Value == "")
        MyConsumer.isTradeIn.isGuess = (MyConsumer.isTradeIn.Value == "")
        MyConsumer.isTradeIn.isGuess = (MyConsumer.isTradeIn.Value == "")
        MyConsumer.TradeInPayoff.isGuess = (MyConsumer.TradeInPayoff.Value == "")
        MyConsumer.UpfrontWant.isGuess = (MyConsumer.UpfrontWant.Value == "")
        MyConsumer.UpfrontMax.isGuess = (MyConsumer.UpfrontMax.Value == "")
        MyConsumer.MonthlyWant.isGuess = (MyConsumer.MonthlyWant.Value == "")
        MyConsumer.MonthlyMax.isGuess = (MyConsumer.MonthlyMax.Value == "")
        MyConsumer.TermWant.isGuess = (MyConsumer.TermWant.Value == "")

        MyConsumer.MakeGuesses(byZIPTable)
        
        return render.CarZumerBrowse(MyConsumer)


# Begin Main

print "*** Start ***"
byZIPTable = byZIP()
# upload Zip tables

MyConsumer = ConsumerInfo("")
# Create a variable holding consumer information

# MyConsumer.GetInfo() # defunct code for manual input of info

# print "*** Showing MyConsumer before making guesses ***"
# print MyConsumer
MyConsumer.MakeGuesses(byZIPTable)
# print "*** Showing MyConsumer after making guesses ***"
# print MyConsumer
# print "*** Finished ***"

# Now, lets start the web app
urls = (  '/', 'Index')

app = web.application(urls, globals())

render = web.template.render('templates/', base="layout")

if __name__ == "__main__":
    app.run()