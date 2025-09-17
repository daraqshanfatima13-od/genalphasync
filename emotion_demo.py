from transformers import pipeline

# Load a ready-made emotion detection model
emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

# Try some example sentences
texts = [
    "I am very happy today, yaar!",
    "I feel so sad and alone.",
    "I am angry with my friend.",
    "I want to die."
]

for t in texts:
    result = emotion_model(t)
    print(f"Text: {t}")
    print("Prediction:", result)
    print("-" * 40)
