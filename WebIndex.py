# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 14:47:13 2015

@author: Dan
"""

import web  # This is web.py -- central to the prototype
import time
import shelve

import cfg
from APR import MyAPR
from ReadMakeModelTrim import MyMMT
from ConsumerClass import ConsumerInfo
from FilterClass import FilterArray
from VehicleClass import VehicleArray
from UserDBModule import MyUsers

AccountsData = shelve.open(cfg.ConsumersShelve)
MyConsumersTable = {}
for key in AccountsData:
    MyConsumersTable[key] = AccountsData[key]
AccountsData.close()

def IndexGet():
    # global SessionConsumer, SessionFilterArray, SessionSelections
    SessionConsumer = ConsumerInfo("")
    SessionID = SessionConsumer.ConsumerID
    SessionFilterArray = FilterArray(MyMMT)
    SessionSelections = VehicleArray(SessionFilterArray, SessionConsumer, MyAPR)
    SessionAll = (SessionConsumer, SessionFilterArray, SessionSelections)
    MyConsumersTable.update({SessionID: SessionAll} )
    return SessionAll

def IndexPost():
    form = web.input(SessionID="",
                     LogAttempt="",
                     Username="",
                     Password="",
                     VerifyPassword="",
                     eMail="",
                     Zip="",
                     UpfrontWant="",
                     UpfrontMax="",
                     MonthlyWant="",
                     MonthlyMax="",
                     TermWant="",
                     Fico="",
                     Income="",
                     DebtService="",
                     isHomeowner="",
                     isCosigner="",
                     Cosigner="",
                     isTradeIn="",
                     TradeInValue="",
                     TradeInPayoff="",
                     SubmitButton="",
                     AllCheckList=[],
                     ClearCheckList=[],
                     OtherCheckList=[],
                     DetailedCheckList=[])

    if form.SubmitButton == "ReStartPressed":
        # Will create a new customer
        return IndexGet()

    FormID = str(form.SessionID)
    tried = False
    FailureMessage = ""

    if form.LogAttempt == "Create":
        # protocol to create new account and fill it with session data
        tried = True
        FailureMessage = MyUsers.CreateUser(form.Username, form.Password, form.eMail, FormID)

    if form.LogAttempt == "Login" or FailureMessage == "LogMe":
        # Protocol to authenticate account and log in
        # If the account exists and authenticated, merge input data with old data
        # If does not exist, send problem message, offer to create account
        # if Attempt succeed, set status to loggedin
        tried = True
        PriorID = str(MyUsers.FindUser(form.Username, form.Password))
        if (PriorID != ""):
            FormID = PriorID
            FailureMessage = ""
            # TODO: Merging code may come here
        else:
            FailureMessage = "No account matches username / password combination"

    #print "FormID = ", FormID
    #print "MyConsumersTable =", MyConsumersTable

    (SessionConsumer, SessionFilterArray, SessionSelections) = \
        MyConsumersTable[FormID]

    SessionConsumer.LastAccessed = time.time()
    SessionConsumer.LastAccessedTimeStamp = time.asctime()

    if tried and FailureMessage == "":
        SessionConsumer.loggedIn = "Y"
        SessionConsumer.username = form.Username
        SessionConsumer.Message = "Succesfully logged in"
        AccountsData = shelve.open(cfg.ConsumersShelve)
        AccountsData[FormID] = MyConsumersTable[FormID]
        AccountsData.close()
        return MyConsumersTable[FormID]


    SessionConsumer.Message = FailureMessage

    FoundFocus = False
    AvailFocus = True

    SessionConsumer.Zip, FoundFocus, AvailFocus =  \
        SessionConsumer.Zip.UpdateField(form.Zip, FoundFocus, AvailFocus)
    SessionConsumer.UpfrontWant, FoundFocus, AvailFocus =  \
        SessionConsumer.UpfrontWant.UpdateField(form.UpfrontWant, FoundFocus, AvailFocus)
    SessionConsumer.UpfrontMax, FoundFocus, AvailFocus =  \
        SessionConsumer.UpfrontMax.UpdateField(form.UpfrontMax, FoundFocus, AvailFocus)
    SessionConsumer.MonthlyWant, FoundFocus, AvailFocus =  \
        SessionConsumer.MonthlyWant.UpdateField(form.MonthlyWant, FoundFocus, AvailFocus)
    SessionConsumer.MonthlyMax, FoundFocus, AvailFocus =  \
        SessionConsumer.MonthlyMax.UpdateField(form.MonthlyMax, FoundFocus, AvailFocus)
    SessionConsumer.TermWant, FoundFocus, AvailFocus =  \
        SessionConsumer.TermWant.UpdateField(form.TermWant, FoundFocus, AvailFocus)

    SessionConsumer.Fico, FoundFocus, AvailFocus =  \
        SessionConsumer.Fico.UpdateField(form.Fico, FoundFocus, AvailFocus)
    SessionConsumer.Income, FoundFocus, AvailFocus =  \
        SessionConsumer.Income.UpdateField(form.Income, FoundFocus, AvailFocus)
    SessionConsumer.DebtService, FoundFocus, AvailFocus =  \
        SessionConsumer.DebtService.UpdateField(form.DebtService, FoundFocus, AvailFocus)
    SessionConsumer.Cosigner, FoundFocus, AvailFocus =  \
        SessionConsumer.Cosigner.UpdateField(form.Cosigner, FoundFocus, AvailFocus)

    SessionConsumer.TradeInValue, FoundFocus, AvailFocus =  \
        SessionConsumer.TradeInValue.UpdateField(form.TradeInValue, FoundFocus, AvailFocus)
    SessionConsumer.TradeInPayoff, FoundFocus, AvailFocus =  \
        SessionConsumer.TradeInPayoff.UpdateField(form.TradeInPayoff, FoundFocus, AvailFocus)

    SessionConsumer.isHomeowner, FoundFocus, AvailFocus =  \
        SessionConsumer.isHomeowner.UpdateField(form.isHomeowner, FoundFocus, AvailFocus)
    SessionConsumer.isCosigner, FoundFocus, AvailFocus =  \
        SessionConsumer.isCosigner.UpdateField(form.isCosigner, FoundFocus, AvailFocus)
    SessionConsumer.isTradeIn, FoundFocus, AvailFocus =  \
        SessionConsumer.isTradeIn.UpdateField(form.isTradeIn, FoundFocus, AvailFocus)

    SessionConsumer.Zip.isFocus = AvailFocus

    SessionConsumer.MakeGuesses()

    # Code to unpack the AllCheckList
    for AvailableFilter in SessionFilterArray.Filter:
        isCheckAll = AvailableFilter in form.AllCheckList
        isCheckClear = AvailableFilter in form.ClearCheckList
        SessionFilterArray.Filter[AvailableFilter].isFocus = \
            isCheckAll or isCheckClear
        SessionFilterArray.Filter[AvailableFilter].isOther = \
            isCheckAll or (not(isCheckClear) and \
            AvailableFilter in form.OtherCheckList)
        # Code to unpack the DetailedCheckList
        for AvailableChoice in SessionFilterArray.Filter[AvailableFilter].Choices:
            SessionFilterArray.Filter[AvailableFilter].Choices[AvailableChoice] = \
            isCheckAll or (not(isCheckClear) and \
            (AvailableFilter + " " + AvailableChoice) in form.DetailedCheckList)

    SessionFilterArray.Filter["3Model"] = SessionFilterArray.FixModel(MyMMT)
    SessionFilterArray.Filter["4Trim"] = SessionFilterArray.FixTrim(MyMMT)

    # Code to serach the database for matching entries
    SessionSelections = VehicleArray(SessionFilterArray, SessionConsumer, MyAPR)

    SessionAll = (SessionConsumer, SessionFilterArray, SessionSelections)
    MyConsumersTable[FormID] = SessionAll
    if SessionConsumer.loggedIn == "Y":
        AccountsData = shelve.open(cfg.ConsumersShelve)
        AccountsData[FormID] = SessionAll
        AccountsData.close()

    return SessionAll