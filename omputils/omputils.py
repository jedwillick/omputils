#!/usr/bin/env python3

import argparse
import os
import sys
import glob
import subprocess
import re

DEFAULT_URL = "raw.githubusercontent.com/jedwillick/onedark-omp/main/onedark.omp.json"
DEFAULT_NAME = "onedark"

OS = sys.platform
if OS not in ["linux", "win32"]:
    print("Unsupported OS :(")
    sys.exit(1)


def setup_argparse():
    p_root = argparse.ArgumentParser(
        description="Utility commands for Oh My Posh. Custom themes must match '*.omp.json' to work.")
    subparser = p_root.add_subparsers(metavar="MODE", required=True, dest='command')
    p_theme = subparser.add_parser("theme", help="Commands to alter the overall theme.")
    group_theme = p_theme.add_mutually_exclusive_group(required=True)
    group_theme.add_argument("-s", "--set", metavar="NAME", nargs='?', const=DEFAULT_NAME,
                             help="Sets to the specified theme, or to the default.")
    group_theme.add_argument("-l", "--list", metavar='SEARCH', nargs='?',
                             help="Lists all the themes or only those that match the search term.")
    group_theme.add_argument("-g", "--get", metavar="URL", nargs='?',
                             help="Downloads a theme or the default into your theme path and then sets to it.")
    group_theme.add_argument("-d", "--default", metavar="URL", help="Change the default theme URL and NAME")
    group_theme.add_argument("-dn", "--default-name", metavar="NAME", help="Change the default theme NAME. e.g. space")
    group_theme.add_argument("-r", "--random", action='store_true')

    p_path = subparser.add_parser("path", help="Commands to alter the pathstlye.")

    p_update = subparser.add_parser("update", help="Updates Oh My Posh")
    p_update.add_argument('-nt', '--not-themes', action="store_false", help="Flag to specify not to update the themes")
    return p_root.parse_args()


def handle_theme(args):
    POSH_THEME = os.environ.get("POSH_THEME")
    THEME_PATH = os.path.dirname(POSH_THEME)

    def set_theme(theme: str):
        if glob.glob(f"{THEME_PATH}/{theme}.omp.json"):
            if OS == "linux":
                subprocess.call(["bash", "-c",
                                f'sed -i "s|export POSH_THEME=.*|export POSH_THEME={THEME_PATH}/{theme}.omp.json|" ~/.bashrc'])
            else:
                subprocess.call(["pwsh", "-c",
                                f"""(Get-Content $PROFILE).replace('$env:POSH_THEME = "{POSH_THEME}"', 
                                    '$env:POSH_THEME = "{THEME_PATH}\\{theme}.omp.json"') | Set-Content $PROFILE"""])
        else:
            print(f"Invalid theme '{theme}'")
            print("Try 'omputils theme --help for more information")
            sys.exit(1)

    if args.default or args.default_name:
        with open(__file__, 'r') as reader:
            lines = reader.readlines()

        for i, line in enumerate(lines):
            if args.default and line.startswith("DEFAULT_URL"):
                lines[i] = f"DEFAULT_URL = '{args.default}'\n"
            elif line.startswith("DEFAULT_NAME"):
                if args.default:
                    args.default_name = re.findall(r'([^/]+).omp.json', args.default)[0]
                lines[i] = f"DEFAULT_NAME = '{args.default_name}'\n"
                break

        with open(__file__, "w") as writer:
            writer.writelines(lines)

        set_theme(args.default_name)

    elif args.set:
        set_theme(args.set)
    elif args.get:
        pass


def main():
    args = setup_argparse()
    print(vars(args))
    if args.command == "theme":
        handle_theme(args)
