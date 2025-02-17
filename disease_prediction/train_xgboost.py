import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb
import pickle
import os

# Load dataset
csv_path = "Dataset/disease_data.csv"  # Update path if needed
df = pd.read_csv(csv_path)

# Prepare features and labels
X = df.drop(columns=['prognosis'])
y = df['prognosis']

# Convert disease names to numeric labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

# Define XGBoost model
xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='mlogloss',
    use_label_encoder=False,
    random_state=42
)

# Train the model
xgb_model.fit(X_train, y_train)

# Evaluate accuracy
train_acc = xgb_model.score(X_train, y_train)
test_acc = xgb_model.score(X_test, y_test)

print(f"\n✅ Train Accuracy: {train_acc:.2f}")
print(f"✅ Test Accuracy: {test_acc:.2f}")

# Save model and required objects
model_data = {
    'model': xgb_model,
    'scaler': scaler,
    'label_encoder': label_encoder,
    'symptoms_list': X.columns.tolist(),
    'diseases': label_encoder.classes_.tolist()
}

model_path = os.path.join(os.path.dirname(__file__), "disease_model_xgb.pkl")
with open(model_path, "wb") as file:
    pickle.dump(model_data, file)

print("\n✅ XGBoost model saved successfully as 'disease_model_xgb.pkl'")
