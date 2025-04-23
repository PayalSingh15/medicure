import os
import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Django setup to use settings
import django
from pathlib import Path

# Set up Django environment manually since this script might be run independently
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicure.settings')
django.setup()

from django.conf import settings

# === Load dataset ===
file_path = os.path.join(settings.BASE_DIR, 'health_prediction', 'datasets', 'cleaned_mentalDisorder.csv')
df = pd.read_csv(file_path, encoding='utf-8-sig')

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Drop irrelevant or problematic columns
df = df.drop(columns=["ï»¿patient_number"], errors="ignore")

# Debug: print updated columns
print("Updated Columns:", df.columns.tolist())

# Ensure 'expert_diagnose' exists
if "expert_diagnose" not in df.columns:
    raise KeyError("❌ ERROR: 'expert_diagnose' column is missing. Check the dataset.")

# Separate features and target
X = df.drop(columns=["expert_diagnose"], errors="ignore")
y = df["expert_diagnose"]

# Encode target variable
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model and label encoder
model_data = {
    "model": model,
    "label_encoder": label_encoder
}

# === Save the trained model ===
model_dir = os.path.join(settings.BASE_DIR, 'health_prediction', 'models')
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, 'mental_health_model.pkl')
with open(model_path, "wb") as f:
    pickle.dump(model_data, f)

print(f"✅ Model trained and saved successfully at {model_path}!")
