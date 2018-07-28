import tabula
import re

page = 1
keywords = ["income", "revenue", "expense", "profit", "cost"]


df = tabula.read_pdf("annual_reports/ubs2.pdf",
                         encoding='cp1252',
                         output_format="json",
                         pages=page,area=[0,0,1000,1000])#, options={'pages': 169})


def isItNumber(text):
    # TODO: More currencies
    text = text.replace(",","").replace("$","").replace(" ","").replace("%","").replace(u"\xA3","").replace("(","").replace(")","")
    try:
        a = float(text)
        return True
    except:
        return False

def isDate(text):
    reg = re.findall("^[12][0-9]{3}$", text.strip())
    if len(reg) > 0:
        return True
    else:
        return False

def currencySymbolCheck(text):
    currencyList = ["$", u"\xA3", "USD", "CHF", "GBP", "YEN"]
    for c in currencyList:
        if text.strip() == c:
            return True
    return False


def cluster(data, maxgap):
    '''Arrange data into groups where successive elements
       differ by no more than *maxgap*'''
    data.sort()
    groups = [[data[0]]]
    for x in data[1:]:
        if abs(x - groups[-1][-1]) <= maxgap:
            groups[-1].append(x)
        else:
            groups.append([x])
    return groups


# --- MERGE COLUMNS WHICH HAVE EMPTY HEADERS ---
listOfMerges = []
for col in range(0, len(df[0]["data"][0]) - 1):
    columnToMerge = False
    if df[0]["data"][0][col]["text"] == "":
        numberCount = 0
        totalNonEmpty = 0
        for row in range(0, len(df[0]["data"])):
            if currencySymbolCheck(df[0]["data"][row][col]["text"]): numberCount += 1
            if df[0]["data"][row][col]["text"] != "": totalNonEmpty += 1
        ratio = float(numberCount) / totalNonEmpty if totalNonEmpty != 0 else 0
        if ratio > 0.5:
            columnToMerge = True
            listOfMerges.append(col)

    if columnToMerge:
        for row in range(0, len(df[0]["data"])):
            df[0]["data"][row][col + 1]["text"] = df[0]["data"][row][col]["text"] + df[0]["data"][row][col + 1]["text"]
            df[0]["data"][row][col]["text"] = ""


# --- DELETE COLUMNS ON THE LEFT OF ROW LABELS === OUTCOME IS startColumn
startColumn = 0
for col in range(0, len(df[0]["data"][0])):
    numberCount = 0
    totalNonEmpty = 0
    for rows in df[0]["data"]:
        if isItNumber(rows[col]["text"]): numberCount += 1
        if rows[col]["text"] != "": totalNonEmpty += 1
    ratio = float(numberCount) / totalNonEmpty if totalNonEmpty != 0 else 0
    #print "column " + str(col) + " " + str()
    if ratio > 0.5:
        #print "Column " + str(col) + " is numerical"
        for d in range(0, col - 1 - len([i for i in listOfMerges if i < col])):
            # DELETE COLUMN
            for r in range(0, len(df[0]["data"])):
                df[0]["data"][r][d]["text"] = " - "
        startColumn = col - 1 - len([i for i in listOfMerges if i < col])
        break

# --- DELETE COLUMNS ON THE RIGHT OF THE TABLE === OUTCOME IS lastColumn
lastColumn = len(df[0]["data"][0]) - 1
for col in range(len(df[0]["data"][0]) - 1, 0, -1):
    numberCount = 0
    totalNonEmpty = 0
    for rows in df[0]["data"]:
        if isItNumber(rows[col]["text"]): numberCount += 1
        if rows[col]["text"] != "" and rows[col]["text"] != " - ": totalNonEmpty += 1
    ratio = float(numberCount) / totalNonEmpty if totalNonEmpty != 0 else 0
    if ratio < 0.3:
        for r in range(0, len(df[0]["data"])):
            df[0]["data"][r][col]["text"] = " - "
    else:
        lastColumn = col + 1 #+ len([i for i in listOfMerges if i > col])
        break

# --- FIGURE OUT FIRST ROW WITH NUMBERS === OUTCOME IS firstNumbersRow ALSO listOfNumericalRows
firstNumbersRow = 0
listOfNumericalRows = []
foundLabel = False
for row in range(0, len(df[0]["data"])):
    numberCount = 0
    totalNonEmpty = 0
    for col in range(startColumn + 1, lastColumn):
        for numb in df[0]["data"][row][col]["text"].split(" "):
            # TODO: "$" is considered non empty but not a number
            if isItNumber(numb) and not isDate(numb): numberCount += 1
            if numb != "" and numb != " - ": totalNonEmpty += 1
    ratio = float(numberCount) / totalNonEmpty if totalNonEmpty != 0 else 0
    if ratio > 0.4:
        if not foundLabel:
            firstNumbersRow = row
            foundLabel = True
        listOfNumericalRows.append(row)
    elif foundLabel:
        for col in range(0, len(df[0]["data"][0])):
            df[0]["data"][row][col]["text"] = " - "


print "First number row: %s" % firstNumbersRow
print "First column: %s" % startColumn
print "Last column: %s" % lastColumn



# --- GET A LIST OF RIGHT SIDE LOCATIONS FOR EACH CELL
listOfRightValues = []
listOfCells = []
r_it = 0
for r in listOfNumericalRows:
    for col in range(startColumn + 1, lastColumn):
        cell = df[0]["data"][r][col]

        # Sometimes Tabula doesn't return coordinates - in that case - use row above
        if cell["text"] != "" and cell["left"] == 0.0 and cell["width"] == 0.0:
            if " " not in cell["text"]:
                for previous_row_it in range(r_it - 1, 0, -1):
                    if df[0]["data"][listOfNumericalRows[previous_row_it]][col]["left"] != 0.0:
                        listOfRightValues.append(df[0]["data"][listOfNumericalRows[previous_row_it]][col]["left"] + df[0]["data"][listOfNumericalRows[previous_row_it]][col]["width"])
                        listOfCells.append([df[0]["data"][listOfNumericalRows[previous_row_it]][col]["left"] + df[0]["data"][listOfNumericalRows[previous_row_it]][col]["width"], cell["text"]])
                        break
            else:
                # TODO: Fix this problem
                if " - " not in cell["text"]:
                    print " !!!! TABULA COORDINATES ERROR !!!!"


        if cell["text"] != "" and (cell["left"] != 0.0 and cell["width"] != 0.0):
            previousLeft = cell["left"]
            fullStr = cell["text"]

            # If single cell value
            if " " not in fullStr:
                listOfRightValues.append(cell["left"] + cell["width"])
                listOfCells.append([cell["left"] + cell["width"], cell["text"]])
            # If multi cell value - split
            else:
                # TODO: In some casses not accurate - e.g. "12 54      10"
                chunks = fullStr.split(" ")
                # FORMULA for width of a number = height * (0.81 * digits + 0.41 * commas + 0.2)
                # ignoring ")" bracket because it's usually shifted
                firstChunkWidth = cell["height"] * (0.81 * len(re.findall("[\d\(\-\+\$]", chunks[0])) + 0.41 * (chunks[0].count(".") + chunks[0].count(",")) + 0.2)
                listOfRightValues.append(cell["left"] + firstChunkWidth)
                listOfCells.append([cell["left"] + firstChunkWidth, chunks[0]])
                previousLeft = cell["left"] + firstChunkWidth
                chunks = chunks[1:]
                singleCellWidth = float(cell["width"] - firstChunkWidth) / len(chunks)
                for chunk in chunks:
                    right = previousLeft + singleCellWidth
                    previousLeft = right
                    listOfRightValues.append(right)
                    listOfCells.append([right, chunk])
    r_it += 1

# --- CLUSTER COLUMN RIGHTS ---
cellsCluster = cluster(listOfRightValues, maxgap=5)
#print cellsCluster





for c in cellsCluster:
    if len(c) > 2:
        print ">>" + str(float(sum(c)) / len(c))
        for a in range(0, len(listOfCells)):
            if listOfCells[a][0] < (float(sum(c)) / len(c) + 4):
                print listOfCells[a][1]
                listOfCells[a][0] = 10000



# --- CHECK AND FIX MERGED COLUMNS WITH SPACES BETWEEN THEM ---
# for col in range(startColumn + 1, len(df[0]["data"][0])):
#     numberCount = 0
#     totalNonEmpty = 0
#     for row in range(labelRow + 1, len(df[0]["data"])):
#         if " " in df[0]["data"][row][col]["text"]: numberCount += 1
#         if df[0]["data"][row][col]["text"] != "": totalNonEmpty += 1
#     ratio = float(numberCount) / totalNonEmpty if totalNonEmpty != 0 else 0
#     if ratio > 0.8:
#         for row in range(0, len(df[0]["data"])):
#             df[0]["data"][row][col]["text"] = df[0]["data"][row][col]["text"].replace(" ", " | ")



# --- PRINT OUT ----
for row in df[0]["data"]:
    line = ""
    for col in row:
        line += col["text"] + " | "
    print line