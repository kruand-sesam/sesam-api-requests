import envVarChecker
import requests
import json
import os
import sesamutils

logger = sesamutils.sesam_logger('getPermissions', timestamp=True)


CONFIG = {
    "node": os.environ.get("SESAM_NODE_URL"),
    "jwt": os.environ.get("SESAM_NODE_JWT"),
    "subid": os.environ.get("SESAM_SUBID"),
    "role": "UNproject",
    "pipespath": os.path.abspath("/Users/andreas/Sesam/Elvia/Apps/master-node-2/node/pipes")
}

headers = {
  'Content-Type': 'application/json',
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

for pipeName in pipes:
  try:
    
    url = f'https://{CONFIG["node"]}/api/pipes/{pipeName}/config?force=false'
    pathToPipe = f'{CONFIG["pipespath"]}/{pipeName}.conf.json'
    print(f'\nDeploying pipe {pathToPipe} \nto URL {url}\n\n')
    pipeConfig = ""
    with open(pathToPipe, "r") as f:
      pipeConfig = json.load(f)

    #print(pipeConfig)
    response = requests.request("PUT", f'{url}', headers=headers, data=json.dumps(pipeConfig))
    print(f'RESPONSE:\n{response.text}\n\n')
  except BaseException as e:
    print(f'!!! ERROR updating pipe {pipeName}:\n{str(e)}')
    logger.exception(e)
    exit(1)
