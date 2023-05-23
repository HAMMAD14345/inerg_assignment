import pandas as pd
import sqlite3
from flask import Flask, jsonify, request

# Load the Excel file into a datafram
df = pd.read_excel("C:\\Users\\RIT\\Downloads\\INNERG\\20210309_2020_1 - 4 (1).xls")

# Convert 'QUARTER 1,2,3,4' column to string
df['QUARTER 1,2,3,4'] = df['QUARTER 1,2,3,4'].astype(str)

# Extract quartile information
df['QUARTER'] = df['QUARTER 1,2,3,4'].str.extract('(\d+)')

# Group the data by API WELL NUMBER and QUARTER, and calculate the sum of quarterly data for oil, gas, and brine
grouped_data = df.groupby(['API WELL  NUMBER', 'QUARTER'])[['OIL', 'GAS', 'BRINE']].sum()

# Reset the index to remove the multi-level index
grouped_data = grouped_data.reset_index()

# Group the data by API WELL NUMBER and calculate the sum of quartile data for oil, gas, and brine as annual data
annual_data = grouped_data.groupby('API WELL  NUMBER')[['OIL', 'GAS', 'BRINE']].sum().reset_index()

# Load the calculated annual data into a local SQLite database
conn = sqlite3.connect('mydatabase.db')
annual_data.to_sql('Annual_data', conn, if_exists='replace')
conn.close()

# Create Flask app
app = Flask(__name__)

# Define route for getting the annual data for a specific API WELL NUMBER
@app.route('/data', methods=['GET'])
def get_annual_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('mydatabase.db')

    # Get the API WELL NUMBER from the request query parameters
    api_well_number = request.args.get('well')

    # Query to fetch the annual data for the specified API WELL NUMBER
    query = f"SELECT OIL, GAS, BRINE FROM Annual_data WHERE `API WELL  NUMBER` = '{api_well_number}'"

    # Execute the query and fetch the result
    result = conn.execute(query).fetchone()

    # Close the database connection
    conn.close()

    # Check if the API WELL NUMBER exists in the database
    if result:
        # Create a dictionary to store the annual data
        annual_data_dict = {
            'API WELL NUMBER': api_well_number,
            'oil': result[0],
            'gas': result[1],
            'brine': result[2]
        }

        # Return the annual data as a JSON response
        return jsonify(annual_data_dict)
    else:
        # Return a 404 error if the API WELL NUMBER is not found
        return jsonify({'error': 'API WELL NUMBER not found'}), 404

# Run the Flask app on port 8080
if __name__ == '__main__':
    app.run(port=8080)
