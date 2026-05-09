import pandas as pd
import numpy as np

# Generate a synthetic dataset for video meta-learner
np.random.seed(42)
n_samples = 200

# Create dummy ground truth (0 or 1)
ground_truth = np.random.randint(0, 2, n_samples)

# Create synthetic probabilities with some noise
# When truth is 0, prob is mostly low. When truth is 1, prob is mostly high.
probs = np.where(ground_truth == 1, 
                 np.random.normal(0.85, 0.1, n_samples),
                 np.random.normal(0.15, 0.1, n_samples))

# Clip probabilities to [0, 1]
probs = np.clip(probs, 0.0, 1.0)

# Create DataFrame
df = pd.DataFrame({
    'video_path': [f'dummy_vid_{i}.mp4' for i in range(n_samples)],
    'video_name': [f'dummy_vid_{i}' for i in range(n_samples)],
    'cross_efficient_vit_prob': probs,
    'ground_truth': ground_truth
})

# Save to CSV
output_path = './meta_learning_data/meta_features_dataset_video.csv'
df.to_csv(output_path, index=False)
print(f'Generated {output_path}')
