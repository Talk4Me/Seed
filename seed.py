import requests
import csv
import StringIO
import copy
import json

SHEET_URL = "https://docs.google.com/spreadsheets/d/1wcafLIbIbmHAo9Gglp3xGc7RIzxoQEBAbyn_OM4KlVU/export?format=csv"
FIREBASE_URL = "https://chatdb-80b85.firebaseio.com/Messages.json"

def skip(row):
	if row[0] == "id":
		return True
	return False

# get data from google sheets
raw_text = requests.get(SHEET_URL).text

f = StringIO.StringIO(raw_text)
reader = csv.reader(f, delimiter=',')

conversation_rows = []
block = None
for row in reader:
	if skip(row):
		continue

	if row[0] != "":
		if (block != None):
			conversation_rows.append(copy.copy(block))
		block = []

	block.append(row)
conversation_rows.append(copy.copy(block))	

result = []
for convo_rows in conversation_rows:
	convo_dict = {}
	convo_dict["id"] = convo_rows[0][0]
	convo_dict["source"] = convo_rows[0][1]
	convo_dict["user"] = convo_rows[0][2]

	messages = []
	sent = False
	for row in convo_rows[1:]:
		message = {}
		message["MessageBody"] = row[3]
		message["Timestamp"] = row[4]
		message["Sent"] = sent
		sent = not sent
		messages.append(message)

	convo_dict["Messages"] = messages
	result.append(convo_dict)

seed_data = json.dumps(result) 

# kill the database
requests.delete(FIREBASE_URL)

# write the seed data to the database
requests.put(FIREBASE_URL, seed_data)



