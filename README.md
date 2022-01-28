# OMP UTILS

A utility script for [Oh My Posh](https://ohmyposh.dev/)  
Currently only supports bash and powershell.

## Bash

Ensure the following is set in your `.bashrc` or `.profile` or equivalent.

```bash
export POSH_THEME=/path/to/poshthemes/your_theme.omp.json
eval "$(oh-my-posh --init --shell bash --config $POSH_THEME)"

# Optional but provides instant changing between themes. Function name can be whatever you like.
theme() {
    omputils theme "$@" && source ~/.bashrc
}
```

## Powershell

Ensure the following is set in your `$PROFILE`

```powershell
$env:POSH_THEME = "\path\to\poshthemes\your_theme.omp.json"
oh-my-posh --init --shell pwsh --config $env:POSH_THEME | Invoke-Expression

# Optional but provides instant changing between themes. Alias can be whatever you like.
function Edit-PoshTheme {
    omputils theme $args 
    . $PROFILE
}

Set-Alias theme Edit-PoshTheme
```

## More

[Check out my One Dark inspired theme.](https://github.com/jedwillick/onedark-omp)
