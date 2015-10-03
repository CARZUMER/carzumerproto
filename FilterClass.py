# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 06:50:13 2015

@author: Dan
"""

import cfg
from ReadMakeModelTrim import MyMMT

class SearchFilter(object):
    # Create a class that holds one serach filter
    isGuess = True
    isFocus = False
    isOther = False
    GuessBasis = "Default is Check-All"

    def __init__(self, TableLabel):
        self.Choices = {}
        self.TableLabel = TableLabel

    def __repr__(self):
        if self.isGuess:
            GuessText = "Guess - " + self.GuessBasis
        else:
            GuessText = "User Selection"
        return "%s = %s Other:%s [%s] " % \
            (self.TableLabel, self.Choices, self.isOther, GuessText)


class FilterArray(object):
    # Creates a class that holds the entire array of search filters
    Filter = {"1Year": SearchFilter("Year"),
              "2Make": SearchFilter("Make"),
              "3Model": SearchFilter("Model"),
              "4Trim": SearchFilter("Trim"),
              "5Color": SearchFilter("Ext_Color_Generic"),
              "6Options": SearchFilter("Options"),
              "7Filter1": SearchFilter("F1"),
              "8Filter2": SearchFilter("F2")
              }

    Filter["1Year"].Choices.update({"2012": True, "2013": True, "2014": True})
    Filter["5Color"].Choices.update({"Black": True,
                                    "White": True,
                                    "Silver": True,
                                    "Gray": True,
                                    "Red": True,
                                    "Blue": True,
                                    "Brown": True
                                    })

    def __init__(self, MMList,
                 DMake=cfg.DefaultMake,
                 DModel=cfg.DefaultModel,
                 DTrim=cfg.DefaultTrim):
        for AvailableMake in MMList.MakesDict.keys():
            self.Filter["2Make"].Choices.update({AvailableMake: False})
        self.Filter["2Make"].Choices[DMake] = True
        self.Filter["2Make"].isGuess = True
        self.Filter["2Make"].GuessBasis = "Default is one popular Make checked"
        self.Filter["3Model"].Choices[DModel] = True
        self.Filter["3Model"] = self.FixModel(MMList)
        self.Filter["3Model"].isGuess = True
        self.Filter["3Model"].GuessBasis = "Default is one popular Model checked"
        self.Filter["4Trim"].Choices[DTrim] = True
        self.Filter["4Trim"] = self.FixTrim(MMList)
        self.Filter["4Trim"].isGuess = True
        self.Filter["4Trim"].GuessBasis = "Default is one popular Trim checked"

    def __repr__(self):
        Outstring = ""
        for FilterName in self.Filter:
            Outstring = Outstring + str(self.Filter[FilterName]) + "\n"
        return Outstring

    def FixModel(self, MMList):
        # Update the Models Filter Choices in light of the selected Makes
        # 1. Create a new Model Filter
        # 2. Loop through all selected Makes
        #       2A. For each Make, loop through all available models
        #           2Aa. Create entry in new Model filter for model
        #           2Ab. If Model exist in original Model filer, copy checkbox
        #           2Ab. If not, set checkbox to FALSE
        NewModelFilter = SearchFilter("Model")
        for CheckedMake in self.Filter["2Make"].Choices:
            if self.Filter["2Make"].Choices[CheckedMake]:
                for AvailableModel in MMList.MakesDict[CheckedMake]:
                    NewModelFilter.Choices.update({AvailableModel:
                        self.Filter["3Model"].Choices.get(AvailableModel, False) })
        NewModelFilter.isOther = self.Filter["3Model"].isOther
        return NewModelFilter

    def FixTrim(self, MMList):
        # Update the Trims Filter Choices in light of the selected Models
        # 1. Create a new Trim Filter
        # 2. Loop through all selected Makes
        #       2A. For each checked Make, loop through all selected Models
        #           2Aa. Construct MMKey = 'MAKE(MODEL)'
        #           2Ab. Loop through all Trims for MMKey
        #               2Abi. Create entry in new Trim filter for trim
        #               2Abii. If trim exist in original trim filer, copy checkbox
        #               2Abiii. If not, set checkbox to FALSE
        NewTrimFilter = SearchFilter("Trim")
        for CheckedMake in self.Filter["2Make"].Choices:
            if self.Filter["2Make"].Choices[CheckedMake]:
                for AvailableModel in MMList.MakesDict[CheckedMake]:
                    if self.Filter["3Model"].Choices.get(AvailableModel, False):
                        MMKey = CheckedMake + '(' + AvailableModel + ')'
                        for AvailableTrim in MMList.ModelsDict[MMKey]:
                            NewTrimFilter.Choices.update({AvailableTrim:
                                self.Filter["4Trim"].Choices.get(AvailableTrim, False)})
        NewTrimFilter.isOther = self.Filter["4Trim"].isOther
        return NewTrimFilter


#MyFilterArray = FilterArray(MyMMT)
#MyFilterArray0 = MyFilterArray