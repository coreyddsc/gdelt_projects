#%% IMPORTS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlalchemy as sql
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, delete, insert, DateTime, Float, Boolean

#%% READ DATA
cameo_country = pd.read_csv('CAMEO.country.txt', sep='\t', header=0, names=['CODE', 'LABEL'])
cameo_eventcodes = pd.read_csv('CAMEO.eventcodes.txt', sep='\t', header=0, names=['CODE', 'DESCRIPTION'])
cameo_goldsteinscale = pd.read_csv('CAMEO.goldsteinscale.txt', sep='\t', header=0, names=['CODE', 'GOLDSTEINSCALE'])

# %%
cameo_country.head()
# %%
cameo_eventcodes.head()

# %%
cameo_goldsteinscale.head()
# %% ENGINE
# Create a single in-memory SQLite engine
engine = create_engine('sqlite:///:memory:')


# %% CREATE TEMP SQL TABLES
def create_temp_sql_tables(path):
    # Get list of CSV files in the path
    csv_files = [file for file in os.listdir(path) if file.endswith('.csv')]
    
    for file in csv_files:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(os.path.join(path, file))
        
        # Remove file extension from the table name
        table_name = file.replace('.csv', '')
        
        # Write the DataFrame to the shared SQLite engine
        df.to_sql(table_name, engine, index=False, if_exists='replace')
        
        # Print confirmation
        print(f"Table '{table_name}' created")
    
    # Query the SQLite database to list all tables
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables_df = pd.read_sql(tables_query, con=engine)

# %% CREATE TEMP SQL TABLES
# New function to create temp SQL tables from the cameo dataframes defined above.
def create_temp_sql_tables():
    # Write the DataFrames to the shared SQLite engine
    cameo_country.to_sql('cameo_country', engine, index=False, if_exists='replace')
    cameo_eventcodes.to_sql('cameo_eventcodes', engine, index=False, if_exists='replace')
    cameo_goldsteinscale.to_sql('cameo_goldsteinscale', engine, index=False, if_exists='replace')
    
    # Query the SQLite database to list all tables
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables_df = pd.read_sql(tables_query, con=engine)
    
    # Print confirmation
    print(tables_df)
# %%
create_temp_sql_tables()
# %%
# Query the cameo_country table
query = "SELECT * FROM cameo_country"
cameo_country_df = pd.read_sql(query, con=engine)
cameo_country_df.head()
# %%
