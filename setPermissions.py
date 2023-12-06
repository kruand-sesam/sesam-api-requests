import envVarChecker
import os
import requests
import sesamutils
import json
import datetime

logger = sesamutils.sesam_logger('getPermissions', timestamp=True)

if not envVarChecker.checkEnvironmentVariables():
	logger.fatal("Missing required Environment Variables")
	exit(1)

CONFIG = {
    "node": os.environ.get("SESAM_NODE_URL"),
    "jwt": os.environ.get("SESAM_NODE_JWT"),
    "subid": os.environ.get("SESAM_SUBID"),
    "role": "UNproject"
}

snapshotsDir = "tmp/permission-runs"
if not os.path.exists(snapshotsDir):
    os.makedirs(snapshotsDir)

headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {CONFIG["jwt"]}'
}

# Possible permission values: 'run_pump_operation', 'read_config', 'write_config', 'write_data', 'read_data'
newPermissions = ["read_config", "read_data"]

pipes = []
tmpFile = os.path.join("tmp", "pipes.txt")
with open(tmpFile, "r") as f:
  while True:
    line = f.readline().replace("\n", "")
    if not line:
      break
    pipes.append(line)

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

for pipeName in pipes:
  try:
    print(f'\nStart updating pipe {pipeName}\n')
    url = f'https://{CONFIG["node"]}/api/permissions/pipes/{pipeName}'

    response = requests.request("GET", url, headers=headers)

    permissions = json.loads(response.text)["local"]
    print(f'Existing permissions in the pipe:\n{permissions}\n')

    # Write a snapshot of how permissions looked before modification, in case of need for rollback
    dirName = f'{snapshotsDir}/{timestamp}'
    if not os.path.exists(dirName):
        os.makedirs(dirName)

    with open(os.path.join(dirName, f'{pipeName}.before.json'), "w") as f:
      f.writelines(json.dumps(permissions))

    payloadList = []
    doRoleExist = False

    # example of list element of the permissions: ['allow', ['754ae017-d674-486d-9c17-bde175c5ba3c_testrole'], ['read_config', 'read_data']]
    for l in permissions:
      if type(l) == list and l[0] == "allow" and CONFIG["subid"] in l[1][0] and CONFIG["role"] == l[1][0].split("_")[1]:
        # Maintain existing permissions if the pipe already has configured permissions for the Group
        print(f'Existing permissions for group {CONFIG["role"]}:\n{str(l)}\n')
        newPermissionsInnerValues = list(set().union(l[2], newPermissions))
        newPermissionsList = ['allow', [f'{CONFIG["subid"]}_{CONFIG["role"]}'], newPermissionsInnerValues]
        print(f'New Permissions for group {CONFIG["role"]}:\n{newPermissionsList}\n')
        payloadList.append(newPermissionsList)
        doRoleExist = True

      else:
        payloadList.append(l)

    if not doRoleExist:
        # Add the group as new permission row
        newPermissionsList = ['allow', [f'{CONFIG["subid"]}_{CONFIG["role"]}'], newPermissions]
        payloadList.append(newPermissionsList)

    payload = json.dumps(payloadList)

    print(f'Payload List:\n{payload}\n')

    # Snapshot of what is to be posted to the pipe permissions
    with open(os.path.join(dirName, f'{pipeName}.to-be-posted.json'), "w") as f:
      f.writelines(payload)

    # PUT the new permissions to the pipe

    # Using request json=payloadList as shorthand for using 'Content-Type': 'application/json'
    response = requests.request("PUT", url, headers=headers, json=payloadList)

    print(response.text)
    print(f'Finished updating pipe {pipeName}\n========================\n\n')
  except BaseException as e:
     print(f'!!! ERROR updating pipe {pipeName}:\n{str(e)}')
     logger.exception(e)
     exit(1)
