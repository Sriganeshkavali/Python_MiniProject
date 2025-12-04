import smtplib
import datetime as dt
import random
import pandas as pd
import os

# --- 1. CONFIGURATION ---
MY_EMAIL = "your_email@gmail.com"
MY_PASSWORD = "<Your Password>"  # Use your  Password here

# --- 2. CHECK TODAY'S DATE ---
now = dt.datetime.now()
today_tuple = (now.month, now.day)

# --- 3. READ BIRTHDAY DATA ---
# Read the CSV file
data = pd.read_csv("birthdays.csv")

# Create a dictionary where the key is (month, day) and value is the data row
# Format: {(month, day): data_row}
birthdays_dict = {(data_row["month"], data_row["day"]): data_row for (index, data_row) in data.iterrows()}

# --- 4. CHECK MATCH & SEND EMAIL ---
if today_tuple in birthdays_dict:
    birthday_person = birthdays_dict[today_tuple]
    
    # Select a random letter template
    file_path = f"letter_templates/letter_{random.randint(1, 3)}.txt" 
    
    # Read the letter and replace the placeholder
    try:
        with open(file_path) as letter_file:
            contents = letter_file.read()
            # Replace [NAME] with the actual name from CSV
            final_letter = contents.replace("[NAME]", birthday_person["name"])
            
        # Send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls() # Secure the connection
            connection.login(user=MY_EMAIL, password=MY_PASSWORD)
            
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=birthday_person["email"],
                msg=f"Subject:Happy Birthday!\n\n{final_letter}"
            )
            print(f"Email sent successfully to {birthday_person['name']}!")
            
    except FileNotFoundError:
        print("Error: Template file not found. Check your 'letter_templates' folder.")
    except smtplib.SMTPAuthenticationError:
        print("Authentication Error: Check your App Password.")
else:
    print("No birthdays today.")