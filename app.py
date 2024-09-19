import requests
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['cybersecurity_club']
collection = db['registrations']

# Fetch approximate geolocation from IP
def get_location_from_ip(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()
        return data.get('loc', None)  # Returns a string like "latitude,longitude"
    except:
        return None

# Route to handle registration form submission
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    # If location wasn't provided (browser denied), try IP-based location
    if not data.get('location'):
        ip = data['ip']
        loc = get_location_from_ip(ip)
        if loc:
            latitude, longitude = loc.split(',')
            data['location'] = {
                'latitude': latitude,
                'longitude': longitude
            }
    
    collection.insert_one(data)  # Insert into MongoDB
    return jsonify({"status": "success"}), 200

# Route for admin page
@app.route('/admin')
def admin():
    all_entries = collection.find()
    return render_template('admin.html', entries=all_entries)

# Simple thank you page
@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == "__main__":
    app.run(debug=True)
