import os
from django.conf import settings
import pandas as pd

file_path = os.path.join(settings.BASE_DIR, "health_prediction", "datasets", "cleaned_mentalDisorder.csv")
df = pd.read_csv(file_path, encoding='utf-8-sig')

print("Model Features:", df.drop(columns=["expert_diagnose"], errors="ignore").columns.tolist())
