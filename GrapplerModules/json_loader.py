# Function to load JSON data from a file
import json


def load_json(filename):
    try:
        with open(filename) as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return {}