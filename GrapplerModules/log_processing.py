# helpers/log_processing.py
import subprocess
import sys
import os
import time
import itertools
from GrapplerModules.file_parser import file_parser
from threading import Thread
from queue import Queue, Empty

def enqueue_output(pipe, queue):
    """Helper function to read process output asynchronously."""
    for line in iter(pipe.readline, ''):
        queue.put(line)
    pipe.close()

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
def run_process(log_type, cloud_arg1, cloud_arg2, query, json_output, source_type, start_date, end_date, file_size, intel):
    if log_type not in ["cloudtrail", "azure", "gcp"]:
        print(f"Invalid log type: {log_type}")
        return
    
    location = f"{cloud_arg1}/{cloud_arg2}" if cloud_arg2 else cloud_arg1
    print("\n")
    loading = f"\033[38;5;90m[+] Extracting data from {location} [+]\n\033[0m"
    print(loading)
    
    loading_bar = f"["

    bar_length = 40

    # Constructing the command based on log_type
    if log_type == "cloudtrail":
        
        prefix_option = f"--prefix {cloud_arg2}" if cloud_arg2 else ""        
        command = f"{mod_command} -b {cloud_arg1} {prefix_option} -q {query} --log_type {log_type} -jo"
        
        if start_date:
            command += f" -s {start_date}"
        if end_date:
            command += f" -e {end_date}"
        if file_size:
            command += f" -fs {file_size}"
    elif log_type == "azure":

        container_option = f"-cn {cloud_arg2}" if cloud_arg2 else ""
        command = f"{mod_command} -an {cloud_arg1} {container_option} -q {query} --log_type {log_type} -jo"

        if start_date:
            command += f" -s {start_date}"
        if end_date:
            command += f" -e {end_date}"
        if file_size:
            command += f" -fs {file_size}"
            
    elif log_type == 'gcp':

        command = f"{mod_command} -gb {cloud_arg1} -q {query} --log_type {log_type} -jo"
        if start_date:
            command += f" -s {start_date}"
        if end_date:
            command += f" -e {end_date}"
        if file_size:
            command += f" -fs {file_size}"

    # Run the command with progress bar
    run_command_with_progress(command, bar_length, cloud_arg1, cloud_arg2, json_output, source_type, intel)

def run_command_with_progress(command, bar_length, cloud_arg1, cloud_arg2, json_output, source_type, intel):
    try:        
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Queues to hold stdout and stderr
        stdout_queue = Queue()
        stderr_queue = Queue()

        # Threads to read stdout and stderr asynchronously
        stdout_thread = Thread(target=enqueue_output, args=(process.stdout, stdout_queue))
        stderr_thread = Thread(target=enqueue_output, args=(process.stderr, stderr_queue))
        stdout_thread.start()
        stderr_thread.start()

        colors = itertools.cycle(["\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m"])
        shapes = itertools.cycle(["█", "▓", "▒", "░"])
        loading_bar = "["

        fill = 0
        while process.poll() is None:
            # Increment the bar fill over time
            fill = min(fill + 1, bar_length)  # Increment but not beyond the bar length
            color = next(colors)
            shape = next(shapes)
            bar = f"{color}{shape * fill}{' ' * (bar_length - fill)}\033[0m"
            
            sys.stdout.write(f"\r{loading_bar}{bar}] {int((fill/bar_length) * 100)}%")
            sys.stdout.flush()
            time.sleep(0.1)

            if fill == bar_length:  # Reset fill if bar length is reached before process ends
                fill = 0

        # Finalize progress bar at 100% when the process ends
        sys.stdout.write(f"\r{loading_bar}\033[92m{'█' * bar_length}\033[0m] 100%")
        sys.stdout.flush()
        print(f"\033[92m ✔\033[0m Extract Completed\n")

        # Collect all stdout and stderr
        stdout = []
        stderr = []
        while not stdout_queue.empty():
            try:
                stdout.append(stdout_queue.get_nowait())
            except Empty:
                break
        while not stderr_queue.empty():
            try:
                stderr.append(stderr_queue.get_nowait())
            except Empty:
                break

        # Handle process output
        stdout_output = ''.join(stdout)
        stderr_output = ''.join(stderr)
        if stdout_output:
            file_parser(stdout_output, cloud_arg1, cloud_arg2, json_output, source_type, intel)
        elif stderr_output:
            print(f"STDERR:\n{stderr_output}")

        stdout_thread.join()
        stderr_thread.join()

    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
    except FileNotFoundError as e:
        print(f"Command not found: {e}")
    except PermissionError as e:
        print(f"Permission denied: {e}")
        print(f"\033[1;31mTry configuring creds again\033[0m \n")
    except Exception as e:
        print(f"Error occurred: {e}")