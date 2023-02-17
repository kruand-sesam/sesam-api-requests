import envVarChecker
import json
import os
import subprocess
import requests
import requests.structures
import sesamutils

logger = sesamutils.sesam_logger('createCSVFiles', timestamp=True)

if not envVarChecker.checkEnvironmentVariables():
	logger.fatal("Missing required Environment Variables")
	exit(1)

CONFIG = {
    "node": os.environ.get("SESAM_NODE_URL"),
    "jwt": os.environ.get("SESAM_NODE_JWT")
}

tmpFile = os.path.join("tmp", "pipes")
url = "/api/pipes?verbose=false&fields=config&include-internal-pipes=false"
headers = requests.structures.CaseInsensitiveDict()
headers["Authorization"] = "Bearer " + CONFIG["jwt"]
url = CONFIG["node"] + url
logger.info(f'Getting all pipe names for ArcGIS UN globals from URL:  {url}')
pipes = ""
try:
    r = requests.get(url, headers=headers)
    r.raise_for_status()

    pipes = json.loads(r.content.decode("utf-8"))  
    with open(tmpFile + ".json", "w") as jsonOut:        
        jsonOut.write(json.dumps(pipes))  

except requests.exceptions.HTTPError as e:
    logger.exception(f'HTTPError on {url} - HTTP code {r.status_code} - {str(e)}')
except ValueError as e:
    logger.exception(e)
except AttributeError as e:
    logger.exception(f'AttributeError on {url} - No pipe names found from the JQ operation - {str(e)}')
except Exception as e:
    logger.exception(f'Exception  on {url} - HTTP code {r.status_code} - {str(e)}')

"""
jq = f'jq ".[] | select(.config.original.source.alternatives.prod.dataset == \\"kafka-ni-ifs-equipmentfunctional-raw\\")? | ._id" {tmpFile}.json'
process = subprocess.Popen(jq, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)

pipesIfs = process.stdout.read()
pipesIfs = pipesIfs.replace('"', "").split("\n") # Create python list from each line, remove quotes
pipesIfs = list(set(pipesIfs)) # Keep only unique values by using set()
pipesIfs = list(filter(None, pipesIfs))  # Remove empty list elements
pipesIfs.sort()
pipesIfs.insert(0, "kafka-ni-ifs-equipmentfunctional-raw")
"""

jq = f'jq ".[] |  select(._id | startswith(\\"kafka-ni-arcgisun\\")) | ._id" tmp/pipes.json'
process = subprocess.Popen(jq, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)

pipesKafkaUN = process.stdout.read()
pipesKafkaUN = pipesKafkaUN.replace('"', "").split("\n") # Create python list from each line, remove quotes
pipesKafkaUN = list(set(pipesKafkaUN)) # Keep only unique values by using set()
pipesKafkaUN = list(filter(None, pipesKafkaUN))  # Remove empty list elements
pipesKafkaUN.sort()

jq = 'jq ".[] | select([.config.effective.metadata.tags[] == \\"ArcGIS-UN\\"]? | any) | ._id" tmp/pipes.json'
process = subprocess.Popen(jq, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)

pipesArcGISUN = process.stdout.read()
pipesArcGISUN = pipesArcGISUN.replace('"', "").split("\n") # Create python list from each line, remove quotes
pipesArcGISUN = list(set(pipesArcGISUN)) # Keep only unique values by using set()
pipesArcGISUN = list(filter(None, pipesArcGISUN))  # Remove empty list elements
pipesArcGISUN.sort()

pipes = pipesKafkaUN + pipesArcGISUN

with open(tmpFile + ".txt", "w") as jsonOut:
    jsonOut.write('\n'.join(pipes))