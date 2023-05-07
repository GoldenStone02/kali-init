#!/usr/bin/env python3

# This is used for installing the necessary tools for kali linux
import os
import logging
import subprocess

# Get current directory and sudo user
# [NOTE]: This script must be run with sudo privileges
CURRENT_DIR = os.getcwd()
USER = os.getenv("USER")

# List of repositories to clone
REPOSITORIES = [
    {
        'url':'https://github.com/pwndbg/pwndbg',
        'required-setup': True,
        'setup': ['cd pwndbg', 'chmod +x setup.sh', './setup.sh']
    },
    {
        'url':'https://raw.githubusercontent.com/Crypto-Cat/CTF/main/auto_ghidra.py',
        'required-setup': False
    },
    {
        'url':'https://github.com/bitsadmin/wesng',
        'required-setup': False
    }
]

# List of applications to install
APPS = [
    'fcrackzip',
    'checksec',
    'gdb',
    'ghidra',
    'gobuster',
    'seclists',
    'ffuf',
    'tldr',
    'ltrace',
    'strace',
    'rustscan'
]

# Lists of aliases to add to the shell rc file
ALIASES = [
    '\n# Additional aliases for extra packages',
    f'alias ghidra_auto="python3 /home/{USER}/Desktop/apps/auto_ghidra.py"',
    'alias lsa="ls -la"'
]

# Dict of Files and commands to write additional configuration to
CONFIG = {
    '.gdbinit': 'source ~/Desktop/apps/pwndbg/gdbinit.py'    # Installation of pwndbg into gdb
}

# Used for coloring the logging output
# Credit to: 
#  https://betterstack.com/community/questions/how-to-color-python-logging-output/
#  https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/
class CustomFormatter(logging.Formatter):
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    # Old formatting version
    # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    time = "[%(asctime)s] ["
    type = "%(levelname)s"
    end = "] %(name)s - %(message)s (%(filename)s:%(lineno)s)"

    FORMATS = {
        logging.DEBUG: grey + time + grey + type + reset + end,
        logging.INFO: grey + time + blue + type + reset + end + reset,
        logging.WARNING: grey + time + yellow + type + reset + end + reset,
        logging.ERROR: grey + time + red + type + reset + end + reset,
        logging.CRITICAL: grey + time + bold_red + type + reset + end + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Create custom logger logging all five levels
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler()
# stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(CustomFormatter())
logger.addHandler(stdout_handler)

def add_aliases():
    '''Check the shell in use and add aliases to its respective rc file. 
    \nE.g.`.bash_aliases` or `.zshrc`
    '''
    # As a side note, Kali Linux uses zsh by default.
    # While OS's such as Parrot OS use bash by default.
    # So this script checks for both shell types.

    # Get Shell version
    filename = ""
    shell = os.environ.get("SHELL")
    logger.debug(shell)

    # Add aliases into shell rc file
    if shell:
        if "zsh" in shell:
            filename = ".zshrc"
        elif "bash" in shell:
            filename = ".bash_aliases"
        else:
            logger.error("The shell used is not supported.")
            return
        
        added = 0
        # Check if the aliases already exist in the rc file
        with open(filename, 'r') as f:
            config_file = f.read()
            for alias in ALIASES:
                if alias in config_file:
                    logger.info(f"Alias already exists in {filename}")
                else:
                    added += 1
                    # Opens and appends in the new aliases
                    with open(filename, 'a') as f:
                        f.write("\n" + alias)
        # Check if any aliases were added
        if added:
            logger.info(f"Aliases added to the {filename} file.")
    
    else:
        logger.warning("Unable to determine the shell in use.")
        return

def main():
    # Update and upgrade the system
    for command in ["sudo apt-get update -y", "sudo apt-get upgrade -y"]:
        logger.info("Executing the command: " + command)
        result = os.system(command)
        if result != 0:
            logger.error("Unable to run the command: " + command)
            return
        logger.info("Finished: " + command)

    # Install the applications
    try:
        os.chdir("/home/" + USER + "/Desktop/apps") # Change to user's Desktop/apps directory
    except FileNotFoundError:
        os.mkdir("/home/" + USER + "/Desktop/apps") # Create the directory if it doesn't exist
        os.chdir("/home/" + USER + "/Desktop/apps") # Change to user's Desktop/apps directory
        logger.info("Created Desktop/apps directory.")
    
    # Clone the repositories
    for repo in REPOSITORIES:
        logger.debug(repo)
        repo_url = repo['url']
        # Check if repository already exists
        if repo_url.split('/')[-1] in os.listdir():
            logger.info("Repository already exists: " + repo_url)
            continue
        else:
            if "raw.githubusercontent.com" in repo_url:
                check = subprocess.run(["wget", repo_url])
            elif "github.com":
                check = subprocess.run(["git", "clone", repo_url])
            else:
                logger.error("Unable to clone the repository: " + repo_url)
                return

            # Write the configuration files
            if check.returncode != 0:
                logger.critical("Unable to download the file: " + repo_url)
                return
        
        if repo['required-setup']:
            for command in repo['setup']:
                if "cd" in command:
                    os.chdir(command.split(" ")[1])
                    continue
                os.system(command)
                logger.info("Successfully ran the command: " + command)
            os.chdir("/home/" + USER + "/Desktop/apps") # Change to user's Desktop/apps directory

        logger.info("Successfully downloaded and configured: " + repo_url)
    
    # Check the current working directory and change it to the user's home directory
    if CURRENT_DIR != "/home/" + USER:
        os.chdir("/home/" + USER) # Change to user's home directory
    
    # Install the applications
    for app in APPS:
        check = subprocess.run(["sudo", "apt-get", "install", "-y", app])
        if check.returncode != 0:
            logger.error("Unable to install the application: " + app)
            return
        logger.info("Successfully installed the application: " + app)
    
    add_aliases()

    # Write the configuration files
    for file, command in CONFIG.items():
        # Checks if the file exists
        if os.path.exists(file):
            with open(file, 'r') as f:
                config_file = f.read()
                if command in config_file:
                    logger.info("Configuration already exists in the file: " + file)
                    continue
                else:
                    with open(file, 'a') as f:
                        f.write(command)
        else:
            with open(file, 'w') as f:
                f.write(command)
        
        logger.info("Successfully wrote the configuration file: " + file)

if __name__ == "__main__":
    main()