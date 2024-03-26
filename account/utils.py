from googletrans import Translator
import pickle

def translate_to_english(text):
    translator = Translator()
    translated_text = translator.translate(text, dest='en')
    return translated_text.text

def detect_cyberbullying(text):
    # Load the trained pipeline from the file
    with open('pipeline.pkl', 'rb') as f:
        tfidf_loaded, logistic_regression_loaded = pickle.load(f)
    
    # Make predictions using the loaded pipeline
    X_input = [text]
    X_input_tfidf = tfidf_loaded.transform(X_input)
    predicted_label = logistic_regression_loaded.predict(X_input_tfidf)
    
    # Assuming the model predicts 1 for cyberbullying and 0 otherwise
    return predicted_label[0] == 1
