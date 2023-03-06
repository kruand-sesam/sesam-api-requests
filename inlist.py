entitiesFromIfs = []
with open("tmp/id.txt", "r") as f:
    while(True):
        line = f.readline().replace("\n", "")
        if not line:
            break
        entitiesFromIfs.append(line)

kraftstasjoner = []
with open("tmp/kraftstasjoner.txt", "r") as f:
    while(True):
        line = f.readline().replace("\n", "")
        if not line:
            break
        kraftstasjoner.append(line)

for id in entitiesFromIfs:
    if id in kraftstasjoner:
        print(id)