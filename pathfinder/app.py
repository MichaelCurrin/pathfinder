#!/usr/bin/env python
"""
Main application file.

Check whether inputs URIs are valid or not and either send an email with the
result. Also prints all results.
"""
import argparse

import requests

from lib import read_csv, send_mail
from lib.config import AppConf

conf = AppConf()


def validate_uri(uri):
    """Check whether a URI is valid.

    @param uri: URI to validate as string.

    @return: True if URI request is results in 200 response code, otherwise
        return False for any other response code or request errors.
    """
    print("Validating: {0}".format(uri))

    try:
        response = requests.get(uri, timeout=conf.getfloat('Scrape', 'timeout'))
    except requests.exceptions.RequestException:
        return False

    if response.status_code == 200:
        return True
    else:
        return False


def build_html(title, uri_data):
    """Use templates to build an HTML mail with dynamic table rows.

    @param title: Title value to use in metadata and body.
    @param uri_data: List of URI rows to add to the HTML table output.

    @return: Completed HTML template with rows of URI data.
    """
    base = """
<!DOCTYPE html>
<html>
    <head>
        <title>{title}</title>
        <style>
            table, th, td {{
                border: 1px solid black;
                border-collapse: collapse;
            }}
        </style>
    </head>

    <body>
        <h1>{title}</h1>

        <table>
            <tr>
                <th>Result</th>
                <th>Title</th>
                <th>URI</th>
            </tr>
            {table_data}
        </table>
    </body>
</html>
    """

    row_template = """
            <tr>
                <td>{result}</td>
                <td>{title}</td>
                <td>{URI}</td>
            </tr>
    """

    formatted_rows = [row_template.format(**row) for row in uri_data]

    return base.format(
        title=title,
        table_data="\n".join(formatted_rows)
    )


def run(uri_data, subject):
    """Validate the given URIs then print and email the results.

    @param uri_data: List of rows of data which each row is a dictionary
        with the following format:
            {
                'title': str,
                'URI': str,
                'notify': str
            }
    @param subject: Message to use for the subject of the mail.

    @return: None
    """
    for row in uri_data:
        row['result'] = validate_uri(row['URI'])

    # Handle printing of plain text report of all rows.
    template = "{result:10} {title:20} {uri}"
    header = template.format(result="Result", title="Title", uri="URI")

    rows_as_text = [
        template.format(
            result='OK' if row['result'] else 'Invalid',
            title=row['title'],
            uri=row['URI']
        ) for row in uri_data
    ]
    plain_text = "\n".join(
        [header, "=" * len(header)] + rows_as_text
    )
    print(plain_text)
    print()

    # Handle mail an HTML report, for rows matching notification conditions.
    matched_rows = []
    for data in uri_data:
        assert data['notify'] in ('always', 'valid', 'invalid'), \
            "Got notify value as '{0}' but expected value as one of:"\
            " always, valid, invalid".format(data['notify'])

        if (data['notify'] == 'always' or
            (data['result'] is True and data['notify'] == 'valid') or
                (data['result'] is False and data['notify'] == 'invalid')):
            matched_rows.append(data)

    if matched_rows:
        html = build_html(subject, matched_rows)
        send_mail(
            subject,
            plain_text=plain_text,
            html=html
        )
        print("Send mail with {0} rows.".format(len(matched_rows)))
    else:
        print("Zero rows matched so no mail was sent.")
