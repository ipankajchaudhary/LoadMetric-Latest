import sys
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
# app_config = {"host": "0.0.0.0", "port": sys.argv[1]}

"""
---------------------- DEVELOPER MODE CONFIG -----------------------
"""
# # Developer mode uses app.py
# if "app.py" in sys.argv[0]:
#   # Update app config
#   app_config["debug"] = True

#   # CORS settings
#   cors = CORS(
#     app,
#     resources={r"/*": {"origins": "http://localhost*"}},
#   )

#   # CORS headers
#   app.config["CORS_HEADERS"] = "Content-Type"


"""
--------------------------- REST CALLS -----------------------------
"""
# Remove and replace with your own

# #    if (runningforfirsttime == 'Y' or runningforfirsttime == 'y'):
# #         finaldf.to_csv("RES.csv", index=False)
# #     else:
# #         previousloadtimedf = pd.read_csv("RES.csv")
# #         finaldf['PreviousLoadTime'] = "0"
# #         print(previousloadtimedf)
# #         for j in previousloadtimedf.index:
# #             for i in finaldf.index:
# #                 if (finaldf['Query'][i] == previousloadtimedf['Query'][j]):
# #                     finaldf.at[i, 'PreviousLoadTime'] = previousloadtimedf.at[j, 'LoadTime']

# #         finaldf['ChangeinLoadTime'] = ""
# #         for i in finaldf.index:
# #             load_time = float(finaldf['LoadTime'][i])
# #             prev_load_time = float(finaldf['PreviousLoadTime'][i])
# #             change_in_load_time = load_time - prev_load_time
# #             finaldf['ChangeinLoadTime'][i] = round(change_in_load_time, 9)

# #         finaldf.to_csv("RES.csv", index=False)


import sys
import subprocess
import pkg_resources
import json
import math
import socket
from zipfile import ZipFile
import os
import shutil
from sys import path

import csv

import time
import concurrent.futures
import multiprocessing



try:
    import pandas as pd
    from flask import Flask, jsonify, request
    from flask_cors import CORS


except Exception:
    required = {'pandas', 'pyadomd', 'pythonnet', 'flask', }
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', *missing])
    else:
        print("all installed")
finally:
    import pandas as pd
path.append('\\Program Files\\Microsoft.NET\\ADOMD.NET\\160')
try:
    from pyadomd import Pyadomd
except Exception:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyadomd'])
finally:
    from pyadomd import Pyadomd


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

        # changing the encoding of layout file
        # os.rename("Report\Layout", base + ".txt")
        with open("Report\Layout.txt", "rb") as user_file:
            file_contents = json.loads(user_file.read())

        # getting the length of sections
        length = len(file_contents['sections'])
        f = open("OUTPUT.txt", "w")
        g = open("data.txt","w")
        g.write("{")
        f.write("PageName,VisualName,MeasureName,ColumnName,DimensionName,VisualTitle")
        f.write("\n")
        for i in range(0, length):
            length2 = len(file_contents['sections'][i]['visualContainers'])
            CapturedPage = file_contents['sections'][i]['displayName']
            strr = str(file_contents['sections'][i])
            
            # print("page name", CapturedPage)
            for j in range(0, length2):
                try:
                    data = json.loads(file_contents['sections'][i]['visualContainers'][j]['config'])[
                        'singleVisual']  # ['projections']
                    if (data["visualType"] == "textbox"):
                        continue
                    CapturedVisual = data["visualType"]
                    # print(CapturedVisual)
                    
                    CapturedVisualTitle = ""
                    try:
                        CapturedVisualTitle = data["vcObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"]
                        CapturedVisualTitle = CapturedVisualTitle.replace("'",'')
                        CapturedVisualTitle = CapturedVisualTitle.replace(",",'')
                    except Exception as e:
                        print(e)

                    data = data["prototypeQuery"]["Select"]

                    # g.write(str(data) + "\n")



                    t = len(data)
                    ColumnList = []
                    MeasureList = []
                    DimensionList = []
                    for z in range(0, t):
                        Column = 'Column'
                        


 
                        col = ""
                        dimension = ""
                        measure = ""
                        # if "Aggregation" in data[z]:
                        #     # print(data[z]["Name"])
                        #     # f.write("Column : " +  data[z]["Aggregation"]["Expression"]["Column"]["Property"] + "\n")
                        #     ColumnList.append(data[z]["Name"])
                        if Column in data[z]:
                            # f.write("Column : " +  data[z]["Column"]["Property"]+ "\n") #["Aggregation"]["Expression"]["Column"]["Property"])
                            ColumnList.append(data[z]["Column"]["Property"])
                            col = data[z]["Column"]["Property"]
                            dimension = data[z]["Name"]
                            dimension = dimension.split(".")[0]
                            dimension = dimension.replace("Min(","")
                            DimensionList.append(dimension)

                        if "Measure" in data[z]:
                            # print("Measure : " +   data[z]["Measure"]["Property"]  +  "Visual Name : " + CapturedVisual + "\n")
                            measure = data[z]["Measure"]["Property"]
                            MeasureList.append(data[z]["Measure"]["Property"])
                            if(CapturedPage == 'Sales Overview' and CapturedVisual == 'card'):
                        # g.write(str(data))
                        # break

                                print("error is not here")
                    for w in range(0,len(MeasureList)):
                        for e in range(0,len(ColumnList)):
                            measurename = MeasureList[w]
                            measurename = measurename.replace(",",";")
                           
                            f.write(CapturedPage+","+CapturedVisual+","+measurename+","+ColumnList[e]+","+DimensionList[e]+","+CapturedVisualTitle+"\n")

                        
                        # f.write("\n")
                    # for w in range(0, len(MeasureList)):
                    #     for e in range(0,len(ColumnList)):
                    #         for u in range(0,len(DimensionList)):
                    #             f.write(CapturedPage+","+CapturedVisual+","+MeasureList[w]+","+ColumnList[e]+","+DimensionList[u]+"\n")
                    # if len(MeasureList)==0:
                    #     for e in range(0,len(ColumnList)):
                    #         f.write(CapturedPage+","+CapturedVisual+",Blank,"+ColumnList[e]+"\n")
                except KeyError as e:
                    print("e")
        f.close()
        g.write("}")
        g.close()
        df = pd.read_csv("OUTPUT.txt")
        df.to_csv("ResultTable.csv", index=False)
        # with open("ResultTable.csv", 'r') as csv_file:
        #     reader = csv.DictReader(csv_file)
        #     # Convert each row to a dictionary and append to a list
        #     data = [row for row in reader]

        # # Convert the data to JSON string
        # json_data = json.dumps(data, indent=4)

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
        # try:
        #     os.remove("ResultTable")
        # except Exception:
        #     print("\n")
        # try:
        #     os.remove("OUTPUT.txt")
        # except Exception:
        #     print("\n")
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

    # def firequery(self,query):
    #     con = Pyadomd(self.connection_string)
    #     con.open()
    #     print("Currently running : " + query + "\n")
    #     result = con.cursor().execute(query)
    #         # time.sleep(2)
    #     dftemp = pd.DataFrame(result.fetchone())
    #         # count_value1 = dftemp.values[0]
    #     self.count = self.count + 1
    #     con.close()



    # def worker(self,query,queue):
    #     try:
    #         result = self.firequery(query)
    #         queue.put(result)
    #     except Exception as e:
    #         queue.put(e)


    def process_query(self, query, i):
        try:
            con = Pyadomd(self.connection_string)
            con.open()
            start_time = time.time()
            elapsed_time = 0
            print("Currently running : " + query + "\n")
            result = con.cursor().execute(query)
            # time.sleep(2)
            # self.fire_query(con,query)



            # timeout_seconds = self.threshold_time
            # queue = multiprocessing.Queue()

            # process = multiprocessing.Process(target=self.worker, args=(query,queue,))
            # process.start()
            # process.join(timeout=timeout_seconds)

            # if process.is_alive():
            #     process.terminate()
            #     process.join()
            #     elapsed_time = self.threshold_time
            #     print("Function timed out, skipping to the next line.")
            # else:
            #     result = queue.get()
            #     if isinstance(result, Exception):
            #         print(f"Function raised an exception: {result}")
            #     else:
            #         print(f"Function result: {result}")

                
            dftemp = pd.DataFrame(result.fetchone())
            count_value1 = dftemp.values[0]
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
            # Create a list of futures for each query
            futures = [executor.submit(self.process_query, query, i)
                       for i, query in enumerate(df["Query"])]
            # Get the results of each future as they complete
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                # Store the result in a new column in the dataframe
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
            # self.connection_string = connectionstring
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
        RowNumberPerDimension.to_csv("RowNumberPerDimension.csv")
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
        MeasuresWithDimensions.to_csv("MeasurewithDimensionsQuery.csv")


        self.parseddf['LoadTime'] = "x"
        self.parseddf['isMeasureUsedInVisual'] = "1"
        self.parseddf['hasDimension'] = '0'

        self.parseddf.rename(columns={'MeasureName': 'Measure'}, inplace=True)

        # self.parseddf['Query'] = "SELECT [Measures].[" + self.parseddf['Measure'] + \
        #     "] ON 0 FROM ["+MeasuresWithDimensions['CubeName'][0] + "]"
        

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
        return finaldf

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
    checkforlocal = 'y'
    connection_string = "Provider=MSOLAP.8;Integrated Security=SSPI;Persist Security Info=True;Initial Catalog=d26bbfe2-687d-439b-b953-9a75aaba583b;Data Source=localhost:54709;MDX Compatibility=1;Safety Options=2;MDX Missing Member Mode=Error;Update Isolation Level=2"
    print(data)


    if(singleFile == True):
        parser = Parser(data["filePath"])
        parsed_df = parser.parse()
        parsed_df['MeasureName'] = parsed_df['MeasureName'].str.replace(';', ',')
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

    parsed_df.to_csv("parsed.csv")
    loadtimechecker = LoadTimeChecker(
        modelname, endpoint, connection_string, checkforlocal, isFirstTime, parsed_df, thresholdvalue)
    li = loadtimechecker.get_load_time()

    df = li[0]
    filen, extension = os.path.splitext(os.path.basename(data['filePath']))

    # df['ReportName'] = filen
    # df.to_csv("df.csv")
    connection_string = li[1]

    result = "{" '\"result\": ' + df.to_json(
        orient='records') + "," + '\"connection_string\": ' + '"' + str(connection_string) + '"' + "}"

    return jsonify(result)

import psutil
def list_power_bi_files():
    dictt = {
        'filepath' : []
    }
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        # print(process.info["name"])
        if process.info['name'] == 'PBIDesktop.exe':
            cmdline = process.info['cmdline']
            # print(cmdline)
            file_paths = [arg for arg in cmdline if arg.lower().endswith('.pbix')]
            # print(file_paths)
            if file_paths:
                dictt['filepath'].append(file_paths)
                # print(file_paths)
                # print(f"Power BI Desktop PID {process.info['pid']} - Files: {', '.join(file_paths)}")
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
    checkforlocal = 'y'
    connection_string = "Provider=MSOLAP.8;Integrated Security=SSPI;Persist Security Info=True;Initial Catalog=d26bbfe2-687d-439b-b953-9a75aaba583b;Data Source=localhost:54709;MDX Compatibility=1;Safety Options=2;MDX Missing Member Mode=Error;Update Isolation Level=2"
    print(data)

    if(singleFile == True):
        parser = Parser(data["filePath"])
        parsed_df = parser.parse()
        parsed_df['MeasureName'] = parsed_df['MeasureName'].str.replace(';', ',')

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
    li = loadtimechecker.ColumnValuesCountQueryforprogress()

    # df = li[0]
    # filen, extension = os.path.splitext(os.path.basename(data['filePath']))

    # df['ReportName'] = filen
    # df.to_csv("df.csv")
    # connection_string = li[1]

    result = "{" '\"result\": ' + '"' + str(li) + '"' + "}"

    return jsonify(result)


@app.route('/firequery', methods=['POST'])
def fire_query():
    data = request.json
    connection_string = data['connection_string']
    threshold_time = data['threshold_time']
    final = data['result']


    finaldf = pd.DataFrame(final)
    query_executor = QueryExecutor(
            threshold_time, connection_string, finaldf)
    query_executor.execute_queries(finaldf)
    result = "{" '\"result\": ' + finaldf.to_json(
        orient='records') + "," + '\"connection_string\": ' + '"' + str(connection_string) + '"' + "}"
    return jsonify(result)

    # if(query == None):
    #     print("query is none")
    # # ColumnName =data['connection_string']
    # # DimensionName =data['connection_string']
    # # LoadTime = data['connection_string']
    # # Measure = data['connection_string']
    # # PageName =data['connection_string']
    # # Query = "SELECT [Measures].[# Partners with Support Plan] ON 0 FROM [Model]"
    # # VisualName = "card"
    # # isMeasureUsedInVisual = "1"

    # try:
    #     con = Pyadomd(connection_string)
    #     con.open()
    #     start_time = time.time()
    #     print(query)
    #     result = con.cursor().execute(query)
    #        # time.sleep(2)
    #     dftemp = pd.DataFrame(result.fetchone())
    #        # count_value1 = dftemp.values[0]
    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     if elapsed_time >= float(threshold_time):
           
    #         con.close()
    #         result = "{" '\"result\": ' + threshold_time + \
    #             "," + '\"query\": ' + '"' + query + '"' + "}"
    #         return jsonify(result)
    #     else:
    #         con.close()
    #         result = "{" '\"result\": ' + f"{elapsed_time:0.12f}" + \
    #             "," + '\"query\": ' + '"' + query + '"' + "}"
    #         return jsonify(result)
    # except Exception as e:
    #     # print(query)
    #     # result = '{"result": "{}"}'.format(str(e) if e is not None else "")

    #     result = "{" '\"result\": '  +  "adsfasd"   + \
    #             "," + '\"query\": '  + "query" + "}"
    #     return jsonify(result)

"""
-------------------------- APP SERVICES ----------------------------
"""
# Quits Flask on Electron exit
@app.route("/quit")
def quit():
  shutdown = request.environ.get("werkzeug.server.shutdown")
  shutdown()

  return
# def kill_process_by_port(port_number):
    

# kill_process_by_port(3002)
if __name__ == "__main__":
    # hostname = socket.gethostname()
    # ip_address = socket.gethostbyname(hostname)
    # print(ip_address)
    netstat_output = subprocess.check_output(['netstat', '-ano']).decode('utf-8')
    for line in netstat_output.splitlines():
        if f':{3002}' in line:
            process_id = line.split()[-1]
            subprocess.call(['taskkill', '/PID', process_id, '/F'])
            print(f"Process with Port {3002} (PID: {process_id}) killed.")
    # app.debug = True
    app.run(port=3002)

    netstat_output = subprocess.check_output(['netstat', '-ano']).decode('utf-8')
    for line in netstat_output.splitlines():
        if f':{3002}' in line:
            process_id = line.split()[-1]
            subprocess.call(['taskkill', '/PID', process_id, '/F'])
            print(f"Process with Port {3002} (PID: {process_id}) killed.")
