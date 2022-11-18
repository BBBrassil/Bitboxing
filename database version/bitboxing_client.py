# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 23:32:46 2022

@author: mikkelsonm
"""
from tkinter import *
from functools import partial
import bitboxing_message_formatting
import socket
import login_window

HOST = '127.0.0.1' #socket.gethostname()

PORT = 9999
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
username = 'not logged in'

root = Tk()
root.title('Main')
root.geometry('500x300')





def openNewUser():
    newUserWindow.mainloop
    loginWindow.destroy


def openLoginWin():
    loginWindow = Toplevel(root)
    loginWindow.geometry('200x200')
    loginWindow.title('Login')
        
    Label(loginWindow, text='Login to Bitboxing').pack()
        
    Label(loginWindow, text='Username').pack()
    loginUsername = Entry(loginWindow)
    loginUsername.pack()
        
    Label(loginWindow, text='Password').pack()
    loginPassword = Entry(loginWindow)
    loginPassword.pack()
        
    loginErrorLabel = Label(loginWindow, text='')
        
    loginBtn = Button(loginWindow, text='login', command=partial(login, loginWindow, loginUsername, loginPassword, loginErrorLabel))
    loginBtn.place(x=25, y=135)
        
    newUsrBtn = Button(loginWindow, text='new user', command=openNewUser)
    newUsrBtn.place(x=75, y=135)
        
    loginQuitBtn = Button(loginWindow, text='go back', command=loginWindow.destroy)
    loginQuitBtn.place(x=145, y=135)
        
    loginErrorLabel.pack()
    
def login(window, usernamel, passwordl, label):
    u = usernamel.get()
    p = passwordl.get()
    bitboxing_message_formatting.send_msg(s, bitboxing_message_formatting.format_request(u, "LOGIN", p))
    response = bitboxing_message_formatting.parse_response(bitboxing_message_formatting.receive_msg(s))
    if response[0] == "0":
        username = u
        window.destroy()
    else:
        label["text"] = response[1]

def refresh():
    print(username)
    usernameRoot["text"] = username

Label(root, text='Choose an option').place(x=0,y=0)
usernameRoot = Label(root, text=username).place(x=0,y=25)
openLoginBtn = Button(root, text='login / switch user', command=openLoginWin).place(x=30, y=50)
refreshBtn = Button(root, text='refresh', command=refresh).place(x=60, y=80)
quitBtn = Button(root, text='Quit', command=root.destroy).place(x=60, y=110)

protocols = Listbox(root)
protocols.insert(1, 'Found Item')
protocols.insert(2, 'Solve Puzzle')
protocols.insert(3, 'Request Hint')
protocols.insert(4, 'Open Leaderboard')
protocols.insert(5, 'My stats')
protocols.insert(6, 'logout')
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
