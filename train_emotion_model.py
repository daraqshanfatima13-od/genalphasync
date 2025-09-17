# gen_alpha_emotion.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import string

# -----------------------------
# Step 1: Create Dataset
# -----------------------------
data = {
    "text": [
        # Happy sentences
        "I feel so happy today!", "This is the best day ever!", "I am thrilled with the results!",
        "Life feels wonderful right now.", "I can’t stop smiling!", "Everything is going perfectly.",
        "I am overjoyed with this news.", "I feel cheerful and energetic.", "This moment makes me so delighted.",
        "I am in a fantastic mood.", "I am loving this experience!", "I feel amazing!", "This is awesome!",
        "I am so joyful.", "Everything is going well.", "I feel wonderful.", "I am in high spirits.",
        "This day is fantastic.", "I feel ecstatic.", "I am really content.",

        # Sad sentences
        "I feel sad and lonely.", "Nothing seems to be going right.", "I am heartbroken.",
        "I feel down today.", "Everything feels hopeless.", "I am disappointed with the outcome.",
        "I feel miserable right now.", "Life seems so unfair.", "I am in a gloomy mood.", "I feel sorrowful and tired.",
        "I am feeling blue.", "I feel depressed.", "Nothing makes me happy.", "I am disheartened.", "I feel miserable today.",
        "I am upset.", "Life feels heavy.", "I feel melancholic.", "I feel gloomy.", "I am downcast.",

        # Angry sentences
        "I am really angry at what happened.", "This makes me so frustrated!", "I can’t believe this injustice!",
        "I feel furious right now.", "How could they do this to me?", "I am mad and upset.", "I feel outraged by the situation.",
        "This is completely unacceptable!", "I am seething with anger.", "I feel irritated and annoyed.",
        "I am furious.", "I feel enraged.", "I am annoyed by this.", "I feel very upset.", "I am extremely mad.",
        "This situation is infuriating.", "I feel exasperated.", "I am mad at everyone.", "I feel wrathful.", "I am angry.",

        # Neutral sentences
        "I feel nothing special today.", "Life is just okay.", "I don’t feel any strong emotions.",
        "Today is just another ordinary day.", "I am neither happy nor sad.", "Everything seems normal.",
        "I feel indifferent about this.", "Nothing much to report.", "I feel calm and relaxed.", "I am in a neutral state of mind.",
        "Life feels normal.", "I feel average.", "I am not feeling anything.", "Today is fine.", "I am feeling neutral.",
        "I am okay.", "Everything is usual.", "I feel so-so.", "I am ordinary today.", "I feel balanced.",

        # Surprise sentences
        "Wow! I did not expect that!", "That was completely unexpected!", "I am amazed by this!",
        "What a shocking turn of events!", "I can’t believe what just happened!", "This is astonishing!",
        "I feel so surprised right now.", "I did not see that coming!", "That was unbelievable!", "I am stunned by this news.",
        "I am flabbergasted.", "I am astonished.", "I can’t believe it!", "I am shocked.", "This blew my mind!",
        "What a surprise!", "I am taken aback.", "This is incredible!", "I am amazed beyond words.", "I am startled!"
    ],
    "label": (
        ["happy"]*20 +
        ["sad"]*20 +
        ["angry"]*20 +
        ["neutral"]*20 +
        ["surprise"]*20
    )
}

df = pd.DataFrame(data)

# -----------------------------
# Step 2: Preprocess Text
# -----------------------------
def preprocess(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

df['text'] = df['text'].apply(preprocess)

# -----------------------------
# Step 3: Split Dataset
# -----------------------------
X = df['text']
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -----------------------------
# Step 4: Vectorize Text
# -----------------------------
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# -----------------------------
# Step 5: Train Model
# -----------------------------
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

# Evaluate
y_pred = model.predict(X_test_vec)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# -----------------------------
# Step 6: Live Testing
# -----------------------------
print("\nType sentences to detect emotion (type 'exit' to quit)")
while True:
    sentence = input("You: ")
    if sentence.lower() == 'exit':
        break
    sentence_vec = vectorizer.transform([preprocess(sentence)])
    prediction = model.predict(sentence_vec)
    print("Predicted emotion:", prediction[0])
