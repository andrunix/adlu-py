#! /usr/bin/python

import smtplib, sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import COMMASPACE

def send_notification(smtp, frm, to, cc, mgr_name, usr):

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Email subject"
	msg['From'] = frm
	msg['To'] = COMMASPACE.join(to)
	msg['Cc'] = COMMASPACE.join(cc)

	# add the "importance" flag
	msg.add_header("X-Priority", "1")

	# Create the body of the message (a plain-text and an HTML version).
	text = "Important - ACTION REQUIRED\n\n"
	text += "Manager: " + mgr_name + "\n\n"
	text += """\
			Last year, Internal Audit conducted a review of your system. Part of this
			review focused on access. It was determined that several users are 
			inappropriately included. Therefore, a close review is being conducted.

			You are receiving this email because you have direct reports that have access to
			this application. In order to determine that this access is valid, please review the list 
			below and respond to this email to indicate whether or not this access is apprpriate.
			Please note: If you do not respond to this email by June 11, 2010, access for the
			users listed below will be revoked.\n\n
		"""
	for u in usr:
		text += "* " + u + "\n"

	text += "Thank you for your cooperation.\n\nAndrew Pierce"

	html = """\
	<html>
	<head></head>
	    <body>
	    <p style="font-family: Arial, sans serif; font-size: 14pt; font-weight: bold">
	    Important - ACTION REQUIRED
	    </p>
	    <p style="font-family: Arial, sans serif; font-size: 12pt; font-weight: bold">
	    Manager: 
	    """
	html += mgr_name
	
	html += """\
	    </p>
	    <p style="font-family: Calibri, Arial, sans serif; font-size: 12 pt">
	    Last year, Internal Audit conducted a review of your system. Part of this
	    review focused on access. It was determined that several users are
	    inappropriately included. Therefore, a close review is being conducted.
	    </p>
	    <p style="font-family: Calibri, Arial, sans serif; font-size: 12 pt">
	    You are receiving this email because you have direct reports that have access to
	    this application. In order to determine that this access is valid, please review the list
	    below and respond to this email to indicate whether or not this access is 
	    appropriate.
	    </p>
	    <p style="font-family: Calibri, Arial, sans serif; font-size: 12 pt; color: red">
	    <b>Please Note: If you do not respond to this email by June 11, 2010, access for
    the users listed below will be revoked.</b>
    </p>
    <p style="font-family: Calibri, Arial, sans serif; font-size: 12 pt">
    <ul style="font-family: Calibri, Arial, sans serif; font-size: 12 pt">
	"""
	for u in usr:
		html+= "<li>%s</li><br/>" % (u)

	html += """\
		</ul>
	    </p>

	    <p style="font-family: Calibri, Arial, sans serif; font-size: 12 pt">
	    Thank you for your cooperation.<br/><br/>
	    Andrew Pierce
	    </p>
	    </body>
	</html>
	"""

	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	msg.attach(part1)
	msg.attach(part2)

	# Send the message via local SMTP server.
	s = smtplib.SMTP(smtp)
	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	# s.sendmail(me, you, msg.as_string())
	addrs = to + cc
	s.sendmail(frm, addrs, msg.as_string())
	s.quit()

if __name__=='__main__':

	smtp = 'smtp.example.com'
	me = 'fromuser@example.com'
	you = ['touser@example.com']
	cc = ['ccuser1@example.com', 'ccuser2@example.com']
	mname = 'Duck, Daffy'
	usr = [ 'Spears, Britney', 'Perry, Katie']

	send_notification(smtp, me, you, cc, mname, usr)

	
