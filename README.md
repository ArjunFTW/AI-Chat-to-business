# AI-Chat-to-business

An intelligent, real-time inventory management system built for WhatsApp. Instead of navigating clunky ERP dashboards, field workers can simply text a WhatsApp bot in natural language (e.g., *"I need 50 bags of cement"*), and the AI automatically parses the request and updates a live Google Sheet database.

Built for College-Hackathon.

## ✨ Features
* **Natural Language Processing:** Powered by Google's `gemini-2.5-flash` model to accurately extract intent, item names, and quantities from messy, typo-ridden text messages.
* **Fuzzy Matching:** Automatically maps slang or misspelled items (e.g., "cemnt") to official database records.
* **Real-Time Database Sync:** Instantly deducts or updates inventory levels in a live Google Sheet.
* **WhatsApp Interface:** Zero-friction UX. Field workers use the app they already have installed via the Twilio API.
* **Fail-safe Guardrails:** Strict JSON-mode prompting ensures the AI never hallucinates database inputs, and stock limits prevent negative inventory.

## 🛠️ Tech Stack
* **Frontend:** WhatsApp (via Twilio Sandbox API)
* **Backend:** Python / Flask
* **AI Engine:** Google Gemini (`gemini-2.5-flash`)
* **Database:** Google Sheets API (`gspread`)
* **Local Tunneling:** ngrok

## 🚀 How It Works
1. A user texts the Twilio WhatsApp number: *"Grab me 15 pvc pipes."*
2. Twilio sends a webhook (POST request) via ngrok to the local Flask server.
3. The server passes the raw text to Gemini AI, enforcing a strict JSON output schema.
4. Gemini returns structured data: `{"intent": "remove_inventory", "item": "pvc pipes", "qty": 15}`.
5. The backend queries the Google Sheet via a Service Account, verifies sufficient stock, and updates the cell.
6. A success message is routed back through Twilio to the user's WhatsApp.

## 💻 Local Setup & Installation

**1. Clone the repository**
```bash
git clone [https://github.com/ArjunFTW/AI-Chat-to-business.git](https://github.com/ArjunFTW/AI-Chat-to-business.git)
cd inventory-bot
