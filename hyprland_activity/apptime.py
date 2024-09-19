import time
import argparse
import sys
import os
import re
from pathlib import Path as p
import logger as l
from utils import get_usetime_path, active_win, updatedb, load_file, print_usage_data, list_data

DATA_DIR = '~/.local/share/apptime/'

def start(sleep_time=5, save_threshold=60):
    """
    The program loop
    """
    # Ensure that correct path exists
    l.log_deb(f"Ensuring that the directory '{DATA_DIR}' exists")
    base_path = p(DATA_DIR).expanduser()
    base_path.mkdir(parents=True, exist_ok=True)

    l.log_inf("Started monitoring app usage.")
    classes_time = {}
    sleep_time = 5
    timer = save_threshold / sleep_time

    while True:
        win = active_win()
        if win is None:
            time.sleep(sleep_time)
            l.log_deb("No active window.")
            continue
        l.log_deb(f"Captured active window: '{win}'")
        classes_time[win] = classes_time.get(win, 0) + sleep_time
        timer -= 1
        if timer <= 0:
            updatedb(classes_time)
            classes_time = {}
            timer = save_threshold / sleep_time
        time.sleep(sleep_time)


def main():
    """
    The main function that mostly does argparsing and arginterpreting
    """
    date_pattern = r'^\d\d-\d\d$'

    parser = argparse.ArgumentParser(description='Apptime monitor for Hyprland')
    parser.add_argument('-v', '--verbosity', help='set logger verbosity')
    parser.add_argument('command', nargs='?', choices=['show', 'start', 'list'], help='the command to execute')
    parser.add_argument('time', nargs='?', help='date of the usage data to show')

    args = parser.parse_args()

    if args.verbosity:
        l.set_verbosity(int(args.verbosity))

    if args.command == 'show':
        data = None

        if args.time is None:
            l.log_err("You must specify the file to show. Possible choices: today, yesterday, file date in DD-MM format.")
            sys.exit(1)

        if args.time == 'today':
            data = load_file(get_usetime_path())
        elif args.time == 'yesterday':
            data = load_file(get_usetime_path("yesterday"))
        elif re.match(date_pattern, args.time):
            data = load_file(p(f"{DATA_DIR}usetime-{os.getlogin()}-{args.time}").expanduser())
        else:
            l.log_err(f"No such file: {args.time}")

        if data is not None:
            print("Usage data:")
            print_usage_data(data)
            sys.exit()

        elif not args.time:
            l.log_err("You must specify what to show.")
            sys.exit(1)
        else:
            l.log_err("Nothing to show.")
            sys.exit(1)

    elif args.command == 'list':
        list_data()
        sys.exit()

    elif args.command == 'start':
        start()

    l.log_err("No command to execute")
    sys.exit(1)

if __name__ == '__main__':
    main()
