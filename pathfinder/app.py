#!/usr/bin/env python
"""
Main application file.

Check whether inputs URIs are valid or not and either send an email with the
result or print the result.
"""


def send_mail(from_addr, to_addr, passwd, subject, msg):
    """Send an email using Gmail using provided details and content.

    @param from_addr:
    @param to_addr:
    @param passwd:
    @param subject:
    @param msg:

    @return: None
    """
    pass


def read_csv(fpath):
    """Read path to CSV and return data.

    @param fpath: path to input CSV file, as absolute path or relative to
        the app dir.

    @return: two-dimensional list representing rows and columns of CSV data.
    """
    pass


def validate_uri(uri):
    """Check whether a URI is valid.

    @param uri: URI to validate as string.

    @return: True if URI request is successful and False otherwise.
    """
    pass


def process_uris(uris, condition, email_credentials):
    """Iterate through URIs and handle mailing of the validation results.

    @param uris:
    @param condition:
    @param email_credentials:

    @return: None
    """
    pass


def run(subject, titles, uris, email_trigger=None):
    """Valid given URIs with convenient titles and mail the results.

    @param subject:
    @parma titles:
    @param uris:
    @param email_trigger:

    @param: None
    """
    pass


if __name__ == '__main__':
    run()
