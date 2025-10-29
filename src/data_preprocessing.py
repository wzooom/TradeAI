#!/usr/bin/env python
# coding: utf-8

# # 🧩 Data Preprocessing
# Fetches raw data from API, cleans it, and saves to CSV.

# In[7]:


# --- Imports ---
import requests
import pandas as pd
import numpy as np
import nfl_data_py as nfl
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.preprocessing import StandardScaler

# --- Fetch Data ---
years = list(range(2015, 2024))

df = nfl.import_seasonal_data(years, s_type='REG')
players = nfl.import_players()             # Player metadata (name, position, team history)
teams = nfl.import_team_desc()             # Team info (abbr, full name, etc.)
rosters = nfl.import_weekly_rosters(years)        # Links player_id <-> team for each season

# --- Merge with player info ---
df = df.merge(players[['gsis_id', 'display_name', 'position', 'height', 'weight', 
                       'college_name', 'draft_year', 'draft_round', 'draft_pick']],
              left_on='player_id', right_on='gsis_id', how='left')

# --- Merge with roster info ---
df = df.merge(rosters[['player_id', 'team', 'season', 'position', 'status']],
              on=['player_id', 'season'], how='left', suffixes=('', '_roster'))

# --- 🧹 Clean up old and legacy team abbreviations ---
old_to_new = {
    # Legacy / old internal codes
    'BLT': 'BAL',  # Baltimore Ravens
    'CLV': 'CLE',  # Cleveland Browns
    'HST': 'HOU',  # Houston Texans
    'ARZ': 'ARI',  # Arizona Cardinals
    'SL':  'LAR',  # St. Louis Rams → Los Angeles Rams

    # Relocations / rebrands
    'OAK': 'LV',   # Oakland Raiders → Las Vegas Raiders
    'SD':  'LAC',  # San Diego Chargers → Los Angeles Chargers
    'STL': 'LAR',  # St. Louis Rams → Los Angeles Rams
    'WSH': 'WAS',  # Washington Football Team → Washington Commanders
}

# Apply replacements
df['team'] = df['team'].replace(old_to_new)


# --- Merge with team info ---
df = df.merge(teams[['team_abbr', 'team_name', 'team_conf', 'team_division']],
              left_on='team', right_on='team_abbr', how='left')
df.drop(columns=['team_abbr'], inplace=True)

try:
    adv = nfl.import_advanced_seasonal_data(years, s_type='REG')
    df = df.merge(adv, on=['player_id', 'season'], how='left', suffixes=('', '_adv'))
except Exception as e:
    print(f"Advanced data not available: {e}")

display(df.head())


# In[8]:


# --- Cleaning ---

# --- Remove Unimportant Positions --
positions_to_drop = ["FS", "P", "OT", "DT", "DB", "CB", "DE", "G", "S", "LB", "OLB", "ILB", "MLB", "SAF", "C"]  # example list
df = df[~df["position"].isin(positions_to_drop)]
# Merge FB into RB
df["position"] = df["position"].replace("FB", "RB")


# --- Impute 0 for undrafted players ---
for col in ['draft_pick', 'draft_round', 'draft_year']:
    df[col] = df[col].fillna(0).astype(int)

# --- Add Boolean Flag for Undrafted ---
df['was_drafted'] = (df['draft_year'] > 0).astype(int)

# --- Impute 0 for players with no rtd_sh, dom, or w8dom ---
for col in ['rtd_sh', 'dom', 'w8dom']:
    df[col] = df[col].fillna(0.0)

# --- Optional sanity check for team column ---
if 'team' in df.columns:
    missing_teams = df[df['team'].isna()]['team'].value_counts()
    if not missing_teams.empty:
        print("\n⚠️ Missing teams found:\n", missing_teams)

# --- Final NaN summary ---
null_counts = df.isna().sum()
null_counts = null_counts[null_counts > 0].sort_values(ascending=False)

print("\n--- Null Value Summary ---")
if null_counts.empty:
    print("✅ No columns contain null values.")
else:
    print("⚠️ Columns with remaining null values:\n")
    for col, count in null_counts.items():
        print(f"{col:<30} {count}")


# In[9]:


# --- Feature Engineering for NFL Dataset ---

# Save current columns so we can track new ones later
original_cols = df.columns.tolist()

# --- Safe division helper ---
def safe_div(num, denom):
    """Divide num by denom safely (avoiding divide-by-zero and NaN propagation)."""
    return np.where((denom != 0) & (~pd.isna(denom)), num / denom, np.nan)

# --- 1. Basic Efficiency Metrics ---
if {'passing_yards', 'attempts'}.issubset(df.columns):
    df['pass_yards_per_attempt'] = safe_div(df['passing_yards'], df['attempts'])
if {'completions', 'attempts'}.issubset(df.columns):
    df['completion_rate'] = safe_div(df['completions'], df['attempts'])
if {'passing_tds', 'interceptions'}.issubset(df.columns):
    df['td_to_int_ratio'] = safe_div(df['passing_tds'], df['interceptions'])
if {'rushing_yards', 'rushing_attempts'}.issubset(df.columns):
    df['yards_per_carry'] = safe_div(df['rushing_yards'], df['rushing_attempts'])
if {'receiving_yards', 'receptions'}.issubset(df.columns):
    df['yards_per_reception'] = safe_div(df['receiving_yards'], df['receptions'])
if {'receptions', 'targets'}.issubset(df.columns):
    df['catch_rate'] = safe_div(df['receptions'], df['targets'])

# --- 2. Total & Combined Stats ---
df['total_yards'] = (
    df.get('passing_yards', 0)
    + df.get('rushing_yards', 0)
    + df.get('receiving_yards', 0)
)
df['total_tds'] = (
    df.get('passing_tds', 0)
    + df.get('rushing_tds', 0)
    + df.get('receiving_tds', 0)
)
df['touches'] = df.get('rushing_attempts', 0) + df.get('receptions', 0)
df['yards_per_touch'] = safe_div(df['total_yards'], df['touches'])

# --- 3. Per-Game Stats ---
if 'games' in df.columns:
    df['passing_yards_per_game'] = safe_div(df.get('passing_yards', 0), df['games'])
    df['rushing_yards_per_game'] = safe_div(df.get('rushing_yards', 0), df['games'])
    df['receiving_yards_per_game'] = safe_div(df.get('receiving_yards', 0), df['games'])
    df['total_yards_per_game'] = safe_div(df['total_yards'], df['games'])
    df['tds_per_game'] = safe_div(df['total_tds'], df['games'])
    if 'fantasy_points' in df.columns:
        df['fantasy_points_per_game'] = safe_div(df['fantasy_points'], df['games'])

# --- 4. Experience Features ---
if {'season', 'draft_year'}.issubset(df.columns):
    df['years_in_league'] = (df['season'] - df['draft_year']).clip(lower=0) + 1
    df['is_rookie'] = (df['season'] == df['draft_year']).astype(int)

# --- 5. Role Flags ---
if 'position' in df.columns:
    df['is_qb'] = (df['position'] == 'QB').astype(int)
    df['is_rb'] = (df['position'] == 'RB').astype(int)
    df['is_wr'] = (df['position'] == 'WR').astype(int)
    df['is_te'] = (df['position'] == 'TE').astype(int)

# --- 6. Turnovers ---
if {'interceptions', 'fumbles_lost'}.issubset(df.columns):
    df['turnovers'] = df['interceptions'] + df['fumbles_lost']

# --- Impute missing engineered features logically ---
engineered_cols = [
    "td_to_int_ratio",
    "pass_yards_per_attempt",
    "completion_rate",
    "yards_per_reception",
    "yards_per_touch",
    "catch_rate"
]

for col in engineered_cols:
    if col in df.columns:
        nulls = df[col].isna().sum()
        if nulls > 0:
            df[col] = df[col].fillna(0)
            print(f"Filled {nulls} NaNs in '{col}' with 0")

# --- 7. Sanity cleanup ---
df.replace([np.inf, -np.inf], np.nan, inplace=True)

# --- Summary ---
new_cols = [c for c in df.columns if c not in original_cols]
print(f"✅ Feature engineering complete! Added {len(new_cols)} new columns.")
print("🆕 New features include:")
for col in new_cols:
    print(f"  - {col}")

# Display preview
df[new_cols].head()


# In[10]:


# --- Analysis for Encoding ---
non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()

print(f"Non-numeric columns ({len(non_numeric_cols)}):\n{non_numeric_cols}\n")

for col in non_numeric_cols:
    print(f"\n--- {col} ---")
    unique_vals = df[col].dropna().unique()
    print(f"Unique count: {len(unique_vals)}")
    print(f"Example values: {unique_vals[:15]}")


# In[11]:


# --- Encoding ---

# --- Drop high-cardinality or useless columns ---
drop_cols = ['player_id', 'gsis_id', 'display_name', 'season_type', 
             'team_name', 'touches']  # <- added new drop columns
df = df.drop(columns=[c for c in drop_cols if c in df.columns])

# --- Identify columns for encoding ---
one_hot_cols = [
    'team', 'position', 'position_roster', 'status',
    'team_conf', 'team_division'  # <- team_name removed
]
label_cols = ['college_name']

# --- Handle missing categorical values ---
df[one_hot_cols + label_cols] = df[one_hot_cols + label_cols].fillna('Unknown')

# --- Label encode high-cardinality columns ---
le = LabelEncoder()
for col in label_cols:
    df[col] = le.fit_transform(df[col])

# --- One-hot encode moderate-cardinality columns ---
ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
encoded = ohe.fit_transform(df[one_hot_cols])
encoded_df = pd.DataFrame(encoded, columns=ohe.get_feature_names_out(one_hot_cols))

# --- Combine all numeric + encoded columns ---
df_encoded = pd.concat([df.drop(columns=one_hot_cols).reset_index(drop=True),
                        encoded_df.reset_index(drop=True)], axis=1)

# --- Confirm results ---
print(f"✅ Encoded DataFrame shape: {df_encoded.shape}")
print(f"Numeric columns: {df_encoded.select_dtypes(include=['number']).shape[1]}")
print(f"Non-numeric columns left: {df_encoded.select_dtypes(exclude=['number']).columns.tolist()}")
print(f"Sample columns: {df_encoded.columns[:15].tolist()}")


# In[12]:


# --- Scaling ---

from sklearn.preprocessing import StandardScaler

# --- Identify numeric columns (everything should be numeric at this point) ---
numeric_cols = df.select_dtypes(include=['number']).columns

# --- Initialize the scaler ---
scaler = StandardScaler()  # or MinMaxScaler() for [0,1] range

# --- Fit + transform the data ---
scaled_data = scaler.fit_transform(df[numeric_cols])

# --- Create a scaled DataFrame with the same column names ---
df_scaled = pd.DataFrame(scaled_data, columns=numeric_cols)

# --- Save the scaled dataset ---
df_scaled.to_csv("nfl_seasonal_preprocessed.csv", index=False)

print(f"✅ Scaled dataset saved as nfl_seasonal_scaled.csv")
print(f"Shape: {df_scaled.shape}")
print(f"Example columns: {df_scaled.columns[:10].tolist()}")


# In[13]:


# --- Final nan Value Check ---
df = pd.read_csv("nfl_seasonal_preprocessed.csv")
print(df.isna().sum().sort_values(ascending=False))


# In[ ]:




