# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

def sendEmail(me, to, subject, msg):

	msg = MIMEText(msg)

	msg['Subject'] = subject
	msg['From'] = me
	msg['To'] = to

	try:
		s = smtplib.SMTP("smtp.gmail.com", 587)
		s.ehlo()
		s.starttls()
		s.login("zhangdog@gmail.com", "Adsl2000")
		s.send_message(msg)
		s.quit()
	except:
		print("failed to send mail")
