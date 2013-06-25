#!/usr/bin/env python2
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
# @author Walter Barbagallo
# @contact turbometalskater at gmail dot com
# @version 0.2
#
#
# TODO
#	installazione fbcmd
#	check if connesso
#	check posta
#	cl-options
#	ripetizione delle notifiche [1,2,4,8..]
#	libnotify bindings for python
#	icone notify-send
#	se ci sono problemi a salvare il log non salvarlo e skippa ma continua
#	print usage
#	fb classe
#

import sys, time
import subprocess


refresh_time = 60


class log(object):
	def __init__(self):
		import os, datetime
		self.filename = "pyno.log"
		self.now = lambda : datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
		cwd = os.path.dirname(os.path.realpath(__file__))
		os.chdir(cwd)

		try:
			f = open(self.filename, 'w')
		except IOError:
			print "[errore] impossibile creare il file " + self.filename + "."
			sys.exit(1)
		f.write("[" + self.now() + "]\npyno started\n\n")
		f.close()

	def append(self, s):
		try:
			f = open(self.filename, 'a')
		except IOError:
			print "[errore] impossibile aprire il file " + self.filename + "."
			sys.exit(2)
		f.write("[" + self.now() + "]\n" + s + '\n\n')
		f.close()


""" Class used for having fibonacci style timed notifications.
	Everytime you touch() a pybonacci object, it return you if need to
	wait or not.
"""
class pybonacci(object):
	def __init__(self):
		self.val   = 1;
		self.last  = 0;
		self.count = 0;
	def touch(self):
		self.count += 1
		actual      = self.val
		self.val   += self.last
		self.last   = actual
		return self.val == self.count
	def reset(self):
		self.__init__()
	def cl_info(self):
		print "self.val: " + str(self.val) + "\nself.last: " + str(self.last) + "\nself.count: " + str(self.count)



""" check if deps are installed in the system """
def check_system():
	cmds = [ "notify-send", "fbcmd" ]
	err_msg = "\n\
[Errore] Impossibile lanciare pyno (Mancate dipendenze)\n\
Installare:"
	out_msg = ""
	some_err = 0;
	for c in cmds:
		ret = subprocess.call( "which " + c + " &> /dev/null ", shell = True )
		if ret != 0: # command not found
			if not some_err:
				out_msg += err_msg
			some_err = 1
			out_msg += "  - " + c
	if some_err:
		print(out_msg)
		LOG.append(out_msg)
		sys.exit(2)

	LOG.append("system check: ok")


def notify(title = "", msg = ""):
	cmd = "notify-send " + " \"" + title + "\" \"" + msg + "\""
	subprocess.call(cmd, shell = True)
	return 0


def check_fb():

	def fbcmd_notices(s = "fbcmd notices unread"):
		output = str(subprocess.check_output(s, shell = True))
		#f = open("/home/walter/tmp/fbcmd_example_output/3notices", 'r')
		#output = f.read()
		#f.close()
		notices = []
		for comment in output.split("\n\n"):
			""" TODO posso fare un for per le linee per poter exittare senza l'eccezione """
			if "[#]" in comment or comment == "":
				continue
			if not ":title" in comment:
				LOG.append("[ERRORE] formato commento non valido:\n" + comment)
			value = " ".join(comment[comment.index(":title")+6:].split())
			notices.append(value)
		return notices

	def fbcmd_inbox(s = "fbcmd inbox unread"):
		output = str(subprocess.check_output(s, shell = True))
		#f = open("/home/walter/tmp/fbcmd_example_output/1msg", 'r')
		#output = f.read()
		#f.close()
		inbox = []
		for message in output.split("\n\n"):
			if "[#]" in message or message == "":
				continue
			sender = ""
			text = ""
			for line in message.split('\n'):
				if "subject" in line:
					continue
				if ":to/from" in line:
					sender += line[line.index(":to/from")+8:].strip()
				else:
					if ":snippet" in line:
						text += line[line.index(":snippet")+8:].strip()
					else:
						text += line.strip()

			if sender == "" or text == "":
				LOG.append("[ERRORE] formato messaggio non valido:\n" + message)
				sys.exit(1)
			inbox.append(sender + " ha scritto: " + text)
		return inbox

	# initialize some vars
	def init_fb():
		FB_VARS['last_msg'] = "no last messages :)"
		FB_VARS['fib'] = pybonacci()


	# function start
	if FB_VARS == {}:
		init_fb()

	# sometimes fbcmd returns error messages. try-except prevent this case
	try:
		notices = fbcmd_notices()
		inbox   = fbcmd_inbox()
	except:
		pass

	notices_len = len(notices)
	inbox_len   = len(inbox)

	if notices_len == 0 and inbox_len == 0:
		# nothing to notify
		return

	# compose the title
	title = ""

	if notices_len == 1:
		title += "1 notifica"
	elif notices_len > 1:
		title += str(notices_len) + " notifiche"

	if notices_len != 0 and inbox_len != 0:
		title += " e "

	if inbox_len == 1:
		title += "1 messaggio"
	elif inbox_len > 1:
		title += str(inbox_len) + " messaggi"

	title = "Facebook: " + title
	msg = "> " + "\n> ".join(notices+inbox).replace('"', '\\"')

	# fibonacci wait
	if FB_VARS['last_msg'] == msg:
		if FB_VARS['fib'].touch():
			return
	else:
		FB_VARS['fib'].reset()

	FB_VARS['last_msg'] = msg
	notify(title, msg)

	# check_fb() end



if __name__ == '__main__':
	LOG = log()
	NUM_POLLING = 0;
	FB_VARS = {}

	check_system()
	try:
		while 1:
			NUM_POLLING += 1
			check_fb()
			time.sleep(refresh_time)
	except KeyboardInterrupt:
		print("\nLooped " + str(NUM_POLLING) + " times.\nBye!")
		pass
	except:
		import traceback
		LOG.append(traceback.format_exc())
		notify(title = "Errore inaspettato", msg = "Perfavore controlla pyno.log o invialo a walter")
		raise
