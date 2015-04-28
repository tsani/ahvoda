#!/usr/bin/env python

from smtplib import SMTP
import json
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("no")
        sys.exit(1)

    email_name = sys.argv[1]

    with open('secrets.json', 'r') as f:
        creds = json.load(f)

    with open(email_name, 'r') as f:
        email_contents = f.read()

    with SMTP(host='localhost', port=587) as smtp:
        smtp.starttls()
        smtp.login(creds['username'], creds['password'])
        smtp.sendmail("jake@mail.ahvoda.com", "jake@mail.ahvoda.com",
                '\n'.join([
                    "Subject: New opportunities for you!",
                    "To: Jacob Thomas Errington <jake@mail.ahvoda.com>",
                    "Content-type: text/html",
                    "",
                    email_contents]))
