from flask import Flask, request, jsonify
import os
import pymongo
from flask_cors import CORS
import re
import random
import time
import json
from flask_cors import cross_origin


app = Flask(__name__)
CORS(app)

# MongoDB Atlas connection details
MONGODB_URI = "mongodb+srv://workforshreyas:yiEOXA7G7qxY90Pf@cluster0.li4h8f5.mongodb.net/?retryWrites=true&w=majority"  # Replace with your MongoDB Atlas connection string
DB_NAME = "ChatBot"  # Replace with your database name
COLLECTION_NAME = "user_answers"
USER_INFO = "user_info"


# MongoDB setup
client = pymongo.MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
userinfo = db[USER_INFO]

teach_flag = False
flag_variable = False
stored_messages = ''

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

    search_question = message

    query = {"question": search_question}

    result = collection.find_one(query)

    if result:
        # Access the answer from the document
        found_answer = result["answer"]
        print(found_answer)
        return str(found_answer)

    
    responce = find_answer(message, qa_data, custom_stop_words)

    for category, patterns in question_patterns.items():
        if any(pattern in message.lower() for pattern in patterns):
            return str(generate_response(category))

    return str(responce)

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
         return str(process_question(user_message))
    


# Save user answers to MongoDB
def save_user_answers(sample, user_answer):
    # Create the document
    document = {
        "question": sample,
        "answer": user_answer
    }

    # Insert the document into the collection
    collection.insert_one(document)


def custom_tokenize(text, stop_words):
    # Convert the text to lowercase for case-insensitivity
    text = text.lower()

    # Replace punctuation with spaces
    for char in '.,?!':
        text = text.replace(char, ' ')

    # Split the text into words
    words = text.split()

    # Remove stop words
    tokens = [word for word in words if word not in stop_words]

    return tokens

def calculate_similarity(user_tokens, question_tokens):
    # Calculate the Jaccard similarity
    intersection = set(user_tokens) & set(question_tokens)
    union = set(user_tokens) | set(question_tokens)

    # Avoid division by zero
    similarity = len(intersection) / len(union) if len(union) > 0 else 0

    return similarity

def replace_words(sentence, word_dict):
    replaced_sentence = []

    for word in sentence:
        lower_word = word.lower()
        found = False

        for key, synonyms in word_dict.items():
            if lower_word in synonyms:
                replaced_sentence.append(key)
                found = True
                break

        if not found:
            replaced_sentence.append(word)

    return replaced_sentence

mapping = {
    "location": ["locating", "located", "address", "area", "site"],
    "reset": ["change", "update", "modify"],
    "password": ["passcode", "security code"],
    "meaning": ["significance", "purpose", "sense"],
    "introduce": ["present", "describe", "provide information","about"],
    "contact": ["reach", "get in touch with", "communicate with"],
    "number": ["phone number", "contact number", "telephone"],
    "location": ["place", "address", "site"],
    "course": ["program", "study program", "educational program"],
    "be": ["bachelor of engineering", "undergraduate engineering"],
    "hod": ["head of department", "department head"],
    "seats": ["available slots", "openings", "positions"],
    "engineering": ["technical", "engineering studies"],
    "college": ["institution", "educational institution"],
    "principal": ["headmaster", "school head", "director"],
    "admission": ["enrollment", "registration", "entry"],
    "fees": ["tuition fees", "cost", "charges"],
    "cutoff": ["minimum score", "qualifying score", "threshold"],
    "hostel": ["dormitory", "residence", "accommodation"],
    "canteen": ["cafeteria", "food court", "dining area"],
    "bus": ["shuttle", "transport", "vehicle"],
    "transportation": ["bus service", "shuttle service", "commute"],
    "pg": ["postgraduate", "graduate studies", "master's degree"],
    "ug": ["undergraduate", "bachelor's degree", "college degree"],
    "principal": ["dr. mahesh prasanna", "mahesh prasanna"],
    "uniform": ["dress code", "attire", "clothing policy"],
    "blocks": ["buildings", "structures", "facilities"],
    "ieee": ["institute of electrical and electronics engineers", "professional association"],
    "eee": ["electrical and electronics engineering", "branch"],
    "library": ["resource center", "book repository", "study center"],
    "wifi": ["wireless network", "internet access"],
    "computer": ["computing", "it", "technology"],
    "aiml": ["artificial intelligence and machine learning", "ai and ml", "machine learning"],
    "cse": ["computer science and engineering", "computing", "cs"],
    "ec": ["electronics and communication engineering","electronics"],
    "mech": ["mechanical engineering", "mechanical", "me"],
    "vcet":["vivekananda college of engineering and technology","vivekananda college","vivekananda college of engg and tech"]
    # Add more mappings as needed
}

def find_answer(user_input, qa_data, stop_words, similarity_threshold=0.4):
    user_tokens = custom_tokenize(user_input, stop_words)
    replaced_sentence = replace_words(user_tokens, mapping)
    print(user_tokens,replaced_sentence)

    # Initialize variables for the best match
    best_match_question = ""
    best_match_answer = ""
    best_similarity = 0

    for entry in qa_data["data"]:
        question = entry["question"]
        answer = entry["answer"]

        question_tokens = custom_tokenize(question, stop_words)
        similarity = calculate_similarity(replaced_sentence, question_tokens)

        # Check if the current question has a higher similarity
        if similarity > best_similarity:
            best_similarity = similarity
            best_match_question = question
            best_match_answer = answer

    # Check if the best match has at least the specified similarity threshold
    if best_similarity >= similarity_threshold:
        return best_match_answer
    else:
        return "Sorry, I couldn't find a suitable answer."

# Load the JSON file with question-answer pairs
with open('you.json', 'r') as file:
    qa_data = json.load(file)

# Custom stop words list
custom_stop_words = ['the', 'and', 'is', 'in', 'to', 'it', 'of','I', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was',
    'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and',
    'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on',
    'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
    'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're',
    've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn',
    'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn', "won't", "wouldn't"
]


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'OPTIONS, POST')
    return response

@app.route('/bot', methods=['POST'])
def bot_reply():
    global flag_variable
    global stored_messages
    global teach_flag
    global sample



    user_message = request.json.get('message', '')

    if user_message:

        if "can I teach you?" in user_message:
            teach_flag = True
            return jsonify({'bot_reply': "Sure happy to learn from the Master...Tell me the question first and once I get it Provide me with the answer"})


        if(teach_flag):
            user_answer = user_message

            if(user_answer):
                sample = user_answer
                flag_variable = True
                teach_flag = False
                return jsonify({'bot_reply': "Provide me the answer"})



        if(flag_variable):
            user_answer = user_message
            save_user_answers(sample, user_answer)
            flag_variable = False
            stored_messages = ''
            return jsonify({'bot_reply': "Thanks, I'll remember next time!!!"})

        bot_response = simulate_bot_processing(user_message)

        return jsonify({'bot_reply': bot_response})

    return jsonify({'error': 'Invalid request'}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))

