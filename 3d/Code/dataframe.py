import pandas as pd
import os
import bpy

blender_file_directory = os.path.dirname(bpy.data.filepath)

def create_dataframe():
    # Initialisiere den DataFrame
    columns = [
        'Size', 'Highways', 'Rivers', 'River Chance', 'Road Chance', 
        'House Chance', 'Industrial Chance', 'Park Chance', 'Randomness',
        'Vertex Group', 'Initial Entropy', 'Current Entropy', 'Entropy Reduction Percentage', 
        'Average Weight', 'Vertex Count', 'Vertex Percentage', 
        'Criteria Fulfilled Count', 'Criteria Fulfilled Percentage','Overall Constraints Fulfilled'
    ]
    df = pd.DataFrame(columns=columns)
    return df

def add_data_to_dataframe(df, data):
    # Füge eine Zeile zum DataFrame hinzu
    df = df._append(data, ignore_index=True)
    return df

def save_dataframe_to_csv(df, filename):
    filepath = os.path.join(blender_file_directory, filename)
    print(filepath)
    try:
        if not os.path.isfile(filename):
            df.to_csv(filename, index=False)
        else:
            df.to_csv(filename, mode='a', header=False, index=False)
    except PermissionError as e:
        print("------NO PERMISSION TO WRITE EVAL FILE-----")
        print("------Run Blender as Admin to Fix----------")  
        print(e)
        print("-------------------------------------------")

def load_dataframe_from_csv(filename):
    filepath = os.path.join(blender_file_directory, filename)
    if os.path.isfile(filename):
        return pd.read_csv(filename)
    else:
        return create_dataframe()
