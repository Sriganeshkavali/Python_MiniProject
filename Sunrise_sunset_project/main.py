from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# --- HTML TEMPLATE ---
# We store the HTML as a string here to keep the project in one file.
# In a larger project, this would go in a 'templates/index.html' file.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sunrise & Sunset Lookup</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 350px; text-align: center; }
        h1 { color: #333; margin-bottom: 1.5rem; font-size: 1.5rem; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background-color: #ff8c00; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; }
        button:hover { background-color: #e07b00; }
        .result { margin-top: 20px; text-align: left; background: #fafafa; padding: 15px; border-radius: 5px; border: 1px solid #eee; }
        .result p { margin: 8px 0; color: #555; }
        .label { font-weight: bold; color: #333; }
        .error { color: red; margin-top: 10px; }
        .note { font-size: 0.8rem; color: #888; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>☀️ Sun Cycle Lookup 🌑</h1>
        <form method="POST">
            <input type="text" name="latitude" placeholder="Latitude (e.g. 40.7128)" required value="{{ lat or '' }}">
            <input type="text" name="longitude" placeholder="Longitude (e.g. -74.0060)" required value="{{ lng or '' }}">
            <button type="submit">Get Times</button>
        </form>

        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        {% if result %}
            <div class="result">
                <p><span class="label">Sunrise:</span> {{ result.sunrise }}</p>
                <p><span class="label">Sunset:</span> {{ result.sunset }}</p>
                <p><span class="label">Day Length:</span> {{ result.day_length }}</p>
            </div>
            <p class="note">Note: Times are in UTC.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None
    lat = ""
    lng = ""

    if request.method == "POST":
        lat = request.form.get("latitude")
        lng = request.form.get("longitude")

        if lat and lng:
            try:
                # API Endpoint for Sunrise-Sunset.org
                # We use formatted=1 to get human-readable times (12-hour format)
                url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&formatted=1"
                
                response = requests.get(url)
                response.raise_for_status() # Check for network errors
                
                data = response.json()
                
                if data["status"] == "OK":
                    result = data["results"]
                else:
                    error = "Invalid coordinates or API error."
                    
            except Exception as e:
                error = f"Error fetching data: {e}"
        else:
            error = "Please enter both Latitude and Longitude."

    return render_template_string(HTML_TEMPLATE, result=result, error=error, lat=lat, lng=lng)

if __name__ == "__main__":
    app.run(debug=True)