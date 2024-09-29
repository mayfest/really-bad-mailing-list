import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import re
import os
from dotenv import load_dotenv 

load_dotenv()

# Email configuration
sender_email = os.getenv("SENDER_EMAIL")
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = os.getenv("SMTP_PORT")
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")

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


print("List of users:", users)

subject = "Reminder: Mayfest Productions Application and Info Sessions"

def create_personalized_body(first_name):
    return f"""
<html>
<body>
<p>Hey <strong>{first_name}</strong>!</p>

<p>You're receiving this email because you expressed interest in joining <strong>Mayfest Productions for the 2024 - 2025 school year</strong>! This is a friendly reminder about two important items:</p>

<ol>
    <li><strong>Application Deadline:</strong><br>
    Don't forget to fill out your application for Mayfest Productions!<br>
    The deadline is approaching, and we don't want you to miss out on this opportunity.<br><br>
    You can find the application form here: <a href="https://docs.google.com/forms/d/e/1FAIpQLSdA5zY0zDwe6yXaQ-FQmtOzdQ8ksdD2_FabsN0hzbHVTpLHZQ/viewform">Mayfest Productions Application</a></li>

    <li><strong>Upcoming Info Sessions:</strong><br>
    We have scheduled information sessions to answer any questions you may have about 
    Mayfest Productions. These sessions are a great way to learn more about our organization 
    and the application process.<br><br>
    <strong>Info Session Dates:</strong>
    <ul>
        <li><strong>September 27th (TODAY!!)</strong> at 3:30 PM on Zoom
            <ul>
                <li>Feel free to join using this link: <a href="https://northwestern.zoom.us/j/95079968506">Zoom Meeting</a></li>
                <li>Or using the Meeting ID: 950 7996 8506</li>
            </ul>
        </li>
        <li><strong>September 29th</strong> at 2:00 PM at Annenberg Hall, Room G15</li>
    </ul>
    </li>
</ol>

<p>Still looking for more information about Mayfest? Check out our website, <a href="https://www.dilloday.com/">dilloday.com</a></p>

<p>To stay updated on all things Mayfest, make sure to follow us on social media:</p>
<ul>
    <li>Instagram: <a href="https://www.instagram.com/dillo_day/">@dillo_day</a></li>
    <li>TikTok: <a href="https://www.tiktok.com/@dilloday">@dilloday</a></li>
    <li>Twitter: <a href="https://twitter.com/Dillo_Day">@Dillo_day</a></li>
</ul>

<p>If you have any questions, please don't hesitate to reach out to us.</p>

<p>We look forward to receiving your application and seeing you at the info sessions!</p>

<p>Best regards,<br>
The Mayfest Productions Team</p>
</body>
</html>
"""

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def send_email(recipient, first_name):
    if not is_valid_email(recipient):
        print(f"Invalid email address: {recipient}. Skipping this recipient.")
        return False

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    
    html_body = create_personalized_body(first_name)
    message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            
            try:
                server.login(smtp_username, smtp_password)
            except smtplib.SMTPAuthenticationError:
                print(f"SMTP Authentication failed. Please check your username and password.")
                return False
            
            try:
                server.sendmail(sender_email, recipient, message.as_string())
                print(f"Email sent successfully to {recipient}")
                return True
            except smtplib.SMTPRecipientsRefused:
                print(f"Recipient refused: {recipient}. This email address may not exist.")
            except smtplib.SMTPSenderRefused:
                print(f"Sender refused. Your email provider may have blocked the sending of this email.")
            except smtplib.SMTPDataError:
                print(f"The SMTP server refused to accept the message data for {recipient}.")
            except smtplib.SMTPException as e:
                print(f"SMTP error occurred while sending to {recipient}: {str(e)}")
    
    except smtplib.SMTPConnectError:
        print(f"Failed to connect to the SMTP server. Please check your internet connection and SMTP server settings.")
    except smtplib.SMTPServerDisconnected:
        print(f"Server unexpectedly disconnected while sending to {recipient}. Please try again later.")
    except Exception as e:
        print(f"An unexpected error occurred while sending to {recipient}: {str(e)}")
    
    return False

# Main loop to send emails
success_count = 0
failure_count = 0

for user in users:
    if send_email(user["email"], user["first_name"]):
        success_count += 1
    else:
        failure_count += 1

print(f"\nEmail sending process completed.")
print(f"Successful sends: {success_count}")
print(f"Failed sends: {failure_count}")