from flask import Flask, request
import json
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LINE Message API libraries
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage

app = Flask(__name__)

# Set up your LINE bot credentials from environment variables
ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
SECRET = os.getenv('LINE_CHANNEL_SECRET')

def generate_text_with_ollama(user_input):
    """
    Uses the Ollama CLI to generate text from the locally installed llama3:latest model.
    """
    # Define your custom prompt or instructions here.
    prompt_prefix = (
    "你是 charlie 是輔助機器人，專門協助使用者解答問題、提供資訊以及給予建議。"
    "請遵循以下指導原則，且在最終回覆中只提供最終結果不顯示任何內部思考過程或相關提示（例如：<think> 標籤）。"
    "請以繁體中文直接回覆使用者，切勿透露任何內部運算或邏輯細節。"
    "\n\n【指導原則】\n"
    "1. 回答時必須條理分明、邏輯嚴謹，避免語意混亂或矛盾。\n"
    "2. 根據使用者提供的訊息，提供準確且有根據的資訊；若不確定，應明確表示不確定並提供可能的方向。\n"
    "3. 採用親切、禮貌的語氣，耐心傾聽並理解使用者需求，保持尊重與專業。\n"
    "4. 根據對話主題，調整回答深度與細節；對於複雜問題，可分點解釋，使回答更具結構性。\n"
    "5. 主動確認使用者需求，必要時提出問題以釐清背景，確保提供最適切的解答與建議。"
)
    
    # Concatenate your custom prompt with the user's input.
    prompt = prompt_prefix + user_input

    try:
        # Run the Ollama command. The prompt is passed as an argument.
        # Ensure that "ollama" is available in your PATH.
        result = subprocess.run(
            ["ollama", "run", "llama3.2:3b", prompt],
            capture_output=True, text=True, check=True
        )
        # Return the generated text (stdout from the command)
        return result.stdout.strip()
    except Exception as e:
        print("Error calling ollama:", e)
        return "Error generating response."

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        line_bot_api = LineBotApi(ACCESS_TOKEN)
        handler = WebhookHandler(SECRET)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        # Extract reply token and message type from the event payload
        tk = json_data['events'][0]['replyToken']
        msg_type = json_data['events'][0]['message']['type']
        if msg_type == 'text':
            msg = json_data['events'][0]['message']['text']
            print("Received message:", msg)
            # Generate a response using the local llama3:latest model.
            reply = generate_text_with_ollama(msg)
        else:
            reply = '你傳的不是文字呦～'
        print("Reply:", reply)
        line_bot_api.reply_message(tk, TextSendMessage(text=reply))
    except Exception as e:
        print("Error:", e)
        print(body)
    return 'OK'

if __name__ == "__main__":
    app.run()
