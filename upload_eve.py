import sys
import requests
import json

# Play with this to find a sweet spot
MAX_REQUEST_SIZE = 2000000

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: " + sys.argv[0] + " <eve file> <index name>"
        sys.exit(1) 


    eve = open(sys.argv[1], "r")
    index = sys.argv[2]
    request_body = ""

    request_url = "http://localhost:9200/" + index + "/_bulk"

    print "Counting lines in " + sys.argv[1]
    line_count = 0
    for line in eve:
        line_count += 1
    print "Number of lines in " + sys.argv[1] + ": " + str(line_count)

    action_map = {}
    line_index = 0
    for line in eve:
        line_index = line_index + 1

        try:
            event = json.loads(line)
        except ValueError:
            print "ValueError encountered. Skipping line " + str(line_index)
            continue

        if len(request_body) >= MAX_REQUEST_SIZE:
            print 'Sending request of size ' + str(len(request_body)) + " (line " + str(line_index) + "/" + str(line_count) ")"
            r = requests.put(request_url, data=request_body)
            print r
            request_body = ""

        if event["event_type"] not in action_map:
            action_map[event["event_type"]] = "{\"index\": {\"_type\":\"" + event["event_type"] + "\"}}\n"
        
        index_json = action_map[event["event_type"]]
        request_body += index_json + line + "\n"

    if len(request_body) > 0:
        print 'Sending request of size ' + str(len(request_body)) + " (line " + str(line_index) + "/" + str(line_count) ")"
        r = requests.put(request_url, data=request_body)
        print r
