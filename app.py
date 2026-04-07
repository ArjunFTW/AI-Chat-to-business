import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Load hidden variables from the .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SHEET_ID = os.getenv("SHEET_ID")

app = Flask(__name__)

# --- 1. GEMINI AI SETUP ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

def extract_inventory_data(user_message):
    system_prompt = """
    You are an automated inventory extraction tool.
    Map user input to this official list: ["quick-dry cement", "steel rebar", "red bricks", "pvc pipes"].
    If the user makes a typo, map it to the closest official item. 
    If no quantity is given, assume 1.
    You must output a JSON object with exactly these keys: "intent", "item", "qty".
    """
    try:
        full_prompt = f"{system_prompt}\n\nUser Request: {user_message}"
        response = model.generate_content(full_prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Error: {e}")
        return {"intent": "error", "item": "unknown", "qty": 0}

# --- 2. GOOGLE SHEETS SETUP ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_key.json", scope)
g_client = gspread.authorize(creds)
sheet = g_client.open_by_key(SHEET_ID).sheet1

def update_inventory(item_name, qty_to_deduct):
    if item_name == "unknown": return False, "AI failed to understand."
    try:
        cell = sheet.find(item_name)
        row_num = cell.row
        current_stock = int(sheet.cell(row_num, 2).value)
        
        if current_stock >= qty_to_deduct:
            new_stock = current_stock - qty_to_deduct
            sheet.update_cell(row_num, 2, new_stock)
            return True, new_stock
        else:
            return False, current_stock
    except Exception as e:
        print(f"Sheet Error: {e}")
        return False, f"Could not find '{item_name}' in the database."

# --- 3. WHATSAPP WEBHOOK ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').lower()
    print(f"\n📱 User texted: {incoming_msg}")
    
    extracted_data = extract_inventory_data(incoming_msg)
    item = extracted_data.get('item', 'unknown')
    qty = extracted_data.get('qty', 0)
    
    twiml_response = MessagingResponse()
    
    if item == "unknown":
        twiml_response.message("🤖 I couldn't understand that inventory request. Please try again.")
        return str(twiml_response)
        
    success, result = update_inventory(item, qty)
    
    if success:
        twiml_response.message(f"✅ Success! Deducted {qty} of '{item}'. New stock: {result}")
    else:
        twiml_response.message(f"❌ Error: Could not deduct {qty} of '{item}'. Stock available: {result}")
        
    return str(twiml_response)

if __name__ == '__main__':
    # Running locally on port 5000
    app.run(port=5000, debug=True)