import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import re
import os
from dotenv import load_dotenv 
from concurrent.futures import ThreadPoolExecutor, as_completed
load_dotenv()
import time
from aiosmtpd.controller import Controller
import argparse

# Email configuration
sender_email = os.getenv("SENDER_EMAIL")
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = os.getenv("SMTP_PORT")
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")
RATE_LIMIT = os.getenv("RATE_LIMIT")
DAILY_LIMIT = os.getenv("GMAIL_DAILY_LIMIT")

users = []

with open("data/mayfest_productions_interest_form.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row["Preferred Email Address"], row["First Name"], row["Last Name"])
        user_email = row["Preferred Email Address"]
        user_first_name = row["First Name"]
        user_last_name = row["Last Name"]
        user_to_append = {
            "email": user_email,
            "first_name": user_first_name,
            "last_name": user_last_name
        }
        users.append(user_to_append)

users.append({
    "email": "EthanPineda2025@u.northwestern.edu",
    "first_name": "Ethan",
    "last_name": "Pineda"
})

# users.append({
#     "email": "AlexKahn2025@u.northwestern.edu",
#     "first_name": "Alex",
#     "last_name": "Kahn"
# })

# users.append({
#     "email": "DefneDeda2025@u.northwestern.edu",
#     "first_name": "Defne",
#     "last_name": "Deda"
# })

print("List of users:", users)

subject = "MAYFEST APPLICATIONS DUE 10/3 @ 11:59 PM"

def create_personalized_body(first_name):
    return f"""
<!doctype html>
<html>
  <body>
    <div
      style='background-color:#F5F5F5;color:#262626;font-family:"Helvetica Neue", "Arial Nova", "Nimbus Sans", Arial, sans-serif;font-size:16px;font-weight:400;letter-spacing:0.15008px;line-height:1.5;margin:0;padding:32px 0;min-height:100%;width:100%'
    >
      <table
        align="center"
        width="100%"
        style="margin:0 auto;max-width:600px;background-color:#FFFFFF"
        role="presentation"
        cellspacing="0"
        cellpadding="0"
        border="0"
      >
        <tbody>
          <tr style="width:100%">
            <td>
              <h2
                style="font-weight:bold;text-align:center;margin:0;font-size:24px;padding:16px 24px 16px 24px"
              >
                MAYFEST PRODUCTIONS MAILING LIST
              </h2>
              <div style="padding:8px 12px 8px 12px">
                <img
                  alt="Sample product"
                  src="https://i.postimg.cc/cHySR4N5/5U9A7913.jpg"
                  style="outline:none;border:none;text-decoration:none;vertical-align:middle;display:inline-block;max-width:100%"
                />
              </div>
              <div
                style="font-size:18px;font-weight:normal;padding:16px 24px 16px 24px"
              >
                <p>Hey {first_name} 👋</p>
                <p>Hope week 2 is treating you well!</p>
                <p>
                  Our Mayfam is here to send you a reminder that
                  <strong
                    >applications for Mayfest Productions close on Thursday,
                    October 3rd at 11:59 PM</strong
                  >. Here is a
                  <a
                    href="https://docs.google.com/forms/d/e/1FAIpQLSdA5zY0zDwe6yXaQ-FQmtOzdQ8ksdD2_FabsN0hzbHVTpLHZQ/viewform"
                    target="_blank"
                    >link</a
                  >
                  to our application as well as our
                  <a
                    href="https://docs.google.com/presentation/d/1lroDJY0nKB7zNeyiUP3pQhiQvqPFVEq7RjIkohg6e54/edit?usp=sharing"
                    target="_blank"
                    >info session slides</a
                  >
                  if you weren&#39;t able to catch us earlier.
                </p>
                <p>
                  Please please please <strong>do not</strong> hesitate to email
                  us at
                  <a href="mailto:dilloday@u.northwestern.edu" target="_blank"
                    >dilloday@u.northwestern.edu</a
                  >
                  if you have any questions about the applications or anything
                  Mayfest!
                </p>
                <p>
                  <em>Sending dillove</em>,<br />DEX<br />Alex &amp; Defne<br />Mayfest
                  Productions Co-Chair 2024-2025
                </p>
              </div>
              <div style="height:16px"></div>
              <div
                style="font-size:12px;font-weight:normal;padding:16px 24px 16px 24px"
              >
                <p>
                  <em
                    >you are reciving this email because you previously
                    expressed interest in being a part of the Mayfest
                    Productions mailing list. Want to be removed? Please reach
                    out
                    <a href="mailto:technology@dilloday.com" target="_blank"
                      >technology@dilloday.com</a
                    ></em
                  >
                </p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </body>
</html>
"""

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

class TestHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        print(f'Received message from: {envelope.mail_from}')
        print(f'Message recipients: {envelope.rcpt_tos}')
        print(f'Message content: {envelope.content.decode("utf8")}')
        print('--------')
        return '250 Message accepted for delivery'

def start_test_smtp_server():
    controller = Controller(TestHandler(), hostname='127.0.0.1', port=1025)
    controller.start()
    return controller

def send_email(user, test_mode=False):
    recipient = user["email"]
    first_name = user["first_name"]

    if not is_valid_email(recipient):
        print(f"Invalid email address: {recipient}. Skipping this recipient.")
        return False

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    
    html_body = create_personalized_body(first_name)
    message.attach(MIMEText(html_body, "html"))

    if test_mode:
        print(f"TEST MODE: Would send email to {recipient}")
        print(f"Subject: {subject}")
        print(f"Body: {html_body[:100]}...")  # Print first 100 characters of body
        return True

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient, message.as_string())
            print(f"Email sent successfully to {recipient}")
            return True
    except Exception as e:
        print(f"Failed to send email to {recipient}: {str(e)}")
        return False

def send_emails_rate_limited(users, max_workers=5, test_mode=False):
    success_count = 0
    failure_count = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, user in enumerate(users):
            if i >= int(DAILY_LIMIT):
                print(f"Daily limit of {int(DAILY_LIMIT)} emails reached. Stopping.")
                break
            
            futures.append(executor.submit(send_email, user, test_mode))
            
            # Rate limiting
            if (i + 1) % int(DAILY_LIMIT) == 0:
                time_elapsed = time.time() - start_time
                if time_elapsed < 60:
                    time.sleep(60 - time_elapsed)
                start_time = time.time()

        for future in as_completed(futures):
            try:
                if future.result():
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as exc:
                print(f'An email generated an exception: {exc}')
                failure_count += 1

    print(f"\nEmail sending process completed.")
    print(f"Successful sends: {success_count}")
    print(f"Failed sends: {failure_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email sender with testing modes")
    parser.add_argument("--mode", choices=["live", "print", "local"], default="print",
                        help="Sending mode: live (real sending), print (console output), local (local SMTP server)")
    args = parser.parse_args()

    if args.mode == "local":
        controller = start_test_smtp_server()
        smtp_server = "127.0.0.1"
        smtp_port = 1025

    test_mode = args.mode != "live"
    send_emails_rate_limited(users, test_mode=test_mode)

    if args.mode == "local":
        controller.stop()