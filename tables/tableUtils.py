import tabula


def cleanUpTheTable(df):
    def isItNumber(text):
        # TODO: More currencies
        text = text.replace(",","").replace(".","").replace("$","").replace(u"\xA3","")
        try:
            a = int(text)
            return True
        except:
            return False

    def currencySymbolCheck(text):
        currencyList = ["$", u"\xA3", "USD", "CHF", "GBP", "YEN"]
        for c in currencyList:
            if text.strip() == c:
                return True
        return False

    # --- MERGE COLUMNS WHICH HAVE EMPTY HEADERS ---
    listOfMerges = []
    for col in range(0, len(df["data"][0]) - 1):
        columnToMerge = False
        if df["data"][0][col]["text"] == "":
            numberCount = 0
            totalNonEmpty = 0
            for row in range(0, len(df["data"])):
                if currencySymbolCheck(df["data"][row][col]["text"]): numberCount += 1
                if df["data"][row][col]["text"] != "": totalNonEmpty += 1
            ratio = float(numberCount) / totalNonEmpty if totalNonEmpty != 0 else 0
            if ratio > 0.5:
                columnToMerge = True
                listOfMerges.append(col)


        if columnToMerge:
            for row in range(0, len(df["data"])):
                df["data"][row][col + 1]["text"] = df["data"][row][col]["text"] + df["data"][row][col + 1]["text"]
                df["data"][row][col]["text"] = ""


    # --- DELETE COLUMNS ON THE LEFT OF ROW LABELS ---
    for col in range(0, len(df["data"][0])):
        numberCount = 0
        totalNonEmpty = 0
        for rows in df["data"]:
            if isItNumber(rows[col]["text"]): numberCount += 1
            if rows[col]["text"] != "": totalNonEmpty += 1
        ratio = float(numberCount) / totalNonEmpty if totalNonEmpty != 0 else 0
        #print "column " + str(col) + " " + str()
        if ratio > 0.5:
            #print "Column " + str(col) + " is numerical"
            for d in range(0, col - 1 - len([i for i in listOfMerges if i < col])):
                # DELETE COLUMN
                for r in range(0, len(df["data"])):
                    df["data"][r][d]["text"] = " - "
            break

    return df