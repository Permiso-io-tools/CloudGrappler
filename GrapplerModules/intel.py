from collections import Counter
from datetime import datetime
import json
import os

current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M %p")
folder = "./reports"

def process_data(formatted_output, cloud_arg1, cloud_arg2, json_output, source_type):

    if formatted_output:
        data = json.loads(formatted_output)

        if not data:
            print("\033[1;94m***********************************************************************\033[0m")
            print("\033[1;31m[-] No hits found\033[0m")
            print("\033[1;94m***********************************************************************\033[0m")

            return
        
        azure_type = any(entry.get('line', {}).get('correlationId') for entry in data)
        aws_type = any(entry.get('line', {}).get('eventVersion') for entry in data)

        if azure_type or aws_type:
           
            keys = set(entry.get('query') for entry in data if 'query' in entry)
            duplicates = {key: count for key, count in Counter(entry.get('query') for entry in data if 'query' in entry).items() if count > 0}
            hits(data, duplicates, cloud_arg1, cloud_arg2, json_output, source_type)
    else:

        print("\033[1;94m***********************************************************************\033[0m")
        print("\033[1;31m[-] No hits found\033[0m")
        print("\033[1;94m***********************************************************************\033[0m")


def hits(data, duplicates, cloud_arg1, cloud_arg2, json_output, source_type):
    
    print("\033[1;94m***********************************************************************\033[0m")
    for key, count in duplicates.items():
        print("")
        print(f"\033[1;92m[+] {count} {'hits' if count > 1 else 'hit' if count == 1 else 'no hits'} for {key}\033[0m")
        print("")
        if json_output:
            write_json_output(data, source_type, cloud_arg1, key, cloud_arg2, json_output)
    print("\033[1;94m***********************************************************************\033[0m")


def write_json_output(data, source_type, cloud_arg1, key, cloud_arg2, json_output):
    
    if cloud_arg2:
        clean_prefix = cloud_arg2.replace("/", "_")
        folder_name = f"./{folder}/json/{source_type}/{current_datetime}/{cloud_arg1}/{clean_prefix}"
    else:
        folder_name = f"./{folder}/json/{source_type}/{current_datetime}/{cloud_arg1}"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_name = f"{folder_name}/{key}.json"

    try:
        if data:
            with open(file_name, 'w') as new_file:
                json.dump(data, new_file)
        else:
            with open(file_name, 'w') as new_file:
                new_file.write("No hits found")
    except FileNotFoundError:

        print(f"\033[1;31mCould not generate json file for {file_name}\033[0m \n")


def intel(data):
    for entry in data:
        query = entry.get("Query")
        print(f"\033[91m\033[1m[+] Running {query} for {entry.get('Source')} \033[00m")
        print(f"\033[1;33m[+] {entry.get('Intel', {}).get('Type')}: {entry.get('Intel', {}).get('Value')}\033[0m ")
        print(f"\033[1;33m[+] Severity: {entry.get('Severity')}\033[0m ")
        print(f"\033[1;33m[+] Description: {entry.get('Description')}\033[0m \n")
        print("------------------------------------------------------------------------------------------------------------------------------")
