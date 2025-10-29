#!/usr/bin/env python
# coding: utf-8

# # 📊 Model Testing
# Loads trained model and test data, evaluates performance, and plots predictions.

# In[1]:


# --- Imports and Setup ---

import os
# Completely disable GPU/MPS usage
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_MPS_ENABLED"] = "0"
os.environ["TF_USE_LEGACY_KERAS"] = "1"

# Optional safety (macOS): disable Metal runtime explicitly
os.environ["TF_MPS_ENABLED"] = "0"

import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

# Display options
pd.set_option('display.max_columns', None)
sns.set(style="whitegrid")

print("✅ Libraries imported successfully.")


# In[2]:


# --- Load Cleaned and Feature-Engineered Dataset ---
df = pd.read_csv('nfl_seasonal_preprocessed.csv')
print("✅ Dataset loaded. Shape:", df.shape)
#print(df.head())

# Separate features and target
X = df.drop(columns=['fantasy_points', 'fantasy_points_ppr'])
y = df['fantasy_points_ppr']


# In[3]:


# --- Split into Test Set (same random_state as training) ---
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("✅ Data split into train/test sets.")
print("Train shape:", X_train.shape)
print("Test shape:", X_test.shape)


# In[ ]:


# --- Load Trained Keras Model ---
import tensorflow as tf
tf.config.set_visible_devices([], 'GPU')

from tensorflow.keras.models import load_model

# Replace this path with your actual model file name if different
model = load_model('fp_model_final.keras')

print("✅ Keras model loaded successfully!")
model.summary()


# In[ ]:


# --- Evaluate the Keras Model ---
# Predict on the test set
y_pred = model.predict(X_test)

# Bc it's a regression model, flatten predictions
y_pred = y_pred.flatten()

# Metrics
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("📊 Model Performance on Test Set:")
print(f"Mean Squared Error (MSE): {mse:.4f}")
print(f"R² Score: {r2:.4f}")


# In[ ]:


# --- Visualization: Predicted vs Actual ---
plt.figure(figsize=(6,5))
plt.scatter(y_test, y_pred, alpha=0.6, color='teal')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.xlabel("Actual Target")
plt.ylabel("Predicted Target")
plt.title("Keras Model: Actual vs Predicted")
plt.show()


# In[ ]:


# --- Save Test Results ---
results_df = pd.DataFrame({
    'Actual': y_test,
    'Predicted': y_pred
})

results_df.to_csv('test_predictions.csv', index=False)
print("💾 Test predictions saved to 'test_predictions.csv'")


# In[ ]:




