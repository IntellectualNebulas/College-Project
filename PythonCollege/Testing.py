import csv
import random
from flask import Flask, jsonify, request

# 1. Flask must always be initialized with __name__ so it can map your project files
app = Flask(__name__)

# 2. Flask routes MUST start with a forward slash '/'
@app.route('/api/suspects', methods=['GET'])
def getSuspects():
    suspectsList = []

    try:
        with open('Spreadsheets/suspects.csv', mode='r', encoding='utf-8') as file:
            csvReader = csv.DictReader(file)
            for row in csvReader:
                suspectsList.append(row)
        return jsonify(suspectsList)

    # 3. Fixed indentation and added the missing colon ':' here
    except FileNotFoundError:
        return jsonify({"error": "suspects not found in Spreadsheets Folder"}), 404

# 4. Standard Python files always use '__main__' to check if the script is being run directly
if __name__ == '__main__':
    # Runs the server on http://127.0.0.1:5000
    app.run(debug=True)
