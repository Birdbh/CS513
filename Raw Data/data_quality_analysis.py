import pandas as pd
import glob
import os

csv_files = glob.glob('*.csv')

for file in csv_files:
    print(f"\n{'='*50}")
    print(f"Data Quality Report for: {os.path.basename(file)}")
    print(f"{'='*50}")
    
    try:
        df = pd.read_csv(file, low_memory=False)
        total_rows = len(df)
        print(f"Total Rows: {total_rows}")
        
        print("\n--- Missing Data ---")
        missing_data = df.isnull().sum()
        missing_pct = (missing_data / total_rows) * 100
        for col in df.columns:
            if missing_data[col] > 0:
                print(f"{col}: {missing_data[col]} missing ({missing_pct[col]:.2f}%)")
        if missing_data.sum() == 0:
            print("No missing data found.")
            
        print("\n--- Uniqueness ---")
        for col in df.columns:
            unique_count = df[col].nunique()
            print(f"{col}: {unique_count} unique values")
            
        print("\n--- Data Formatting & Variances (Text Columns) ---")
        text_cols = df.select_dtypes(include=['object']).columns
        for col in text_cols:
            non_null_series = df[col].dropna().astype(str)
            if len(non_null_series) == 0:
                continue
                
            leading_trailing_ws = non_null_series.str.contains(r'^\s+|\s+$', regex=True).sum()
            
            lower_series = non_null_series.str.lower()
            unique_original = non_null_series.nunique()
            unique_lower = lower_series.nunique()
            casing_inconsistencies = unique_original - unique_lower
            
            special_chars = non_null_series.str.contains(r'[^a-zA-Z0-9\s]', regex=True).sum()
            
            print(f"\nColumn: {col}")
            print(f"  Values with leading/trailing whitespace: {leading_trailing_ws}")
            print(f"  Possible casing inconsistencies (unique case-insensitive vs original): {casing_inconsistencies}")
            print(f"  Values with special characters/punctuation: {special_chars}")
            
            normalized = non_null_series.str.lower().str.replace(r'[^a-z0-9]', '', regex=True)
            temp_df = pd.DataFrame({'Original': non_null_series, 'Normalized': normalized})
            temp_df = temp_df[temp_df['Normalized'] != '']
            grouped = temp_df.groupby('Normalized')['Original'].unique()
            variations = grouped[grouped.apply(len) > 1]
            
            if not variations.empty:
                print(f"  Found {len(variations)} distinct root words that have multiple spelling/formatting variations.")
                print(f"  Examples of inconsistency:")
                count = 0
                for norm_key, originals in variations.items():
                    print(f"    - Root '{norm_key}' -> Appears as: {list(originals)}")
                    count += 1
                    if count >= 5:
                        break
            
        print("\n--- Mixed Data Types (Numbers vs Letters) ---")
        for col in df.columns:
            non_null_series = df[col].dropna().astype(str)
            if len(non_null_series) == 0:
                continue
            
            is_numeric = non_null_series.str.match(r'^-?\d+(?:\.\d+)?$')
            has_letters = non_null_series.str.contains(r'[a-zA-Z]', regex=True)
            
            num_count = is_numeric.sum()
            letter_count = has_letters.sum()
            
            if num_count > 0 and letter_count > 0:
                print(f"Column '{col}' has mixed formats: {num_count} numeric values and {letter_count} values with letters.")
                print(f"  Example numeric: {non_null_series[is_numeric].iloc[0]}")
                print(f"  Example text: {non_null_series[has_letters].iloc[0]}")
            
    except Exception as e:
        print(f"Error processing {file}: {e}")
