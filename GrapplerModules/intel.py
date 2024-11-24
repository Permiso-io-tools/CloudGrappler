from collections import Counter
from datetime import datetime
import itertools
import json
import os
import random
import sys
import time
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED

current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M %p")
folder = "./reports"

def process_data(formatted_output, cloud_arg1, cloud_arg2, json_output, source_type, intel):
    loading = "\033[38;5;90m[+] Scanning for hits [+]\033[0m\n"
    print(loading)
    loading_bar = "["
    bar_length = 40  # Length of the progress bar
    colors = itertools.cycle(["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m"])  # Red, Green, Yellow, Blue, Magenta
    shapes = itertools.cycle(["█", "▓"])  # Various shapes

    for i in range(bar_length + 1):
        color = next(colors)
        shape = next(shapes)

        # Calculate the percentage
        percentage = int((i / bar_length) * 100)

        # Construct the bar with colors and shapes
        bar = color + shape * i + ' ' * (bar_length - i) + "\033[0m"  # Reset color at the end

        # Display the loading bar with percentage
        sys.stdout.write(f"\r{loading_bar}{bar}] {percentage}%")
        sys.stdout.flush()
        time.sleep(0.05)

    sys.stdout.write(f"\r{loading_bar}\033[92m{'█' * bar_length}\033[0m] 100%")
    sys.stdout.flush()
    print(f"\033[92m ✔\033[0m Scan Completed")
    if formatted_output:
        data = json.loads(formatted_output)
        if not data:        
            print("\033[1;31m\n[-] No hits found\033[0m")
            return
        
        azure_type = any(entry.get('line', {}).get('correlationId') or entry.get('line', {}).get('Workload') for entry in data)
        aws_type = any(entry.get('line', {}).get('eventVersion') for entry in data)
        gcp_type = any(entry.get('line', {}).get('protoPayload') for entry in data)


        if azure_type or aws_type or gcp_type:
           
            keys = set(entry.get('query') for entry in data if 'query' in entry)
            duplicates = {key: count for key, count in Counter(entry.get('query') for entry in data if 'query' in entry).items() if count > 0}
            hits(data, duplicates, cloud_arg1, cloud_arg2, json_output, source_type, intel)
    else:

        print("\033[1;31m[-] No hits found\033[0m")

def hits(data, duplicates, cloud_arg1, cloud_arg2, json_output, source_type, intel):

    if intel != None:
        console = Console()
        text = "\033[1;32;40m\n[+] Printing results! [+]\033[0m\n\n"
        for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.05)
        time.sleep(1)

    
        table = Table(
            show_header=True,
            header_style="bright_blue",
            box=ROUNDED,  # Rounded corners for a modern look
            padding=(0, 1),  # Add padding between columns
        )
        table.add_column("Name", justify="left", style="bold cyan", width=25)
        table.add_column("TA", justify="center", style="yellow", width=10)
        table.add_column("Severity", justify="center", style="bold red", width=13)
        table.add_column("Description", justify="left", style="white", width=95)

        # Populate the table dynamically
        for key, count in duplicates.items():
            print(f"\033[91m[-] {count} {'hits' if count > 1 else 'hit' if count == 1 else 'no hits'} for {key}\033[0m")
            for query in intel:
                if query['Query'] == key:
                    table.add_row(
                        query['Query'],
                        query['Intel']['Value'],
                        query['Severity'],
                        query['Description'],
                    )
                    # Add a separator row as empty row with dashed style
                    table.add_row("", "", "", "", end_section=True)
            if json_output:
                write_json_output(data, source_type, cloud_arg1, key, cloud_arg2, json_output)

        # Print the unified table at once
        console.print(table)
        print("\n")
    else:
        text = "\033[1;32;40m\n[+] Printing results! [+]\033[0m\n\n"
        for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.05)
        time.sleep(1)
        for key, count in duplicates.items():
            print(f"\033[91m[-] {count} {'hits' if count > 1 else 'hit' if count == 1 else 'no hits'} for {key}\033[0m")
            if json_output:
                write_json_output(data, source_type, cloud_arg1, key, cloud_arg2, json_output)

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
