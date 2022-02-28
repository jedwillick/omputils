import argparse
import glob
import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path

import psutil

DEFAULT_THEME = 'min'

STYLES = [
    "full",
    "folder",
    "mixed",
    "letter",
    "agnoster",
    "agnoster_full",
    "agnoster_short",
    "agnoster_left",
    "unique"
]

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
    p_root = argparse.ArgumentParser(description="Utility commands for Oh My Posh.\nUse 'omputils <CMD> --help' for more info",
                                     formatter_class=argparse.RawTextHelpFormatter)
    subparser = p_root.add_subparsers(metavar="CMD", required=True, dest='command')

    desc = f"Commands to alter the overall theme. Themes must match '{os.path.join(THEME_PATH, '*.omp.json')}'"
    p_theme = subparser.add_parser("theme", help=desc, description=desc)
    group_theme = p_theme.add_mutually_exclusive_group(required=True)
    group_theme.add_argument("-s", "--set", metavar="NAME", nargs='?', const=DEFAULT_THEME,
                             help="Sets to the specified theme. Defaults to '%(const)s'.")
    group_theme.add_argument("-l", "--list", metavar='SEARCH', nargs='?', const="",
                             help="Lists all the themes or only those that match the search term.")
    group_theme.add_argument("-g", "--get", metavar="URL",
                             help="Downloads a theme into your theme path and then sets to it. ")
    group_theme.add_argument("-d", "--default", action='store_true',
                             help="Change the default theme to the current theme.")
    group_theme.add_argument("-r", "--random", action='store_true', help="Randomly selects a theme.")
    group_theme.add_argument("-c", '--current', action='store_true',
                             help="Displays information about the current theme.")

    desc = "Commands to alter the pathstlye."
    p_path = subparser.add_parser("path", help=desc, description=desc)
    p_path.add_argument("-s", "--style", choices=STYLES, metavar="STYLE",
                        help=f"Select one of the available styles: {STYLES}")
    p_path.add_argument("-l", "--link", action='store_true', help="Enables hyperlink on path")
    p_path.add_argument("-nl", "--no-link", action='store_true', help="Disables hyperlink on path")
    p_path.add_argument('-d', '--depth', type=int,
                        help="Sets the maximum depth of the path when using agnoster_short.")

    desc = "Updates Oh My Posh and Themes"
    p_update = subparser.add_parser("update", help=desc, description=desc)
    p_update.add_argument("-m", '--mode', choices=INSTALL_MODES, metavar="MODE", default=INSTALL_MODES[0],
                          help="Specifies the mode of installation. Defaults to '%(default)s'.")

    return p_root.parse_args()


def handle_theme(args: argparse.Namespace) -> None:
    def extract_name(url: str) -> str:
        return re.findall(r'([^\/\\]+)\.omp\.json', url)[0]

    def set_theme(theme: str) -> None:
        if theme.endswith('.omp.json'):
            theme = theme.replace('.omp.json', '')

        if glob.glob(f"{THEME_PATH}/{theme}.omp.json"):
            if PARENT in BASH:
                subprocess.call([*SHELL,
                                 f'sed -i "s|export POSH_THEME=.*|export POSH_THEME={THEME_PATH}/{theme}.omp.json|" ~/.bashrc'])
            else:
                subprocess.call([*SHELL,
                                 f"""(Get-Content $PROFILE).replace('$env:POSH_THEME = "{POSH_THEME.replace(str(Path.home()), '$env:USERPROFILE')}"',
                                    '$env:POSH_THEME = "{THEME_PATH.replace(str(Path.home()), '$env:USERPROFILE')}\\{theme}.omp.json"') | Set-Content $PROFILE"""])
        else:
            print(f"Invalid theme '{theme}'")
            print("Try 'omputils theme --help for more information")
            sys.exit(1)

    if args.default:
        with open(__file__, 'r') as reader:
            lines = reader.readlines()

        for i, line in enumerate(lines):
            if line.startswith("DEFAULT_THEME"):
                lines[i] = f"DEFAULT_THEME = '{extract_name(POSH_THEME)}'\n"
                break

        with open(__file__, "w") as writer:
            writer.writelines(lines)

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
            print(f"\u001b]8;;{theme}\u001b\\{extract_name(theme)}\u001b]8;;\u001b\\\n")

    elif args.current:
        print("Theme:", extract_name(POSH_THEME))
        print("Open:", Path(POSH_THEME).as_uri())

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
        target["template"] = " {{ path .Path .Location }} "
    if args.no_link:
        target["template"] = " {{ .Path }} "
    if args.style:
        target["style"] = args.style
    if args.depth:
        target["max_depth"] = args.depth

    with open(POSH_THEME, "w", encoding="utf-8") as writer:
        json.dump(data, writer, indent=2)


def handle_update(args: argparse.Namespace) -> None:
    if PARENT in BASH:
        if args.mode == "homebrew":
            command = "brew update && brew upgrade oh-my-posh"
        else:
            command = ' && '.join([
                'OMP_OV="v$(oh-my-posh --version)"',
                'sudo wget -q --show-progress https://github.com/JanDeDobbeleer/oh-my-posh/releases/latest/download/posh-linux-amd64 -O /usr/local/bin/oh-my-posh',
                'sudo chmod +x /usr/local/bin/oh-my-posh',
                f'mkdir -p {THEME_PATH}',
                f'wget -q --show-progress https://github.com/JanDeDobbeleer/oh-my-posh/releases/latest/download/themes.zip -O {THEME_PATH}/themes.zip',
                f'unzip -oqq {THEME_PATH}/themes.zip -d {THEME_PATH}',
                f'chmod u+rw {THEME_PATH}/*.json',
                f'rm {THEME_PATH}/themes.zip',
                'OMP_NV="v$(oh-my-posh --version)"',
                'if [ "$OMP_OV" == "$OMP_NV" ]; then printf "Stayed on "; else printf "Updated to "; fi',
                r'echo -e "\e]8;;https://github.com/JanDeDobbeleer/oh-my-posh/releases/tag/${OMP_NV}\a${OMP_NV}\e]8;;\a"'
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

    if retcode := subprocess.call([*SHELL, command]):
        print("Failed to update Oh My Posh!")
        sys.exit(retcode)


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
