from flask import Flask, render_template, request, session, redirect, url_for
from google import genai
import os

app = Flask(__name__)
app.secret_key = 'gemini_chatbot_secret_key'  # Secret key for session management

# Read API key from environment variable
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

@app.route('/')
def index():
    session['chat_history'] = []
    return render_template('index.html', chat_history=session['chat_history'])

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']

    if 'chat_history' not in session:
        session['chat_history'] = []

    session['chat_history'].append({'role': 'user', 'content': user_message})

    try:
        client = genai.Client(api_key=api_key)
        chat = client.chats.create(model="gemini-2.5-flash")

        for msg in session['chat_history']:
            if msg['role'] == 'user':
                response = chat.send_message(msg['content'])

        bot_response = response.text

        session['chat_history'].append({'role': 'assistant', 'content': bot_response})
        session.modified = True

        return render_template('index.html', chat_history=session['chat_history'])

    except Exception as e:
        error_message = f"Error: {str(e)}"
        return render_template('index.html', chat_history=session['chat_history'], error=error_message)

@app.route('/reset')
def reset():
    session['chat_history'] = []
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
