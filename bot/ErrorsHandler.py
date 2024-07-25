import os, traceback, json
from datetime import datetime
#ScriptsNames
#imageDivider


folder = "..\\Errors\\"
def ExceptionHandler(ExceptionInfo, user_id, ScriptName):
    traceback_str = traceback.format_exc()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    filePath = folder + str(user_id) + ".json"
    if os.path.exists(filePath):
        with open(filePath, 'r') as jsonFile:
                try:
                    data = json.load(jsonFile)
                except:
                    data = {}

                if ScriptName not in data:
                    data[ScriptName] = {}
                
                data[ScriptName][time] = {
                    "ExceptionName": str(ExceptionInfo),
                    "Traceback": traceback_str.splitlines()
                }

        with open(filePath, 'w') as jsonFile:
            json.dump(data,jsonFile, indent=4)
    else:
        open(filePath, 'x')
        ExceptionHandler(ExceptionInfo, user_id, ScriptName)
            
            