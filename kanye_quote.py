import tkinter as tk
from tkinter import messagebox
import requests

def get_quote():
    """Fetches a random quote from the Kanye Rest API and updates the canvas."""
    try:
        response = requests.get("https://api.kanye.rest")
        response.raise_for_status() # Raise an error for bad status codes (4xx or 5xx)
        data = response.json()
        quote = data["quote"]
        
        # Update the text on the canvas
        canvas.itemconfig(quote_text, text=quote)
        
    except requests.exceptions.ConnectionError:
        canvas.itemconfig(quote_text, text="Error: No Internet Connection")
    except Exception as e:
        canvas.itemconfig(quote_text, text=f"Error: {e}")

# --- UI SETUP ---
window = tk.Tk()
window.title("Kanye Says...")
window.config(padx=50, pady=50, bg="white")

# Create a Canvas for the Quote Background
# We use a canvas so we can easily wrap text and place it nicely
canvas = tk.Canvas(width=300, height=250, bg="white", highlightthickness=0)

# Create the text element on the canvas
# width=250 ensures the text wraps if the quote is long
quote_text = canvas.create_text(
    150, 
    125, 
    text="Click the button below\nto get a Kanye quote.", 
    width=250, 
    font=("Arial", 20, "bold"), 
    fill="#333333" # Dark grey text
)
canvas.grid(row=0, column=0)

# --- BUTTON ---
# A large button to fetch the new quote
kanye_button = tk.Button(
    text="Get Quote", 
    command=get_quote,
    font=("Arial", 14, "bold"),
    bg="#F5F5F5",
    fg="black",
    highlightthickness=0,
    padx=20,
    pady=10
)
kanye_button.grid(row=1, column=0, pady=20)

# Load the first quote automatically on launch
get_quote()

window.mainloop()