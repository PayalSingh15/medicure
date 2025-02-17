import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import os
import pickle
from collections import Counter

# Load new dataset
csv_path = os.path.join(os.path.dirname(__file__), "Dataset/disease_data.csv")
df = pd.read_csv(csv_path)

# Prepare data
X = df.drop(['prognosis'], axis=1)
y = df['prognosis']

print("Original class distribution:")
print(Counter(y))

# Perform upsampling dynamically
max_samples = max(Counter(y).values())
data_resampled = pd.DataFrame()

data = pd.concat([X, y], axis=1)
for class_name in y.unique():
    class_data = data[data['prognosis'] == class_name]
    upsampled = resample(class_data, replace=True, n_samples=max_samples, random_state=42)
    data_resampled = pd.concat([data_resampled, upsampled])

X_resampled = data_resampled.drop(['prognosis'], axis=1)
y_resampled = data_resampled['prognosis']

print("\nResampled class distribution:")
print(Counter(y_resampled))

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_resampled)

# Stratified sampling for better train-test split
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in sss.split(X_scaled, y_resampled):
    X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
    y_train, y_test = y_resampled.iloc[train_idx], y_resampled.iloc[test_idx]

# Train the model with stronger regularization to prevent overfitting
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    min_samples_split=10,
    min_samples_leaf=15,
    max_features=0.5,
    bootstrap=True,
    oob_score=True,
    random_state=42,
    n_jobs=-1
)

print("\nTraining model...")
model.fit(X_train, y_train)

# Save model and scaler
model_data = {
    'model': model,
    'scaler': scaler,
    'symptoms_list': X.columns.tolist(),
    'diseases': y.unique().tolist()
}

model_path = os.path.join(os.path.dirname(__file__), "disease_model.pkl")
with open(model_path, "wb") as file:
    pickle.dump(model_data, file)

print(f"\nTrain accuracy: {model.score(X_train, y_train):.2f}")
print(f"Test accuracy: {model.score(X_test, y_test):.2f}")
print(f"Out-of-Bag accuracy: {model.oob_score_:.2f}")

# Feature importance analysis
feature_importance = pd.DataFrame({
    'symptom': X.columns,
    'importance': model.feature_importances_
})
print("\nTop 10 most important symptoms:")
print(feature_importance.sort_values('importance', ascending=False).head(10))