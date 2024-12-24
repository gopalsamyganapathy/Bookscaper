import streamlit as st
import pandas as pd
import sqlalchemy



# def filter_data(df, search_term):
 
#   # Convert all DataFrame values to lowercase for case-insensitive search
#   df_lower = df.astype(str).apply(lambda x: x.str.lower())

#   # Filter rows where any column contains the search term
#   filtered_df = df.query()

#   return filtered_df

def filter_dataframe(df: pd.DataFrame,) -> pd.DataFrame:
    
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # # Try to convert datetimes into a standard format (datetime, no timezone)
    # for col in df.columns:
    #     if pd.api.types.is_datetime64_any_dtype(df[col]):
    #         df[col] = df[col].dt.tz_localize(None)

    # Filter by column
    # for col in filter_columns:    
        
    #     if col in df.columns: 
    #        filtered_df = df[df['book_title'].isin([25, 45])]
    #         # if df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col]):
    #         #     print('Inside Object')
    #         #     # Select unique values for filtering                
    #         #     unique_values = df[col].unique()
    #         #     # Create a multiselect widget
    #         #     user_input = st.multiselect(f'Select {col}', unique_values)                
    #         #     if user_input:
    #         #         # df = df[df[col].isin(user_input)]
    #         #         df = df[df['book_title'].str.contains(user_input, case=False)] 
    #         # elif df[col].dtype == 'bool':
    #         #     user_input = st.selectbox(f'Select {col}', ['All', True, False])
    #         #     if user_input == 'All':
    #         #         pass
    #         #     else:
    #         #         df = df[df[col] == user_input]
    #         # elif pd.api.types.is_numeric_dtype(df[col]):
    #         #     # Create sliders for numeric columns
    #         #     min_value = float(df[col].min())
    #         #     max_value = float(df[col].max())
    #         #     step = (max_value - min_value) / 100  # Adjust step size as needed
    #         #     user_input = st.slider(f'Select range for {col}', min_value, max_value, (min_value, max_value), step=step)
    #         #     df = df[df[col].between(*user_input)]
    #         # elif pd.api.types.is_datetime64_any_dtype(df[col]):
    #         #     # Create date range selectors for datetime columns
    #         #     start_date, end_date = st.date_input(f'Select date range for {col}', value=(df[col].min(), df[col].max()))
    #         #     start_datetime = pd.to_datetime(start_date)
    #         #     end_datetime = pd.to_datetime(end_date)
    #         #     df = df[(df[col] >= start_datetime) & (df[col] <= end_datetime)]

    # Add search box
    search_term = st.text_input("Search")
    # row will appear here
    if search_term:
        df = df[df['book_title'].str.contains(search_term, case=False)]

    return df

# **Connect to your database (replace with your actual connection string)**
engine = sqlalchemy.create_engine('mysql+pymysql://root:''@localhost:3306/book_db') 

# **Query your data**
query = "SELECT * FROM book_summary"  # Replace with your actual SQL query
df = pd.read_sql_query(query, engine)


# # **Define columns to filter**
# filter_columns = ['book_title',]  # Replace with the desired columns

# # **Apply the filtering function**
filtered_df = filter_dataframe(df)

# **Display the filtered DataFrame**
st.dataframe(filtered_df)