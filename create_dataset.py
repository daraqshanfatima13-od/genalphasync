import pandas as pd

# Define dataset
data = {
    "text": [
        "I feel so happy today!", "This is the best day ever!", "I am thrilled with the results!",
        "Life feels wonderful right now.", "I can’t stop smiling!", "Everything is going perfectly.",
        "I am overjoyed with this news.", "I feel cheerful and energetic.", "This moment makes me so delighted.",
        "I am in a fantastic mood!", "I feel sad and lonely.", "Nothing seems to be going right.", 
        "I am heartbroken.", "I feel down today.", "Everything feels hopeless.", "I am disappointed with the outcome.",
        "I feel miserable right now.", "Life seems so unfair.", "I am in a gloomy mood.", "I feel sorrowful and tired.",
        "I am really angry at what happened.", "This makes me so frustrated!", "I can’t believe this injustice!", 
        "I feel furious right now.", "How could they do this to me?", "I am mad and upset.", "I feel outraged by the situation.",
        "This is completely unacceptable!", "I am seething with anger.", "I feel irritated and annoyed.", 
        "I feel nothing special today.", "Life is just okay.", "I don’t feel any strong emotions.", 
        "Today is just another ordinary day.", "I am neither happy nor sad.", "Everything seems normal.", 
        "I feel indifferent about this.", "Nothing much to report.", "I feel calm and relaxed.", "I am in a neutral state of mind.",
        "Wow! I did not expect that!", "That was completely unexpected!", "I am amazed by this!", 
        "What a shocking turn of events!", "I can’t believe what just happened!", "This is astonishing!", 
        "I feel so surprised right now.", "I did not see that coming!", "That was unbelievable!", "I am stunned by this news!"
    ],
    "label": [
        "happy","happy","happy","happy","happy","happy","happy","happy","happy","happy",
        "sad","sad","sad","sad","sad","sad","sad","sad","sad","sad",
        "angry","angry","angry","angry","angry","angry","angry","angry","angry","angry",
        "neutral","neutral","neutral","neutral","neutral","neutral","neutral","neutral","neutral","neutral",
        "surprise","surprise","surprise","surprise","surprise","surprise","surprise","surprise","surprise","surprise"
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("gen_alpha_emotion_dataset.csv", index=False)
print("Starter dataset created! Total samples:", len(df))
