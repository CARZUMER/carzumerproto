help# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 17:13:16 2015

@author: Dan
"""
import cfg
import hashlib
from Crypto.Cipher import AES
import base64
import os
import re
import string


def hashed(input_string, sanitization=""):
    Sanitized = sanitize(input_string, sanitization)
    if Sanitized == "":
        return ""

    input_length    = len(Sanitized)
    salt_length     = len(cfg.SALT)

    salted_string = "%s%s%s"%(cfg.SALT[:(input_length%salt_length)],
                              Sanitized,
                              cfg.SALT[((input_length+1)%salt_length):])

    return hashlib.sha256(salted_string).hexdigest()


def sanitize(input_string, Regex="USERNAME", Kills=""):
    # Will sanitize a string using the regular expression methodology
    # intended to keep dbase clean of SQL injections or other bad data
    if Regex == "USERNAME":
        Regex = "[\w]+"
    elif Regex == "PASSWORD":
        Regex = "[\S]+"
    elif Regex == "EMAIL":
        Regex = "[\w.-]+[@][\w.-]+"
    elif Regex == "FLOAT":
        Regex = "[-]?[\d]*[.]?[\d]*"
    elif Regex == "INTEGER":
        Regex = "[-]?[\d]+"
    elif Regex == "STREET":
        Regex = "[\w -]+"
        Kills = ",;./\\@#&()+"
    elif Regex == "UNIT":
        Regex = "[\w-]*"
        Kills = " ,;./\\@#&()+"
    elif Regex == "CITY":
        Regex = "[\w -]+"
        Kills = ",;./\\@#&()+"
    elif Regex == "STATE":
        Regex = "[\w]{2}"
    elif Regex == "ZIP":
        Regex = "[\d]{5}"
    elif Regex == "PHONE":
        Regex = "[\d]{10}"
        Kills = ".()-"
    elif Regex == "SSN":
        Regex = "[\d]{9}"
        Kills = ".-"
    elif Regex == "YN":
        Regex = "[YNyn]"

    if Regex == "":
        return input_string

    Stripped = string.strip(input_string)
    for c in Kills:
        Stripped = string.replace(Stripped, c, "")

    try:
        Sanitized = re.match(Regex, Stripped)
        if Sanitized is None:
            return ""
        else:
            return str(Sanitized.group())
    except:
        return ""


def encryption(privateInfo, key, BLOCK_SIZE=32):
    PADDING = '@'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    NewCipher = AES.new(key)
    encoded = EncodeAES(NewCipher, privateInfo)
    return encoded


def decryption(encryptedString, key):
    PADDING = '@'
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
    encryption = encryptedString
    NewCipher = AES.new(key)
    decoded = DecodeAES(NewCipher, encryption)
    return decoded


if False:
    BLOCK_SIZE = 32
    key = os.urandom(BLOCK_SIZE)


    enpw = hashed(" myname!","PASSWORD").decode('hex')
    #enpw = b'Sixteen byte key'

    message = "Hi this is me"
    CipherText = encryption(message, enpw, BLOCK_SIZE)
    clear = decryption(CipherText, enpw)
    print "enpw=", enpw
    print "message=", message
    print "CipherText=", CipherText
    print "clear=", clear

