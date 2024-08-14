import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    filters,
    MessageHandler,
)
import io
import requests


def GeminiChat(prompt):
    # Replace "YOUR_API_KEY" with your actual API key
    API_KEY = os.environ.get("Gemini_Key")

    # Define the request data
    data = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ]
    }

    # Set the request headers
    headers = {"Content-Type": "application/json"}

    # Construct the API endpoint URL with the API key
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}"

    # Send the POST request
    response = requests.post(url, headers=headers, json=data)

    # Check for successful response
    if response.status_code == 200:
        # Parse the JSON response
        response_data = response.json()
        generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        # Access the generated text from the response
        return generated_text

    else:
        return {"Error": response.status_code}


IMAGE_API_URL = (
    "https://api-inference.huggingface.co/models/cagliostrolab/animagine-xl-3.0"
)
headers = {"Authorization": "Bearer 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"}
TOKEN = os.environ.get("TELEGRAM_TOKEN")


def query_image(payload):
    response = requests.post(IMAGE_API_URL, headers=headers, json=payload)
    return response.content


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.lower()

    if user_input.startswith(("jade", "/bro", "bro", "bot")):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action="typing"
        )

        user_input = " ".join(user_input.split()[1:])
        output = GeminiChat(user_input)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=output,
            reply_to_message_id=update.message.message_id,
        )

    elif user_input.startswith(("generate", "make")):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action="typing"
        )
        try:
            image_bytes = query_image({"inputs": user_input})
            image = io.BytesIO(image_bytes)
            image.seek(0)
            if image:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=image,
                    reply_to_message_id=update.message.message_id,
                )
        except Exception as e:
            logging.error(f"Error generating image: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, I am loading the generative AI model right now, please wait a min.",
                reply_to_message_id=update.message.message_id,
            )


if __name__ == "__main__":
    try:
        # Initialize your application
        application = ApplicationBuilder().token(TOKEN).build()

        # Set up the handlers
        start_handler = CommandHandler("bro", start)
        application.add_handler(start_handler)
        chat_handler = MessageHandler(filters.TEXT, start)
        application.add_handler(chat_handler)
        image_handler = CommandHandler("generate", start)
        application.add_handler(image_handler)

        application.run_polling()
    except Exception as e:
        # Log any exceptions
        logging.error(f"An error occurred: {e}")
