# from sys import path
# path.append("C:\\Program Files\\Microsoft.NET\\ADOMD.NET\\160\\")

# from flask import Flask, jsonify
# from flask_cors import CORS  # Import the CORS extension

# app = Flask(__name__)

# # Enable CORS for all routes
# # CORS(app)

# CORS(app, origins=['http://localhost:3000'],
#      methods=['GET', 'POST', 'PUT', 'DELETE'])



# # print(path)

# from pyadomd import Pyadomd

# endpoint = 'powerbi://api.powerbi.com/v1.0/myorg/Sprouts%20EDW%20-%20Test%20Marketing'
# modelname = "Marketing Dashboard Dataset"

# PowerBIEndpoint = endpoint + ";initial catalog=" + modelname
# PowerBILogin = ""
# PowerBIPassword = ""
# connection_string = "Provider=MSOLAP.8;Data Source=" + PowerBIEndpoint + \
#                 ";UID=" + PowerBILogin + ";PWD=" + PowerBIPassword


# conn_str = connection_string
# print(conn_str)
# query = """EVALUATE DimWeek"""

# with Pyadomd(conn_str) as conn:
#     with conn.cursor().execute(query) as cur:
#         print(cur.fetchall())


# @app.route('/api/data', methods=['GET'])
# def get_data():
#     data = {'message': str(conn_str)}
#     return jsonify(data)

# if __name__ == '__main__':
#     # Run the Flask app on port 5000 (you can change this to any port you want)
#     # app.run(debug=True, port=5000)
#     app.run(port=3002)


# import subprocess
# cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Description'
# proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
# for line in proc.stdout:
#     print(line)
#     # if line.rstrip():
#     #     # only print lines that are not empty
#     #     # decode() is necessary to get rid of the binary string (b')
#     #     # rstrip() to remove `\r\n`
#     #     print(line.decode().rstrip())


import psutil

def list_power_bi_files():
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        # print(process.info["name"])
        if process.info['name'] == 'PBIDesktop.exe':
            cmdline = process.info['cmdline']
            # print(cmdline)
            file_paths = [arg for arg in cmdline if arg.lower().endswith('.pbix')]
            # print(file_paths)
            if file_paths:
                print(file_paths)
                # print(f"Power BI Desktop PID {process.info['pid']} - Files: {', '.join(file_paths)}")

if __name__ == "__main__":
    list_power_bi_files()


# import multiprocessing
# import time

# def your_function():
#     # Your code here
#     time.sleep(10)
#     print("adsf")

# def worker(queue):
#     try:
#         result = your_function()
#         queue.put(result)
#     except Exception as e:
#         queue.put(e)

# if __name__ == "__main__":
#     timeout_seconds = 15
#     queue = multiprocessing.Queue()

#     process = multiprocessing.Process(target=worker, args=(queue,))
#     process.start()
#     process.join(timeout=timeout_seconds)

#     if process.is_alive():
#         process.terminate()
#         process.join()
#         print("Function timed out, skipping to the next line.")
#     else:
#         result = queue.get()
#         if isinstance(result, Exception):
#             print(f"Function raised an exception: {result}")
#         else:
#             print(f"Function result: {result}")


# z1 = "Sales Overview"
# for i in range(0,5):
#     for j in range(0,5):
#         print(z1)


