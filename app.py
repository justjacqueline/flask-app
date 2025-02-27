
from flask import Flask, request, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# Public Google Sheets URL (change it to your actual sheet)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1B8l-TyxWk4g9lCEszhOg-wjD4TOxGGAo8Kp0-N7BIvk/export?format=csv"

# Load Google Sheets data
df = pd.read_csv(SHEET_CSV_URL)
df.columns = df.columns.str.strip()  # Remove any leading/trailing spaces in headers

print("CSV Headers:", df.columns)  # Debugging: Print column names to check

@app.route("/", methods=["GET", "POST"])
def home():
    global df
    df = pd.read_csv(SHEET_CSV_URL)  # Reload data to get fresh updates
    df.columns = df.columns.str.strip()  # Strip spaces again

    if request.method == "POST":
        email = request.form.get("email")
        print("Received email:", email)  # Debugging

        if "email" in df.columns:
            user_data = df[df["email"] == email]  
        else:
            return f"Column 'email' not found in Google Sheet. Available columns: {df.columns.tolist()}"

        if not user_data.empty:
            return render_template("result.html", data=user_data.to_dict(orient="records")[0])
        else:
            return render_template("result.html", error="No RSVP found for this email.")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)