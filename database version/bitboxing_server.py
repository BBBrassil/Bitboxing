# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 21:12:41 2022

@author: mikkelsonm
"""
import bitboxing_database
import bitboxing_message_formatting
import socket



'''
methods for protocol handling
checks for correct number of parameters for protocol
if yes, then makes database query
'''

def loginHandler(username, args):
    if len(args) != 1:
        return ("1", "Wrong Number of parameters")
    else:
        return bitboxing_database.loginUser(username, args[0])

def newUserHandler(username, args):
    if len(args) != 1:
        return ("1", "Wrong Number of parameters")
    else:
        return bitboxing_database.newUser(username, args[0])

def findHandler(username, args):
    if len(args) != 1:
        return ("1", "Wrong Number of parameters")
    else:
        return bitboxing_database.foundPuzzle(username, args[0])

def hintHandler(username, args):
    if len(args) != 1:
        return ("1", "Wrong Number of parameters")
    else:
        return bitboxing_database.getHint(username, args[0])

def solveHandler(username, args):
    if len(args) != 2:
        return ("1", "Wrong Number of parameters")
    else:
        return bitboxing_database.solvePuzzle(username, args[0], args[1])

def statsHandler(username):
    return bitboxing_database.getStats(username)

def leaderboardHandler():
    return bitboxing_database.getLeaderboard()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('', 9999))
s.listen(50)

print("The server is ready to receive")

while True:
    clientSocket, clientAddress = s.accept()
    print ('Connected with ' + str(clientAddress))
    break

while True:
    clientMessage = bitboxing_message_formatting.parse_request(bitboxing_message_formatting.receive_msg(clientSocket))
    
    print (clientMessage)

    '''
    #if message correct,
    clientMessage[0] = username
    clientMessage[1] = protocol
    clientMessage[2] = args
    '''

    '''
    methods = {"LOGIN", "NEW_USER", "FIND", "HINT", "SOLVE", "STATS", "LEADERBOARD", "CACHE_LEADERBOARD"}
    '''

    #verify length of clientMessage is three
    if(len(clientMessage) != 3):
        serverResponse = ("1", "Wrong Number of parameters")
    else:
        #verify that the protocol is valid
        if(bitboxing_message_formatting.is_valid_method(clientMessage[1])):
            #run appropriate protocol handler
            if(clientMessage[1] == "LOGIN"):
                serverResponse = loginHandler(clientMessage[0], clientMessage[2])
            elif(clientMessage[1] == "NEW_USER"):
                serverResponse = newUserHandler(clientMessage[0], clientMessage[2])
            elif(clientMessage[1] == "FIND"):
                serverResponse = findHandler(clientMessage[0], clientMessage[2])
            elif(clientMessage[1] == "HINT"):
                serverResponse = hintHandler(clientMessage[0], clientMessage[2])
            elif(clientMessage[1] == "SOLVE"):
                serverResponse = solveHandler(clientMessage[0], clientMessage[2])
            elif(clientMessage[1] == "STATS"):
                serverResponse = statsHandler(clientMessage[0])
            elif(clientMessage[1] == "LEADERBOARD"):
                serverResponse = leaderboardHandler()
            else:
                serverResponse = ("2", "Not valid protocol")
        else:
            #if protocol not valid, throw appropriate error
            serverResponse = ("2", "Not valid protocol")
            
        #serverResponse should be (status_code, msg)
        print(serverResponse)
        #format tuple and send response
        bitboxing_message_formatting.send_msg(clientSocket, bitboxing_message_formatting.format_response(serverResponse[0], serverResponse[1]))
        

