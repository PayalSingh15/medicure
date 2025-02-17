import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load the PCOS dataset
file_path = "datasets\CLEAN- PCOS SURVEY SPREADSHEET.csv"
df = pd.read_csv(file_path, encoding='utf-8-sig')

# Define features (X) and target (y)
features = [
    "Age (in Years)",
    "Weight (in Kg)",
    "Height (in Cm / Feet)",
    "After how many months do you get your periods?\n(select 1- if every month/regular)",  # Updated
    "Have you gained weight recently?",
    "Do you have excessive body/facial hair growth ?",
    "Are you noticing skin darkening recently?",
    "Do have hair loss/hair thinning/baldness ?",
    "Do you have pimples/acne on your face/jawline ?",
    "Do you eat fast food regularly ?",
    "Do you exercise on a regular basis ?",
    "Do you experience mood swings ?",
    "Are your periods regular ?",
    "How long does your period last ? (in Days)\nexample- 1,2,3,4.....",  # Updated
    "Can you tell us your blood group ?"
]

X = df[features]  # Features
y = df["Have you been diagnosed with PCOS/PCOD?"]  # Target

# Split into training & testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the trained model
model_path = "models/pcos_model.pkl"
with open(model_path, "wb") as f:
    pickle.dump({"model": model, "features": features}, f)

print(f"✅ PCOS Model trained and saved successfully at {model_path}!")