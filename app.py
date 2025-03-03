import os

from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Public Google Sheets CSV URL
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/1B8l-TyxWk4g9lCEszhOg-wjD4TOxGGAo8Kp0-N7BIvk/export?format=csv"
)

def load_google_sheets():
    """
    Fetch and process Google Sheets data, ensuring correct metadata alignment.
    """
    # 1) Read the sheet, explicitly setting the second row (1-based) as the header
    df_full = pd.read_csv(SHEET_CSV_URL, dtype=str)  # FIXED: Now event names are headers

    # Debug: Print first 10 rows of full data
    print("\n🔹 FULL DATA (First 10 Rows):")
    print(df_full.head(10))

    # 2) Strip whitespace from column headers
    df_full.columns = df_full.columns.str.strip()

    # 3) Extract metadata from rows 1 through 4 (1-based) → Rows 0 to 3 in Pandas
    metadata_df = df_full.iloc[0:4]  # FIXED: Correct indexing

    # Debug: Print metadata DataFrame
    print("\n🔹 METADATA DATAFRAME:")
    print(metadata_df)

    # 4) User data starts at row 5 (1-based) → Row 4 (0-based)
    df_data = df_full.iloc[4:].reset_index(drop=True)  # FIXED: Correct user row start

    # Preprocess email addresses
    # need to check if emails are there... some empty rows may cause problems with splitting
    # Also set all to lower to prevent case sensitivity
    df_data['email'] = df_data['email'].apply(lambda x: ';'.join([e.strip().lower() for e in x.split(';')]) if isinstance(x, str) else x)


    # Debug: Print user data DataFrame
    print("\n🔹 USER DATA (First 5 Rows):")
    print(df_data.head())

    # 5) Convert metadata rows into a structured dictionary (keep NaNs as they are)
    metadata = {}
    for col in metadata_df.columns[8:]:  # Event data starts at column I (index 8)
        metadata[col] = {
            "Date":     metadata_df.iloc[0][col],  # Corrected row mapping
            "Time":     metadata_df.iloc[1][col],  
            "Location": metadata_df.iloc[2][col],  
            "Link":     metadata_df.iloc[3][col],  
        }

    # Debug: Print metadata dictionary
    print("\n🔹 METADATA DICTIONARY:")
    for key, value in metadata.items():
        print(f"{key}: {value}")

    return df_data, metadata

@app.route("/", methods=["GET", "POST"])
def home():
    """
    On GET: render a simple index page with a form for user email.
    On POST: find user data by email, merge with event metadata, and render result.html.
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower() # set to lower to prevent case sensitivity
        if not email:
            return render_template("result.html", error="No email provided.")

        # Load fresh data from the Google Sheet
        df, metadata = load_google_sheets()

        # Confirm the 'email' column exists
        if "email" not in df.columns:
            print(f"\n❌ ERROR: Column 'email' not found! Available columns: {df.columns.tolist()}")
            return f"Column 'email' not found in CSV. Available columns: {df.columns.tolist()}"

        # Filter for user’s record
        # check for string type to avoid errors
        user_data = df[df["email"].apply(lambda x: any(e.strip() == email for e in x.split(';')) if isinstance(x, str) else False)]

        # Debug: Print filtered user data
        print(f"\n🔹 USER DATA FOR EMAIL {email}:")
        print(user_data)

        if user_data.empty:
            print(f"\n❌ ERROR: No RSVP found for {email}")
            return render_template("result.html", error=f"No RSVP found for {email}.")
        else:
            # Convert the single row to a dictionary
            user_info = user_data.to_dict(orient="records")[0]

            # Debug: Print user_info before cleaning
            print("\n🔹 USER INFO BEFORE CLEANING:")
            print(user_info)

            # Remove keys (columns) where user has NaN values
            user_info_cleaned = {key: value for key, value in user_info.items() if pd.notna(value)}

            # Debug: Print cleaned user info
            print("\n🔹 USER INFO AFTER CLEANING:")
            print(user_info_cleaned)

            # Merge metadata with user's RSVP (excluding dropped NaN values)
            event_details = {}
            for event in metadata.keys():
                if event in user_info_cleaned:  # Only include if user has an RSVP
                    event_details[event] = {
                        "Date":     metadata[event].get("Date", ""),
                        "Time":     metadata[event].get("Time", ""),
                        "Location": metadata[event].get("Location", ""),
                        "Link":     str(metadata[event].get("Link", "")) if pd.notna(metadata[event].get("Link")) else "",  # Convert NaN to empty string
                        "RSVP":     user_info_cleaned.get(event, ""),
                    }





            # Debug: Print final event details
            print("\n🔹 FINAL EVENT DETAILS:")
            print(event_details)

            return render_template(
                "result.html",
                user=user_info_cleaned,
                events=event_details,
                error=None
            )
    else:
        return render_template("index.html")

#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=5000, debug=True)
# This was causing bad gateway 500 error on render.com
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default to 10000, but use Render's $PORT if available
    app.run(host="0.0.0.0", port=port)