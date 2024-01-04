import envVarChecker
import os
import requests
import sesamutils
import time

logger = sesamutils.sesam_logger('commit-circuit-breaker', timestamp=True)

if not envVarChecker.checkEnvironmentVariables():
	logger.fatal("Missing required Environment Variables")
	exit(1)

CONFIG = {
    "node": os.environ.get("SESAM_NODE_URL"),
    "jwt": os.environ.get("SESAM_NODE_JWT")
}

url = f'https://{CONFIG["node"]}/api'

payload = ""
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {CONFIG["jwt"]}'
}
pipes = []
tmpFile = os.path.join("tmp", "pipes.txt")
with open(tmpFile, "r") as f:
  while True:
    line = f.readline().replace("\n", "")
    if not line:
      break
    pipes.append(line)

for pipe in pipes:
  print(f'Committing circuit breaker for: {pipe}')
  payload = {'operation': 'commit-circuit-breaker'}
  response = requests.request("POST", f'{url}/datasets/{pipe}', headers=headers, data=payload)
  print(response.text)
  time.sleep(1)
  payload = {'operation': 'start'}
  response = requests.request("POST", f'{url}/pipes/{pipe}/pump', headers=headers, data=payload)
  print(f'RUN STATUS: {str(response.status_code)}')