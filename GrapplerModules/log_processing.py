# helpers/log_processing.py
import os
import subprocess
import sys
from GrapplerModules.file_parser import file_parser


def run_grep_once():
    
    current_directory = os.getcwd()
    local_cloudgrep_path = f"{current_directory}/cloudgrep/cloudgrep.py"
    if os.path.isfile(local_cloudgrep_path): 
        mod_command = f"python3 cloudgrep/cloudgrep.py"
    
        return mod_command
    else:
        print(f"""\033[91m\033[1mCannot find local cloudgrep.py file at the following location: {local_cloudgrep_path}.
Run build.sh file to clone cloudgrep repository or clone it manually. \033[00m""")
        sys.exit(1)

mod_command = run_grep_once()

# Function to run a specific log processing command
def run_process(log_type, cloud_arg1, cloud_arg2, query, json_output, source_type, start_date, end_date, file_size):
    if log_type not in ["cloudtrail", "azure"]:
        print(f"Invalid log type: {log_type}")
        return
    location = f"{cloud_arg1}/{cloud_arg2}" if cloud_arg2 else cloud_arg1
    print("\n")
    print(f"Checking for hits in \033[91m\033[1m{location} for {query} \033[00m\n")


    if log_type == "cloudtrail":
        prefix_option = f"--prefix {cloud_arg2}" if cloud_arg2 else ""
        # Change this
        command = f"{mod_command} -b {cloud_arg1} {prefix_option} -q {query} --log_type {log_type} -jo"

        if start_date:
            command += f" -s {start_date}"

        if end_date:
            command += f" -e {end_date}"

        if file_size:
            command += f" -fs {file_size}"
    
    elif log_type == "azure":
        container_option = f"-cn {cloud_arg2}" if cloud_arg2 else ""
        # Change this
        command = f"{mod_command} -an {cloud_arg1} {container_option} -q {query} --log_type {log_type} -jo"
       
        if start_date:
            command += f" -s {start_date}"

        if end_date:
            command += f" -e {end_date}"

        if file_size:
            command += f" -fs {file_size}"

    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        logs = result.stderr
        file_parser(result, cloud_arg1, cloud_arg2, json_output, source_type, logs)

    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        print(f"stderr: {e.stderr}")
    except FileNotFoundError as e:
        print(f"Command not found: {e}")
    except PermissionError as e:
        print(f"Permission denied: {e}")
        print(
        f"\033[1;31mTry configuring creds again with `aws config` or `az login`\033[0m \n")
    except Exception as e:
        print(f"Error occurred: {e}")