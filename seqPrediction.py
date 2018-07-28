from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets import SupervisedDataSet,UnsupervisedDataSet
from pybrain.structure import LinearLayer
import pandas as pd
import sys
import pickle
import os

# SEQUENCE PREDICTION ! MULTIVARIATE ? FEATURES ?
# MACD, RSI, Volume, Fees,

# data from https://bitcoincharts.com/charts/coinbaseUSD#rg60zig30-minzczsg2018-02-18zeg2018-02-19zm1g10zm2g25

# ds = SupervisedDataSet(21, 21)

# sampleInput = map(int,'1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21'.split())
# sampleOutput = map(int,'21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41'.split())
#
# ds.addSample(sampleInput, sampleOutput)



df = pd.read_csv('Book1.csv', delimiter=',', index_col=None)

inputPrices = [int(x) for x in df.values]
print "Using %s samples" % len(inputPrices)


# THIS USES EVERY TIME STEP AS A TRAINING DATA
ds = SupervisedDataSet(100, 101)
z = inputPrices
obsLen = 100
predLen = 101

verificationSamples = []

print "CREATE TRAINING SAMPLES"
v = 0
for i in xrange(len(z)):
    # b = ("Training " + str(i))
    # sys.stdout.write('\r' + b)
    if i + (obsLen - 1) + predLen + obsLen < len(z):
        sampleI = [z[d] for d in range(i, i + obsLen)]
        sampleO = [z[d] for d in range(i + 1 + obsLen, i + 1 + predLen + obsLen)]
        minimumLevel = min(sampleI + sampleO)
        sampleI = [element - minimumLevel for element in sampleI]
        sampleO = [element - minimumLevel for element in sampleO]
        maximumLevel = max(sampleI)
        sampleI = [element / float(maximumLevel * 2) for element in sampleI]
        sampleO = [element / float(maximumLevel * 2) for element in sampleO]
    if v < 20:
           ds.addSample(sampleI, sampleO)
    else: # take verification sample
        verificationSamples.append([sampleI, sampleO])
        v = 0
    v += 1

print "BUILD MODEL"

if not os.path.exists('trainingData'):
    print "> Calculating a new model and saving to file"
    net = buildNetwork(100, 20, 101, outclass=LinearLayer, bias=True, recurrent=True)
    trainer = BackpropTrainer(net, ds)
    #trainer.trainEpochs(100)
    maxepochs = 50
    for i in range(0, maxepochs):
        sys.stdout.write('\r' + str(i) + " / " + str(maxepochs))
        aux = trainer.train()

    fileObject = open('trainingData', 'w')
    pickle.dump(net, fileObject)
    fileObject.close()
else:
    print "> Using a model from file"
    fileObject = open('trainingData','r')
    net = pickle.load(fileObject)

print "CLASSIFY"

ts = UnsupervisedDataSet(100,)
#input = map(int,'13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33'.split())

df = pd.read_csv('lastDay.csv', delimiter=',', index_col=None)

input = [int(x) for x in df.values]
print "Last day values: %s" % input

minimumLevel = min(input)
maximumLevel = max(input) - minimumLevel
input = [element - minimumLevel for element in input]
input = [element / float(maximumLevel * 2) for element in input]

# ts.addSample(input)
# verID = 175
# input = verificationSamples[verID][0]
# minimumLevel = min(input)
#input = [0.7] * 100
ts.addSample(input)

#output = [ int(round(i)) for i in net.activateOnDataset(ts)[0]]
output = [ i for i in net.activateOnDataset(ts)[0]]

outputReal = [int(round(element * maximumLevel * 2 + minimumLevel)) for element in output]
output = [element + minimumLevel for element in output]
input = [element + minimumLevel for element in input]
print "Prediction: %s" % outputReal

from datetime import datetime, timedelta
timeDelta = datetime.now() + timedelta(hours=50)

print "Price will be $" + str(format(round(outputReal[-1]), ',')) + " on " + str(timeDelta)

# print "VERIFYING"
# diff = 0
# for ver in verificationSamples:
#     ts.addSample(ver[0])
#     checkOutput = [int(round(i)) for i in net.activateOnDataset(ts)[0]]
#     err = 0
#     for i in range(0, len(ver[0])):
#         #print float(ver[1][i]/float(checkOutput[i]))
#         if ver[1][i]/float(checkOutput[i]) > 0.2:
#             err += 1
#     #print err / len(ver[0])
#
# print "Verification diff: %s" % str(diff)

import matplotlib.pyplot as plt
#plt.plot([0] * 21 + output)
#plt.plot(input)
dates = range(1, 101)
plt.scatter(dates, input)
plt.plot(dates, input)

dates = range(101, 202)
plt.scatter(dates, output)
plt.plot(dates, output)

# plt.scatter(dates, verificationSamples[verID][1])
# plt.plot(dates, verificationSamples[verID][1])

plt.ylabel('some numbers')
plt.show()



