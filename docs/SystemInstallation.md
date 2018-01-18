# System Installation

Instructions are for Linux OS.

## Setup repo and environment

This app requires Python3. It is recommended to use Python3.5 or higher.

It is recommended to install dependencies in a virtual environment in a directory such as the one indicated below.

1. Install virtualenv and pip as needed.
    ```bash
    $ sudo apt-get update
    $ sudo apt-get install python-pip
    $ sudo apt-get install virtualenv
    ```
2. Create a virtual environment.
    ```bash
    $ cd ~/.local/
    $ mkdir virtualenvs && cd virtualenvs
    $ virtualenv pathfinder --python=python3
    ```
3. Clone the repo and install dependencies into the virtual environment.
    ```bash
    $ mkdir ~/repos && cd ~/repos
    $ git clone git@github.com:MichaelCurrin/pathfinder.git
    $ cd pathfinder
    $ # Create a symlink to the virtualenv created in step 2.
    $ ln -s ~/.local/virtualenvs/pathfinder virtualenv
    $ source virtualenv/bin/activate
    $ pip install -r requirements.txt
    ```

## Configure

The repo comes with a default configuration file called [app.conf](pathfinder/etc/app.conf). It follows the standard set by the configparser Python package.

Local configuration is recommended especially to make use of the email functionality, since the default credentials are empty.

The values can be customised by creating a local configuration file, which will be read by the application when it runs to override the default values. 

Create a local conf file at one of the following locations:
- `~/.config/pathfinder.conf`
- `PATH_TO_REPO/pathfinder/etc/app.local.conf`

A example file might look like this:
```
# Local app configuration file

[Email]
from: my_email@gmail.com
password: my_password


[Scrape]
timeout: 3
```

Creating a file at the first path is preferred for persisting values in the file, since a file at the second path would be lost if the repo is deleted. Also, the first path is shorter and therefore quicker to access from anywhere in the terminal. This may be useful if the app is ever setup to run as an installed application, so that one does not have to find the location of package in order to customise it.

_TODO Consider for cross-platform use that ~/.config may not exist and needs instructions to be created on Mac or Linux. And may have a different convention on Windows, or may still be fine._

Now that you're setup, you can follow the [Usage](Usage.md) instructions.
