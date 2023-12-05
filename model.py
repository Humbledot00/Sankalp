import pickle
import numpy as np
from tensorflow.keras.models import load_model

# Load vectorizer
with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Load model
model = load_model('chatbot_model.h5')

# Adjusted label mapping
label_mapping = {label: idx for idx, label in enumerate(set(labels))}
responses = [f"intent: {label}" for label in label_mapping.keys()]

def predict(text):
    text_vector = vectorizer.transform([text]).toarray()
    pred = model.predict(text_vector).argmax(axis=1)[0]
    return responses[pred]

print(predict("what is your name"))
print(predict("what time is it"))
