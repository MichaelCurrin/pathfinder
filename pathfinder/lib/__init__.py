"""Initialisation file for lib directory."""
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from formencode.validators import Email

from .config import AppConf


conf = AppConf()


def send_mail(subject, plain_text, html=None, from_addr=None, passwd=None,
              to_addr=None):
    """Send an email with Gmail using provided details and content.

    Thanks to StackOverflow answer:
        https://stackoverflow.com/questions/882712/sending-html-email-using-python

    @param subject: Subject for mail.
    @param plain_text: Body of mail in plain text.
    @param html: Optional body of mail in HTML form.
    @param from_addr: Email address to send from. If not supplied, configured
        default value is used.
    @param passwd: Password of email address to send from. If not the supplied,
        the configured default value is used.
    @param to_addr: Email address to send to. If not supplied, the configured
        default is used.

    @return: None
    """
    if not from_addr:
        to_addr = conf.get('Email', 'to')
        from_addr = conf.get('Email', 'from')
        passwd = conf.get('Email', 'password')

    # Raise Invalid error for bad email formatting.
    Email.to_python(to_addr)
    Email.to_python(from_addr)

    assert from_addr.endswith("@gmail.com"), "Configured from address must be"\
        " a Gmail account."

    msg = MIMEMultipart('alternative')
    msg['To'] = to_addr
    msg['From'] = from_addr
    msg['Subject'] = subject

    msg.attach(MIMEText(plain_text, 'plain'))
    if html:
        msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(from_addr, passwd)
    except smtplib.SMTPAuthenticationError:
        raise ValueError("Invalid Username and Password. Update conf file and"
                         " try again.")
    text = msg.as_string()
    server.sendmail(from_addr, to_addr, text)
    server.quit()


def read_csv(fpath):
    """Read path to CSV and return data.

    @param fpath: path to input CSV file, as absolute path or relative to
        the app dir. The header row is required and will be used to create
        column names as keys.

    @return data: list of CSV data, where each element is a row in the CSV
        represented as a dictionary.
    """
    with open(fpath) as csv_file:
        reader = csv.DictReader(csv_file)
        data = list(reader)

    return data


def test():
    """Send the sample CSV to the configured email address."""
    import os
    import json
    from config import AppConf
    conf = AppConf()
    fpath = os.path.join(conf.appDir, 'var', 'lib', 'paths.csv.template')
    data = read_csv(fpath)
    indented_text = json.dumps(data, indent=4)

    send_mail(
        subject="TEST Python",
        plain_text=indented_text,
    )


if __name__ == '__main__':
    test()
