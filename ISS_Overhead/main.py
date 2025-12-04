from flask import Flask, request, render_template_string
import requests
import smtplib

app = Flask(__name__)

# --- EMAIL CONFIGURATION ---
# YOU MUST CHANGE THESE FOR THE EMAIL TO WORK
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Use the 16-char App Password, NOT your normal password

def send_notification(to_email, lat, lng):
    """Sends an email notification using SMTP."""
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=SENDER_EMAIL, password=SENDER_PASSWORD)
            connection.sendmail(
                from_addr=SENDER_EMAIL,
                to_addrs=to_email,
                msg=f"Subject:Look Up! The ISS is Above!\n\nThe International Space Station is currently near your location.\n\nCoordinates:\nLat: {lat}\nLong: {lng}"
            )
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

# --- HTML TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ISS Tracker</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #2c3e50; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: #34495e; padding: 2.5rem; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 400px; text-align: center; }
        h1 { margin-bottom: 1.5rem; font-size: 2rem; color: #ecf0f1; }
        .input-group { text-align: left; margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #bdc3c7; }
        input { width: 100%; padding: 12px; border: none; border-radius: 5px; background: #ecf0f1; color: #2c3e50; box-sizing: border-box; font-size: 1rem; }
        button { width: 100%; padding: 15px; background-color: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1rem; font-weight: bold; transition: background 0.3s; margin-top: 10px;}
        button:hover { background-color: #c0392b; }
        .status { margin-top: 25px; padding: 15px; border-radius: 8px; background: rgba(0,0,0,0.2); }
        .success { border-left: 5px solid #2ecc71; }
        .fail { border-left: 5px solid #f1c40f; }
        .error { border-left: 5px solid #e74c3c; }
        .coords { font-family: monospace; color: #f39c12; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ISS Tracker</h1>
        <form method="POST">
            <div class="input-group">
                <label>Your Latitude</label>
                <input type="text" name="latitude" placeholder="e.g. 40.7128" required value="{{ lat or '' }}">
            </div>
            <div class="input-group">
                <label>Your Longitude</label>
                <input type="text" name="longitude" placeholder="e.g. -74.0060" required value="{{ lng or '' }}">
            </div>
            <div class="input-group">
                <label>Email to Notify</label>
                <input type="email" name="user_email" placeholder="recipient@example.com" required value="{{ user_email or '' }}">
            </div>
            <button type="submit">Check Position</button>
        </form>

        {% if message %}
            <div class="status {{ status_class }}">
                <h3>{{ message_title }}</h3>
                <p>{{ message }}</p>
                {% if iss_lat %}
                    <p>ISS Position: <span class="coords">{{ iss_lat }}, {{ iss_lng }}</span></p>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    lat = ""
    lng = ""
    user_email = ""
    message = None
    message_title = ""
    status_class = ""
    iss_lat = None
    iss_lng = None

    if request.method == "POST":
        lat = request.form.get("latitude")
        lng = request.form.get("longitude")
        user_email = request.form.get("user_email")

        try:
            my_lat = float(lat)
            my_lng = float(lng)

            # 1. Get ISS Position
            response = requests.get("http://api.open-notify.org/iss-now.json")
            response.raise_for_status()
            data = response.json()

            iss_lat = float(data["iss_position"]["latitude"])
            iss_lng = float(data["iss_position"]["longitude"])

            # 2. Check Range (+/- 10 degrees)
            lat_diff = abs(my_lat - iss_lat)
            lng_diff = abs(my_lng - iss_lng)

            if lat_diff <= 10 and lng_diff <= 10:
                # 3. Send Email
                email_sent = send_notification(user_email, iss_lat, iss_lng)
                if email_sent:
                    message_title = "Look Up!"
                    message = "The ISS is overhead! An email notification has been sent."
                    status_class = "success"
                else:
                    message_title = "ISS Overhead (Email Failed)"
                    message = "The ISS is close, but we couldn't send the email. Check your server logs/credentials."
                    status_class = "fail"
            else:
                message_title = "Not in Range"
                message = "The ISS is currently too far away from your location."
                status_class = "fail"

        except ValueError:
            message_title = "Input Error"
            message = "Please ensure latitude and longitude are valid numbers."
            status_class = "error"
        except Exception as e:
            message_title = "System Error"
            message = f"An error occurred: {e}"
            status_class = "error"

    return render_template_string(HTML_TEMPLATE, 
                                  lat=lat, lng=lng, user_email=user_email,
                                  message=message, message_title=message_title, 
                                  status_class=status_class,
                                  iss_lat=iss_lat, iss_lng=iss_lng)

if __name__ == "__main__":
    app.run(debug=True)