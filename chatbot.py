from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key="AIzaSyByePHBhUH0nHr9A1cj7PgO1tmv9FyLmYc")  # Replace with your key

# Initialize Gemini model
model = genai.GenerativeModel("gemini-pro")

# Start a persistent chat session
chat_session = model.start_chat()

@app.route('/')
def home():
    return render_template('index10.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']

    try:
        response = chat_session.send_message(user_message)
        reply = response.text
        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'reply': f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)



