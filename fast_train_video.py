import pandas as pd
import numpy as np
import os
import json
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

np.random.seed(42)
n_samples = 200

ground_truth = np.random.randint(0, 2, n_samples)
probs = np.where(ground_truth == 1, 
                 np.random.normal(0.85, 0.1, n_samples),
                 np.random.normal(0.15, 0.1, n_samples))
probs = np.clip(probs, 0.0, 1.0)

df = pd.DataFrame({
    'video_path': [f'dummy_vid_{i}.mp4' for i in range(n_samples)],
    'video_name': [f'dummy_vid_{i}' for i in range(n_samples)],
    'cross_efficient_vit_prob': probs,
    'ground_truth': ground_truth
})

feature_cols = ['cross_efficient_vit_prob']
X = df[feature_cols]
y = df['ground_truth']

imputer = SimpleImputer(strategy="median")
scaler = StandardScaler()
model = LogisticRegression(solver="liblinear", random_state=42, class_weight="balanced")

X_imputed = imputer.fit_transform(X)
X_scaled = scaler.fit_transform(X_imputed)
model.fit(X_scaled, y)

media_type_artifact_subdir = "./api/meta_model_artifacts/video"
os.makedirs(media_type_artifact_subdir, exist_ok=True)

joblib.dump(model, os.path.join(media_type_artifact_subdir, "deepfake_meta_learner.joblib"))
joblib.dump(scaler, os.path.join(media_type_artifact_subdir, "deepfake_meta_scaler.joblib"))
joblib.dump(imputer, os.path.join(media_type_artifact_subdir, "deepfake_meta_imputer.joblib"))

with open(os.path.join(media_type_artifact_subdir, "deepfake_meta_feature_columns.json"), "w") as f:
    json.dump(feature_cols, f, indent=2)

print("Created video meta learner artifacts successfully.")
