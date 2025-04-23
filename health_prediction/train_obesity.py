import os
import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Set up Django environment if running this as a standalone script
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicure.settings')
django.setup()

from django.conf import settings

# === Load Obesity dataset ===
file_path = os.path.join(settings.BASE_DIR, 'health_prediction', 'datasets', 'obesity_data.csv')
df = pd.read_csv(file_path, encoding='utf-8-sig')

# Convert Gender column to numeric
df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})

# Encode target variable (ObesityCategory)
label_encoder = LabelEncoder()
df["ObesityCategory"] = label_encoder.fit_transform(df["ObesityCategory"])

# Separate features and target
X = df.drop(columns=["ObesityCategory"])
y = df["ObesityCategory"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Prepare to save
model_data = {
    "model": model,
    "label_encoder": label_encoder
}

# Ensure model directory exists
model_dir = os.path.join(settings.BASE_DIR, 'health_prediction', 'models')
os.makedirs(model_dir, exist_ok=True)

# Save model
model_path = os.path.join(model_dir, 'obesity_model.pkl')
with open(model_path, "wb") as f:
    pickle.dump(model_data, f)

print(f"✅ Obesity Model trained and saved successfully at {model_path}!")
