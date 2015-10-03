# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 05:48:37 2015

@author: Dan
"""


# Functions to clean Inputs
# -------------------------


def isNull(v):
    return (v == "") or (v == None)


def fixNull(v, fix=""):
    if isNull(v):
        return fix
    else:
        return v


def fixZero(v, fix=""):
    if isNull(v) or (str(v) == "0"):
        return fix
    else:
        return v


def float0(s):
    if (s == "") or (s == None) or (s == "#N/A") or (s == "."):
        return 0
    else:
        try:
            return max(0, float(s))
        except ValueError:
            return 0
        except:
            print "Unexpected Error in float0:"
            print "s = " + str(s)
            raise


def strRound(v, multiple=1, minimum=0, maximum=1000000):
    # Returns a string value of v rounded to nearest (integer) multiple
    # This function is used when guesses are made.  Since consumer selections
    # are always stored as strings, the value is converted out of its string
    # form, rounded, and converted back.
    # Will return blank for error conditions
    if isNull(v): return ""
    try:
        numeric = int(float(v)/multiple + 0.5) * multiple
        if (numeric >= minimum) and (numeric <= maximum):
            return str(numeric)
        else:
            return ""
    except ValueError:
        return ""
    except:
        print "Unexpected error in strRound:"
        print "v = " + str(v)
        print "multiple = " + str(multiple)
        print "minimum = " + str(minimum)
        print "maximum = " + str(maximum)
        raise