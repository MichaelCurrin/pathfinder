"""Initialisation file for lib directory."""
import csv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from lib import AppConf

conf = AppConf()


def send_mail(subject, body, from_addr=None, to_addr=None, passwd=None):
    """Send an email with Gmail using provided details and content.

    @param subject:
    @param body:

    @param from_addr:
    @param to_addr:
    @param passwd:

    @return: None
    """
    if not from_addr:
        from_addr = conf.get('Email', 'from')
        to_addr = conf.get('Email', 'to')
        passwd = conf.get('Email', 'password')

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(from_addr, passwd)
    text = msg.as_string()
    server.sendmail(from_addr, to_addr, text)
    server.quit()


def read_csv(fpath):
    """Read path to CSV and return data.

    @param fpath: path to input CSV file, as absolute path or relative to
        the app dir.

    @return data: list of CSV data, where each element is a row in the CSV
        represented as a dictionary.
    """
    with open(fpath) as csv_file:
        reader = csv.DictReader(csv_file)
        data = list(reader)

    return data


def test():
    """Send the sample CSV to the configure email address."""
    import os
    import json
    from config import AppConf
    conf = AppConf()
    fpath = os.path.join(conf.appDir, 'var', 'lib', 'input.csv.template')
    data = read_csv(fpath)

    send_mail(
        subject="TEST Python",
        body=json.dumps(data, ident=4)
    )


if __name__ == '__main__':
    test()
