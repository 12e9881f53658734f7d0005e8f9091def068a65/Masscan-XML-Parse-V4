from logging import exception
import xml.etree.ElementTree as et
from socket import gethostbyaddr 
import requests
import threading
from time import sleep
requests.urllib3.disable_warnings()

# Settings
maxAmountOfThreads = 50
xmlFileName = "only 80 nov.xml"
outputFileName = "11-17-22 http.txt"

# Internal varibles
que = []
httpPorts = ["80", "443", "8008", "8080", "8081", "8000"]
threads = []
writingToFile = False
finished = False
currentLineNumber = 1 # Might be for testing purposes.
xmlDumpData = {
    "ip": "",
    "port": ""
}

# Functions
def findHTMLTitle(content):
    n1 = content.find("<title>")
    n2 = content.find("</title>")
    if n1 != -1 and n2 != -1:
        return content[n1 + 7:n2]
    else:
        return "No Title"

def PTRRecord(ip):
    try:
        return gethostbyaddr(str(ip))[0]
    except:
        return None

def networkRequest(ip, port):
    if port in httpPorts:
        try:
            return findHTMLTitle(str(requests.get(f"http://{ip}:{port}", verify=False, timeout=25, allow_redirects=True).content))
        except:
            return None
    else:
        return None

def writeOutFileQue(fileName, dataQue):
    clonedDataQue = dataQue.copy()
    dataQue.clear()

    with open(fileName, "a") as file:
        for data in clonedDataQue:
            file.write(data)

def processData(ip, port):
    name = PTRRecord(ip)

    if name == None:
        name = networkRequest(ip, port)
    
    if name != None:
        que.append(f"{ip}:{port}\t{name}\n")
    
    return

def listToFile():
    while finished == False:
        if len(que) >= 10:
            writingToFile = True
            writeOutFileQue(outputFileName, que)
            writingToFile = False
        sleep(0.5)
    while threading.active_count() > 2:
        sleep(0.5)
    if len(que) > 0: # ALSO OR MAYBE INSTEAD CHECK AMOUNT OF THREADS LEFT
        writingToFile = True
        writeOutFileQue(outputFileName, que)
        writingToFile = False
    print(que)
    return

thread = threading.Thread(target=listToFile)
thread.start()

context = et.iterparse(xmlFileName, events=("start", "end"))
context = iter(context)
event, root = next(context)

for event, element in context:
    if event == "start":
        if element.tag == "address":
            xmlDumpData["ip"] = element.attrib["addr"]
        elif element.tag == "port":
            xmlDumpData["port"] = element.attrib["portid"]
        else:
            continue
    
    elif event == "end" and element.tag == "host":
        try:
            thread = threading.Thread(target=processData, args=(xmlDumpData["ip"], xmlDumpData["port"], ))
            threads.append(thread)
            thread.start()
        except Exception as error:
            print(error)

        root.clear()
        xmlDumpData.clear()
        currentLineNumber += 1

        threads = threading.enumerate()
        while (len(threads) >= maxAmountOfThreads) or (writingToFile == True):
            sleep(0.02)
            threads = threading.enumerate()
        # print(currentLineNumber)

print("Waiting some seconds...")
finished = True