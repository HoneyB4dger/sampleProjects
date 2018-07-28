from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer


#######################################################################
#                                                                     #
# TODO: Titles of Tables (e.g. ubs page 18, 14)                       #
# TODO: Multiline row labels                                          #
# TODO: Multi level column labels                                     #
# TODO: Inlcude "millions", "billions" noted near the table           #
# TODO: Ubs page 17 - Tabula not picking up the table?                #
#                                                                     #
#######################################################################


pageToAnalyse = 89
path = 'annual_reports/gs.pdf'

def isItNumber(text):
    # TODO: More currencies
    text = text.replace(",","").replace("$","").replace(" ","").replace("%","").replace(u"\xA3","").replace("(","").replace(")","")
    try:
        a = float(text)
        return True
    except:
        return False


fp = open(path, 'rb')

# Create a PDF parser object associated with the file object.
parser = PDFParser(fp)

# Create a PDF document object that stores the document structure.
# Password for initialization as 2nd parameter
document = PDFDocument(parser)

# Check if the document allows text extraction. If not, abort.
if not document.is_extractable:
    raise PDFTextExtractionNotAllowed

# Create a PDF resource manager object that stores shared resources.
rsrcmgr = PDFResourceManager()

# Create a PDF device object.
device = PDFDevice(rsrcmgr)

# BEGIN LAYOUT ANALYSIS
# Set parameters for analysis.
laparams = LAParams()

# Create a PDF page aggregator object.
device = PDFPageAggregator(rsrcmgr, laparams=laparams)

# Create a PDF interpreter object.
interpreter = PDFPageInterpreter(rsrcmgr, device)
listOfTextBlocks = []

def parse_obj(lt_objs, page):

    # loop over the object list
    for obj in lt_objs:

        # if it's a textbox, print text and location
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            listOfTextBlocks.append({"text": obj.get_text().replace('\n', '_'),
                                     "x": obj.bbox[0],
                                     "y": layout.height - obj.bbox[3],
                                     "xMax": obj.bbox[2],
                                     "yMax": layout.height - obj.bbox[1],
                                     "page": str(page)})

        # if it's a container, recurse
        elif isinstance(obj, pdfminer.layout.LTFigure):
            parse_obj(obj._objs, page)

# loop over all pages in the document
for pageNumber, page in enumerate(PDFPage.create_pages(document)):

    if pageNumber == pageToAnalyse - 1:
        # read the page into a layout object
        interpreter.process_page(page)
        layout = device.get_result()

        # extract text from this object
        parse_obj(layout._objs, pageNumber)

listOfTextBlocks = sorted(listOfTextBlocks, key=lambda k: k['y'])
listOfTableBlocks = []

for i in range(0, len(listOfTextBlocks)):
    numberCount = 0
    totalNonEmpty = 0
    for chunk in listOfTextBlocks[i]["text"].split("_"):
        if isItNumber(chunk): numberCount += 1
        if chunk != "" and chunk != " - ": totalNonEmpty += 1
    ratio = float(numberCount) / totalNonEmpty if totalNonEmpty != 0 else 0
    #print listOfTextBlocks[i]["text"]
    if ratio > 0.4 and len(listOfTextBlocks[i]["text"].split("_")) > 2:
        #print listOfTextBlocks[i]["text"]
        if i > 0 and listOfTextBlocks[i - 1] not in listOfTableBlocks:
            listOfTableBlocks.append(listOfTextBlocks[i - 1])
        listOfTableBlocks.append(listOfTextBlocks[i])

maxX = 0
maxY = 0
minX = 10000
minY = 10000
for b in listOfTableBlocks:
    #print b
    if b["x"] < minX: minX = b["x"]
    if b["xMax"] > maxX: maxX = b["xMax"]
    if b["y"] < minY: minY = b["y"]
    if b["yMax"] > maxY: maxY = b["yMax"]

maxX += 10
maxY += 10
minX -= 10
minY -= 10

print "x: " + str(minX)
print "y: " + str(minY)
print "maxX: " + str(maxX)
print "maxY: " + str(maxY)



import tabula
import re


df = tabula.read_pdf(path,
                         encoding='cp1252',
                         output_format="json",
                         pages=pageToAnalyse,area=[minY,minX,maxY,maxX])#(top,left,bottom,right)


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
        account = df[0]["data"][r][startColumn]["text"]

        # Sometimes Tabula doesn't return coordinates - in that case - use row above
        if cell["text"] != "" and cell["left"] == 0.0 and cell["width"] == 0.0:
            if " " not in cell["text"]:
                for previous_row_it in range(r_it - 1, 0, -1):
                    if df[0]["data"][listOfNumericalRows[previous_row_it]][col]["left"] != 0.0:
                        listOfRightValues.append(df[0]["data"][listOfNumericalRows[previous_row_it]][col]["left"] + df[0]["data"][listOfNumericalRows[previous_row_it]][col]["width"])
                        listOfCells.append([df[0]["data"][listOfNumericalRows[previous_row_it]][col]["left"] + df[0]["data"][listOfNumericalRows[previous_row_it]][col]["width"], cell["text"], account])
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
                listOfCells.append([cell["left"] + cell["width"], cell["text"], account])
            # If multi cell value - split
            else:
                # TODO: In some casses not accurate - e.g. "12 54      10"
                chunks = fullStr.split(" ")
                # FORMULA for width of a number = height * (0.81 * digits + 0.41 * commas + 0.2)
                # ignoring ")" bracket because it's usually shifted
                firstChunkWidth = cell["height"] * (0.81 * len(re.findall("[\d\(\-\+\$]", chunks[0])) + 0.41 * (chunks[0].count(".") + chunks[0].count(",")) + 0.2)
                listOfRightValues.append(cell["left"] + firstChunkWidth)
                listOfCells.append([cell["left"] + firstChunkWidth, chunks[0], account])
                previousLeft = cell["left"] + firstChunkWidth
                chunks = chunks[1:]
                singleCellWidth = float(cell["width"] - firstChunkWidth) / len(chunks)
                for chunk in chunks:
                    right = previousLeft + singleCellWidth
                    previousLeft = right
                    listOfRightValues.append(right)
                    listOfCells.append([right, chunk, account])
    r_it += 1

# --- CLUSTER COLUMN RIGHTS ---
cellsCluster = cluster(listOfRightValues, maxgap=5)
#print cellsCluster

# --- LIST WORDS WHICH MAKE UP COLUMN LABELS ---
columnLabelChunks = []
for col in range(startColumn + 1, lastColumn):
    # TODO: Need to split into chunks if merged columns
    columnLabelChunks.append([df[0]["data"][firstNumbersRow - 1][col]["left"] + \
                             df[0]["data"][firstNumbersRow - 1][col]["width"],
                             df[0]["data"][firstNumbersRow - 1][col]["text"]])


for c in cellsCluster:
    if len(c) > 2:
        print ">>>>>>>>>>>>>>>>" + str(float(sum(c)) / len(c))
        columnLabel = ""
        for a in range(0, len(columnLabelChunks)):
            if columnLabelChunks[a][0] < (float(sum(c)) / len(c) + 4):
                columnLabel += columnLabelChunks[a][1]
                columnLabelChunks[a][0] = 10000
        print ">>>>>>>>>>>>>>>>" + columnLabel

        for a in range(0, len(listOfCells)):
            if listOfCells[a][0] < (float(sum(c)) / len(c) + 4):
                print listOfCells[a][1] + " " + listOfCells[a][2]
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
# for row in df[0]["data"]:
#     line = ""
#     for col in row:
#         line += col["text"] + " | "
#     print line