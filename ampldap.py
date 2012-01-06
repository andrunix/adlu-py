#!/usr/bin/python
import sys
import ldap

def main(srv, usr, pwd):
	con = ldap.open(srv)
	con.simple_bind_s(usr, pwd) 
	
	# display a "header" line
	print "User ID\tUser Name\tUser Email\tManager Name\tManager Email";

	# do a loop here to read the input file line-by-line
	file = open("users.txt") 
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

			print "%s\t%s\t%s\t%s\t%s" % \
					(uid, \
					att['cn'][0], \
					att['mail'][0], \
					mgr.lstrip('CN='),
					mgr_email)
		else:
			# what we have here is a terminated employee
			print "%s\t\t\t\t" % \
					(uid)


######################################################################################
# userlu() 
def userlu(con, usr):
	res_attrs = {}

	# TODO: set the base_dn properly. this is what we needed for
	#       our needs.
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

######################################################################################

if __name__=='__main__':

	# read the user id from the command line
	who = sys.argv[1]

	# get the password from the command line
	cred = sys.argv[2]

	# the server is hard-coded. Fix it for your environment.
	server="ldapserver"

	# let's get the party started...
	main(server, who, cred)


