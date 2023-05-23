import pandas as pd
import sqlite3
from flask import Flask, jsonify, request


df = pd.read_excel("C:\\Users\\RIT\\Downloads\\INNERG\\20210309_2020_1 - 4 (1).xls")


df['QUARTER 1,2,3,4'] = df['QUARTER 1,2,3,4'].astype(str)


df['QUARTER'] = df['QUARTER 1,2,3,4'].str.extract('(\d+)')


grouped_data = df.groupby(['API WELL  NUMBER', 'QUARTER'])[['OIL', 'GAS', 'BRINE']].sum()


grouped_data = grouped_data.reset_index()

# calculate the sum of quartile data for oil, gas, and brine as annual data
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
    
    conn = sqlite3.connect('mydatabase.db')

    
    api_well_number = request.args.get('well')

    # Query to fetch the annual data for the specified API WELL NUMBER
    query = f"SELECT OIL, GAS, BRINE FROM Annual_data WHERE `API WELL  NUMBER` = '{api_well_number}'"

    # Execute the query and fetch the result
    result = conn.execute(query).fetchone()

    # Close the database connection
    conn.close()

    
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
