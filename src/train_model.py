#!/usr/bin/env python
# coding: utf-8

# # 🧠 Model Training
# Loads processed data, trains TensorFlow model, and saves the trained model.

# In[1]:


# --- Imports ---
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

import tensorflow as tf
tf.config.set_visible_devices([], 'GPU')

'''
print("TF version:", tf.__version__)
print("Devices:", tf.config.list_physical_devices())
print("Is TensorFlow built with MPS?", tf.config.list_logical_devices('GPU'))
print("Visible devices:", tf.config.get_visible_devices())

with tf.device('/CPU:0'):
    a = tf.random.uniform((1000, 1000))
    b = tf.random.uniform((1000, 1000))
    c = tf.matmul(a, b)
    print("Matrix multiply completed successfully on CPU.")
'''
from tensorflow.keras.layers import Normalization
from sklearn.model_selection import train_test_split

# --- Load Data ---
df = pd.read_csv("nfl_seasonal_preprocessed.csv")


# In[2]:


# --- Split into Features and Labels ---
X = df.drop(columns=["fantasy_points", "fantasy_points_ppr"], errors="ignore") #have to drop both fantasy points bc one gives away the other
y = df.get("fantasy_points_ppr", pd.Series([0]*len(df)))

# --- Train/Test Split ---
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

display(X_train.columns[62:70])


X_train = np.asarray(X_train).astype(np.float32)
X_val   = np.asarray(X_val).astype(np.float32)
y_train = np.asarray(y_train).astype(np.float32)
y_val   = np.asarray(y_val).astype(np.float32)


# In[3]:


# --- Build Model ---
def build_model(X_train):
    # ✅ Remove redundant normalization if X_train is already standardized with StandardScaler
    # Only adapt normalizer if your inputs are *raw*, unscaled data.
    # If you already scaled them earlier, skip normalizer entirely.
    # (comment out this section if you use sklearn.StandardScaler)
    normalizer = Normalization()
    normalizer.adapt(X_train)

    model = tf.keras.Sequential([
        normalizer,  # or remove this line if you pre-scaled with StandardScaler
        tf.keras.layers.Dense(
            256, activation='relu',
            kernel_initializer='he_normal',
            kernel_regularizer=tf.keras.regularizers.l2(1e-4)
        ),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),

        tf.keras.layers.Dense(
            128, activation='relu',
            kernel_initializer='he_normal',
            kernel_regularizer=tf.keras.regularizers.l2(1e-4)
        ),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),

        tf.keras.layers.Dense(64, activation='relu', kernel_initializer='he_normal'),
        tf.keras.layers.Dense(1)
    ])

    # ✅ Use Adam with gradient clipping and smaller learning rate
    optimizer = tf.keras.optimizers.Adam(
        learning_rate=5e-4,  # half of before
        clipnorm=1.0         # prevents exploding gradients
    )

    # ✅ Huber loss is stable for outliers; you can also try MAE if still unstable
    model.compile(
        optimizer=optimizer,
        loss=tf.keras.losses.Huber(delta=1.0),
        metrics=['mae']
    )

    return model


# In[4]:


# --- Sanity Check ---
print("Train shape:", X_train.shape, y_train.shape)
print("Validation shape:", X_val.shape, y_val.shape)
print("Any NaNs in X_train?", np.any(np.isnan(X_train)))
print("Any NaNs in y_train?", np.any(np.isnan(y_train)))
print("Feature range (X_train):", np.min(X_train), "→", np.max(X_train))

'''
nan_counts = np.isnan(X_train).sum()
nan_cols = nan_counts[nan_counts > 0]
print("Columns with NaNs:")
display(nan_cols)
'''

print("Any NaNs in X_train?", np.isnan(X_train).any())
print("Any Infs in X_train?", np.isinf(X_train).any())

if np.isnan(X_train).any() or np.isinf(X_train).any():
    print("Indices of NaNs:")
    print(np.argwhere(np.isnan(X_train)))


# In[5]:


# --- Training ---

model = build_model(X_train)

# --- Callbacks ---
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True,
    verbose=1
)
lr_schedule = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=5,
    min_lr=1e-6,
    verbose=1
)

# 🧩 Optional but recommended: checkpoint best model so it’s not lost if NaNs appear
checkpoint = tf.keras.callbacks.ModelCheckpoint(
    "best_model.keras",
    monitor='val_loss',
    save_best_only=True,
    verbose=1
)

callbacks = [early_stop, lr_schedule, checkpoint]

# --- Training ---
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=100,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

# --- Debug Info ---
print("\nTraining complete.")
print("History keys:", list(history.history.keys()))
print("Final losses:")
for k, v in history.history.items():
    if isinstance(v, list) and len(v) > 0:
        print(f"  {k}: {v[-1]:.4f}")

# --- NaN check ---
import numpy as np
for k in ["loss", "val_loss"]:
    arr = np.array(history.history.get(k, []))
    if np.any(np.isnan(arr)):
        print(f"⚠️ NaNs detected in {k}! Check learning rate or input normalization.")

# --- Save Model ---
model.save("fp_model_final.keras")
print("✅ Model saved as fp_model_final.keras")


# In[6]:


print("Any NaNs in loss?", np.any(np.isnan(history.history.get("loss", []))))


# In[7]:


# --- Analyze Training Metrics ---
import matplotlib.pyplot as plt

# Convert history to DataFrame
history_df = pd.DataFrame(history.history)
print("Available metrics:", list(history_df.columns))

# Summary stats
print("\nFinal Training Metrics:")
print(history_df.tail(1).T)

# --- Plot loss curves ---
plt.figure(figsize=(8, 5))
plt.plot(history_df["loss"], label="Training Loss")
if "val_loss" in history_df:
    plt.plot(history_df["val_loss"], label="Validation Loss", linestyle="--")
plt.title("Model Loss over Epochs")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)
plt.show()

# --- Plot additional metrics (if available) ---
metrics_to_plot = [m for m in history_df.columns if m not in ["loss", "val_loss"]]
if metrics_to_plot:
    for metric in metrics_to_plot:
        plt.figure(figsize=(8, 5))
        plt.plot(history_df[metric], label=f"Training {metric}")
        if f"val_{metric}" in history_df:
            plt.plot(history_df[f"val_{metric}"], label=f"Validation {metric}", linestyle="--")
        plt.title(f"{metric.capitalize()} over Epochs")
        plt.xlabel("Epoch")
        plt.ylabel(metric.capitalize())
        plt.legend()
        plt.grid(True)
        plt.show()


# In[ ]:




