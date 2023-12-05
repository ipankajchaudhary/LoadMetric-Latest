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


msi_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static\ADOMD\\x64_16.0.5384.0_SQL_AS_ADOMD.msi")
command = ['msiexec', '/i', msi_file_path]
CopyPath = "C:/Program Files/Microsoft.NET/ADOMD.NET/160/Microsoft.AnalysisServices.AdomdClient.dll"
if not os.path.exists(os.path.dirname(CopyPath)):
    try:
        subprocess.run(command, check=True)
        print("MSI installation completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"MSI installation failed with error: {e}")

path.append('\\Program Files\\Microsoft.NET\\ADOMD.NET\\160')

from pyadomd import Pyadomd
import pandas as pd 

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'],
     methods=['GET', 'POST', 'PUT', 'DELETE'])


class Parser:
    def __init__(self, filename):
        self.filename = filename
        pass

    def parse(self):
        shutil.copyfile(self.filename, self.filename[:-5] + "(1).pbix")

        self.filename = self.filename[:-5] + "(1).pbix"
        base = os.path.splitext(self.filename)[0]

        # zipping the file
        os.rename(self.filename, base + ".zip")

        # unzipping the file
        with ZipFile(self.filename[:-5] + ".zip", 'r') as zip:
            zip.extractall()

        base = os.path.splitext("Report\Layout")[0]
        old_file_path = "Report\\Layout"
        new_file_path = base + ".txt"

        if os.path.exists(new_file_path):
            os.remove(new_file_path)

        os.rename(old_file_path, new_file_path)

        with open("Report\Layout.txt", "rb") as user_file:
            file_contents = json.loads(user_file.read())

        length = len(file_contents['sections'])
        f = open("OUTPUT.txt", "w")
        g = open("data.txt","w")
        f.write("PageName,VisualName,MeasureName,ColumnName,DimensionName,VisualTitle")
        f.write("\n")
        dictt = []
        for i in range(0, length):
            length2 = len(file_contents['sections'][i]['visualContainers'])
            PageNames = file_contents['sections'][i]['displayName']
            for j in range(0, length2):
                try:
                    data = json.loads(file_contents['sections'][i]['visualContainers'][j]['config'])[
                        'singleVisual']  # ['projections']
                    if (data["visualType"] == "textbox"):
                        continue
                    CapturedVisualName = data["visualType"]
                    
                    CapturedVisualTitle = ""
                    try:
                        CapturedVisualTitle = data["vcObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"]
                        CapturedVisualTitle = CapturedVisualTitle.replace("'","")
                        CapturedVisualTitle = CapturedVisualTitle.replace(",","")

                    except Exception as e:
                        print(e)
                    data = data["prototypeQuery"]["Select"]
                    g.write(str(data) + "\n")
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
                            singlerow = {}
                            singlerow["PageName"] = PageNames
                            singlerow["VisualName"] = CapturedVisualName
                            singlerow["MeasureName"] = MeasureList[w]
                            singlerow["ColumnName"] = ""
                            singlerow["DimensionName"] = ""
                            singlerow["VisualTitle"] = CapturedVisualTitle
                            dictt.append(singlerow)
                        else:

                            for e in range(0,len(ColumnList)):
                                singlerow = {}
                                singlerow["PageName"] = PageNames
                                singlerow["VisualName"] = CapturedVisualName
                                singlerow["MeasureName"] = MeasureList[w]
                                singlerow["ColumnName"] = ColumnList[e]
                                singlerow["DimensionName"] = DimensionList[e]
                                singlerow["VisualTitle"] = CapturedVisualTitle
                                dictt.append(singlerow)
                                

                except KeyError as e:
                    print(e)
        f.close()
        g.close()
        df = pd.DataFrame(dictt)
        df.to_csv("ResultTable.csv", index=False)
        df.drop_duplicates(inplace=True)
        try:
            os.remove("DataModel")
        except Exception:
            print("\n")
        try:
            os.remove("Connections")
        except Exception:
            print("\n")
        try:
            os.remove("DiagramLayout")
        except Exception:
            print("\n")
        try:
            os.remove("[Content_Types].xml")
        except Exception:
            print("\n")
        try:
            os.remove("DiagramState")
        except Exception:
            print("\n")
        try:
            os.remove(self.filename[:-5] + ".zip")
        except Exception:
            print("\n")
        try:
            os.remove("Metadata")
        except Exception:
            print("\n")
        try:
            os.remove("SecurityBindings")
        except Exception:
            print("\n")
        try:
            os.remove("Settings")
        except Exception:
            print("\n")
        try:
            os.remove("ResultTable")
        except Exception:
            print("\n")
        try:
            os.remove("OUTPUT.txt")
        except Exception:
            print("\n")
        return df



class QueryExecutor:
    def __init__(self, threshold_time, connection_string, df):
        self.num_threads = 5
        self.threshold_time = threshold_time
        self.connection_string = connection_string
        self.res = []
        self.df = df
        self.count = 0
        self.unique_queries = {}

    def process_query(self, query, i):
        try:
            con = Pyadomd(self.connection_string)
            con.open()
            start_time = time.time()
            print("Currently running : " + query + "\n")
            result = con.cursor().execute(query)
            dftemp = pd.DataFrame(result.fetchone())
            self.count = self.count + 1
            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time >= float(self.threshold_time):
                print(
                    f"Query {query} took too long to execute ({elapsed_time}). Aborting query...")
                con.close()
                return self.threshold_time
            else:
                con.close()
                return f"{elapsed_time:0.12f}"
        except Exception as e:
            print(e)
            return None

    def execute_queries(self, df):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [executor.submit(self.process_query, query, i)
                       for i, query in enumerate(df["Query"])]
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                if result is None:
                    df.drop(i, inplace=True)
                else:
                    df.loc[i, "LoadTime"] = result


class LoadTimeChecker:
    def __init__(self, modelname, endpoint, connectionstring, checkforlocal, runningforfirsttime, parseddf, thresholdvalue):
        self.modelname = modelname
        self.endpoint = endpoint
        self.checkforlocal = checkforlocal
        self.connection_string = ''
        self.thresholdvalue = thresholdvalue
        self.parseddf = parseddf
        print(self.modelname, self.endpoint)
        if (self.checkforlocal == 'Y' or self.checkforlocal == 'y'):
            self.connection_string = connectionstring
        else:
            self.PowerBIEndpoint = self.endpoint + ";initial catalog=" + self.modelname
            self.PowerBILogin = ""
            self.PowerBIPassword = ""
            self.connection_string = "Provider=MSOLAP.8;Data Source=" + self.PowerBIEndpoint + \
                ";UID=" + self.PowerBILogin + ";PWD=" + self.PowerBIPassword
        print(self.connection_string)
        self.runningforfirsttime = runningforfirsttime
        self.con = Pyadomd(self.connection_string)

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
        print(df)
        df.to_csv("columnvaluescountquery.csv")
        return len(df.index)
    
    def ColumnValuesCountQuery(self):
        df = pd.read_csv("columnvaluescountquery.csv")
        for i, row in df.iterrows():
            self.con.open()
            query = row['ValuesQuery']
            try:
                result = self.con.cursor().execute(query)
                tempdf = pd.DataFrame(result.fetchone(), columns=["Count"])
                df.at[i, 'Count'] = tempdf['Count'][0]
                print(tempdf['Count'][0])
                print("Column Values Count queries are running....")
                self.con.close()
            except:
                print(query)
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

        final_columns = []

        for index, row in RowNumberPerDimension.iterrows():
            table_name = row['TableName']
            column_name = row['ColumnName']
            row_number = row['RowNumber']

            for mean_row in MeanRowNumberdf.itertuples(self):
                if table_name == mean_row.TableName and row_number == mean_row.MeanRowNumber:
                    final_columns.append([table_name, column_name, row_number])
                    break

        final_df = pd.DataFrame(final_columns, columns=[
                                'TableName', 'ColumnName', 'RowNumber'])

        return final_df

    def MeasureWithDimensionsQuery(self):
        TempMeasureCalculationQuery = self.MeasureListSQLQuery()
        MeasureReferences = self.MeasureReferenceQuery()
        Relationships = self.RelationshipQuery()
        Tables = self.TableQuery()
        FinalColumnsFromTables = self.FinalColumnsFromTablesQuery()
        Columns = self.ColumnsQuery()

        measures_with_dimensions = pd.merge(
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

        return measures_with_dimensions

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
        measures_with_dimensions = self.MeasureWithDimensionsQuery()
        MeasureTimeWithDimensions['Measure'] = measures_with_dimensions['Measure']
        MeasureTimeWithDimensions['MeasureGroup'] = measures_with_dimensions['MeasureGroup']
        MeasureTimeWithDimensions['EXPRESSION'] = measures_with_dimensions['EXPRESSION']
        MeasureTimeWithDimensions['CubeName'] = measures_with_dimensions['CubeName']
        MeasureTimeWithDimensions['ColumnName'] = measures_with_dimensions['ColumnName']
        MeasureTimeWithDimensions['DimensionName'] = measures_with_dimensions['ToTableName']
        MeasureTimeWithDimensions['Query'] = 'SELECT {[Measures].[' + MeasureTimeWithDimensions['Measure'] + ']} ON 0 ,NON EMPTY{[' + \
            MeasureTimeWithDimensions['DimensionName'] + '].[' + MeasureTimeWithDimensions['ColumnName'] + \
            '].children} ON 1 FROM [' + \
            MeasureTimeWithDimensions['CubeName'] + "]"
        MeasureTimeWithDimensions['WithDimension'] = 1

        return MeasureTimeWithDimensions

    def get_load_time(self):

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

        self.parseddf['LoadTime'] = "x"
        self.parseddf['isMeasureUsedInVisual'] = "1"
        self.parseddf['hasDimension'] = '0'

        self.parseddf.rename(columns={'MeasureName': 'Measure'}, inplace=True)


        self.parseddf['Query'] = ''
        
        for i, row in self.parseddf.iterrows():
            if(row["ColumnName"] == ""):
                self.parseddf['Query'] = 'SELECT {[Measures].[' + self.parseddf['Measure'] + ']} ON 0 FROM [' + \
                    MeasuresWithDimensions['CubeName'][0] + "]"
            else:
                self.parseddf['Query'] = 'SELECT {[Measures].[' + self.parseddf['Measure'] + ']} ON 0 ,NON EMPTY{[' + \
                    self.parseddf['DimensionName'] + '].[' + self.parseddf['ColumnName'] + \
                    '].children} ON 1 FROM [' + \
                    MeasuresWithDimensions['CubeName'][0] + "]"
                

        self.parseddf.to_csv("PossibleCombinations.csv")
        tempdf = self.parseddf.groupby('Measure')
        tempdf = tempdf.first()

        df = tempdf.merge(MeasuresWithoutDimensions, indicator=True, on="Measure", how='outer').query(
            '_merge != "both"').drop(labels='_merge', axis=1)
        df.drop(columns=['PageName_x', 'VisualName_x', 'LoadTime_x','VisualTitle_x','VisualTitle_y',
                         'isMeasureUsedInVisual_x', 'CubeName',
                         'isMeasureUsedInVisual_y', 'PageName_y', 'VisualName_y', 'Query_x'], inplace=True)
        df['isMeasureUsedInVisual'] = '0'
        df['PageName'] = "-"
        df['VisualName'] = "-"
        df['VisualTitle'] = "-"
        df['ColumnName'] = "-"
        df['DimensionName'] = "-"
        df['hasDimension'] = '0'
        df.rename(columns={'LoadTime_y': "LoadTime",
                  'Query_y': 'Query'}, inplace=True)


        finaldf = pd.concat(
            [self.parseddf, df, MeasuresWithDimensions], ignore_index=True, axis=0)
        finaldf = finaldf.loc[:, ['Measure', 'DimensionName', 'ColumnName',
                                  'LoadTime', 'isMeasureUsedInVisual','ReportName', 'PageName', 'VisualName', 'VisualTitle', 'Query','hasDimension']]
        query_executor = QueryExecutor(
            self.thresholdvalue, self.connection_string, finaldf)
        query_executor.execute_queries(finaldf)
        print("Queries execution completed\n")

        

        if (self.runningforfirsttime == True):
            finaldf.to_csv("RES.csv", index=False)
        else:
            previousloadtimedf = pd.read_csv("RES.csv")
            finaldf['PreviousLoadTime'] = "0"
            print(previousloadtimedf)
            for j in previousloadtimedf.index:
                for i in finaldf.index:
                    if (finaldf['Query'][i] == previousloadtimedf['Query'][j]):
                        finaldf.at[i, 'PreviousLoadTime'] = previousloadtimedf.at[j, 'LoadTime']

            finaldf['ChangeinLoadTime'] = ""
            for i in finaldf.index:
                load_time = float(finaldf['LoadTime'][i])
                prev_load_time = float(finaldf['PreviousLoadTime'][i])
                change_in_load_time = load_time - prev_load_time
                finaldf['ChangeinLoadTime'][i] = round(change_in_load_time, 9)

            finaldf.to_csv("RES.csv", index=False)

        return [finaldf, self.connection_string]


@app.route('/')
def index():
    return render_template('index.html')
 

@app.route('/data', methods=['POST'])
def get_data():
    data = request.json
    print(data)
    response = {'message': 'Data received', 'data': data}

    singleFile = data["singleFile"]
    filepath = data["filePath"]
    modelname = data["modelName"]
    endpoint = data["xmlaEndpoint"]
    thresholdvalue = data["thresholdValue"]
    isFirstTime = data["isFirstTime"]
    checkforlocal = 'n'
    connection_string = "Provider=MSOLAP.8;Integrated Security=SSPI;Persist Security Info=True;Initial Catalog=a105a363-e6db-4947-acf2-5b3078bdab89;Data Source=localhost:53624;MDX Compatibility=1;Safety Options=2;MDX Missing Member Mode=Error;Update Isolation Level=2"
    print(data)

    if(singleFile == True):
        parser = Parser(data["filePath"])
        parsed_df = parser.parse()
        filen, extension = os.path.splitext(os.path.basename(data['filePath']))
        parsed_df['ReportName'] = filen
    else:
        filepath = filepath.split(',')
        print(filepath)
        newfolderpaths = []
        for file_name in filepath:

            folder_name = os.path.splitext(os.path.basename(file_name))[0]
            new_folder_path = os.path.join(os.path.dirname(file_name), folder_name)
            os.makedirs(new_folder_path, exist_ok=True)

            print(folder_name,new_folder_path)

            shutil.copy2(file_name, new_folder_path)

            new_file_path = os.path.join(new_folder_path, os.path.basename(file_name))
            print("New file path:", new_file_path)
            csv_path = new_folder_path + "\Res.csv"
            newfolderpaths.append(new_folder_path)
            parser = Parser(file_name)
            parsed_df = parser.parse()
            filen, extension = os.path.splitext(os.path.basename(file_name))
            parsed_df['ReportName'] = filen
            # df.drop(columns = ['Query'])
            # df = df.reset_index().rename(columns={'index': 'id'})
            parsed_df.to_csv(csv_path,index = False)
            print(parsed_df)
            print("\n")

        df_list = []
        for folder_path in newfolderpaths:
            csv_path = os.path.join(folder_path, "Res.csv")
            
            df = pd.read_csv(csv_path)
            
            df_list.append(df)

        parsed_df = pd.concat(df_list)


    loadtimechecker = LoadTimeChecker(
        modelname, endpoint, connection_string, checkforlocal, isFirstTime, parsed_df, thresholdvalue)
    li = loadtimechecker.get_load_time()

    df = li[0]
    filen, extension = os.path.splitext(os.path.basename(data['filePath']))

    connection_string = li[1]

    result = "{" '\"result\": ' + df.to_json(
        orient='records') + "," + '\"connection_string\": ' + '"' + str(connection_string) + '"' + "}"

    return jsonify(result)



def list_power_bi_files():
    dictt = {
        'filepath' : []
    }
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['name'] == 'PBIDesktop.exe':
            cmdline = process.info['cmdline']
            file_paths = [arg for arg in cmdline if arg.lower().endswith('.pbix')]
            if file_paths:
                dictt['filepath'].append(file_paths)
    return dictt

@app.route('/getreport', methods=['GET'])
def get_report():
    result = list_power_bi_files()
    return jsonify(result)



@app.route('/progress', methods=['POST'])
def get_progress():
    data = request.json
    print(data)
    response = {'message': 'Data received', 'data': data}

    singleFile = data["singleFile"]
    filepath = data["filePath"]
    modelname = data["modelName"]
    endpoint = data["xmlaEndpoint"]
    thresholdvalue = data["thresholdValue"]
    isFirstTime = data["isFirstTime"]
    checkforlocal = 'n'
    connection_string = "Provider=MSOLAP.8;Integrated Security=SSPI;Persist Security Info=True;Initial Catalog=a105a363-e6db-4947-acf2-5b3078bdab89;Data Source=localhost:53624;MDX Compatibility=1;Safety Options=2;MDX Missing Member Mode=Error;Update Isolation Level=2"
    print(data)

    if(singleFile == True):
        parser = Parser(data["filePath"])
        parsed_df = parser.parse()
        filen, extension = os.path.splitext(os.path.basename(data['filePath']))
        parsed_df['ReportName'] = filen
    else:
        filepath = filepath.split(',')
        print(filepath)
        newfolderpaths = []
        for file_name in filepath:

            folder_name = os.path.splitext(os.path.basename(file_name))[0]
            new_folder_path = os.path.join(os.path.dirname(file_name), folder_name)
            os.makedirs(new_folder_path, exist_ok=True)

            print(folder_name,new_folder_path)

            shutil.copy2(file_name, new_folder_path)

            new_file_path = os.path.join(new_folder_path, os.path.basename(file_name))
            print("New file path:", new_file_path)
            csv_path = new_folder_path + "\Res.csv"
            newfolderpaths.append(new_folder_path)
            parser = Parser(file_name)
            parsed_df = parser.parse()
            filen, extension = os.path.splitext(os.path.basename(file_name))
            parsed_df['ReportName'] = filen
            parsed_df.to_csv(csv_path,index = False)
            print(parsed_df)
            print("\n")

        df_list = []
        for folder_path in newfolderpaths:
            csv_path = os.path.join(folder_path, "Res.csv")  
            df = pd.read_csv(csv_path) 
            df_list.append(df)
        parsed_df = pd.concat(df_list)

    loadtimechecker = LoadTimeChecker(
        modelname, endpoint, connection_string, checkforlocal, isFirstTime, parsed_df, thresholdvalue)
    li = loadtimechecker.ColumnValuesCountQueryforprogress()

    result = "{" '\"result\": ' + '"' + str(li) + '"' + "}"

    return jsonify(result)


@app.route("/quit")
def quit():
  shutdown = request.environ.get("werkzeug.server.shutdown")
  shutdown()
  return

if __name__ == "__main__":
    netstat_output = subprocess.check_output(['netstat', '-ano']).decode('utf-8')
    for line in netstat_output.splitlines():
        if f':{3002}' in line:
            process_id = line.split()[-1]
            subprocess.call(['taskkill', '/PID', process_id, '/F'])
            print(f"Process with Port {3002} (PID: {process_id}) killed.")
    # app.debug = True
    

    netstat_output = subprocess.check_output(['netstat', '-ano']).decode('utf-8')
    for line in netstat_output.splitlines():
        if f':{3002}' in line:
            process_id = line.split()[-1]
            subprocess.call(['taskkill', '/PID', process_id, '/F'])
            print(f"Process with Port {3002} (PID: {process_id}) killed.")

    FlaskUI(app=app, server="flask",width=1920, height=1080, port=3002).run()