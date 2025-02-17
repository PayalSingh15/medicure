import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Load the Obesity dataset
file_path = "D:/Medicure/health_prediction/datasets/obesity_data.csv"
df = pd.read_csv(file_path, encoding='utf-8-sig')

# Convert categorical columns to numeric
df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})

# Encode the target variable (ObesityCategory)
label_encoder = LabelEncoder()
df["ObesityCategory"] = label_encoder.fit_transform(df["ObesityCategory"])

# Define features (X) and target (y)
X = df.drop(columns=["ObesityCategory"])  # Features
y = df["ObesityCategory"]  # Target

# Split into training & testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the trained model and label encoder
model_data = {
    "model": model,
    "label_encoder": label_encoder
}

# Ensure the models directory exists
import os
os.makedirs("D:/Medicure/health_prediction/models", exist_ok=True)

# Save the trained model
model_path = "D:/Medicure/health_prediction/models/obesity_model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(model_data, f)

print(f"✅ Obesity Model trained and saved successfully at {model_path}!")
