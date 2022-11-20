# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 23:32:46 2022

@author: mikkelsonm
"""
from tkinter import *
from functools import partial
import bitboxing_message_formatting
import socket
#import login_window

HOST = '127.0.0.1' #socket.gethostname()

PORT = 9999
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
NO_USER = 'not logged in'

root = Tk()
root.title('Main')
root.geometry('500x300')


    
def login():
    u = usernamelbl.get()
    p = passwordlbl.get()
    bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request(u, "LOGIN", p))
    response = bitboxing_message_formatting.parse_response(bitboxing_message_formatting.receive_msg(s))
    if response[0] == "0":
        usernameRoot["text"] = "user: " + u
        errorLbl["text"] = ''
    else:
        errorLbl["text"] = response[1]

def newUser():
    u = usernamelbl.get()
    p = passwordlbl.get()
    bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request(u, "NEW_USER", p))
    response = bitboxing_message_formatting.parse_response(bitboxing_message_formatting.receive_msg(s))
    if response[0] == "0":
        errorLbl["text"] = "user successfully created"
        usernameRoot["text"] = "user: " + u
    else:
        errorLbl["text"] = response[1]

def selectProtocol():
    
    if len(protocols.curselection()) < 1:
        errorLbl["text"] = "no protocol selected"
    elif len(protocols.curselection()) > 1:
        errorLbl["text"] = "too many protocols selected"
    else:
        #get which protocol is being choosen
        command = protocols.curselection()[0]
        #check if leaderboard
        if(command == 3):
            #run leaderboard
            print("leaderboard")
        else:
            #if not, verify logged in
            if(usernameRoot["text"] == NO_USER):
                print("not logged in")
                errorLbl["text"] = "Must login first"
            else:
                #open appropriate window
                if(command == 0):
                    findWindow(usernameRoot["text"])
                elif(command == 1):
                    #run solve
                    solveWindow(usernameRoot["text"])
                elif(command == 2):
                    #run hint
                    hintWindow(usernameRoot["text"])
                elif(command == 4):
                    #run stats
                    statsWindow(usernameRoot["text"])
    
'''
protocol Windows
'''

'''
FIND PROTOCOL
'''
def findPuzzle(label, entry, u):
    p = entry.get()
    bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request(u, "FIND", p))
    response = bitboxing_message_formatting.parse_response(bitboxing_message_formatting.receive_msg(s))
    label["text"] = response[1]

def findWindow(username):

    findWindow = Toplevel(root)
    findWindow.title("Found Puzzle")
    findWindow.geometry("350x250")

    Label(findWindow, text="Enter puzzle number").pack()

    puzzleEntry = Entry(findWindow)
    puzzleEntry.pack()
    
    output = Label(findWindow, text="placing")
    output.place(x=10, y=100)

    submitBtn = Button(findWindow, text="submit", command=partial(findPuzzle, output, puzzleEntry, username))
    submitBtn.pack()
    
    backBtn = Button(findWindow, text="Go Back", command=findWindow.destroy)
    backBtn.pack()

    
    
    findWindow.mainloop()

'''
HINT PROTCOL
'''   

def getHint(label, entry, u):
    p = entry.get()
    bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request(u, "HINT", p))
    response = bitboxing_message_formatting.parse_response(bitboxing_message_formatting.receive_msg(s))
    label["text"] = response[1]

def hintWindow(username):

    hintWindow = Toplevel(root)
    hintWindow.title("Request Hint")
    hintWindow.geometry("350x250")

    Label(hintWindow, text="Enter puzzle number").pack()

    puzzleEntry = Entry(hintWindow)
    puzzleEntry.pack()
    
    output = Label(hintWindow, text="placing")
    output.place(x=10, y=100)

    submitBtn = Button(hintWindow, text="submit", command=partial(getHint, output, puzzleEntry, username))
    submitBtn.pack()
    
    backBtn = Button(hintWindow, text="Go Back", command=hintWindow.destroy)
    backBtn.pack()

    hintWindow.mainloop()
    
'''   
SOLVE PROTOCOL
'''

def solvePuzzle(label, entryP, entryS, u):
    puzzle = entryP.get()
    solution = entryS.get()
    bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request(u, "SOLVE", puzzle, solution))
    response = bitboxing_message_formatting.parse_response(bitboxing_message_formatting.receive_msg(s))
    label["text"] = response[1]

def solveWindow(username):
    solveWindow = Toplevel(root)
    solveWindow.title("Request Hint")
    solveWindow.geometry("350x250")

    Label(solveWindow, text="Enter puzzle number").pack()

    puzzleEntry = Entry(solveWindow)
    puzzleEntry.pack()
    
    Label(solveWindow, text="Enter solution").pack()
    
    solutionEntry = Entry(solveWindow)
    solutionEntry.pack()
    
    output = Label(solveWindow, text="placing")
    output.place(x=10, y=150)

    submitBtn = Button(solveWindow, text="submit", command=partial(solvePuzzle, output, puzzleEntry, solutionEntry, username))
    submitBtn.pack()
    
    backBtn = Button(solveWindow, text="Go Back", command=solveWindow.destroy)
    backBtn.pack()

    solveWindow.mainloop()

'''
STATS PROTOCOL
'''

def statsWindow(username):
    statsWindow = Toplevel(root)
    statsWindow.title("User Stats")
    statsWindow.geometry("350x350")
    
    bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request(username, "STATS"))
    response = bitboxing_message_formatting.parse_response(bitboxing_message_formatting.receive_msg(s))
    
    Label(statsWindow, text=response[1], justify=LEFT).pack()
    
    backBtn = Button(statsWindow, text="Go Back", command=statsWindow.destroy)
    backBtn.pack(side=BOTTOM)
    
    statsWindow.mainloop()

'''
    
def leaderboardWindow():
    
'''
Label(root, text='Choose an option').pack()
usernameRoot = Label(root, text=NO_USER)
usernameRoot.place(x=10,y=25)

Label(root, text='Username').place(x=10, y=50)
usernamelbl = Entry(root)
usernamelbl.place(x=10, y=75)
    
Label(root, text='Password').place(x=10, y=100)
passwordlbl = Entry(root)
passwordlbl.place(x=10, y=125)
    
errorLbl = Label(root, text='')
errorLbl.place(x=10, y=150)
    
loginBtn = Button(root, text='login', command=login)
loginBtn.place(x=10, y=175)
    
newUsrBtn = Button(root, text='create new user', command=newUser)
newUsrBtn.place(x=60, y=175)




quitBtn = Button(root, text='Quit', command=root.destroy).place(x=10, y=205)

protocols = Listbox(root)
protocols.insert(1, 'Found Item')
protocols.insert(2, 'Solve Puzzle')
protocols.insert(3, 'Request Hint')
protocols.insert(4, 'Open Leaderboard')
protocols.insert(5, 'My stats')

selectBtn = Button(root, text='select protocol', command=selectProtocol)
selectBtn.pack()

protocols.pack()

root.mainloop()

#open login window
    #if user presses login button, send username|LOGIN|password request
        #if login successful, open main window
        #otherwise, display appropriate error
    #if user presses new user button, open newUser window
        #if button pressed, send username|NEW_USER|password request
            #if successful, open main window
            #otherwise, display appropriate error

#when main window open: username should be saved as a variable
    #when option selected, save appropriate protocol as a variable and open appropriate window to get the rest of the arguments


'''
methods = {"LOGIN", "NEW_USER", "FIND", "HINT", "SOLVE", "STATS", "LEADERBOARD", "CACHE_LEADERBOARD"}
'''


'''
print("TESTING SOLVE")
print("successful solve")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "SOLVE", "3", "13"))
print(bitboxing_message_formatting.receive_msg(s))

print("wrong answer")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "SOLVE", "1", "13"))
print(bitboxing_message_formatting.receive_msg(s))

print("user hasn't found puzzle")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "SOLVE", "2", "13"))
print(bitboxing_message_formatting.receive_msg(s))

print("puzzle not found")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "SOLVE", "10", "13"))
print(bitboxing_message_formatting.receive_msg(s))

print("wrong number of parameters")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "SOLVE"))
print(bitboxing_message_formatting.receive_msg(s))
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "SOLVE", "A", "A", "13"))
print(bitboxing_message_formatting.receive_msg(s))

print("TESTING HINT")
print("success retriving hint")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "HINT", "1"))
print(bitboxing_message_formatting.receive_msg(s))

print("user hasn't found puzzle")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "HINT", "2"))
print(bitboxing_message_formatting.receive_msg(s))

print("puzzle not found")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("B", "HINT", "10"))
print(bitboxing_message_formatting.receive_msg(s))

print("wrong number of parameters")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "HINT"))
print(bitboxing_message_formatting.receive_msg(s))
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "HINT", "A", "A"))
print(bitboxing_message_formatting.receive_msg(s))


print("TESTING FIND")
print("successful find")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("B", "FIND", "5"))
print(bitboxing_message_formatting.receive_msg(s))

print("puzzle already found")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("B", "FIND", "1"))
print(bitboxing_message_formatting.receive_msg(s))

print("puzzle not found")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("B", "FIND", "10"))
print(bitboxing_message_formatting.receive_msg(s))

print("wrong number of parameters")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "FIND"))
print(bitboxing_message_formatting.receive_msg(s))
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "FIND", "A", "A"))
print(bitboxing_message_formatting.receive_msg(s))

print("TESTING LOGIN")
print("successful login")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "LOGIN", "A"))
print(bitboxing_message_formatting.receive_msg(s))


print("username does not exist")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("F", "LOGIN", "F"))
print(bitboxing_message_formatting.receive_msg(s))

print("wrong number of parameters")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "LOGIN"))
print(bitboxing_message_formatting.receive_msg(s))
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "LOGIN", "A", "A"))
print(bitboxing_message_formatting.receive_msg(s))

print("")
print("TESTING NEW_USER")
print("successful new user")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("F", "NEW_USER", "F")) #change each time run
print(bitboxing_message_formatting.receive_msg(s))

print("username already taken")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "NEW_USER", "A"))
print(bitboxing_message_formatting.receive_msg(s))

print("wrong number of parameters")
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "NEW_USER"))
print(bitboxing_message_formatting.receive_msg(s))
bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request("A", "NEW_USER", "A", "A"))
print(bitboxing_message_formatting.receive_msg(s))
'''

'''
clientMessage = bitboxing_message_formatting.format_request("B", "HINT", "1")
clientMessage = bitboxing_message_formatting.format_request("C", "STATS")
'''
