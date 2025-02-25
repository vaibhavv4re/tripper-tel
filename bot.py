from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from transformers import pipeline
import requests
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Health check endpoint
@app.route('/')
def home():
    return "Bot is running!", 200

# Run the Flask server in a thread
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Initialize the LLM pipeline
generator = pipeline('text-generation', model='distilgpt2')

# API keys
MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
#WEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Fetch route from Google Maps
def get_route(origin: str, destination: str) -> dict:
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={MAPS_API_KEY}"
    return requests.get(url).json()

# Fetch POIs along the route
def get_pois(location: str, preference: str) -> dict:
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius=5000&type={preference}&key={MAPS_API_KEY}"
    return requests.get(url).json()


# Handle user messages
def handle_message(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    user_message = update.message.text

    # Log the interaction
    log_interaction(user_id, user_message, "")

    if "route from" in user_message.lower():
        origin, destination = user_message.lower().split("route from")[1].split(" to ")
        origin, destination = origin.strip(), destination.strip()

        # Fetch route
        route_data = get_route(origin, destination)
        route_summary = route_data['routes'][0]['summary']
        steps = route_data['routes'][0]['legs'][0]['steps']

        # Fetch user preferences
        preferences = get_preferences(user_id) or "general"

        # Fetch POIs and weather alerts
        pois = []
        weather_alerts = []
        for step in steps:
            lat = step['end_location']['lat']
            lon = step['end_location']['lng']
            pois.append(get_pois(f"{lat},{lon}", preferences))

        # Generate personalized suggestions
        prompt = f"Suggest stopovers and activities for a trip from {origin} to {destination} based on {preferences}."
        suggestions = generator(prompt, max_length=50)[0]['generated_text']

        # Compile response
        response = (
            f"**Route Summary**: {route_summary}\n\n"
            f"**POIs along the way**: {pois}\n\n"
            f"**Personalized Suggestions**: {suggestions}"
        )

        update.message.reply_text(response)
        log_interaction(user_id, user_message, response)

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! I'm your travel assistant. How can I help you today?")

# Main function
def main():
    # Start Flask server in a separate thread
    Thread(target=run_flask).start()

    # Start the Telegram bot
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
