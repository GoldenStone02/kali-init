# Kali Init
Automatically installs Kali Linux tools and Open-Source tools
> **Note**   
> Open-Source tools within might have issues as `dpkg -i`
> is used to extract the file content.

This takes reference from ippsec's parrot-build installation (https://github.com/IppSec/parrot-build).

## Requirements
- Python 3.7
- An OS (Preferable Debian/Kali)
- An internet connection

## Installation
```bash
git clone https://github.com/GoldenStone02/kali-init
pipx install --include-deps ansible
python3 install_tools.py
```

## To Do
- [ ] Add CTF relevent tools
- [ ] Add CLI for interaction
- [ ] Add compatability with other OS (e.g. Parrot OS)

