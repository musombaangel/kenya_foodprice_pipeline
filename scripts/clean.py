import pandas as pd
df=pd.read_csv('../sheets/wfp_food_prices_ken.csv')

#handling nulls
df.loc[df['market']== 'Hola (Tana River)', ['admin2', 'admin1', 'longitude', 'latitude']] = ['Central', 'Tana River', 40.33, -2.5990]
#casting to datetime
df['date']= pd.to_datetime(df['date'], format='%d/%m/%Y')

import pandas as pd
def standardize_units(df):
    extracted = df['unit'].astype(str).str.extract(r'^\s*([\d.]+)\s*(.*)$')
    
    numbers = pd.to_numeric(extracted[0], errors='coerce')
    remainder = extracted[1].str.strip()
    
    #Mask to select rows where the unit actually started with a number
    mask = numbers.notna()
    
    # Divide the value column by the numeric value
    df.loc[mask, 'price'] = df.loc[mask, 'price'] / numbers[mask]
    
    # Replace unit with remainder of the string
    df.loc[mask, 'unit'] = remainder[mask]    
    
    return df

df = standardize_units(df)
df.rename(columns={'price': 'price_per_unit'}, inplace=True)

print(df.dtypes)
print(df.head())
print(df.unit.unique())

#save the cleaned file
df.to_csv('../sheets/clean_food_prices_ken.csv', index=False)