#from tabula import read_pdf
import tabula

from tableUtils import cleanUpTheTable

page = 18
keywords = ["income", "revenue", "expense", "profit", "cost"]



def getApproximateStringWidth(st, fullStr, width):
    size1 = 0.0
    for s in st:
        if s in 'lij|\' ': size1 += 37
        elif s in '![]fI.,:;/\\t': size1 += 50
        elif s in '`-(){}r"': size1 += 60
        elif s in '*^zcsJkvxy': size1 += 85
        elif s in 'aebdhnopqug#$L+<>=?_~FZT1234567890' : size1 += 95
        elif s in 'BSPEAKVXY&UwNRCHD': size1 += 112
        elif s in 'QGOMm%W@': size1 += 135
        else: size1 += 50
    size2= 0.0
    for s in fullStr:
        if s in 'lij|\' ': size2 += 37
        elif s in '![]fI.,:;/\\t': size2 += 50
        elif s in '`-(){}r"': size2 += 60
        elif s in '*^zcsJkvxy': size2 += 85
        elif s in 'aebdhnopqug#$L+<>=?_~FZT1234567890' : size2 += 95
        elif s in 'BSPEAKVXY&UwNRCHD': size2 += 112
        elif s in 'QGOMm%W@': size2 += 135
        else: size2 += 50

    return int(size1 / size2 * width)

while page > 0:
    print "="*70
    print "Page: %s" % page
    df = tabula.read_pdf("annual_reports/ubs.pdf",
                         encoding='cp1252',
                         output_format="json",
                         pages=page)#, options={'pages': 169})


    for df_table in df: # TABLES

        # --- CLEAN UP THE TABLE ---
        df_table = cleanUpTheTable(df_table)

        columnsDict = {}
        columnHeadersBag = []
        columnsFound = False
        r = 0
        columnLastRow = False
        for a in df_table["data"]: # ROWS
            i = 0
            n_itr = 0
            for b in a: # NUMBERS WITHIN ROW - "COLUMNS"
                # print str(b["left"] + b["width"]) + " |||| " + str(b["text"])
                if i > 0: # NON FIRST COLUMN
                    left = int(b["left"])
                    width = int(b["width"])
                    textNum = str(b["text"].encode('utf-8').strip())
                    if textNum != "":
                        letterLen = width / len(textNum)
                    else:
                        letterLen = 0
                    numbers = textNum.split(" ")
                    previousLeft = left
                    n_itr -= 1
                    for n in numbers: # ADDITIONAL ITERATION BASED ON SPACES
                        n_itr += 1
                        if textNum != "":
                            # TODO: This might *sometimes* not be accurate, in cases like "UBS    Bank Barclays"
                            offset = getApproximateStringWidth(n, textNum, width)
                            right = previousLeft + offset
                            previousLeft = right + 3
                        else:
                            right = left
                        # right = left + (len(n) * letterLen)
                        if columnLastRow: # SET UP COLUMNS
                            columnHeaderTmpStr = ""
                            h = 0
                            for c in columnHeadersBag:
                                if c[0] < columnStart + ((i + n_itr) * columnWidth) + 10: #(right + 12):
                                    columnHeaderTmpStr += c[1] + " "
                                    columnHeadersBag[h][0] = 10000
                                    #columnHeadersBag.pop(h)
                                    #h -= 1
                                h += 1
                            columnHeaderTmpStr += n
                            #columnsDict[right] = str(n)
                            columnsDict[right] = columnHeaderTmpStr.replace("  ", " ").replace("- ", "").strip()
                            print str(right) + " ||| " + str(n)
                        else:
                            pri = False # pri = primary = has got a column header
                            for col in columnsDict:
                                if abs(col - right) < 20:
                                    print columnsDict[col] + " ||| " + str(n)
                                    pri = True
                            if not pri:
                                print str(right) + " ||| " + str(n)
                                if r > 0:
                                    columnHeadersBag.append([right, str(n)])

                        left = right


                else: # FIRST COLUMN IN THE ROW
                    print b["text"]
                    # Check if left most cell is empty or currency amount AND the one below is not (i+1 might error)
                    if ("CHF" in b["text"] or "$" in b["text"] or not b["text"]) and \
                        ("CHF" not in df[0]["data"][r + 1][0]["text"] and "$" not in df[0]["data"][r + 1][0]["text"] and df[0]["data"][r + 1][0]["text"]) and \
                            not columnsFound:
                        columnLastRow = True
                        columnsFound = True # In case there is another table underneath
                        # ------ the new algo calculating column width
                        # TODO: This will only work if the first column is single word and there is a single label column on the left!
                        columnEnd = a[-1]["left"] + a[-1]["width"]
                        totalWidth = columnEnd - (a[1]["left"] + a[1]["width"])
                        # TODO: What if there are multi word column labels (change to first row of numbers)? Different width columns?
                        tot_it = 0
                        for aa in a: # This is so that total number of columns is calculated
                            tot_it += 1 + aa["text"].count(" ")
                        tot_it -= a[0]["text"].count(" ")
                        columnWidth = totalWidth / (tot_it - 2)
                        columnStart = (a[1]["left"] + a[1]["width"]) - columnWidth
                        # --------------------------------------------
                    else:
                        columnLastRow = False
                i += 1
            r += 1
            print ">"
        page += 1

    break

#     #TODO "of which" sublines - need to add extended label
#     #TODO two level column names
#     #TODO "Total" row - should locate title of the table






#print df.iloc[[2]]
#print df.iloc[0]
#print df._slice(slice(0, 0))
#.ix[2] TRANSPOSES THE TABLE
#print list(df)



# print df

# if df and not df.empty:
#    np_df = df.as_matrix()
#    print np_df
# allData = {}
# for row in np_df:
#     i = 0
#     singleRow = {}
#     for col in list(df):
#         if i != 0:
#             for k in keywords:
#                 if k in row[0]:
#                     singleRow[col] = row[i]
#                     break
#         i += 1
#     if singleRow:
#         allData[row[0]] = singleRow
#

#
#     for a in allData:
#         print str(a) + " " + str(allData[a])
#         print " "















