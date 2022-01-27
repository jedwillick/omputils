# OMP UTILS

A utility script for [Oh My Posh](https://ohmyposh.dev/)

## Bash

Ensure the following is set in your `.bashrc` or `.profile` or equivalent.

```bash
export POSH_THEME=/home/jed/.poshthemes/onedark.omp.json
eval "$(oh-my-posh --init --shell bash --config $POSH_THEME)"

#Optional but provides instant changing between themes. Function name can be whatever you like.
theme() {
    omputils theme "$@" && source ~/.bashrc
}
```

## Powershell

Ensure the following is set in your `$PROFILE`

```powershell
$env:POSH_THEME = "C:\Users\Jed\AppData\Local\Programs\oh-my-posh\themes\onedark.omp.json"
oh-my-posh --init --shell pwsh --config $env:POSH_THEME | Invoke-Expression

# Optional but provides instant changing between themes. Alias can be whatever you like.
function Edit-PoshTheme {
    omputils theme $args 
    . $PROFILE
}

Set-Alias theme Edit-PoshTheme
```
