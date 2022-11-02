# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 08:18:50 2022

@author: mikkelsonm
"""

import socket

protocols = ["FIND", "HINT", "SOLVE", "LEADERBOARD", "STATS"]

def find(item_code):
    #look through database for item
    #if item found, return item
    #if item not found, return error
    return

def hint(item_code):
    #find item in database
    find(item_code)
    #if item found, look for hint
    #if no hint available, return error
    return

def solve(item_code, solution_code):
    #find item in database
    find(item_code)
    #if item found, compare solutions
    #if solutions equal, return with next item location
    #else return error
    return

def leaderboard(item_code = ""):
    #if no item_code given, return overall leaderboard
    #else, return item specific leaderboard
    return

def status(username):
    #search database for username
    #if username found, return status
    #else return error
    return

def send_msg(socket, msg):
    socket.send(msg.encode())

def receive_msg(socket):
    return socket.recv(2048).decode()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('', 9999))
s.listen()

while True:
    cs, address = s.accept()
    message = receive_msg(cs).split('|')
    p = -1
    for i in range(len(protocols)):
        if(message[0] == protocols[i]):
            print("recognized protocol")
            send_msg(cs, "recognized protocol")
            p = i
            break
    
    if(p == -1):
        print("protocol not recognized")
        send_msg(cs, "protocol not recognized")
    elif(len(message) == 1):
        if(p == 3):
            leaderboard()
        else:
            print("NUMBER OF PARAMETER ERROR")
    elif(len(message) == 2):
        if(p == 0):
            find(message[1])
        elif(p == 1):
            hint(message[1])
        elif(p == 3):
            leaderboard(message[1])
        elif(p == 4):
            status(message[1])
        else:
            print("NUMBER OF PARAMETER ERROR")
    elif(len(message) == 3):
        if(p == 2):
            solve(message[1], message[2])
        else:
            print("NUMBER OF PARAMETER ERROR")
    else:
        print("NUMBER OF PARAMETER ERROR")
    