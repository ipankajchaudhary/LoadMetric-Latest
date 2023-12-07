from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flaskwebgui import FlaskUI
from flask import Flask, jsonify, request
import subprocess
import json
import math
from zipfile import ZipFile
import os
import shutil
from sys import path
import time
import concurrent.futures
import psutil
from flask_cors import CORS
import logging


logging.basicConfig(filename='log.txt', filemode='w',  level=logging.DEBUG)
msiFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static\ADOMD\\x64_16.0.5384.0_SQL_AS_ADOMD.msi")
command = ['msiexec', '/i', msiFilePath]
copyPath = "C:/Program Files/Microsoft.NET/ADOMD.NET/160/Microsoft.AnalysisServices.AdomdClient.dll"
if not os.path.exists(os.path.dirname(copyPath)):
    try:
        subprocess.run(command, check=True)
        logging.debug("MSI installation completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.debug(f"MSI installation failed with error: {e}")

path.append('\\Program Files\\Microsoft.NET\\ADOMD.NET\\160')

from pyadomd import Pyadomd
import pandas as pd 

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'],
     methods=['GET', 'POST', 'PUT', 'DELETE'])


class Parser:
    def __init__(self, fileName):
        self.fileName = fileName
        pass

    def parse(self):
        shutil.copyfile(self.fileName, self.fileName[:-5] + "(1).pbix")

        self.fileName = self.fileName[:-5] + "(1).pbix"
        base = os.path.splitext(self.fileName)[0]

        os.rename(self.fileName, base + ".zip")

        with ZipFile(self.fileName[:-5] + ".zip", 'r') as zip:
            filesToDelete = zip.namelist()
            zip.extractall()
        base = os.path.splitext("Report\Layout")[0]
        oldfilePath = "Report\\Layout"
        newfilePath = base + ".txt"

        if os.path.exists(newfilePath):
            os.remove(newfilePath)

        os.rename(oldfilePath, newfilePath)

        with open("Report\Layout.txt", "rb") as user_file:
            fileContents = json.loads(user_file.read())

        pages = len(fileContents['sections'])
        parserArray = []
        for i in range(0, pages):
            totalVisuals = len(fileContents['sections'][i]['visualContainers'])
            PageNames = fileContents['sections'][i]['displayName']
            for j in range(0, totalVisuals):
                try:
                    data = json.loads(fileContents['sections'][i]['visualContainers'][j]['config'])[
                        'singleVisual']  
                    if (data["visualType"] == "textbox"):
                        continue
                    CapturedVisualName = data["visualType"]
                    
                    CapturedVisualTitle = ""
                    try:
                        CapturedVisualTitle = data["vcObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"]
                        CapturedVisualTitle = CapturedVisualTitle.replace("'","")
                        CapturedVisualTitle = CapturedVisualTitle.replace(",","")

                    except Exception as e:
                        logging.debug(e)
                    data = data["prototypeQuery"]["Select"]
                    t = len(data)
                    ColumnList = []
                    MeasureList = []
                    DimensionList = []
                    for z in range(0, t):
                        Column = 'Column'
                        dimension = ""
                        if Column in data[z]:
                            ColumnList.append(data[z]["Column"]["Property"])
                            col = data[z]["Column"]["Property"]
                            dimension = data[z]["Name"]
                            dimension = dimension.split(".")[0]
                            dimension = dimension.replace("Min(","")
                            DimensionList.append(dimension)

                        if "Measure" in data[z]:
                            measure = data[z]["Measure"]["Property"]
                            MeasureList.append(data[z]["Measure"]["Property"])
                    for w in range(0,len(MeasureList)):
                        if(len(ColumnList) == 0):
                            parserTemp = {}
                            parserTemp["PageName"] = PageNames
                            parserTemp["VisualName"] = CapturedVisualName
                            parserTemp["MeasureName"] = MeasureList[w]
                            parserTemp["ColumnName"] = ""
                            parserTemp["DimensionName"] = ""
                            parserTemp["VisualTitle"] = CapturedVisualTitle
                            parserArray.append(parserTemp)
                        else:

                            for e in range(0,len(ColumnList)):
                                parserTemp = {}
                                parserTemp["PageName"] = PageNames
                                parserTemp["VisualName"] = CapturedVisualName
                                parserTemp["MeasureName"] = MeasureList[w]
                                parserTemp["ColumnName"] = ColumnList[e]
                                parserTemp["DimensionName"] = DimensionList[e]
                                parserTemp["VisualTitle"] = CapturedVisualTitle
                                parserArray.append(parserTemp)
                                

                except KeyError as e:
                    logging.debug(e)
        df = pd.DataFrame(parserArray)
        df.drop_duplicates(inplace=True)
        os.remove(self.fileName[:-5] + ".zip")
        for file in filesToDelete:
            if('Report' not in file):
                os.remove(file)
        return df



class QueryExecutor:
    def __init__(self, thresholdTime, connectionString, df):
        self.numThreads = 5
        self.thresholdTime = thresholdTime
        self.connectionString = connectionString
        self.res = []
        self.count = 0
        self.df = df

    def processQuery(self, query, i):
        try:
            con = Pyadomd(self.connectionString)
            con.open()
            startTime = time.time()
            logging.debug("Currently running : " + query + "\n")
            result = con.cursor().execute(query)
            dftemp = pd.DataFrame(result.fetchone())
            self.count = self.count + 1
            endTime = time.time()
            elapsedTime = endTime - startTime
            if elapsedTime >= float(self.thresholdTime):
                logging.debug(
                    f"Query {query} took too long to execute ({elapsedTime}). Aborting query...")
                con.close()
                return self.thresholdTime
            else:
                con.close()
                return f"{elapsedTime:0.12f}"
        except Exception as e:
            logging.debug(e)
            return None

    def executeQuery(self, df):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.numThreads) as executor:
            futures = [executor.submit(self.processQuery, query, i)
                       for i, query in enumerate(df["Query"])]
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                if result is None:
                    df.drop(i, inplace=True)
                else:
                    df.loc[i, "LoadTime"] = result


class LoadTimeChecker:
    def __init__(self, modelName, endpoint, connectionstring, checkforlocal, runningFirstTime, parsedDataFrame, thresholdValue):
        self.modelName = modelName
        self.endpoint = endpoint
        self.checkforlocal = checkforlocal
        self.connectionString = ''
        self.thresholdValue = thresholdValue
        self.parsedDataFrame = parsedDataFrame
        if (self.checkforlocal == 'Y' or self.checkforlocal == 'y'):
            self.connectionString = connectionstring
        else:
            self.PowerBIEndpoint = self.endpoint + ";initial catalog=" + self.modelName
            self.PowerBILogin = ""
            self.PowerBIPassword = ""
            self.connectionString = "Provider=MSOLAP.8;Data Source=" + self.PowerBIEndpoint + \
                ";UID=" + self.PowerBILogin + ";PWD=" + self.PowerBIPassword
        self.runningFirstTime = runningFirstTime
        self.con = Pyadomd(self.connectionString)

    def MeasureListSQLQuery(self):
        self.con.open()
        query = "SELECT [MEASURE_NAME],[MEASUREGROUP_NAME],[EXPRESSION],[CUBE_NAME] FROM $SYSTEM.MDSCHEMA_MEASURES WHERE MEASURE_IS_VISIBLE AND MEASUREGROUP_NAME <> 'Reporting Filters' ORDER BY [MEASUREGROUP_NAME]"
        result = self.con.cursor().execute(query)
        df = pd.DataFrame(result.fetchone(), columns=[
                          "Measure", "MeasureGroup", "EXPRESSION", "CubeName"])
        self.con.close()
        return df

    def MeasureReferenceQuery(self):
        self.con.open()
        query = "SELECT DISTINCT [Object] ,[Referenced_Table] FROM $SYSTEM.DISCOVER_CALC_DEPENDENCY WHERE [Object_Type] = 'MEASURE'"
        result = self.con.cursor().execute(query)
        df = pd.DataFrame(result.fetchone(), columns=[
                          "Measure", "Referenced_Table"])
        self.con.close()
        return df

    def RelationshipQuery(self):
        self.con.open()
        query = "SELECT DISTINCT [FromTableID],[FromColumnID],[ToTableID],[ToColumnID]FROM $SYSTEM.TMSCHEMA_RELATIONSHIPS WHERE [IsActive]"
        result = self.con.cursor().execute(query)
        df = pd.DataFrame(result.fetchone(), columns=[
                          "FromTableID", "FromColumnID", "ToTableID", "ToColumnID"])
        self.con.close()
        return df

    def TableQuery(self):
        self.con.open()
        query = "SELECT DISTINCT [Name],[ID] FROM $SYSTEM.TMSCHEMA_TABLES"
        result = self.con.cursor().execute(query)
        df = pd.DataFrame(result.fetchone(), columns=["TableName", "TableID"])
        self.con.close()
        return df

    def ColumnsQuery(self):
        self.con.open()
        query = "SELECT DISTINCT [TableID],[ExplicitName],[ID] FROM $SYSTEM.TMSCHEMA_COLUMNS WHERE [Type] <> 3 AND NOT [IsDefaultImage] AND [State] = 1"
        result = self.con.cursor().execute(query)
        df = pd.DataFrame(result.fetchone(), columns=[
                          "TableID", "ColumnName", "ColumnID"])
        self.con.close()
        return df

    def ColumnValuesCountQueryforprogress(self):

        df = pd.merge(self.TableQuery(), self.ColumnsQuery(),
                      how='inner', on='TableID')
        
        df['ValuesQuery'] = 'WITH MEMBER [Measures].[Count] AS [' + df['TableName'] + '].[' + df['ColumnName'] + \
            '].[' + df['ColumnName'] + \
            '].Count SELECT {[Measures].[Count]} ON COLUMNS  FROM [Model]'
        df.reset_index(drop=True, inplace=True)
        df['ID'] = df.index + 1
        logging.debug(df)
        df.to_csv("columnvaluescountquery.csv")
        return len(df.index)
    
    def ColumnValuesCountQuery(self):
        df = pd.read_csv("columnvaluescountquery.csv")
        for i, row in df.iterrows():
            self.con.open()
            query = row['ValuesQuery']
            try:
                result = self.con.cursor().execute(query)
                tempDF = pd.DataFrame(result.fetchone(), columns=["Count"])
                df.at[i, 'Count'] = tempDF['Count'][0]
                logging.debug(tempDF['Count'][0])
                logging.debug("Column Values Count queries are running....")
                self.con.close()
            except:
                logging.debug(query)
                self.con.close()
        return df


    def FinalColumnsFromTablesQuery(self):

        ColumnValuesCount = self.ColumnValuesCountQuery()
        RowNumberPerDimension = ColumnValuesCount
        RowNumberPerDimension = RowNumberPerDimension.sort_values(
            by=['TableName', 'Count'], ascending=[True, True])
        RowNumberPerDimension['RowNumber'] = RowNumberPerDimension.groupby(
            'TableName').cumcount() + 1
        MeanRowNumber = {}

        for i in RowNumberPerDimension.iterrows():
            key = i[1]['TableName']
            val = i[1]['RowNumber']

            if (key not in MeanRowNumber):
                MeanRowNumber[key] = val
            else:
                if (val > MeanRowNumber[key]):
                    MeanRowNumber[key] = val

        MeanRowNumberdf = pd.DataFrame(list(MeanRowNumber.items()), columns=[
                                       'TableName', 'MeanRowNumber'])
        MeanRowNumberdf['MeanRowNumber'] = MeanRowNumberdf['MeanRowNumber'].apply(
            lambda x: math.ceil(x / 2))
        MeanRowNumberdf['MeanRowNumber'] = MeanRowNumberdf['MeanRowNumber'].astype(
            int)

        finalColumns = []

        for index, row in RowNumberPerDimension.iterrows():
            tableName = row['TableName']
            columnName = row['ColumnName']
            rowNumber = row['RowNumber']

            for mean_row in MeanRowNumberdf.itertuples(self):
                if tableName == mean_row.TableName and rowNumber == mean_row.MeanRowNumber:
                    finalColumns.append([tableName, columnName, rowNumber])
                    break

        resultDataFrame = pd.DataFrame(finalColumns, columns=[
                                'TableName', 'ColumnName', 'RowNumber'])

        return resultDataFrame

    def MeasureWithDimensionsQuery(self):
        TempMeasureCalculationQuery = self.MeasureListSQLQuery()
        MeasureReferences = self.MeasureReferenceQuery()
        Relationships = self.RelationshipQuery()
        Tables = self.TableQuery()
        FinalColumnsFromTables = self.FinalColumnsFromTablesQuery()
        Columns = self.ColumnsQuery()

        MeasuresWithDimensions = pd.merge(
            Relationships, Tables.rename(
                columns={'TableID': 'FromTableID', 'TableName': 'FromTableName'}),
            on='FromTableID'
        ).merge(
            Tables.rename(columns={'TableID': 'ToTableID',
                          'TableName': 'ToTableName'}),
            on='ToTableID'
        ).merge(
            Columns.rename(
                columns={'ColumnID': 'FromColumnID', 'ColumnName': 'FromColumnName'}),
            on='FromColumnID'
        ).merge(
            Columns.rename(
                columns={'ColumnID': 'ToColumnID', 'ColumnName': 'ToColumnName'}),
            on='ToColumnID'
        ).merge(
            MeasureReferences, left_on=['FromTableName'], right_on=['Referenced_Table']
        ).merge(
            TempMeasureCalculationQuery, left_on=['Measure'], right_on=['Measure']
        ).merge(
            FinalColumnsFromTables, left_on=['ToTableName'], right_on=['TableName']
        )

        return MeasuresWithDimensions

    def MeasureTimeWithoutDimensionsQuery(self):
        MeasureTimeWithoutDimensions = pd.DataFrame()
        TempMeasureCalculation = self.MeasureListSQLQuery()
        MeasureTimeWithoutDimensions['Measure'] = TempMeasureCalculation['Measure']
        MeasureTimeWithoutDimensions['MeasureGroup'] = TempMeasureCalculation['MeasureGroup']
        MeasureTimeWithoutDimensions['EXPRESSION'] = TempMeasureCalculation['EXPRESSION']
        MeasureTimeWithoutDimensions['CubeName'] = TempMeasureCalculation['CubeName']
        MeasureTimeWithoutDimensions['Query'] = "SELECT [Measures].[" + \
            MeasureTimeWithoutDimensions['Measure'] + "] ON 0 FROM [" + \
            MeasureTimeWithoutDimensions['CubeName'] + "]"
        MeasureTimeWithoutDimensions['WithDimension'] = 0
        MeasureTimeWithoutDimensions['DimensionName'] = None
        MeasureTimeWithoutDimensions['ColumnName'] = None
        return MeasureTimeWithoutDimensions

    def MeasureTimeWithDimensionsQuery(self):
        MeasureTimeWithDimensions = pd.DataFrame()
        MeasuresWithDimensions = self.MeasureWithDimensionsQuery()
        MeasureTimeWithDimensions['Measure'] = MeasuresWithDimensions['Measure']
        MeasureTimeWithDimensions['MeasureGroup'] = MeasuresWithDimensions['MeasureGroup']
        MeasureTimeWithDimensions['EXPRESSION'] = MeasuresWithDimensions['EXPRESSION']
        MeasureTimeWithDimensions['CubeName'] = MeasuresWithDimensions['CubeName']
        MeasureTimeWithDimensions['ColumnName'] = MeasuresWithDimensions['ColumnName']
        MeasureTimeWithDimensions['DimensionName'] = MeasuresWithDimensions['ToTableName']
        MeasureTimeWithDimensions['Query'] = 'SELECT {[Measures].[' + MeasureTimeWithDimensions['Measure'] + ']} ON 0 ,NON EMPTY{[' + \
            MeasureTimeWithDimensions['DimensionName'] + '].[' + MeasureTimeWithDimensions['ColumnName'] + \
            '].children} ON 1 FROM [' + \
            MeasureTimeWithDimensions['CubeName'] + "]"
        MeasureTimeWithDimensions['WithDimension'] = 1

        return MeasureTimeWithDimensions

    def getLoadTime(self):

        MeasuresWithDimensions = self.MeasureTimeWithDimensionsQuery()
        MeasuresWithoutDimensions = self.MeasureTimeWithoutDimensionsQuery()

        MeasuresWithDimensions['LoadTime'] = "x"
        MeasuresWithDimensions['isMeasureUsedInVisual'] = "0"
        MeasuresWithDimensions['PageName'] = "-"
        MeasuresWithDimensions['VisualName'] = "-"
        MeasuresWithDimensions['VisualTitle'] = "-"
        MeasuresWithDimensions['ReportName'] = "-"
        MeasuresWithDimensions['hasDimension'] = "1"


        MeasuresWithoutDimensions['LoadTime'] = "x"
        MeasuresWithoutDimensions['isMeasureUsedInVisual'] = "0"
        MeasuresWithoutDimensions['PageName'] = "-"
        MeasuresWithoutDimensions['VisualName'] = "-"
        MeasuresWithoutDimensions['VisualTitle'] = "-"
        MeasuresWithoutDimensions['ReportName'] = "-"
        MeasuresWithoutDimensions["hasDimension"] = "0"

        self.parsedDataFrame['LoadTime'] = "x"
        self.parsedDataFrame['isMeasureUsedInVisual'] = "1"
        self.parsedDataFrame['hasDimension'] = '0'

        self.parsedDataFrame.rename(columns={'MeasureName': 'Measure'}, inplace=True)
        self.parsedDataFrame['Query'] = ''
        
        for i, row in self.parsedDataFrame.iterrows():
            if(row["ColumnName"] == ""):
                self.parsedDataFrame['Query'] = 'SELECT {[Measures].[' + self.parsedDataFrame['Measure'] + ']} ON 0 FROM [' + \
                    MeasuresWithDimensions['CubeName'][0] + "]"
            else:
                self.parsedDataFrame['Query'] = 'SELECT {[Measures].[' + self.parsedDataFrame['Measure'] + ']} ON 0 ,NON EMPTY{[' + \
                    self.parsedDataFrame['DimensionName'] + '].[' + self.parsedDataFrame['ColumnName'] + \
                    '].children} ON 1 FROM [' + \
                    MeasuresWithDimensions['CubeName'][0] + "]"
                

        tempDF = self.parsedDataFrame.groupby('Measure')
        tempDF = tempDF.first()

        mergedDF = tempDF.merge(MeasuresWithoutDimensions, indicator=True, on="Measure", how='outer').query(
            '_merge != "both"').drop(labels='_merge', axis=1)
        mergedDF.drop(columns=['PageName_x', 'VisualName_x', 'LoadTime_x','VisualTitle_x','VisualTitle_y',
                         'isMeasureUsedInVisual_x', 'CubeName',
                         'isMeasureUsedInVisual_y', 'PageName_y', 'VisualName_y', 'Query_x'], inplace=True)
        mergedDF['isMeasureUsedInVisual'] = '0'
        mergedDF['PageName'] = "-"
        mergedDF['VisualName'] = "-"
        mergedDF['VisualTitle'] = "-"
        mergedDF['ColumnName'] = "-"
        mergedDF['DimensionName'] = "-"
        mergedDF['hasDimension'] = '0'
        mergedDF.rename(columns={'LoadTime_y': "LoadTime",
                  'Query_y': 'Query'}, inplace=True)


        possibleCombinations = pd.concat(
            [self.parsedDataFrame, mergedDF, MeasuresWithDimensions], ignore_index=True, axis=0)
        possibleCombinations = possibleCombinations.loc[:, ['Measure', 'DimensionName', 'ColumnName',
                                  'LoadTime', 'isMeasureUsedInVisual','ReportName', 'PageName', 'VisualName', 'VisualTitle', 'Query','hasDimension']]
        queryExecutorObject = QueryExecutor(
            self.thresholdValue, self.connectionString, possibleCombinations)
        queryExecutorObject.executeQuery(possibleCombinations)
        logging.debug("Queries execution completed\n")

        

        if (self.runningFirstTime == True):
            possibleCombinations.to_csv("RES.csv", index=False)
        else:
            previousLoadTimeDataFrame = pd.read_csv("RES.csv")
            possibleCombinations['PreviousLoadTime'] = "0"
            logging.debug(previousLoadTimeDataFrame)
            for j in previousLoadTimeDataFrame.index:
                for i in possibleCombinations.index:
                    if (possibleCombinations['Query'][i] == previousLoadTimeDataFrame['Query'][j]):
                        possibleCombinations.at[i, 'PreviousLoadTime'] = previousLoadTimeDataFrame.at[j, 'LoadTime']

            possibleCombinations['ChangeinLoadTime'] = ""
            for i in possibleCombinations.index:
                loadTime = float(possibleCombinations['LoadTime'][i])
                prevLoadTime = float(possibleCombinations['PreviousLoadTime'][i])
                changeinLoadTime = loadTime - prevLoadTime
                possibleCombinations['ChangeinLoadTime'][i] = round(changeinLoadTime, 9)

            possibleCombinations.to_csv("RES.csv", index=False)

        return [possibleCombinations, self.connectionString]


@app.route('/')
def index():
    return render_template('index.html')
 

@app.route('/data', methods=['POST'])
def getData():
    data = request.json
    logging.debug(data)
    response = {'message': 'Data received', 'data': data}

    modelName = data["modelName"]
    endpoint = data["xmlaEndpoint"]
    thresholdValue = data["thresholdValue"]
    isFirstTime = data["isFirstTime"]
    checkforlocal = 'n'
    connectionString = "Provider=MSOLAP.8;Integrated Security=SSPI;Persist Security Info=True;Initial Catalog=5dd1196f-83a2-45c1-a53b-f90aca647bc4;Data Source=localhost:61115;MDX Compatibility=1;Safety Options=2;MDX Missing Member Mode=Error;Update Isolation Level=2"
    logging.debug(data)
    parsedDF = pd.read_csv("ParsedDF.csv")
    loadtimechecker = LoadTimeChecker(
        modelName, endpoint, connectionString, checkforlocal, isFirstTime, parsedDF, thresholdValue)
    li = loadtimechecker.getLoadTime()
    df = li[0]
    connectionString = li[1]

    result = "{" '\"result\": ' + df.to_json(
        orient='records') + "," + '\"connectionString\": ' + '"' + str(connectionString) + '"' + "}"

    return jsonify(result)



def getReportList():
    parserArray = {
        'filepath' : []
    }
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['name'] == 'PBIDesktop.exe':
            cmdline = process.info['cmdline']
            file_paths = [arg for arg in cmdline if arg.lower().endswith('.pbix')]
            if file_paths:
                parserArray['filepath'].append(file_paths)
    return parserArray

@app.route('/getreport', methods=['GET'])
def getReport():
    result = getReportList()
    return jsonify(result)



@app.route('/progress', methods=['POST'])
def getProgress():
    data = request.json
    logging.debug(data)
    response = {'message': 'Data received', 'data': data}

    # singleFile = data["singleFile"]
    filePath = data["filePath"]
    logging.debug(type(filePath))
    modelName = data["modelName"]
    endpoint = data["xmlaEndpoint"]
    thresholdValue = data["thresholdValue"]
    isFirstTime = data["isFirstTime"]
    checkforlocal = 'n'
    connectionString = "Provider=MSOLAP.8;Integrated Security=SSPI;Persist Security Info=True;Initial Catalog=5dd1196f-83a2-45c1-a53b-f90aca647bc4;Data Source=localhost:61115;MDX Compatibility=1;Safety Options=2;MDX Missing Member Mode=Error;Update Isolation Level=2"
    logging.debug(data)

    filePath = filePath.split(',')
    logging.debug(filePath)
    newFolderPaths = []
    for fileName in filePath:

            folderName = os.path.splitext(os.path.basename(fileName))[0]
            newFolderPath = os.path.join(os.path.dirname(fileName), folderName)
            os.makedirs(newFolderPath, exist_ok=True)

            logging.debug(str(folderName) + str(newFolderPath))

            shutil.copy2(fileName, newFolderPath)

            newfilePath = os.path.join(newFolderPath, os.path.basename(fileName))
            logging.debug("New file path:" + str(newfilePath))
            csvPath = newFolderPath + "\Res.csv"
            newFolderPaths.append(newFolderPath)
            parser = Parser(fileName)
            parsedDF = parser.parse()
            filen, extension = os.path.splitext(os.path.basename(fileName))
            parsedDF['ReportName'] = filen
            parsedDF.to_csv(csvPath,index = False)
            logging.debug(parsedDF)
            logging.debug("\n")

    dfList = []
    for folderPath in newFolderPaths:
            csvPath = os.path.join(folderPath, "Res.csv")  
            df = pd.read_csv(csvPath) 
            dfList.append(df)
    parsedDF = pd.concat(dfList)

    parsedDF.to_csv("ParsedDF.csv")

    loadtimechecker = LoadTimeChecker(
        modelName, endpoint, connectionString, checkforlocal, isFirstTime, parsedDF, thresholdValue)
    li = loadtimechecker.ColumnValuesCountQueryforprogress()

    result = "{" '\"result\": ' + '"' + str(li) + '"' + "}"

    return jsonify(result)


@app.route("/quit")
def quit():
  shutdown = request.environ.get("werkzeug.server.shutdown")
  shutdown()
  return

if __name__ == "__main__":
    netstateOutput = subprocess.check_output(['netstat', '-ano']).decode('utf-8')
    for line in netstateOutput.splitlines():
        if f':{3002}' in line:
            processID = line.split()[-1]
            subprocess.call(['taskkill', '/PID', processID, '/F'])
            logging.debug(f"Process with Port {3002} (PID: {processID}) killed.")
            logging.debug(f"Process with Port {3002} (PID: {processID}) killed.")
    # app.debug = True
    
            logging.debug(f"Process with Port {3002} (PID: {processID}) killed.")    
    # app.debug = True
    

    netstateOutput = subprocess.check_output(['netstat', '-ano']).decode('utf-8')
    for line in netstateOutput.splitlines():
        if f':{3002}' in line:
            processID = line.split()[-1]
            subprocess.call(['taskkill', '/PID', processID, '/F'])
            logging.debug(f"Process with Port {3002} (PID: {processID}) killed.")

    FlaskUI(app=app, server="flask",width=1920, height=1080, port=3002).run()