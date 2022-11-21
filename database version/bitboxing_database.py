# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 21:18:59 2022

@author: mikkelsonm
"""

import sqlite3
from sqlite3 import Error
import datetime

'''
method for connecting to database
not for public use
'''
def connection():
    try :
        con = sqlite3.connect('bitboxing_database.db')
        return con
    except Error:
        print(Error)
    



'''
method for creating Tables and inserting predetermined data
For Initialization
'''
def initializeTables():
    #establish connection with database
    con = connection()
    #create cursor object to execute database functions
    cur = con.cursor()
    
    #check if User table has been created. If not, create table
    cur.execute("CREATE TABLE IF NOT EXISTS Users(username TEXT NOT NULL, password TEXT, PRIMARY KEY(username))")
                
    #check if Puzzle table has been created. If not, create table and insert Puzzle data
    try:
        cur.execute("SELECT * FROM Puzzles")
    except sqlite3.OperationalError:
        try:
            cur.execute("CREATE TABLE Puzzles(puzzle_num INT NOT NULL, question TEXT, answer TEXT, hint TEXT, PRIMARY KEY(puzzle_num))")
            cur.execute("INSERT INTO Puzzles VALUES(1, 'Dlsjvtl av Ipaivepun!  Aopz pz aol mpyza wbggsl!', 'Welcome to Bitboxing!  This is the first puzzle!', 'Julius')")
            cur.execute("INSERT INTO Puzzles VALUES(2, 'What is the end of everything?', 'G', 'What is the end of \"everything\"')")
            cur.execute("INSERT INTO Puzzles VALUES(3, 'What is the 8th Fibonacci number?', '13', '0, 1, 1, 2, ...')")
            cur.execute("INSERT INTO Puzzles VALUES(4, '682 1**\n614 1*\n206 2*\n738 0\n870 1*\n???', '042', '* Correct value\n** Correct value and in the right place')")
            cur.execute("INSERT INTO Puzzles VALUES(5, 'Five people were eating apples.\nA finished before B, but behind C.\nD finished before E, but behind B.\nWhat was the finishing order?', 'CABDE', 'Enter the letters in order without space or punctuation. (e.g. ABCDE)')")
        except Error:
            print(Error)
            
    #check if User table has been created. If not, create table
    cur.execute("CREATE TABLE IF NOT EXISTS Users_Puzzles(username TEXT NOT NULL, puzzle_num TEXT NOT NULL, time_found TEXT, time_completed TEXT, attempts INT, PRIMARY KEY(username, puzzle_num), FOREIGN KEY(username) REFERENCES Users(username), FOREIGN KEY(puzzle_num) REFERENCES Puzzles(puzzle_num))")
    
    #commit changes to database
    con.commit()
    #close connection to database
    con.close()

'''
methods for user login and new users
'''

'''
Creates new user and inputs their login info to database
returns:
    0 if new user successfully entered
    1 if username is already taken
    2 if database error occurs
    
    format (status_code, msg)
'''
def newUser(username, password):
    #establish connection with database
    con = connection()
    #create cursor object to execute database functions
    cur = con.cursor()
    
    try:
        #query table to find if username already taken
        cur.execute("SELECT * from Users WHERE username=?", (username))
        
        #if taken, return 1
        #otherwise, insert into table
        if cur.fetchone():
            con.close()
            return ("1", "Username already taken")
        else:
            userData = (username, password)
            cur.execute("INSERT INTO Users(username, password) VALUES(?, ?)", userData)
            con.commit()
            con.close()
            return ("0", "New User Successfully Added")
            
    except Error:
        print(Error)
        con.close()
        return ("2", "DATABASE ERROR")
    
'''
Login existing user by finding username in database and varify password
returns 0 if username exists and password correct
returns 1 if password incorrect
returns 2 if username not found
returns 3 if database error

format (status_code, msg)
'''
def loginUser(username, password):
    #establish connection with database
    con = connection()
    #create cursor object to execute database functions
    cur = con.cursor()
    
    try:
        #query table to find username
        cur.execute("SELECT password from Users WHERE username=?", (username))
        found = cur.fetchall()
        
        con.close()
        
        #if not found return 1
        #otherwise, verify password
        if not found:
            return ("2", "Username not found")
        else:
            if (found[0][0] == password):
                return ("0", "Login Successful")
            else:
                return ("1", "Incorrect Password")
    except Error:
        print(Error)
        con.close()
        return ("3", "DATABASE ERROR")

'''
methods for finding and solving puzzles
'''

'''
Indicating that user has found a puzzle
parameters:
    username --user should already be logged in
    puzzle number
return:
    0 if successfully insert new row to Users_Puzzles
    1 if database error
    2 if puzzle not found
    3 if user has already found puzzle
    
    format (status_code, msg)
'''
def foundPuzzle(username, puzzle_num):
    #establish connection with database
    con = connection()
    #create cursor object to execute database functions
    cur = con.cursor()
    
    #verify that puzzle is in database
    try:
        cur.execute("SELECT question from Puzzles WHERE puzzle_num=?", (puzzle_num,))
        question = cur.fetchall()
        
        if not question:
            con.close()
            return ("2", "PUZZLE NOT FOUND")
        else:
            #verify user hasn't already found the puzzle
            cur.execute("SELECT time_found from Users_Puzzles WHERE username=? and puzzle_num=?", (username, puzzle_num))
            found = cur.fetchall()
            
            if not found:
                #Add row to User_Puzzle table
                cur.execute("INSERT INTO Users_Puzzles(username, puzzle_num, time_found, time_completed, attempts) VALUES(?, ?, ?, ?, ?)", (username, puzzle_num, datetime.datetime.now(), '', 0))
                
                con.commit()
                con.close()
                return ("0", ''.join(question[0]))
            else:
                con.close()
                return ("3", "PUZZLE ALREADY FOUND")
    except Error:
        print(Error)
        con.close()
        return ("1", "DATABASE ERROR")
    
'''
Verifying and indicating if user has solved a puzzle
parameters:
    username -- user should already be logged in
    puzzle_num -- user should already have row for this puzzle in Users_Puzzles table
    answer
return:
    0 if successfully update Users_Puzzles row
    1 if puzzle not found
    2 if user has not found puzzle yet
    3 if answer is incorrect
    4 if database error
'''
def solvePuzzle(username, puzzle_num, answer):
    #establish connection with database
    con = connection()
    #create cursor object to execute database functions
    cur = con.cursor()
    
    #verify that puzzle is in database
    try:
        
        cur.execute("SELECT answer from Puzzles WHERE puzzle_num=?", (puzzle_num,))
        solution = cur.fetchall()
        
        if not solution:
            con.close()
            return ("1", "Puzzle not found")
        else:
            #verify that user has found the puzzle
            cur.execute("SELECT attempts from Users_Puzzles WHERE puzzle_num=? AND username=?", (puzzle_num, username,))
            attempt_num = cur.fetchall()
            
            if not attempt_num:
                con.close()
                return ("2", "User has not found puzzle")
            else:
                #increment number of attempts
                new_attempt = attempt_num[0][0] + 1
                query = """Update Users_Puzzles set attempts = ? where puzzle_num = ? and username = ?"""
                data = (new_attempt, puzzle_num, username)
                cur.execute(query, data)
                con.commit()
                #verify that answer is correct
                if (solution[0][0] == answer):
                    #update User_Puzzle table to include time_completed
                    query = """Update Users_Puzzles set time_completed = ? where puzzle_num = ? and username = ?"""
                    data = (datetime.datetime.now(), puzzle_num, username)
                    cur.execute(query, data)
                    con.commit()
                    con.close()
                    return ("0", "Answer is correct")
                else:
                    con.close()
                    return ("3", "Answer is incorrect")
    except Error:
        print(Error)
        con.close()
        return ("4", "DATABASE ERROR")
                
    
'''
method for returning hint
parameters:
    username -- user should already be logged in
    puzzle_num -- user should already have row for this puzzle in Users_Puzzles table
return:
    0 if successfully return hint
    1 if puzzle not found
    2 if user has not found puzzle yet
    3 if database error
'''
def getHint(username, puzzle_num):
    #establish connection with database
    con = connection()
    #create cursor object to execute database functions
    cur = con.cursor()
    
    #verify puzzle is in database
    try:
        cur.execute("SELECT hint from Puzzles WHERE puzzle_num=?", (puzzle_num,))
        hint = cur.fetchall()
        
        if not hint:
            con.close()
            return ("1", "Puzzle not found")
        else:
            #verify that user has found puzzle
            cur.execute("SELECT * from Users_Puzzles WHERE puzzle_num=? AND username=?", (puzzle_num, username,))
            found = cur.fetchall()
            
            if not found:
                con.close()
                return ("2", "User has not found puzzle")
            else:
                #return hint
                con.close()
                return("0", ''.join(hint[0]))
    except:
        print(Error)
        con.close()
        return ("3", "DATABASE ERROR")


'''
Method for printing user stats
parameter: username -- user should already be logged in
return:
    0 if successful
    1 if database error
'''

def getStats(username):
    #establish connection with database
    con = connection()
    #create cursor object to execute database functions
    cur = con.cursor()
    
    try:
        stats = ''
        cur.execute("SELECT puzzle_num from Puzzles")
        puzzles = cur.fetchall()
        cur.execute("SELECT * from Users_Puzzles where username=?", (username,))
        rows = cur.fetchall()
        stats = stats + "Stats for " + username + ":\n"
        if not rows:
            stats = stats + "No puzzles found"
        else:
            for num in puzzles:
                isFound = False
                for line in rows:
                    if int(line[1])==int(num[0]):
                        isFound = True
                        if len(line) != 5:
                            con.close()
                            return ("1", "DATABASE ERROR")
                        else:
                            stats = stats + "Puzzle " + line[1] + "\n"
                            stats = stats + "\tTime Found: " + line[2] + "\n"
                            stats = stats + "\tTime Completed: " + line[3] + "\n"
                            stats = stats + "\tNumber of Attempts: " + str(line[4]) + "\n"
                        break
                if isFound == False:
                    
                    stats = stats + "Puzzle " + str(num[0]) + ": not found\n"    
        con.close()
        return ("0", stats)
    except:
        print(Error)
        con.close()
        return ("1", "DATABASE ERROR")

'''
Method for sorting the user data
'''



'''
Method for displaying overall leaderboard
'''

def getLeaderboard():
    #establish connection with database
    con = connection()
    #create cursor object to execute database functions
    cur = con.cursor()
    
    try:
        leaderboard = ''
        #get all users
        cur.execute("Select username from Users")
        allUsers = cur.fetchall()
        usersData = []
        #get number of solves and finds from each player
        for u in allUsers:
            #get number of finds
            cur.execute("SELECT time_found from Users_Puzzles WHERE username=?", u)
            finds = cur.fetchall()
            numFinds = 0
            for f in finds:
                if(f[0] != ''):
                    numFinds = numFinds + 1
            
            #get number of solves
            cur.execute("SELECT time_completed from Users_Puzzles WHERE username=?", u)
            
            solves = cur.fetchall()
            numSolves = 0
            for s in solves:
                if(s[0] != ''):
                    numSolves = numSolves + 1
            
            #save in tuple
            data = (numSolves, numFinds, u[0])
            #insert into list
            usersData.append(data)
        
        usersData = sorted(usersData, reverse=True)
        print(usersData)
        for user in usersData:
            leaderboard = leaderboard + "User: " + user[2] + "\tSolves: " + str(user[0]) + "\tFinds: " + str(user[1]) + "\n"
        return ("0", leaderboard)
    except:
        print(Error)
        con.close()
        return ("1", "DATABASE ERROR")

'''
Method for droping all tables
For testing purposes
'''
def dropTables():
    con = connection()
    cur = con.cursor()
    
    cur.execute("DROP TABLE IF EXISTS Users_Puzzles")
    cur.execute("DROP TABLE IF EXISTS Users")
    cur.execute("DROP TABLE IF EXISTS Puzzles")
    
    con.close()
    

def main():
    dropTables()
    initializeTables()
    
    print(newUser("A", "A"))
    print(newUser("B", "B"))
    print(newUser("C", "C"))
    print(loginUser("A", "A"))
    
    print(foundPuzzle("A", "1"))
    print(foundPuzzle("A", "2"))
    print(foundPuzzle("A", "3"))
    print(foundPuzzle("A", "4"))
    print(foundPuzzle("A", "5"))
    
    print(foundPuzzle("B", "1"))
    print(foundPuzzle("B", "2"))
    print(foundPuzzle("B", "3"))
    print(foundPuzzle("B", "4"))
    print(foundPuzzle("B", "5"))
    
    print(foundPuzzle("C", "1"))
    print(foundPuzzle("C", "2"))
    print(foundPuzzle("C", "3"))
    
    print(solvePuzzle("A", "3", "hello"))
    print(solvePuzzle("A", "3", "13"))
    print(solvePuzzle("A", "1", "13"))
    
    print(solvePuzzle("C", "3", "13"))
    
    print(getLeaderboard()[1])
    
    '''
    print("Testing adding new Users")
    print(newUser("A", "A"))
    print(newUser("B", "B"))
    print("")
    
    print("Taken username")
    print(newUser("B", "C"))
    print("")
    
    print("logging in")
    print(loginUser("A", "A"))
    print(loginUser("B", "B"))
    print("")
    
    print("username not found")
    print(loginUser("C", "C"))
    print("")
    
    print("incorrect password")
    print(loginUser("B", "C"))
    print("")
    
    print("testing found puzzle")
    print(foundPuzzle("A", 1))
    print(foundPuzzle("A", 3))
    print("")
    
    print("testing puzzle not found")
    print(foundPuzzle("B", 10))
    print("")
    
    print("testing solve puzzle")
    print(solvePuzzle("A", 3, "13"))
    print("")
    
    print("testing puzzle not in database")
    print(solvePuzzle("A", 10, "13"))
    print("")
    
    print("testing user hasn't found puzzle")
    print(solvePuzzle("A", 5, "13"))
    print("")
    
    print("testing incorrect answer")
    print(solvePuzzle("A", 3, "hello"))
    print("")
    
    print("testing get hint")
    print(getHint("A", 1))
    print("")
    
    print("testing puzzle not found")
    print(getHint("B", 10))
    print("")
    
    print("testing user hasn't found puzzle")
    print(getHint("A", 5))
    print("")
    '''

if __name__ == '__main__':
    main()
    













