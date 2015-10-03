# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 05:19:51 2015

@author: Dan
"""

import sqlite3
import cfg
from Cryptography import hashed, encryption, decryption, sanitize

UserDBFile = cfg.UserDBFile


"""

    if form.LogAttempt == "Create":
        # protocol to create new account and fill it with session data
        tried = True
        FailureMessage = MyUsers.CreateUser(form.Username, form.Password, form.eMail, FormID)

    if form.LogAttempt == "Login":
        # Protocol to authenticate account and log in
        # If the account exists and authenticated, merge input data with old data
        # If does not exist, send problem message, offer to create account
        # if Attempt succeed, set status to loggedin
        tried = True
        PriorID = MyUsers.FindUser(form.Username, form.Password)
        if (PriorID != ""):
            FormID = PriorID
            # TODO: Merging code may come here
        else:
            FailureMessage = "No account matches username / password combination"
"""

class UserDatabase():

    def __init__(self):
        UserDB = sqlite3.connect(UserDBFile)
        cur = UserDB.cursor()
        script = \
            """
            CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY,
                                               user TEXT UNIQUE NOT NULL,
                                               pass TEXT NOT NULL,
                                               email TEXT UNIQUE NOT NULL,
                                               sessionid TEXT UNIQUE NOT NULL);
            """

        cur.execute(script)
        UserDB.commit()
        UserDB.close()

    def CreateUser(self, username, password, email, sessionID):

        # Check for non-complying username
        HashedUsername = hashed(username.lower(), "USERNAME")
        if (HashedUsername == ""):
            return "Invalid username, may only use alphanumeric characters and _ "

        # Check for non-complying password
        HashedPassword = hashed(password, "PASSWORD")
        if (HashedPassword == ""):
            return "Invalid password, may not use white spaces"

        UserDB = sqlite3.connect(UserDBFile)
        cur = UserDB.cursor()

        # Check if already logged in (sessionID exists)
        cur.execute('SELECT COUNT(*) FROM users WHERE sessionid = "%s";' % sessionID)
        c = cur.fetchone()
        if c[0]>0:
            UserDB.commit()
            UserDB.close()
            return "Already Logged In c=" + str(c)

        # Check if account with matching password already exists
        cur.execute('SELECT COUNT(*) FROM users WHERE user = "%s" AND pass = "%s";' \
                 % (HashedUsername, HashedPassword) )
        c = cur.fetchone()
        if c[0]>0:
            UserDB.commit()
            UserDB.close()
            return "LogMe"

        # Check if username is already taken
        cur.execute('SELECT COUNT(*) FROM users WHERE user = "%s";' % HashedUsername)
        c = cur.fetchone()
        if c[0]>0:
            UserDB.commit()
            UserDB.close()
            return "Username already taken, please select another"

        SanitizedEmail = sanitize (email, "EMAIL")
        Key = HashedPassword.decode('hex')
        BLOCK_SIZE = 32
        EncryptedEmail = encryption(SanitizedEmail, Key, BLOCK_SIZE)

        script = '''INSERT OR IGNORE INTO users
                    (user, pass, email, sessionid) VALUES ("%s", "%s", "%s", "%s");''' \
                    % (HashedUsername, HashedPassword, EncryptedEmail, sessionID)

        cur.execute(script)
        UserDB.commit()
        UserDB.close()

        return ""

    def FindUser(self, username, password):
        # Will search user database for a user with matching Username and Password
        # and will return the sessionID if found (or "" if not)
        HashedUsername = hashed(username.lower(), "USERNAME")
        HashedPassword = hashed(password, "PASSWORD")
        if (HashedUsername == "") or (HashedPassword == ""):
            return ""
        UserDB = sqlite3.connect(UserDBFile)
        cur = UserDB.cursor()
        cur.execute('SELECT sessionid FROM users WHERE user = "%s" AND pass = "%s";' \
                 % (HashedUsername, HashedPassword) )
        allrows = cur.fetchall()
        UserDB.commit()
        UserDB.close()
        if len(allrows) == 0:
            return ""
        else:
            return allrows[0][0]



    def PrintDB(self):
        # Show table count, columns, and top 5 rows
        UserDB = sqlite3.connect(UserDBFile)
        cur = UserDB.cursor()
        cur.execute("SELECT COUNT(*) FROM users;")
        c = cur.fetchone()
        cur.execute("SELECT * FROM users LIMIT 5;")
        allrows = cur.fetchall()
        names = [description[0] for description in cur.description]
        print c, names
        for row in allrows:
            print(row)

        UserDB.commit()
        UserDB.close()


MyUsers = UserDatabase()

if False:
    Newbase = UserDatabase()
    Newbase.CreateUser("MyName","MyPass","MyEmail@Domain.com")
    Newbase.CreateUser("Name2","Pass2","P2@Domain.com")
    Newbase.PrintDB()

