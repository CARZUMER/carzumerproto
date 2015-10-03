# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 06:12:10 2015

@author: Dan
"""


import sqlite3  # This is the SQL engine in use.
import cfg
from StringClean import isNull, fixNull, fixZero, float0, strRound


class APRTable (object):
    # Reads, from database, a table of APR by FICO, LTV, and Term
    # There is only one member of this class (MyAPR)
    # MyAPR is initialized once (at startup), and is then used many times
    # Two dictionaries are available: APRGrid and MonthlyGrid
    # APRGrid is a dictionary from the 3-tuplet of (FICO, LTV, Term) to APR
    # Each of the 3 quantities is on an equispaced grid.
    # The class elements LowFico, HighFico, and StepFico define the gridpoints
    #   (Likewise LowLTV, HighLTV and StepLTV; and LowTerm, HighTerm, StepTerm)
    # For example, MyAPR.APRGrid[(690, 0.9, 72)] will provide the APR for
    #   a 72 months term loan at 90% LTV to a FICO 690 borrower
    # Similarly, MonthlyGrid will provide the monthly payment (as a percentage
    #   of loan amount) for a given FICO-LTV-Term tuplet
    # The Methods GetAPR and GetMonthly will return the APR and Monthly,
    #   respectively, for any numeric FICO and LTV; even if not on the grid.
    #   (Term must always be on the grid)
    # For example: MyAPR.GetAPR(711, 0.92, 60) will provide the APR for a
    #    60 months term loan at 90% LTV to a FICO 710 borrower.
    # Both methods return 0 for erroneous and unfixable parameters
    def __init__(self):
        MyDB = sqlite3.connect(cfg.FnameDB)
        cur = MyDB.cursor()
        MyScript = """SELECT FICO, LTV, Term, APR, Monthly
                      FROM APR;"""
        cur.execute(MyScript)
        Results = cur.fetchall()
        MyDB.commit()
        MyDB.close()
        self.APRGrid = {(0, 0, 0): 0}
        self.MonthlyGrid = {(0, 0, 0): 0}
        self.LowFico = int(Results[0][0])
        self.HighFico = self.LowFico
        self.StepFico = 1000
        self.LowLTV = int(Results[0][1])
        self.HighLTV = self.LowLTV
        self.StepLTV = 1000
        self.LowTerm = int(Results[0][2])
        self.HighTerm = self.LowTerm
        self.StepTerm = 1000

        for row in Results:
            Fico = int(row[0])
            LTV = int(row[1])
            Term = int(row[2])
            APR = float(row[3])
            Monthly = float(row[4])
            self.APRGrid.update({(Fico, LTV, Term): APR})
            self.MonthlyGrid.update({(Fico, LTV, Term): Monthly})
            self.HighFico = max(self.HighFico, Fico)
            self.HighLTV = max(self.HighLTV, LTV)
            self.HighTerm = max(self.HighTerm, Term)
            if Fico > self.LowFico:
                self.StepFico = min(self.StepFico, Fico - self.LowFico)
            if LTV > self.LowLTV:
                self.StepLTV = min(self.StepLTV, LTV - self.LowLTV)
            if Term > self.LowTerm:
                self.StepTerm = min(self.StepTerm, Term - self.LowTerm)

    def CleanDeal(self, sFICO, pLTV, sTerm):
        # This function will clean up the sFICO, pLTV, and sTerm
        # parameters, so they can be used to find APR and Monthly payment
        # If uncleanable, return 0-0-0; else, return Fico-LTV-Term
        # The returned values will correspond to a grid point on the
        # tabulated APRGrid and MonthlyGrid dictionaries
        try:
            if isNull(sFICO):
                FICO = self.LowFico
            else:
                FICO = max(self.LowFico, min(self.HighFico, float(sFICO)))
                FICO = int(round((FICO - self.LowFico)/self.StepFico) *
                            self.StepFico + self.LowFico)

            LTV = max(self.LowLTV, min(self.HighLTV, 100.0 * pLTV))
            LTV = int(round((LTV - self.LowLTV)/self.StepLTV) *
                        self.StepLTV + self.LowLTV)

            Term = int(fixNull(sTerm, cfg.TermWanted))
            if (Term < self.LowTerm) or (Term > self.HighTerm) or \
                ( (Term - self.LowTerm) % self.StepTerm != 0):
                    return (0, 0, 0)

            return (FICO, LTV, Term)
        except ValueError:
            return (0, 0, 0)
        except:
            print "Unexpected error in CleanDeal:"
            print "sFICO = " + str(sFICO)
            print "pLTV = " + str(pLTV)
            print "sTerm = " + str(sTerm)
            raise

    def GetAPR(self, sFICO, pLTV, sTerm):
        # Returns the tabulated APR for a prospective loan
        # Will return 0 for error conditions (uncleanable inputs)
        return self.APRGrid[self.CleanDeal(sFICO, pLTV, sTerm)]

    def GetMonthly(self, sFICO, pLTV, sTerm):
        # Returns the tabulated Monthly payment for a prospective loan
        #   (as a percentage of loan amount)
        # Will return 0 for error conditions (uncleanable inputs)
        return self.MonthlyGrid[self.CleanDeal(sFICO, pLTV, sTerm)]


MyAPR = APRTable()
