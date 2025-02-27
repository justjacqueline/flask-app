
from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

# Public Google Sheets URL (change it to your actual sheet)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1B8l-TyxWk4g9lCEszhOg-wjD4TOxGGAo8Kp0-N7BIvk/export?format=csv"

@app.route("/")
def home():
    return "Welcome to the Google Sheets Flask App!"

@app.route("/data")
def get_data():
    try:
        print(f"Fetching data from: {SHEET_CSV_URL}")  # Debugging
        df = pd.read_csv(SHEET_CSV_URL)  # Read data
        print(df.head())  # Print the first 5 rows in the terminal for debugging
        data = df.head(5).to_dict(orient="records")  # Convert first 5 rows to JSON
        return jsonify(data)  # Return as JSON response
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


