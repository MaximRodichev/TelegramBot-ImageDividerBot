import os
import json
from datetime import datetime
import asyncio

pathToBase = "..\data.json"

def createUserData(chatId, userName):
    with open(pathToBase, 'r') as file:
        try:
            data = json.load(file)
        except:
            data = {}
        
        if str(chatId) not in data:
            data[chatId] = {}
                
        data[chatId] = {
                    "userName": userName,
                    "firstAttemp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Count": 0
                }
        
    with open(pathToBase, 'w') as file:
        json.dump(data, file, indent=4)

def updateCount(chatId, userName):
    with open(pathToBase, 'r') as file:
        try:
            data = json.load(file)
        except:
            data = {}
        if str(chatId) not in data:
            createUserData(chatId, userName)
            with open(pathToBase, 'r') as file:
                data = json.load(file)

        data[str(chatId)]["Count"] =  data[str(chatId)]["Count"] + 1
    with open(pathToBase, 'w') as file:
        json.dump(data, file, indent=4)

async def sendBroadcast(sendFunction, text):
    with open(pathToBase, 'r') as file:
        data = json.load(file)

        for x in data:
            chatId = int(x)
            text = text
            await sendFunction(chatId, text, parse_mode = "Markdown")