# Usage

If you do not have the application installed and your environment setup, first see [SystemInstallation](SystemInstallation).

## Help

Get main application help.

```bash
$ cd PATH_TO_REPO
$ source virtualenv/bin/activate
$ # Show basic usage instructions.
$ python pathfinder
$ # Show full help.
$ python pathfinder --help
$ # Alternatively
$ ./pathfinder/__main__.py --help
```

Get help on a command.

```bash
$ python pathfinder custom -h
```


## Run

Ad hoc input

* Specify values in the command-line.

    ```bash
    $ python pathfinder custom --no-send Obama https://twitter.com/BarackObama
    Validating: https://twitter.com/BarackObama
    Result     Title                URI
    ===================================
    OK         Obama                https://twitter.com/BarackObama

    python pathfinder custom --no-send 'Obama Official' https://twitter.com/BarackObamaOfficial
    Validating: https://twitter.com/BarackObamaOfficial
    Result     Title                URI
    ===================================
    Invalid    Obama Official       https://twitter.com/BarackObamaOfficial
    ```

Read in stored values

1. Create a CSV file in `pathfinder/var/lib/`, based on the template file in the same directory. Or use the command below, pasting the contents after pressing enter and then pressing ctrl+D in place of `<< EOF`, to signal end of file.
    ```bash
    $ cat -> pathfinder/var/lib/presidents.csv
    title,URI,notify
    "TW Obama main",https://twitter.com/BarackObama,always
    "TW Obama test",https://twitter.com/BarackObamaOfficial,always
    "TW Obama test2",https://twitter.com/TheBarackObama,valid
    "TW Obama test3",https://twitter.com/Barack_Obama,invalid
    << EOF
    ```
2. Read in the CSV file.

    ```bash
    $ python pathfinder file --no-send pathfinder/var/lib/presidents.csv
    Validating: https://twitter.com/BarackObama
    Validating: https://twitter.com/BarackObamaOfficial
    Validating: https://twitter.com/TheBarackObama
    Validating: https://twitter.com/Barack_Obama
    Result     Title                URI
    ===================================
    OK         TW Obama main        https://twitter.com/BarackObama
    Invalid    TW Obama test        https://twitter.com/BarackObamaOfficial
    OK         TW Obama test2       https://twitter.com/TheBarackObama
    ```

Print a report

* _TODO_

Email a report

1. Create a local application configuration as per instructions in [SystemInstallation.md](docs/SystemInstallation.md)
2. Run a custom or file command. _TODO add a mail argument_


Setup a scheduled mail

1. Setup the `custom` or `file` commands as shown above. If using the file option but only want to get an email notification when changes, then set the 'notify' value to be appropriate for the conditions you are waiting for.
2. Test the command, outside of the active environment (use `deactivate` or open a new terminal). Where FULL_PATH_TO_REPO below is an absolute path.
    ```bash
    $ FULL_PATH_TO_REPO/pathfinder/virtualenv/bin/python \
    FULL_PATH_TO_REPO/pathfinder/pathfinder/ custom Obama https://twitter.com/BarackObama
    ```
3. Add the command to a cron file. For example, enter `crontab -e` then paste the following as your cron schedule file. Visit my [cron tutorials](https://github.com/MichaelCurrin/learn-to-code/tree/master/bash/tutorials/cron) for further details.
    ```
    # m h  dom mon dow   command
    # 0 12 *   *   *     FULL_PATH_TO_REPO/pathfinder/virtualenv/bin/python FULL_PATH_TO_REPO/pathfinder/pathfinder/ custom Obama https://twitter.com/BarackObama
    ```
