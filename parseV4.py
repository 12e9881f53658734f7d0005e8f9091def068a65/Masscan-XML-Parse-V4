from logging import exception
import xml.etree.ElementTree as et
import socket
import requests
import threading
from time import sleep
from smb.SMBConnection import SMBConnection
requests.urllib3.disable_warnings()

# Settings
maxAmountOfThreads = 2000
xmlFileName = "8-28-29 http.xml"
outputFileName = xmlFileName + ".txt"

# Internal varibles
que = []
threads = []
writingToFile = False
finished = False
currentLineNumber = 1 # Might be for testing purposes.
lock = threading.Lock()
xmlDumpData = {
    "ip": "",
    "port": ""
}

# Functions
def findHTMLTitle(content):
    content = content.replace("\"", "")
    n1 = content.find("<title>")
    n2 = content.find("</title>")
    if n1 != -1 and n2 != -1:
        return content[n1 + 7:n2]
    else:
        return "No Title"

def PTRRecord(ip):
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except:
        return None

def networkRequest(ip, port):
    try:
        r = requests.get(f"http://{ip}:{port}", verify=False, timeout=25, allow_redirects=True)
        if r.status_code == 200:
            return findHTMLTitle(str(r.content))
        else:
            r = requests.get(f"https://{ip}:{port}", verify=False, timeout=25, allow_redirects=True)
            return findHTMLTitle(str(r.content))
    except:
        return None

def socketRequest(ip, port):
    try:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.settimeout(5)
        c.connect((ip, int(port)))
        c.send(b"")
        res = c.recv(4096)
        return res.decode("utf-8", errors="replace").replace("\n", "  ")
    except Exception as e:
       return e

def RTSP(ip, port):
    req = bytes(f"DESCRIBE rtsp://admin:12345@{ip}:{port}/Src/MediaInput/h264/stream_1/ch_\r\n\r\n", "utf-8")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("172.28.133.31", 554))
    s.sendall(req)
    data = s.recv(1024)
    return data

def writeOutFileQue(fileName, dataQue):
    clonedDataQue = dataQue.copy()
    dataQue.clear()

    with open(fileName, "a", encoding="utf-8") as file:
        for data in clonedDataQue:
            file.write(data)

def processData(ip, port):
    try:
        name1 = 
        name2 = PTRRecord(ip).strip()

        with lock:
            que.append(f"{ip}:{port}\t{name2}\n")
    except:
        pass
    
    """
    name = ""
    if port == "139":
        dnsLookup = PTRRecord(ip)
        name = getShares(dnsLookup)

    if name != None and name != "":
        with lock:
            que.append(f"{ip}:{port} {dnsLookup} \t{name}\n")
    """
    
    return
# mutexes, .join might be the fix??
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
            #thread.join() # Might be slowing down, might have to put somewhere else.
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