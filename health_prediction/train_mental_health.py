import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Load the cleaned dataset
file_path = "D:/Medicure/health_prediction/datasets/cleaned_mentalDisorder.csv"
df = pd.read_csv(file_path, encoding='utf-8-sig')

# Standardize column names (remove spaces & hidden characters)
df.columns = df.columns.str.strip().str.lower()

# Drop non-numeric columns
df = df.drop(columns=["ï»¿patient_number"], errors="ignore")

# Print updated columns to confirm
print("Updated Columns:", df.columns.tolist())

# Ensure 'expert_diagnose' exists
if "expert_diagnose" not in df.columns:
    raise KeyError("❌ ERROR: 'expert_diagnose' column is missing. Check the dataset.")

# Separate features and target variable
X = df.drop(columns=["expert_diagnose"], errors="ignore")
y = df["expert_diagnose"]

# Convert labels into numbers
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

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

# Ensure models directory exists before saving
import os
os.makedirs("D:/Medicure/health_prediction/models", exist_ok=True)

# Save the trained model
model_path = "D:/Medicure/health_prediction/models/mental_health_model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(model_data, f)

print(f"✅ Model trained and saved successfully at {model_path}!")
