# Sample Projects

### graph-viz
A quick test of a Viz visualisation library. It's purpose was to establish if displaying document data in graph structures can be used in front end. To run, open `index.html` in browser.

### tables
Experiments on data extraction from PDFs containing tables of numerical data. Using a number of different techniques to clean up the data.
- `analyseTable.py` - extract data from a specific area of a specific page
- `findTables.py` - find all tables on a specific page
- `extractTableData.py` - find tables on all pages and build a list of all of the metrics uses (net revenue, costs, headcont, etc.)

You can run the scripts without any arguments.

### comparePPT
Check the diff between two PowerPoint presentations. Returns a list of diffs by page.

### seqPrediction
An neural nets experiment in Bitcoin price prediction. To build a model, create Book1.csv with prices in column A. This will create a model `trainingData`. Once model exists, the script will use `lastDay.csv` to get data for classification. From that, the precition is made.