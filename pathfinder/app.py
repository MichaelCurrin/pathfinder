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

    @return: 'OK' if URI request is results in 200 response code, otherwise
        return 'Invalid' for any other response code or request errors.
    """
    print("Validating: {0}".format(uri))

    try:
        response = requests.get(uri, timeout=conf.getfloat('Scrape', 'timeout'))
    except requests.exceptions.RequestException:
        return 'Invalid'

    if response.status_code == 200:
        return 'OK'
    else:
        return 'Invalid'


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
                <td> <a href="{URI}">{URI}</a> </td>
            </tr>
    """

    formatted_rows = [row_template.format(**row) for row in uri_data]

    return base.format(
        title=title,
        table_data="\n".join(formatted_rows)
    )


def run(uri_data, subject=None):
    """Validate the given URIs then print and email the results.

    @param uri_data: List of rows of data which each row is a dictionary
        with the following format:
            {
                'title': str,
                'URI': str,
                'notify': str
            }
    @param subject: Message to use for the subject of the mail. If not set,
        no mail will be sent.

    @return: None
    """
    for row in uri_data:
        row['result'] = validate_uri(row['URI'])

    # Handle printing of plain text report of all rows.
    template = "{result:10} {title:20} {uri}"
    header = template.format(result="Result", title="Title", uri="URI")

    rows_as_text = [
        template.format(
            result=row['result'],
            title=row['title'],
            uri=row['URI']
        ) for row in uri_data
    ]
    plain_text = "\n".join(
        [header, "=" * len(header)] + rows_as_text
    )
    print(plain_text)
    print()

    if subject:
        # Handle mail an HTML report, for rows matching notification conditions.
        matched_rows = []
        for data in uri_data:
            assert data['notify'] in ('always', 'valid', 'invalid'), \
                "Got notify value as '{0}' but expected value as one of:"\
                " always, valid, invalid".format(data['notify'])

            if (data['notify'] == 'always' or
                (data['result'] == 'OK' and data['notify'] == 'valid') or
                (data['result'] == 'Invalid' and
                    data['notify'] == 'invalid')):
                matched_rows.append(data)

        if matched_rows:
            count = len(matched_rows)
            print("Sending mail with {count} matched row{plural}.".format(
                count=count,
                plural="s" if count != 1 else ""
            ))
            html = build_html(subject, matched_rows)
            send_mail(
                subject,
                plain_text=plain_text,
                html=html
            )
            print("Sent mail.")
        else:
            print("Zero rows matched, so no mail was sent.")


def main():
    """Main function to handle command-line arguments.

    The logic for setting the current command using dest of subparser
    was borrowed from here:
        https://stackoverflow.com/questions/8250010/argparse-identify-which-subparser-was-used

    @return: None
    """
    parser = argparse.ArgumentParser(
        description="Pathfinder app. Expects input values set on command-line"
            " or in a CSV file, then prints output and sends an email"
            " where notification conditions are met."
    )

    subparsers = parser.add_subparsers(
        help="sub-command help",
        dest='command'
    )

    path_parser = subparsers.add_parser(
        'file',
        help="Specify persistent file containing rows of URI data to validate",
    )
    path_parser.add_argument(
        'file',
        metavar='PATH',
        help="Path to CSV file. See var/lib/paths.csv.template as example"
            " of header format. All rows are validated, the results are "
            " printed and a mail is sent if at least on row result meets"
            " its notify condition."
    )
    path_parser.add_argument(
        '-n', '--no-send',
        action='store_true',
        help="If supplied, override the default behavior and prevent a"
            " mail from being sent."
    )
    path_parser.add_argument(
        '--subject',
        help="Subject to use in the mail. Defaults to value set on config file"
            " if not set. Must be quoted to include spaces."
    )

    custom_parser = subparsers.add_parser(
        'custom',
        help="Specify a single URI to validate using command-line arguments",
    )
    custom_parser.add_argument(
        'title',
        metavar='TITLE',
        help="Short label describing the URI. Must be quoted to include spaces."
    )
    custom_parser.add_argument(
        'uri',
        metavar='URI',
        help="URI to validate."
    )
    custom_parser.add_argument(
        '-n', '--no-send',
        action='store_true',
        help="If supplied, override the default behavior and prevent a"
            " mail from being sent."
    )
    custom_parser.add_argument(
        '--subject',
        help="Subject to use in the mail. Defaults to value set on config file"
            " if not set. Must be quoted to include spaces."
    )

    args = parser.parse_args()

    if not args.command:
        args.print_help()
    else:
        if args.command == 'file':
            uri_data = read_csv(args.file)
        else:
            row = {
                'title': args.title,
                'URI': args.uri,
                'notify': 'always'
            }
            uri_data = [row]

        if args.no_send:
            subject = None
        else:
            if args.subject:
                subject = args.subject
            else:
                subject = conf.get('Email', 'default_subject')

        run(uri_data, subject)


if __name__ == '__main__':
    main()
