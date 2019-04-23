# https://docs.python.org/dev/library/cmd.html
import cmd
# https://blog.sicara.com/perfect-python-command-line-interfaces-7d5d4efad6a2
# from tqdm import tqdm
from progress.bar import Bar
import os
import getpass

import browser.parseFP

class CommanderInterface(cmd.Cmd):
	intro = "Hello Incident Commander... What forensics artifacts would you like to extract? Type 'help' or '?' to list options.\n"
	prompt = 'Commander >'

	def do_chrome_correlation(self, arg):
		'I hope you remembered to delete your browser history...(no argument by default runs pulls history for currently logged in user)'
		username = parse(arg)
		if not username:
			username = get_logged_in_user()
		else:
			username = username[0]
		print("Pulling Chrome history for " + username + " ...")
		browser.parseFP.run("chrome", username)
	def do_all(self, arg):
		'Give it everything we got!'
		print("Running all programmed forensics functions...")
		self.do_chrome_correlation(arg)
	def do_bye(self, arg):
		'This is how it ends, Commander.'
		print("Goodbye Commander...")
		return True

def get_logged_in_user():
	return os.getlogin()

def parse(arg):
	'Convert a series of zero or more strings to an argument tuple'
	return tuple(map(str, arg.split()))

if __name__ == '__main__':
	CommanderInterface().cmdloop()