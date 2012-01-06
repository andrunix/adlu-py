#!/usr/bin/python
import sys
import ldap
import emailmgr

# ---------------------------------------------------------------------------
# get_sorted_users
#
def get_sorted_users(infile, srv, usr, pwd):
	con = ldap.open(srv)
	con.simple_bind_s(usr, pwd) 

	# create a list that we will add everyone to after we lookup their manager
	user_list = []
	
	# do a loop here to read the input file line-by-line
	file = open(infile)
	while 1:
		line = file.readline()
		if not line:
			break
		# parse each line for the user id
		uid = line.split("\t")[0]

		# lookup user
		att = userlu(con, "sAMAccountName=" + uid)
		if att:
			mgr = att['manager'][0].replace("\\", "")
			mgr = mgr.split("OU=")[0].rstrip(", ")
			mgr = mgr.replace("(", "\(")
			mgr = mgr.replace(")", "\)")

			# lookup the manager so we can get his email and lan ID
			mgr_att = userlu(con, mgr)
			mgr_email = mgr_att['mail'][0]

			# add this user, as a tuple, to our list
			user_list.append((uid, att['cn'][0], att['mail'][0], mgr[3:], mgr_email))

		else:
			# what we have here is a terminated employee, he does NOT get added 
			# to the list. But we need to do something with him so we need to 
			# remove him from AppWatch. For now, print him on stdout
			print "Terminated employee: %s" % \
					(uid)

	# sort the output list
	slist = sorted(user_list, key=lambda usr: usr[3])
	return slist

# ---------------------------------------------------------------------------
# send_emails
#
def send_emails(slist, srv):
	me  = "fromuser@example.com"
	cc = ['touser1@example.com', 'touser2@example.com']
	
	# iterate over the sorted list and send emails to managers
	mgr = ""
	mgr_email = ""
	users = []
	
	# good old fashioned control-break logic
	email_count = 0

	for u in slist:
		# print "%s\t%s\t%s\t%s\t%s" % (u[0], u[1], u[2], u[3], u[4])
		if mgr != u[3]:
			if mgr:
				print "that is all for mgr: " + mgr
				print "sending email to: " + mgr_email
				print "users: " 
				for usr in users:
					print usr
				print "-----------------------------------------------"

	                        # send the actual email notifications
	                        emailmgr.send_notification(srv, me, [mgr_email], cc, mgr.replace("\\", ""), users)

				# empty out the user list
				users = []

				# increment out email count
				email_count += 1

		mgr = u[3]
		mgr_email = u[4]
		users.append(u[1].replace("\\", ""))

	# polish it off with the last one...
	print "Last manager: " + mgr
	print "Email to: " + mgr_email
	
	for usr in users:
		print usr

	emailmgr.send_notification(srv, me, [mgr_email], cc, mgr.replace("\\", ""), users)

	email_count += 1
	return email_count

# ---------------------------------------------------------------------------
# userlu() 
#
def userlu(con, usr):
	res_attrs = {}
	base_dn="ou=users,ou=accounts,dc=up,dc=corp,dc=upc"
	attrs=['cn', 'sAMAccountName', 'mail', 'manager']
	# attrs=['sAMAccountName', 'mail', 'manager', 'telephoneNumber', 'title']
	filter = usr
	try: 
		result_data = con.search_s(base_dn, ldap.SCOPE_SUBTREE, filter, attrs )
		res_attrs = result_data[0][1]
	except:
		#	print "Uh oh. We must have a terminated employee with : " + usr
		pass
		
	return res_attrs

# ---------------------------------------------------------------------------
# show_usage
#
def show_usage():
	print "adlu.py"
	print "----------------------------------------------------------------------"
	print "Usage: "
	print "\tadlu.py <file> <user> <password>\n"
	print "Where: \n\tfile - the input file of user id's extracted from AppWatch\n"
	print "\tuser - the user id to do lookups in Active Directory\n"
	print "\tpassword - the password used to connect to Active Directory\n"


# ---------------------------------------------------------------------------
# program entry point
#
if __name__=='__main__':

	if len(sys.argv) != 4:
	 	show_usage()
		sys.exit(2)

	inputfile = sys.argv[1]

	# get the user id from the command line
	who = sys.argv[2]

	# get the password from the command line
	cred = sys.argv[3]

	# the server is hard-coded too 
	ldap_srv = "ldap.example.com"
	mail_srv = "smtp.example.com"

	slist = get_sorted_users(inputfile, ldap_srv, who, cred)
	emails_sent = send_emails(slist, mail_srv) 

	print "\n\nSent %d emails to managers" % (emails_sent)

