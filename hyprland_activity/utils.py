import json
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path as p
import logger as l

DATA_DIR = '~/.local/share/apptime/'

def format_datetime(date):
    """
    Formats datetime for easier use
    """
    date_formatted = date.strftime("%d-%m")
    return date_formatted

def active_win():
    """
    Returns current active window name using hyprctl command
    """
    result = subprocess.run(['hyprctl', 'activewindow'], text=True, check=True, capture_output=True)
    if result.stdout is not None:
        output = result.stdout.strip()
        lines = [line.replace('\t', '').replace('\\', '') for line in output.splitlines()]
        for line in lines[1:]:
            key, value = line.split(': ', 1)
            if 'initialTitle' in key:
                return value
    l.log_warn("Failed to get active window!")
    return None

def load_file(file_path):
    """
    Loads JSON file as a dictionary
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            l.log_deb(f"Loaded file '{file_path}'")
            return data
    except FileNotFoundError:
        l.log_warn(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        l.log_warn(f"Invalid JSON: {file_path}")
        return None

def save_file(dict_data, file_path):
    """
    Saves a dictionary as a JSON file
    """
    l.log_deb(f"Saving file '{file_path}'")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(dict_data, f)

def add_dictionaries(dict1, dict2):
    """
    Merges two dictionaries
    """
    merged_dict = {**dict1}
    for key, value in dict2.items():
        if key in merged_dict:
            merged_dict[key] += value
        else:
            merged_dict[key] = value
    return merged_dict

def get_usetime_path(date=None):
    """
    returns usetime file path for current user and date
    """
    if date == "yesterday":
        return p(f"{DATA_DIR}usetime-{os.getlogin()}-{format_datetime(datetime.now() - timedelta(days=1))}").expanduser()
    return p(f"{DATA_DIR}usetime-{os.getlogin()}-{format_datetime(datetime.now())}").expanduser()

def updatedb(usetime):
    """
    Updates the usetime file
    """
    file_path = get_usetime_path()
    loaded_usetime = load_file(file_path)
    if loaded_usetime is None:
        save_file(usetime, file_path)
    else:
        merged_classes = add_dictionaries(usetime, loaded_usetime)
        save_file(merged_classes, file_path)


def format_time(seconds):
    """
    Convert seconds into H:M:S format.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    time_parts = []
    if hours > 0:
        time_parts.append(f"{hours}h")
    if minutes > 0 or hours > 0:
        time_parts.append(f"{minutes}m")
    if seconds > 0 or not time_parts:
        time_parts.append(f"{seconds}s")
    return " ".join(time_parts)

def print_usage_data(data, min_time=0):
    """
    Formats and prints a dictionary in an easy to read format.
    Optionally filters by minimum time.
    """
    max_key_length = max(len(str(key)) for key in data)
    filtered_data = {key: value for key, value in data.items() if value >= min_time}
    sorted_data = sorted(filtered_data.items(), key=lambda item: item[1], reverse=True)

    for key, value in sorted_data:
        if key == 'null':
            continue
        print(f"{key.ljust(max_key_length)}: {format_time(value)}")

def list_data():
    """
    list all usage data files
    """
    filename = f"apptime-{os.getlogin()}-"
    directory = p(DATA_DIR).expanduser()
    l.log_deb(f"Searching for files that start with '{filename}' in directory '{directory}'")
    matching_files = []

    for filename in os.listdir(directory):
        if filename.startswith(filename):
            matching_files.append(filename)

    for file in matching_files:
        print(" -> " + file)
