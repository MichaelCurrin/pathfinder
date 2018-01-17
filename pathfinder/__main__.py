#!/usr/bin/env python
"""
Main application file.

Check whether inputs URIs are valid or not and produces a report which
can be logged and emailed.
"""
import argparse
import datetime
import sys

import requests
from formencode import Invalid

from lib import read_csv, send_mail
from lib.config import AppConf
from lib.validators import UriData


conf = AppConf()


def validate_uri(uri):
    """Check whether a URI is valid.

    @param uri: URI to validate as string.

    @return: 'OK' if URI request is results in 200 response code, otherwise
        return 'Invalid' for any other response code or request errors.
    """
    print("Validating: {0}".format(uri))

    try:
        response = requests.get(
            uri,
            timeout=conf.getfloat('Scrape', 'timeout')
        )
    except requests.exceptions.RequestException:
        return 'Invalid'

    if response.status_code == 200:
        return 'OK'
    else:
        return 'Invalid'


def build_html(mail_title, uri_data):
    """Use templates to build an HTML mail with dynamic table rows.

    Footer is kept at the bottom of the page thanks to:
        http://matthewjamestaylor.com/blog/keeping-footers-at-the-bottom-of-the-page

    @param page_title: Title value to use in metadata and body.
    @param uri_data: List of URI rows to add to the HTML table output.

    @return: HTML template with title and table rows filled in.
    """
    base = """
<!DOCTYPE html>
<html>
    <head>
        <title>{mail_title}</title>

        <style>

            html {{
                font-family: Arial, Helvetica, sans-serif;
            }}

            table, th, td {{
                border: 1px solid black;
                border-collapse: collapse;
            }}

            footer {{
               position:absolute;
               width:100%;
               bottom:0;
               height:60px;
               padding-left: 5px;
               background:#ddd;
            }}

        </style>
    </head>

    <body>
        <h2>{mail_title}</h2>

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
        mail_title=mail_title,
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
    @param subject: Message to use for the subject and heading of the
        mail. The current date will be added to the end of the subject.
        Leave the subject set to None to prevent sending of a mail.

    @return: None
    """
    # Clean the data first.
    uri_schema = UriData()
    cleaned_data = []
    for row in uri_data:
        try:
            cleaned_row = uri_schema.to_python(row)
        except Invalid as e:
            # Print a brief error message and show the problem row, which
            # should not be prettified in case that raises an error. Then exit.
            print("{error}. {message} \n".format(
                error=type(e).__name__,
                message=str(e)
            ))
            print("Input row: \n {0}".format(row))
            sys.exit(1)

        cleaned_data.append(cleaned_row)

    # Perform the main validation logic which this app is based around.
    for row in cleaned_data:
        row['result'] = validate_uri(row['URI'])

    # Handle printing of plain text report of all rows.
    template = "{result:10} {title:20} {uri}"
    header = template.format(result="Result", title="Title", uri="URI")
    plain_text_rows = [
        template.format(
            result=row['result'],
            title=row['title'],
            uri=row['URI']
        ) for row in cleaned_data
    ]
    print(header)
    print("=" * len(header))
    for row in plain_text_rows:
        print(row)

    if subject:
        # Handle mailing an HTML report, for rows matching
        # notification conditions.
        matched_rows = []
        for data in cleaned_data:
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

            subject_with_date = "{subject} {date}".format(
                subject=subject,
                date=str(datetime.date.today())
            )
            matched_rows_as_text = [
                template.format(
                    result=row['result'],
                    title=row['title'],
                    uri=row['URI']
                ) for row in cleaned_data
            ]
            plain_text = [header, "=" * len(header)] + matched_rows_as_text
            html = build_html(
                mail_title=subject_with_date,
                uri_data=matched_rows
            )

            send_mail(
                subject=subject_with_date,
                plain_text="\n".join(plain_text),
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
        " for notification conditions which are met."
    )

    subparsers = parser.add_subparsers(
        help="commands",
        dest='command'
    )

    custom_parser = subparsers.add_parser(
        'custom',
        help="Specify a single URI to validate using command-line arguments",
    )
    custom_parser.add_argument(
        'title',
        metavar='TITLE',
        help="Short label describing the URI. Must be quoted to include"
        " spaces."
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

    path_parser = subparsers.add_parser(
        'file',
        help="Specify persistent file containing rows of URI data to validate",
    )
    path_parser.add_argument(
        'file',
        metavar='PATH',
        help="Path to CSV file. See var/lib/paths.csv.template for"
        " required header format. A 'notify' value must be one of:"
        " 'valid', 'invalid' or 'always'. URIs in all rows will be"
        " validated, the results will be printed and a mail of just the"
        " rows meeting the notify condition will be sent. Or no mail, if"
        " no conditions are met."
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
