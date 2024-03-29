import io
import smtplib
import zipfile
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate

import requests

from .utils import slugify


class Kindle:
    def __init__(self, email: str, password: str, smtp_server: str, smtp_port: int):
        self.email = email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_book(self, to_email: str, title: str, attachment: bytes) -> None:
        # Slugify the title
        title = slugify(title)

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = to_email
        msg['Message-Id'] = make_msgid('S2K')
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "Send to Kindle"

        # Add the message body
        msg.attach(MIMEText("Sent from knowledge-toolkit"))

        # Zip the eBook
        zip_ebook = io.BytesIO()
        with zipfile.ZipFile(zip_ebook, 'w') as zipf:
            zipf.writestr(f'{title}.epub', attachment)
        zip_ebook.seek(0)

        # Add the attachment to the email
        epub = MIMEBase("application", "octet-stream")
        epub.set_payload(zip_ebook.read())

        # Encode the attachment in base64
        encoders.encode_base64(epub)

        # Add header with the attachment's filename
        epub.add_header("Content-Disposition", 'attachment', filename=f"{title}.zip")

        # Add the attachment to the email
        msg.attach(epub)

        # Set up the SMTP server
        server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)

        # Login to the SMTP server using your username and password
        server.login(self.email, self.password)

        # Send the email
        server.sendmail(self.email, to_email, msg.as_string())

        # Disconnect from the server
        server.quit()
