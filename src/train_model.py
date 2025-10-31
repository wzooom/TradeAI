import os
from pathlib import Path
import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Normalization
from sklearn.model_selection import train_test_split

tf.config.set_visible_devices([], "GPU")
# Completely disable GPU/MPS usage
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# --- Load Data ---
df = pd.read_csv(
    Path(__file__).parent.parent / "data" / "nfl_seasonal_preprocessed.csv"
)

X = df.drop(columns=["fantasy_points", "fantasy_points_ppr"], errors="ignore")
y = df.get("fantasy_points_ppr", pd.Series([0] * len(df)))

# --- Train/Test Split ---
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = np.asarray(X_train).astype(np.float32)
X_val = np.asarray(X_val).astype(np.float32)
y_train = np.asarray(y_train).astype(np.float32)
y_val = np.asarray(y_val).astype(np.float32)


# --- Build Model (FIXED VERSION) ---
def build_model(X_train):
    """
    Fixed version that explicitly sets input shape for Normalization layer
    """
    # Get input dimension
    input_dim = X_train.shape[1]
    print(f"Building model with input dimension: {input_dim}")

    # ✅ FIX: Specify input_shape in Normalization layer
    normalizer = Normalization(input_shape=(input_dim,))
    normalizer.adapt(X_train)

    # Alternative: Build entire model with explicit Input layer
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(input_dim,)),  # ✅ Explicit input shape
            normalizer,
            tf.keras.layers.Dense(
                256,
                activation="relu",
                kernel_initializer="he_normal",
                kernel_regularizer=tf.keras.regularizers.l2(1e-4),
            ),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(
                128,
                activation="relu",
                kernel_initializer="he_normal",
                kernel_regularizer=tf.keras.regularizers.l2(1e-4),
            ),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(
                64, activation="relu", kernel_initializer="he_normal"
            ),
            tf.keras.layers.Dense(1),
        ]
    )

    optimizer = tf.keras.optimizers.Adam(
        learning_rate=5e-4,
        clipnorm=1.0,
    )

    model.compile(
        optimizer=optimizer, loss=tf.keras.losses.Huber(delta=1.0), metrics=["mae"]
    )

    return model


# --- ALTERNATIVE: Build without Normalization layer ---
def build_model_no_normalization(X_train):
    """
    Alternative version that doesn't use Keras Normalization layer
    Instead, normalize externally with StandardScaler (recommended for production)
    """
    input_dim = X_train.shape[1]
    print(f"Building model with input dimension: {input_dim}")

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(input_dim,)),
            # No Normalization layer - handle externally
            tf.keras.layers.Dense(
                256,
                activation="relu",
                kernel_initializer="he_normal",
                kernel_regularizer=tf.keras.regularizers.l2(1e-4),
            ),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(
                128,
                activation="relu",
                kernel_initializer="he_normal",
                kernel_regularizer=tf.keras.regularizers.l2(1e-4),
            ),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(
                64, activation="relu", kernel_initializer="he_normal"
            ),
            tf.keras.layers.Dense(1),
        ]
    )

    optimizer = tf.keras.optimizers.Adam(
        learning_rate=5e-4,
        clipnorm=1.0,
    )

    model.compile(
        optimizer=optimizer, loss=tf.keras.losses.Huber(delta=1.0), metrics=["mae"]
    )

    return model


# --- Sanity Check ---
print("Train shape:", X_train.shape, y_train.shape)
print("Validation shape:", X_val.shape, y_val.shape)
print("Any NaNs in X_train?", np.any(np.isnan(X_train)))
print("Any NaNs in y_train?", np.any(np.isnan(y_train)))
print("Feature range (X_train):", np.min(X_train), "→", np.max(X_train))

print("Any NaNs in X_train?", np.isnan(X_train).any())
print("Any Infs in X_train?", np.isinf(X_train).any())

if np.isnan(X_train).any() or np.isinf(X_train).any():
    print("Indices of NaNs:")
    print(np.argwhere(np.isnan(X_train)))

# --- Choose which version to use ---
USE_NORMALIZATION_LAYER = False  # Set to False for production (recommended)

if USE_NORMALIZATION_LAYER:
    print("\n🔧 Using model WITH Normalization layer (fixed version)")
    model = build_model(X_train)
    model_name = "fp_model_final_with_norm.keras"
else:
    print("\n🔧 Using model WITHOUT Normalization layer (recommended)")

    # Normalize data externally using StandardScaler
    from sklearn.preprocessing import StandardScaler
    import joblib

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    # Save the scaler
    scaler_path = Path(__file__).parent.parent / "models" / "scaler.pkl"
    joblib.dump(scaler, scaler_path)
    print(f"✅ Scaler saved to {scaler_path}")

    # Update training data
    X_train = X_train_scaled
    X_val = X_val_scaled

    model = build_model_no_normalization(X_train)
    model_name = "fp_model_final.keras"

# Display model architecture
print("\n📊 Model Architecture:")
model.summary()

# --- Callbacks ---
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss", patience=10, restore_best_weights=True, verbose=1
)
lr_schedule = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6, verbose=1
)

checkpoint_path = (
    Path(__file__).parent.parent / "models" / "best_model_checkpoint.keras"
)
checkpoint = tf.keras.callbacks.ModelCheckpoint(
    str(checkpoint_path), monitor="val_loss", save_best_only=True, verbose=1
)

callbacks = [early_stop, lr_schedule, checkpoint]

# --- Training ---
print("\n🚀 Starting training...")
history = model.fit(
    X_train,
    y_train,
    validation_data=(X_val, y_val),
    epochs=100,
    batch_size=32,
    callbacks=callbacks,
    verbose=1,
)

# --- Debug Info ---
print("\n✅ Training complete.")
print("History keys:", list(history.history.keys()))
print("\nFinal losses:")
for k, v in history.history.items():
    if isinstance(v, list) and len(v) > 0:
        print(f"  {k}: {v[-1]:.4f}")

# --- NaN check ---
for k in ["loss", "val_loss"]:
    arr = np.array(history.history.get(k, []))
    if np.any(np.isnan(arr)):
        print(f"⚠️ NaNs detected in {k}! Check learning rate or input normalization.")
    else:
        print(f"✅ No NaNs in {k}")

# --- Save Model ---
final_model_path = Path(__file__).parent.parent / "models" / model_name
model.save(final_model_path)
print(f"\n✅ Model saved as {model_name}")
print(f"   Location: {final_model_path}")

# --- Test Loading the Model ---
print("\n🧪 Testing model loading...")
try:
    loaded_model = tf.keras.models.load_model(final_model_path, compile=False)
    print("✅ Model loads successfully!")
    print(f"   Input shape: {loaded_model.input_shape}")
    print(f"   Output shape: {loaded_model.output_shape}")

    # Test prediction
    test_pred = loaded_model.predict(X_val[:1], verbose=0)
    print(f"✅ Test prediction successful: {test_pred[0][0]:.2f}")
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    print("   You may need to use the conversion script.")

# --- Analyze Training Metrics ---
history_df = pd.DataFrame(history.history)
print("\nAvailable metrics:", list(history_df.columns))

print("\nFinal Training Metrics:")
print(history_df.tail(1).T)

# --- Plot loss curves ---
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(history_df["loss"], label="Training Loss", linewidth=2)
if "val_loss" in history_df:
    plt.plot(
        history_df["val_loss"], label="Validation Loss", linestyle="--", linewidth=2
    )
plt.title("Model Loss over Epochs", fontsize=14, fontweight="bold")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.grid(True, alpha=0.3)

# --- Plot MAE ---
plt.subplot(1, 2, 2)
if "mae" in history_df:
    plt.plot(history_df["mae"], label="Training MAE", linewidth=2)
if "val_mae" in history_df:
    plt.plot(history_df["val_mae"], label="Validation MAE", linestyle="--", linewidth=2)
plt.title("Mean Absolute Error over Epochs", fontsize=14, fontweight="bold")
plt.xlabel("Epoch")
plt.ylabel("MAE")
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

# Save plot
plot_path = Path(__file__).parent.parent / "results" / "training_history.png"
plot_path.parent.mkdir(exist_ok=True)
plt.savefig(plot_path, dpi=150, bbox_inches="tight")
print(f"\n💾 Training plot saved to: {plot_path}")

plt.show()

print("\n" + "=" * 60)
print("✅ TRAINING COMPLETE!")
print("=" * 60)
if not USE_NORMALIZATION_LAYER:
    print("📌 Remember to use the scaler when making predictions:")
    print("   1. Load scaler: scaler = joblib.load('scaler.pkl')")
    print("   2. Scale features: X_scaled = scaler.transform(X)")
    print("   3. Predict: y_pred = model.predict(X_scaled)")
print("=" * 60)
