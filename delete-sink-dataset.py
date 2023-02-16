import envVarChecker
import os
import requests
import sesamutils
import time

logger = sesamutils.sesam_logger('delete-sink-datasets', timestamp=True)

if not envVarChecker.checkEnvironmentVariables():
	logger.fatal("Missing required Environment Variables")
	exit(1)

CONFIG = {
    "node": os.environ.get("SESAM_NODE_URL"),
    "jwt": os.environ.get("SESAM_NODE_JWT")
}

url = f'{CONFIG["node"]}/api/datasets/'

payload = ""
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {CONFIG["jwt"]}'
}
pipes = []
with open("pipes.txt", "r") as jsonOut:
  pipes = jsonOut.read()
  pipes = pipes.split("\n") # Create python list from each line, remove quotes
  pipes = list(filter(None, pipes))  # Remove empty list elements

for pipe in pipes:
  print("Press anything to process:" + pipe)
  #input()
  response = requests.request("DELETE", f'{url}{pipe}', headers=headers, data=payload)
  print(response)
  time.sleep(2)