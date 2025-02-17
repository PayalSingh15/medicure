import pandas as pd

file_path = "D:/Medicure/health_prediction/datasets/cleaned_mentalDisorder.csv"
df = pd.read_csv(file_path, encoding='utf-8-sig')

print("Model Features:", df.drop(columns=["expert_diagnose"], errors="ignore").columns.tolist())
