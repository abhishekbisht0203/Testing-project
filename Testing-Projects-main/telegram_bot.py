import ast
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    filters,
    MessageHandler,
)
import requests
import os
import io

API_URL = (
    "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"
)
IMAGE_API_URL = (
    "https://api-inference.huggingface.co/models/cagliostrolab/animagine-xl-3.0"
)
headers = {"Authorization": "Bearer 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"}
TOKEN = os.environ.get("TELEGRAM_TOKEN")

def query(payload):
    formatted_payload = f"""<|system|>
        Hey there! I'm Jade, your friendly chat companion. I love chatting about anything and everything. Whether it's tech talk, life updates, or even a joke or two, I'm here for you. Feel free to start a conversation,Siddharth Tiwari made me, developed me and he's my god and let's make this chat a great experience for you!</s>
        <|user|>
        {payload}</s>
        <|assistant|>"""
    response = requests.post(
        API_URL, headers=headers, json={"inputs": formatted_payload}
    )
    return response.json()


def query_image(payload):
    response = requests.post(IMAGE_API_URL, headers=headers, json=payload)
    return response.content


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if user_input.lower().startswith(("jade", "/bro", "bro", "bot")):
        # Show initial typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action="typing"
        )
        output = query({"input": user_input})
        try:
            generated_text = output[0]["generated_text"]
        except:
            generated_text = output

        try:
            output_index = generated_text.find("'output'")
        except:
            try:
                output_index = generated_text.find("<|assistant|>")
            except:
                output_index = generated_text
        try:
            if output_index:
                output_text = generated_text[output_index + len("'output':'") :].strip(
                    "'}\""
                )

            else:
                output_text = generated_text[output_index + len("<|assistant|>") :]
        except:
            output_text = generated_text

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=output_text,
            reply_to_message_id=update.message.message_id,
        )

    if user_input.lower().startswith(("generate", "make")):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action="typing"
        )
        try:
            image_bytes = query_image({"inputs": user_input})  
            image = io.BytesIO(image_bytes)
            image.seek(0)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=image,
                reply_to_message_id=update.message.message_id,
            )
        except:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo="Sorry I cannot generate it, try something else please!",
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
