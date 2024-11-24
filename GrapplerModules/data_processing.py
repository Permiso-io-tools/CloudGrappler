import json
import sys
import time
from GrapplerModules.intel import intel
from GrapplerModules.json_loader import load_json
from GrapplerModules.log_processing import run_process

def process_data(permiso_intel, add_file, new_query, source_type, json_output, start_date, end_date, file_size):
    try: 
        if new_query:
            with open('data/data_sources.json') as input_file:
                data_input = json.load(input_file)
                intel = None
                if source_type == '*':

                    for key, data_type in data_input.items():
                         service_type(data_type, new_query, json_output, key, start_date, end_date, file_size, intel)
              
                else:
                    data_type = data_input.get(source_type.upper(), [])
                    service_type(data_type, new_query, json_output, source_type, start_date, end_date, file_size, intel)
        
        elif add_file:
            intel = load_json(add_file)
            if permiso_intel:
                intel(intel)
            combined_data = {d["Query"]: d["Source"] for d in intel}
      
            source_types = list(set(d["Source"].lower() for d in intel))
            
      
            return combined_data, source_types, intel
        else:
            intel = load_json('data/queries.json')
       

            if permiso_intel:
                intel(intel)
         
            combined_data = {d["Query"]: d["Source"] for d in intel}
            source_types = list(set(d["Source"].lower() for d in intel))
           
            return combined_data, source_types, intel
    except Exception as e:
        print(f"Something went wrong while reading the queries file {e}")
        
def generic_function(combined_data, source_types, json_output, start_date, end_date, file_size, intel):
    try:
        with open('data/data_sources.json') as input_file:
            data_input = json.load(input_file)
    except FileNotFoundError:
        print("Input file not found.")
        return

    for source_type in source_types:
    
        queries = [key for key, value in combined_data.items() if str(value).lower() == source_type]

        source_dict = {source_type: queries}
  
        for key, value in source_dict.items():
            clean_queries = ', '.join(f'"{i}"' for i in value).replace(' ', '') 
            
       
        if clean_queries:
            data_source(data_input, clean_queries, source_type, json_output, start_date, end_date, file_size, intel)
        else:
            print("No source type detected")

def data_source(data_input, queries, source_type, json_output , start_date, end_date, file_size, intel):
    if source_type == '*':
     
        for key, data_type in data_input.items():
            service_type(data_type, queries, json_output, key, start_date, end_date, file_size, intel)
    else:
        
        valid_source_types = ', '.join(f'"{i}"' for i in data_input.keys()).replace(' ', '')   

        data_type = data_input.get(source_type.upper(), [])
        if data_type:
            service_type(data_type, queries, json_output, source_type, start_date, end_date, file_size, intel)
        elif len(data_type) == 0:
            print("")
        else:
            print(f"Query source value \033[1;31m{source_type}\033[0m does not match any source value in data_sources.json (Should be one of the following values: \033[1;31m{valid_source_types}\033[0m )")

def service_type(data_type, queries, json_output, source_type, start_date, end_date, file_size, intel):
    for item in data_type:
        bucket = item.get("bucket")
        prefixes = item.get("prefix")
        accountname = item.get("accountname")
        containers = item.get("container")
        gcp_bucket = item.get("gcp_bucket")

        if bucket:
            print("""\033[38;5;214m
                         ___        ______  
                        / \ \      / / ___| 
                       / _ \ \ /\ / /\___ \ 
                      / ___ \ V  V /  ___) |
                     /_/   \_\_/\_/  |____/                                                                             
                    \033[00m""")   
            if prefixes != None:
                for prefix in prefixes:
                    run_process("cloudtrail", bucket, prefix, queries, json_output, source_type, start_date, end_date, file_size, intel)
            else:
                    prefix = False
                    run_process("cloudtrail", bucket, prefix, queries, json_output, source_type, start_date, end_date, file_size, intel)

        elif accountname:
            print("""\033[38;5;33m
                 _     ______   _ ____  _____ 
                / \   |__  / | | |  _ \| ____|
               / _ \    / /| | | | |_) |  _|  
              / ___ \  / /_| |_| |  _ <| |___ 
             /_/   \_\/____|\___/|_| \_\_____|
                \033[00m""")
            if containers != None:
                for container in containers:
                    run_process("azure", accountname, container, queries, json_output, source_type, start_date, end_date, file_size, intel)
            else:
                    container = False
                    run_process("azure", accountname, container, queries, json_output, source_type, start_date, end_date, file_size, intel)
        elif gcp_bucket:
            print("""\033[38;5;196m                  
                      ____  ____ ____  
                     / ___|/ ___|  _ \ 
                    | |  _| |   | |_) |
                    | |_| | |___|  __/ 
                     \____|\____|_|    
\033[00m""")
            cloud_arg2 = ""
            run_process("gcp",gcp_bucket,cloud_arg2, queries, json_output, source_type, start_date, end_date, file_size, intel)
