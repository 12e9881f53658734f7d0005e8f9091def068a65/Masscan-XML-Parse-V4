import xml.etree.ElementTree as et
import matplotlib.pyplot as plt

# Input file name
xmlFileName = "172 private subnet.xml"


portsDict = {}
xmlDumpData = {
    "ip": "",
    "port": ""
}
amount = []
heights = []
labels = []

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
            portsDict[xmlDumpData["port"]] = portsDict[xmlDumpData["port"]] + 1
        except:
            portsDict[xmlDumpData["port"]] = 1


for i in range(len(portsDict)):
    amount.append(i)

for v in portsDict.items():
    heights.append(v[1])

for v in portsDict:
    labels.append(v)
  
plt.bar(amount, heights, tick_label = labels, width = 0.8)

plt.xlabel("Common Ports")
plt.ylabel("Number Of Devices")

plt.show()