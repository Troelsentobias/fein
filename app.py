import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.title("Fein 🚀")
st.write(
    """Denne app viser alle kominationer per Model, som kan konfigureres. Test away 🤣
    """
)

# List of pickle files
pickle_files = [
    'combinations_output_AP-0602.pkl',
    'combinations_output_AP-0802.pkl',
    'combinations_output_AP-1002.pkl',
    'combinations_output_AP-1202.pkl',
    'combinations_output_AP-1204.pkl',
    'combinations_output_AP-1404.pkl',
    'combinations_output_AP-1406.pkl',
    'combinations_output_AP-1604.pkl',
    'combinations_output_AP-1606.pkl',
    'combinations_output_AP-1804.pkl',
    'combinations_output_AP-2004.pkl',
    'combinations_output_AP-2006.pkl',
    'combinations_output_AP-1806.pkl'
]

# Extract model numbers from pickle file names
model_numbers = [file.split('_')[2].split('.')[0] for file in pickle_files]

# Create a dropdown to select the model number
pickle_option = st.selectbox(
    'Select Model',
    model_numbers
)

# Get the selected pickle file name
selected_pickle_file = next(file for file in pickle_files if pickle_option in file)
st.write(f"Selected pickle file: {selected_pickle_file}")


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import streamlit as st


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df

# Load and display the selected pickle file
if pickle_option:
    df = pd.read_pickle(selected_pickle_file)

filtered_df = filter_dataframe(df)
st.dataframe(filtered_df)

# Add a print statement for the length of the filtered DataFrame
st.write(f"Number of rows after filtering: {len(filtered_df)}")
