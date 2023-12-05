from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import random
import time
import json

app = Flask(__name__)
CORS(app)

flag_variable = False
stored_messages = []

def is_greeting(message):
    greetings = ['hi', 'hello', 'hey']
    return any(greeting in message.lower() for greeting in greetings)

def process_question(message):
    if re.match(r'^[0-9+\-*/(). ]+$', message):
        try:
            result = eval(message)
            return f'The result is: {result}'
        except Exception as e:
            return f'Error: {str(e)}'

    question_patterns = {
        'weather': ['weather', 'temperature', 'forecast'],
        'time': ['time', 'current time', 'clock'],
        'greeting': ['how are you', 'how is it going', 'what\'s up'],
    }

    json_answers = load_user_answers()
    if message in json_answers:
       json_object = f"I'm not sure, but a user suggested this answer\n\n: \t{json_answers[message]}"
       print(json_object)
       return json_object

    for category, patterns in question_patterns.items():
        if any(pattern in message.lower() for pattern in patterns):
            return generate_response(category)

    return "I don\'t have an answer for that."

def generate_response(category):
    response_dict = {
        'weather': 'The weather is nice today.',
        'time': f'The current time is {time.strftime("%H:%M:%S")}.',
        'greeting': 'I\'m doing well, thank you!',
    }

    return str(response_dict.get(category, 'I don\'t have an answer for that.'))

def simulate_bot_processing(user_message):

    time.sleep(1)

    if is_greeting(user_message):
        return random.choice(['Hi there!', 'Hello!', 'Hey!'])
    else:
        return process_question(user_message)

def load_user_answers():
    try:
        with open('user_answers.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_answers(user_answers):
    with open('user_answers.json', 'w') as file:
        json.dump(user_answers, file, indent=2)

@app.route('/bot', methods=['POST'])
def bot_reply():
    global flag_variable
    global stored_messages

    user_message = request.json.get('message', '')

    if user_message:

        if(flag_variable):
            user_answer = user_message
            user_answers = load_user_answers()
            user_answers[stored_messages] = user_answer
            save_user_answers(user_answers)
            flag_variable = False
            stored_messages = ''
            return jsonify({'bot_reply': "Thanks, I'll remember next time!!!"})

        bot_response = simulate_bot_processing(user_message)

        # If the bot is asking for help, store the message in a JSON file
        if "I don't have an answer for that." in bot_response:
            flag_variable = True
            stored_messages = user_message
            return jsonify({'bot_reply': 'Can you help me with the answer?'})

        return jsonify({'bot_reply': bot_response})

    return jsonify({'error': 'Invalid request'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
