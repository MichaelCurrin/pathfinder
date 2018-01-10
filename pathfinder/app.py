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
    try:
        response = requests.get(uri, timeout=conf.getfloat('Scrape', 'timeout'))
    except requests.exceptions.RequestException:
        return False

    if response.status_code == 200:
        return True
    else:
        return False


def validate_uris(uri_data):
    """Validate the input URIs and return results.

    """
    for data in uri_data:
        data['result'] = validate_uri(data['URI'])


def run(uri_data, subject):
    validate_uris(uri_data)

    template = "{result:10} {title:20} {uri}"

    formatted = [
        template.format(
            result='OK' if data['result'] else 'INVALID',
            title=data['title'],
            uri=data['URI']
        )
        for data in uri_data
    ]

    # Print all the results as a report, regardless of the conditions.
    for f in formatted:
        print(f)

    # Process single email for all URIs and only include URIs outcomes which
    # meet their condition. No mail might be sent.
    outbound = []
    for i, data in enumerate(uri_data):
        if (data['notify'] == 'always' or
            (data['result'] is True and data['notify'] == 'valid') or
                (data['result'] is False and data['notify'] == 'invalid')):
            outbound.append(formatted[i])

    send_mail(subject, "\n".join(outbound))
