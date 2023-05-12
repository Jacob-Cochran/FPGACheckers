## JUST FOR MOCKING ##
with open("mockGrid.txt", "r") as f:
    code = f.readline().strip()
    gridMock = ""
    for line in f.readlines():
        gridMock += line.strip().replace(", ", ",")
communicationResult = code + "\n" + gridMock
print(communicationResult)
## END MOCKING ##