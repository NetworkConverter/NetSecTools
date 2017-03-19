import sys
import json
import xml.etree.ElementTree as ET

def text_value(text):
    # Check for empty tags, then try to convert contents to list. If that fails, try integer.
    # If nothing else works, just store it as a string.
    val = None
    if text == None:
        val = ""
    elif text.count('\n'):
        val = ""
        for line in text.splitlines():
            val += line.strip()
    else:
        try:
            val = long(text)
        except ValueError:
            val = text.strip()
            
    return val

def to_json(elem):
    result = {}

    if len(elem) == 0 and len(elem.attrib) == 0:
        result["Value"] = text_value(elem.text)
        return result
    
    # Add the attributes to the result
    if len(elem.attrib) > 0:
        for key, value in elem.attrib.iteritems():
            result[key] = text_value(value)
    
    # Add all children's values to the result
    if len(elem) > 0:
        for child in elem:
            result[child.tag.split('}', 1)[1]] = to_json(child)
    
    # Hopefully they don't have anything crazy here...
    if elem.tail and elem.tail.strip():
        print elem.tail
        raise ValueError("Noooooo")
    
    if elem.text:
        result["Value"] = text_value(elem.text)
        
    return result

def event_to_json(event_xml_tag):
    event = {}
    for event_child in event_xml_tag:
        tag_name = event_child.tag.split('}', 1)[1]
        if tag_name == "EventData":
            data = {}
            data["Other"] = []
            for datum in event_child:
                if 'Name' not in datum.attrib:
                    try:
                        data["Other"].append(str(text_value(datum.text)))
                    except UnicodeEncodeError:
                        print "Unicode error encountered. Skipping event..."
                        continue
                else:
                    datum_name = datum.attrib['Name']
                    del datum.attrib['Name'] # Don't want this twice
                    if datum_name == "IpPort" and datum.text == "-":
                        data[datum_name] = -1 # Assign an invalid port number so that we know it was empty
                    elif datum_name == "IpAddress" and datum.text == "-":
                        data[datum_name] = "0.255.255.255" # Assign an invalid address so that we know it was empty
                    else:
                        data[datum_name] = text_value(datum.text)
            data["Other"] = "\n".join(data["Other"])
            event["Data"] = data
        else:
            event[tag_name] = to_json(event_child)

    return event

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage " + sys.argv[0] + " <evtx XML file> <output file>"
    
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()
    
    with open(sys.argv[2], "w") as json_file:
        for child in root:
            event_json_str = json.dumps(event_to_json(child))
            json_file.write(event_json_str + "\n")
    
