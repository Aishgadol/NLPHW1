import pandas as pd
from tkinter import Tk, filedialog
from collections import Counter

# Open file dialog to select a JSONL file
Tk().withdraw()  # Close the root Tkinter window
file_path = "result.jsonl"

if file_path:  # Check if a file was selected
    try:
        # Read the JSONL file into a DataFrame
        df = pd.read_json(file_path, lines=True)
        print(df.shape[0])
        # Print the DataFrame
        #print(df)
        pd.set_option("display.max_columns", None)  # Show all columns
        pd.set_option("display.max_rows", None)  # Show all rows
        pd.set_option("display.width", 1000)  # Prevent wrapping
        pd.set_option("display.colheader_justify", "left")  # Left-align column headers

        # Group by "name_speaker" and "text_sentence" and filter groups with more than one unique row
        cols_to_check = df.columns[1:]  # Exclude the first column
        all_equal_except_first = df[df.duplicated(subset=cols_to_check, keep=False)]

        # Count the number of rows where all but the first column are equal
        num_all_equal_except_first = all_equal_except_first.shape[0]

        # Print results for rows where all but the first column are equal
        print(f"Number of rows where all but the first column are equal: {num_all_equal_except_first}")
        if num_all_equal_except_first > 0:
            print("\nRows where all but the first column are equal:")
            print(all_equal_except_first)
        else:
            print("\nNo rows found where all but the first column are equal.")

        # Task 2: Find rows where 'name_speaker' contains parentheses
        rows_with_parentheses = df[df["name_speaker"].str.contains(r"\(|\)", na=False)]
        num_rows_with_parentheses = rows_with_parentheses.shape[0]

        # Print results for rows where 'name_speaker' contains parentheses
        print(f"\nNumber of rows where 'name_speaker' contains parentheses: {num_rows_with_parentheses}")
        if num_rows_with_parentheses > 0:
            print("\nRows where 'name_speaker' contains parentheses:")
            print(rows_with_parentheses)
        else:
            print("\nNo rows found where 'name_speaker' contains parentheses.")



    except Exception as e:
        print(f"Error reading the file: {e}")
else:
    print("No file selected.")
