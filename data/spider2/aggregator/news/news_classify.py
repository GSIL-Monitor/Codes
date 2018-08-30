# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import traceback
from pymongo import MongoClient
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../nlp/score'))
import loghelper, url_helper
import config, db
from numpy import *
import random, pymongo

# logger
loghelper.init_logger("news_classify", stream=True)
logger = loghelper.get_logger("news_classify")

mongo = db.connect_mongo()
collection = mongo.temp.beyas


def createVocabList(dataSet):
    vocabSet = set([])
    for docment in dataSet:
        vocabSet = vocabSet | set(docment)  # union of tow sets
    return list(vocabSet)  # convet if to list


def bagOfWords2Vec(vocabList, inputSet):
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] += 1
        else:
            # print ("the word is not in my vocabulry")
            pass
    return returnVec


# tranin algorithm
# the p1Num is mean claclualte in 1 class evrey word contain weight
def train(trainMat, trainGategory):
    numTrain = len(trainMat)
    numWords = len(trainMat[0])  # is vocabulry length
    pAbusive = sum(trainGategory) / float(numTrain)
    p0Num = ones(numWords);
    p1Num = ones(numWords)
    p0Denom = 2.0;
    p1Denom = 2.0
    for i in range(numTrain):
        if trainGategory[i] == 1:
            p1Num += trainMat[i]
            p1Denom += sum(trainMat[i])
        else:
            p0Num += trainMat[i]
            p0Denom += sum(trainMat[i])
    p1Vec = log(p1Num / p1Denom)
    p0Vec = log(p0Num / p0Denom)
    return p0Vec, p1Vec, pAbusive


# classfy funtion
def classfy(vec2classfy, p0Vec, p1Vec, pClass1):
    p1 = sum(vec2classfy * p1Vec) + log(pClass1)
    p0 = sum(vec2classfy * p0Vec) + log(1 - pClass1)
    if p1 > p0:
        return 1;
    else:
        return 0


# split the big string
def textParse(bigString):
    import jieba
    seg_list = jieba.cut(bigString, cut_all=False)
    return [tok.lower() for tok in seg_list]


def get_article_content(contents):
    main = ""
    for content in contents:
        # print content
        if content["content"].strip() != "":
            main = main + content["content"]
    return main


# spam email classfy
def spamTest():
    fullTest = [];
    docList = [];
    classList = []
    scope = 50
    for i in range(1, scope / 2 + 1):  # it only 25 doc in every class
        contents = list(
            mongo.article.news.find({"category": 60101, "processStatus": 1}).sort("_id", pymongo.DESCENDING).skip(
                i).limit(1))[0]['contents']
        wordList = textParse(get_article_content(contents))
        docList.append(wordList)
        fullTest.extend(wordList)
        classList.append(1)
        contents = list(mongo.article.news.find({"category": {'$ne': 60101}, "processStatus": 1}).sort("_id",
                                                                                                       pymongo.DESCENDING).skip(
            i).limit(1))[0]['contents']
        wordList = textParse(get_article_content(contents))
        docList.append(wordList)
        fullTest.extend(wordList)
        classList.append(0)
    vocabList = createVocabList(docList)  # create vocabulry
    trainSet = range(len(docList));
    testSet = []
    # choose 10 sample to test ,it index of trainMat
    for i in range(10):
        randIndex = int(random.uniform(0, len(trainSet)))  # num in 0-49
        testSet.append(trainSet[randIndex])
        del (trainSet[randIndex])
    trainMat = [];
    trainClass = []
    for docIndex in trainSet:
        trainMat.append(bagOfWords2Vec(vocabList, docList[docIndex]))
        trainClass.append(classList[docIndex])
    p0, p1, pSpam = train(array(trainMat), array(trainClass))
    errCount = 0
    oneCnt = 0
    for docIndex in testSet:
        wordVec = bagOfWords2Vec(vocabList, docList[docIndex])
        if classfy(array(wordVec), p0, p1, pSpam) != classList[docIndex]:
            errCount += 1
            if classList[docIndex] == 1: oneCnt += 1
            # print ("classfication error"), docList[docIndex]
            print ("classfication error:%s, should be:%s") % (docIndex, classList[docIndex])

    print ("the error rate is "), float(errCount) / len(testSet)
    print ("the oneCnt is "), oneCnt


def moduleTrain(source):
    # source = 13866
    fullTest = [];
    docList = [];
    classList = []
    scope = 2 * 80
    for i in range(1, scope / 2 + 1):  # it only 25 doc in every class
        contents = list(
            mongo.article.news.find({'source': source, "category": 60101, "processStatus": 1}).sort("_id",
                                                                                                    pymongo.DESCENDING).skip(
                i).limit(1))
        if len(contents)>0:
            contents = contents[0]['contents']
            wordList = textParse(get_article_content(contents))
            docList.append(wordList)
            fullTest.extend(wordList)
            classList.append(1)
        contents = list(mongo.article.news.find({'source': source, "category": {'$ne': 60101}, "processStatus": 1}).sort("_id",
                                                                                                              pymongo.DESCENDING).skip(
            i).limit(1))

        if len(contents)>0:
            contents =contents[0]['contents']
            wordList = textParse(get_article_content(contents))
            docList.append(wordList)
            fullTest.extend(wordList)
            classList.append(0)


    vocabList = createVocabList(docList)  # create vocabulry
    trainSet = range(len(docList))

    trainMat = []
    trainClass = []
    for docIndex in trainSet:
        trainMat.append(bagOfWords2Vec(vocabList, docList[docIndex]))
        trainClass.append(classList[docIndex])

    p0, p1, pSpam = train(array(trainMat), array(trainClass))
    modulemap = {'p0': list(p0),
                 'p1': list(p1),
                 'pSpam': pSpam,
                 'vocabList': vocabList,
                 'createTime': datetime.datetime.now(),
                 'source': source,
                 }
    mongo.temp.beyas.insert(modulemap)


def get_class(content, source):
    modulemap = mongo.temp.beyas.find_one({'source': source})

    doc = textParse(get_article_content(content))
    wordVec = bagOfWords2Vec(modulemap['vocabList'], doc)
    return classfy(array(wordVec), array(modulemap['p0']), array(modulemap['p1']), modulemap['pSpam'])


def test(source):
    source = 13866
    import random
    rdm = int(random.random() * 10)
    content = list(
        mongo.article.news.find({"category": 60101, "processStatus": 1}).sort("_id", pymongo.DESCENDING).skip(
            rdm).limit(1))[0]['contents']

    cnt = 0
    for i in range(20):
        rdm = int(random.random() * 100)
        content = list(mongo.article.news.find({"category": {'$ne': 60101}, "processStatus": 1}).sort("_id",
                                                                                                      pymongo.DESCENDING).skip(
            rdm).limit(1))[0]['contents']

        print rdm, get_class(content)
        if get_class(content) != 0: cnt += 1

    print 'errorcnt:', cnt


if __name__ == '__main__':
    # 下面的为了演示分词的，可注释
    # listWord=textParse(open('email/ham/1.txt').read())
    spamTest()
