import argparse
import glob
import json
import os
import pathlib
import random
import re
import subprocess
import sys

import psutil

DEFAULT_URL = "raw.githubusercontent.com/jedwillick/onedark-omp/main/onedark.omp.json"
DEFAULT_NAME = "onedark"

STYLES = ["full", "folder", "mixed", "letter", "agnoster",
          "agnoster_full", "agnoster_short", "agnoster_left"]

BASH = ["bash", "/bin/bash"]
PS = ["pwsh", "pwsh.exe", "powershell", "powershell.exe"]

pproc = psutil.Process(os.getppid())
PARENT = pproc.name() if "omputils" not in pproc.name() else pproc.parent().name()

if PARENT in BASH:
    INSTALL_MODES = ["manual", "homebrew"]
elif PARENT in PS:
    INSTALL_MODES = ["winget", "scoop", "powershell", "chocolatey"]
else:
    print(f"{PARENT} currently not supported. Sorry :(")
    sys.exit(1)

SHELL = [PARENT, "-c"]

POSH_THEME = os.getenv("POSH_THEME")
if POSH_THEME is None:
    print("Please set the 'POSH_THEME' system variable to the path of your theme!")
    sys.exit(1)
THEME_PATH = os.path.dirname(POSH_THEME)


def setup_argparse() -> argparse.Namespace:
    p_root = argparse.ArgumentParser(description="Utility commands for Oh My Posh.")
    subparser = p_root.add_subparsers(metavar="MODE", required=True, dest='command')

    desc = f"Commands to alter the overall theme. Themes must match '{os.path.join(THEME_PATH, '*.omp.json')}'"
    p_theme = subparser.add_parser("theme", help=desc, description=desc)
    group_theme = p_theme.add_mutually_exclusive_group(required=True)
    group_theme.add_argument("-s", "--set", metavar="NAME", nargs='?', const=DEFAULT_NAME,
                             help="Sets to the specified theme. Defaults to '%(const)s'.")
    group_theme.add_argument("-l", "--list", metavar='SEARCH', nargs='?', const="",
                             help="Lists all the themes or only those that match the search term.")
    group_theme.add_argument("-g", "--get", metavar="URL", nargs='?', const=DEFAULT_URL,
                             help="Downloads a theme into your theme path and then sets to it. Defaults to '%(const)s'.")
    group_theme.add_argument("-d", "--default", dest='default_name', metavar="URL", const=DEFAULT_NAME, nargs='?',
                             help="Change the default theme Name, without arg can be used to set to default theme.")
    group_theme.add_argument("-u", "--default-url", metavar="NAME", help="Change the default theme URL and Name. ")
    group_theme.add_argument("-r", "--random", action='store_true', help="Randomly selects a theme.")
    group_theme.add_argument("-c", '--current', action='store_true',
                             help="Displays information about the current theme.")

    desc = "Commands to alter the pathstlye."
    p_path = subparser.add_parser("path", help=desc, description=desc)
    p_path.add_argument("style", nargs="?", choices=STYLES, metavar="STYLE",
                        help=f"Select one of the available styles: {STYLES}")
    p_path.add_argument("-l", "--link", action='store_true', help="Toggles the enable_hyperlink property")

    desc = "Updates Oh My Posh and Themes"
    p_update = subparser.add_parser("update", help=desc, description=desc)
    p_update.add_argument("-m", '--mode', choices=INSTALL_MODES, metavar="MODE", default=INSTALL_MODES[0],
                          help="Specifies the mode of installation. Defaults to '%(default)s'.")

    return p_root.parse_args()


def handle_theme(args: argparse.Namespace) -> None:
    def extract_name(url: str) -> str:
        return re.findall(r'([^/]+).omp.json', url)[0]

    def set_theme(theme: str) -> None:
        if theme.endswith('.omp.json'):
            theme = theme.replace('.omp.json', '')

        if glob.glob(f"{THEME_PATH}/{theme}.omp.json"):
            if PARENT in BASH:
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

                if not glob.glob(f"{THEME_PATH}/{args.default_name}.omp.json"):
                    print("Unable to update the Default theme.")
                    print(f"Invalid theme '{args.default_name}'")
                    sys.exit(1)

                lines[i] = f"DEFAULT_NAME = '{args.default_name}'\n"
                break

        with open(__file__, "w") as writer:
            writer.writelines(lines)

        set_theme(args.default_name)

    elif args.set:
        set_theme(args.set)

    elif args.get:
        file = os.path.basename(args.get)
        if PARENT in BASH:
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
            print()
            subprocess.call([*SHELL, f"oh-my-posh --config {theme} --shell universal"])
            print(extract_name(theme), "\n")

    elif args.current:
        print("Theme:", extract_name(POSH_THEME))
        print("Open:", pathlib.Path(POSH_THEME).as_uri())

        with open(POSH_THEME, "r", encoding="utf-8") as reader:
            data = json.load(reader)

        details = {}
        for block in data["blocks"]:
            segments = [segment["type"] for segment in block["segments"]]
            details.setdefault(f'{block["alignment"]} - {block["type"]}', []).extend(segments)

        for k, v in details.items():
            print(f"\n{k} \n{', '.join(v)}")


def handle_path(args: argparse.Namespace) -> None:
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


def handle_update(args: argparse.Namespace) -> None:
    if PARENT in BASH:
        if args.mode == "homebrew":
            command = "brew update && brew upgrade oh-my-posh"
        else:
            command = ' && '.join([
                'OMP_OV="v$(oh-my-posh --version)"',
                'sudo wget https://github.com/JanDeDobbeleer/oh-my-posh/releases/latest/download/posh-linux-amd64 -O /usr/local/bin/oh-my-posh',
                'sudo chmod +x /usr/local/bin/oh-my-posh',
                f'wget https://github.com/JanDeDobbeleer/oh-my-posh/releases/latest/download/themes.zip -O {THEME_PATH}/themes.zip',
                f'unzip {THEME_PATH}/themes.zip -d {THEME_PATH}',
                f'chmod u+rw {THEME_PATH}/*.json',
                f'rm {THEME_PATH}/themes.zip',
                'OMP_NV="v$(oh-my-posh --version)"',
                'if [ "$OMP_OV" == "$OMP_NV" ]; then echo "Stayed on $OMP_OV"; else echo "Updated to $OMP_NV"; echo "https://github.com/JanDeDobbeleer/oh-my-posh/releases/tag/$OMP_NV"; fi'
            ])
    else:
        if args.mode == "scoop":
            command = "scoop update oh-my-posh"
        elif args.mode == "powershell":
            command = "Update-Module oh-my-posh"
        elif args.mode == "chocolatey":
            command = "choco upgrade oh-my-posh"
        else:
            command = "winget upgrade JanDeDobbeleer.OhMyPosh"

    subprocess.call([*SHELL, command])


def main() -> int:
    args = setup_argparse()
    # print(vars(args))
    if args.command == "theme":
        handle_theme(args)
    elif args.command == "path":
        handle_path(args)
    elif args.command == "update":
        handle_update(args)

    return 0
