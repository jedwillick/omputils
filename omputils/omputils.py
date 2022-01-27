#!/usr/bin/env python3

import argparse
import json
import os
import sys
import glob
import subprocess
import re
import random


DEFAULT_URL = "raw.githubusercontent.com/jedwillick/onedark-omp/main/onedark.omp.json"
DEFAULT_NAME = "onedark"

STYLES = ["full", "folder", "mixed", "letter", "agnoster",
          "agnoster_full", "agnoster_short", "agnoster_left"]

OS = sys.platform
if OS not in ["linux", "win32"]:
    print("Unsupported OS :(")
    sys.exit(1)

if OS == "linux":
    SHELL = ["bash", "-c"]
    INSTALL_MODES = ["manual", "homebrew"]
else:
    SHELL = ["pwsh", "-c"]
    INSTALL_MODES = ["winget", "scoop", "powershell", "chocolatey"]

POSH_THEME = os.getenv("POSH_THEME")
if POSH_THEME is None:
    print("Please set the 'POSH_THEME' system variable to the path of your theme!")
    sys.exit(1)


def setup_argparse():
    p_root = argparse.ArgumentParser(
        description="Utility commands for Oh My Posh. Custom themes must match '*.omp.json' to work.")
    subparser = p_root.add_subparsers(metavar="MODE", required=True, dest='command')
    p_theme = subparser.add_parser("theme", help="Commands to alter the overall theme.")
    group_theme = p_theme.add_mutually_exclusive_group(required=True)
    group_theme.add_argument("-s", "--set", metavar="NAME", nargs='?', const=DEFAULT_NAME,
                             help="Sets to the specified theme, or to the default.")
    group_theme.add_argument("-l", "--list", metavar='SEARCH', nargs='?', const="",
                             help="Lists all the themes or only those that match the search term.")
    group_theme.add_argument("-g", "--get", metavar="URL", nargs='?', const=DEFAULT_URL,
                             help="Downloads a theme or the default into your theme path and then sets to it.")
    group_theme.add_argument("-d", "--default",  dest='default_name', metavar="URL", const=DEFAULT_URL, nargs='?',
                             help="Change the default theme Name, without arg can be used to set to default theme.")
    group_theme.add_argument("-du", "--default-url", metavar="NAME", help="Change the default theme URL and Name. ")
    group_theme.add_argument("-r", "--random", action='store_true', help="Randomly selects a theme.")

    p_path = subparser.add_parser("path", help="Commands to alter the pathstlye.")
    p_path.add_argument("style", nargs="?", choices=STYLES, metavar="STYLE",
                        help=f"Select one of the available styles: {STYLES}")
    p_path.add_argument("-l", "--link", action='store_true', help="Toggles the enable_hyperlink property")
    p_update = subparser.add_parser("update", help="Updates Oh My Posh and Themes")
    p_update.add_argument("-m", '--mode', choices=INSTALL_MODES, metavar="MODE", default=INSTALL_MODES[0],
                          help="Specifies the mode of installation. Defaults to 'manual' for linux and 'winget' for windows")
    return p_root.parse_args()


def handle_theme(args):
    THEME_PATH = os.path.dirname(POSH_THEME)

    def extract_name(url: str):
        return re.findall(r'([^/]+).omp.json', url)[0]

    def set_theme(theme: str):
        if theme.endswith('.omp.json'):
            theme = theme.replace('.omp.json', '')

        if glob.glob(f"{THEME_PATH}/{theme}.omp.json"):
            if OS == "linux":
                subprocess.call([*SHELL,
                                f'sed -i "s|export POSH_THEME=.*|export POSH_THEME={THEME_PATH}/{theme}.omp.json|" ~/.bashrc'])
            else:
                subprocess.call([*SHELL,
                                f"""(Get-Content $PROFILE).replace('$env:POSH_THEME = "{POSH_THEME}"',
                                    '$env:POSH_THEME = "{THEME_PATH}\\{theme}.omp.json"') | Set-Content $PROFILE"""])
        else:
            print(f"Invalid theme '{theme}'")
            print("Try 'omputils theme --help for more information")
            sys.exit(1)

    if args.default_url or args.default_name:
        with open(__file__, 'r') as reader:
            lines = reader.readlines()

        for i, line in enumerate(lines):
            if args.default_url and line.startswith("DEFAULT_URL"):
                lines[i] = f"DEFAULT_URL = '{args.default_url}'\n"
            elif line.startswith("DEFAULT_NAME"):
                if args.default_url:
                    args.default_name = extract_name(args.default_url)
                lines[i] = f"DEFAULT_NAME = '{args.default_name}'\n"
                break

        with open(__file__, "w") as writer:
            writer.writelines(lines)

        set_theme(args.default_name)

    elif args.set:
        set_theme(args.set)

    elif args.get:
        file = os.path.basename(args.get)
        if OS == "linux":
            subprocess.call([*SHELL, f"wget {args.get} -O {THEME_PATH}/{file}"])
        else:
            subprocess.call([*SHELL, f"Invoke-WebRequest {args.get} -O {THEME_PATH}\\{file}"])
        set_theme(extract_name(args.get))

    elif args.random:
        theme = random.choice([file for file in os.listdir(THEME_PATH) if file.endswith(".omp.json")])
        set_theme(theme)

        # theme = random.choice(glob.glob(f"{THEME_PATH}/*.omp.json"))
        # set_theme(os.path.basename(theme))

    elif args.list is not None:
        for theme in glob.glob(f"{THEME_PATH}/*{args.list}*.omp.json"):
            print("")
            subprocess.call([*SHELL, f"oh-my-posh --config {theme} --shell universal"])
            print(extract_name(theme))
            print("")


def handle_path(args):
    with open(POSH_THEME, "r", encoding="utf-8") as reader:
        data = json.load(reader)

    for block in data["blocks"]:
        for segment in block["segments"]:
            if segment["type"] == "path":
                target = segment["properties"]

    if args.link:
        target["enable_hyperlink"] = not target["enable_hyperlink"]
    if args.style:
        target["style"] = args.style

    with open(POSH_THEME, "w", encoding="utf-8") as writer:
        json.dump(data, writer, indent=4)


def handle_update(args):
    if OS == "linux":
        if args.mode == "manual":
            subprocess.call([
                *SHELL,
                "sudo wget https://github.com/JanDeDobbeleer/oh-my-posh/releases/latest/download/posh-linux-amd64 -O /usr/local/bin/oh-my-posh"
                + "&& sudo chmod +x /usr/local/bin/oh-my-posh"
                + "&& mkdir -p ~/.poshthemes"
                + "&& wget https://github.com/JanDeDobbeleer/oh-my-posh/releases/latest/download/themes.zip -O ~/.poshthemes/themes.zip"
                + "&& unzip ~/.poshthemes/themes.zip -d ~/.poshthemes"
                + "&& chmod u+rw ~/.poshthemes/*.json"
                + "&& rm ~/.poshthemes/themes.zip"
            ])
        elif args.mode == "homebrew":
            subprocess.call([*SHELL, "brew update && brew upgrade oh-my-posh"])
    else:
        if args.mode == "winget":
            subprocess.call([*SHELL, "winget upgrade JanDeDobbeleer.OhMyPosh"])
        elif args.mode == "scoop":
            subprocess.call([*SHELL, "scoop update oh-my-posh"])
        elif args.mode == "powershell":
            subprocess.call([*SHELL, "Update-Module oh-my-posh"])
        elif args.mode == "chocolatey":
            subprocess.call([*SHELL, "choco upgrade oh-my-posh"])


def main():
    args = setup_argparse()
    # print(vars(args))
    if args.command == "theme":
        handle_theme(args)
    elif args.command == "path":
        handle_path(args)
    elif args.command == "update":
        handle_update(args)
