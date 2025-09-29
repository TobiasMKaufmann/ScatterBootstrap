import pandas as pd
import numpy as np
import re

# Load the CSV data for effective radius calculations
# DO NOT USE THIS METHOD AS FLOATS ARE CONVERTED TO STRINGS AND ROUNDED
def recreate_multiindex_dataframe(which_file="parameter_summary_multiindex.csv"):
    """
    Recreate the exact MultiIndex DataFrame structure from the saved CSV,
    parsing the complex pandas Series strings back to proper values.
    """
    
    df_raw = pd.read_csv(which_file, header=[0, 1], index_col=0, dtype=str)
    
    df_raw.columns.names = ['Parameter', 'Statistic']
    df_raw.index.name = 'Dataset'
    
    summary_df = pd.DataFrame(index=df_raw.index, columns=df_raw.columns)
    summary_df.columns.names = ['Parameter', 'Statistic']
    summary_df.index.name = 'Dataset'
    
    def extract_value_from_series_string(series_str):
        """Extract the 'value' from a pandas Series string representation"""
        if pd.isna(series_str) or series_str == '':
            return None
        
        try:
            return float(series_str)
        except (ValueError, TypeError):
            pass
        
        str_repr = str(series_str)
        if 'value' in str_repr:
            value_match = re.search(r'value\s+([0-9.-]+(?:e[+-]?[0-9]+)?)', str_repr)
            if value_match:
                try:
                    return float(value_match.group(1))
                except ValueError:
                    pass
        
        return str_repr
    
    for dataset in df_raw.index:
        for param in df_raw.columns.get_level_values(0).unique():
            for stat in ['Original_Fit', 'Lower_Bound', 'Upper_Bound']:
                if (param, stat) in df_raw.columns:
                    raw_value = df_raw.loc[dataset, (param, stat)]
                    clean_value = extract_value_from_series_string(raw_value)
                    summary_df.loc[dataset, (param, stat)] = clean_value
    
    return summary_df

df = recreate_multiindex_dataframe()
rel_df = df.loc[:, (slice(None), "Original_Fit")].copy()
rel_df.columns = rel_df.columns.droplevel(1)

# Effective radius functions
er = lambda R, t, L: (3 / 4 * (R + t)**2 * (L + 2 * t))**(1 / 3)
er2 = lambda R, t, L: np.sqrt(5 / 3 * ((R + t)**2 / 2 + (L + 2 * t)**2 / 12))

#a_vol = lambda rho_c, rho_sol, rho_s, r, t, l: ((3 * ((rho_c - rho_sol) * np.pi * r**2 * l + (rho_s - rho_sol) * np.pi * ((r + t)**2 - r**2) * l)) / (4 * np.pi * (rho_c - rho_sol)))**(1 / 3)

#rel_df["radius_effective"] = rel_df.apply(lambda row: a_vol(row["core_sld"], row["solvent_sld"], row["shell_sld"], row["radius"], row["thickness"], row["length"]) if row["radius_effective"] < 1.5 * row["length"] else row["radius_effective"], axis=1)
rel_df["radius_effective"] = rel_df.apply(lambda row: er2(row["radius"], row["thickness"], row["length"]) if row["radius_effective"] < 1.5 * row["length"] else row["radius_effective"], axis=1)
rel_df["scale"] = 1
rel_df["background"] = 0.001

print(rel_df["radius_effective"])

rel_df.to_json("initial_params.json", orient="index", indent=4)

print("Effective radius computations completed and saved to initial_params.json")

