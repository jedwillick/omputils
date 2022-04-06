# OMP UTILS

A utility script for [Oh My Posh](https://ohmyposh.dev/)  
Currently only supports bash and powershell.

## Setup

```shell
pip install git+https://github.com/jedwillick/omputils
omputils --help
```

### Bash

Ensure the following is set in your `.bashrc` or `.profile` or equivalent.

```bash
export POSH_THEME=/path/to/poshthemes/your_theme.omp.json
eval "$(oh-my-posh init bash)"

# Optional but provides instant changing between themes.
theme() {
    omputils theme "$@" && source ~/.bashrc
}
```

### Powershell

Ensure the following is set in your `$PROFILE`

```powershell
$env:POSH_THEME = "\path\to\poshthemes\your_theme.omp.json"
oh-my-posh init pwsh | Invoke-Expression

# Optional but provides instant changing between themes.
function Edit-PoshTheme {
    omputils theme $args 
    . $PROFILE
}

Set-Alias theme Edit-PoshTheme
```

## More

[Check out my One Dark inspired theme.](https://github.com/jedwillick/onedark-omp)
