#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import unicodedata
import webbrowser
import hashlib
import sqlite3 as sqlite
import xml.etree.ElementTree as ET
import platform
import sys


class ChatMessage(object):
	def __init__(self):
		super(ChatMessage, self).__init__()
		self.from_username = '[data not available]'
		self.to_username = '[data not available]'
		self.message_body = '[data not available]'
	@property
	def from_username(self):
	    return self._from_username
	@from_username.setter
	def from_username(self, value):
	    self._from_username = value
	@property
	def to_username(self):
	    return self._to_username
	@to_username.setter
	def to_username(self, value):
	    self._to_username = value
	@property
	def message_body(self):
	   	return self._message_body
	@message_body.setter
	def message_body(self, value):
	   	self._message_body = value
	def to_html(self):
		html = """
		<tr>
			<td>__from_username__</td>
			<td>__to_username__</td>
			<td>__msg_body__</td>
		</tr>
		"""
		html = html.replace('__from_username__', self.from_username)
		html = html.replace('__to_username__', self.to_username)
		html = html.replace('__msg_body__', self.message_body)
		return html


class SkypeUser(object):
	def __init__(self):
		super(SkypeUser, self).__init__()
		self.actual_name = '[data not available]'
		self.username = '[data not available]'
		self.birthday = '[data not available]'
		self.phone_home = '[data not available]'
		self.phone_mobile = '[data not available]'
		self.email = '[data not available]'
	@property
	def actual_name(self):
	    return self._actual_name
	@actual_name.setter
	def actual_name(self, value):
	    self._actual_name = value
	@property
	def username(self):
	   	return self._username
	@username.setter
	def username(self, value):
	    self._username = value
	@property
	def birthday(self):
	     return self._birthday
	@birthday.setter
	def birthday(self, value):
	    	self._birthday = str(value)
	@property
	def phone_home(self):
	    return self._phone_home
	@phone_home.setter
	def phone_home(self, value):
	    self._phone_home = value
	@property
	def phone_mobile(self):
	    return self._phone_mobile
	@phone_mobile.setter
	def phone_mobile(self, value):
	    self._phone_mobile = value
	@property
	def email(self):
	    return self._email
	@email.setter
	def email(self, value):
	    self._email = value
	def to_html(self):
		html = """
		<tr>
			<td>__username__</td>
			<td>__fullname__</td>
			<td>__birthday__</td>
			<td>__homphone__</td>
			<td>__mobphone__</td>
			<td>__theemail__</td>
		</tr>
		"""
		html = html.replace('__username__', self.username)
		html = html.replace('__fullname__', self.actual_name)
		html = html.replace('__birthday__', self.birthday)
		html = html.replace('__homphone__', self.phone_home)
		html = html.replace('__mobphone__', self.phone_mobile)
		html = html.replace('__theemail__', self.email)
		return html
	 
def process_skype_database(db_file):
	messages = []
	user = None
	database_connection = sqlite.connect(db_file)
	database_cursor = database_connection.cursor()
	database_cursor.execute('SELECT author,dialog_partner,body_xml FROM Messages')
	for from_username,to_username,body_xml in database_cursor.fetchall():
		chatmessage = ChatMessage()
		if from_username:
			chatmessage.from_username = from_username
		if to_username:
			chatmessage.to_username = to_username
		if body_xml:
			chatmessage.message_body = body_xml
		messages.append(chatmessage)
	database_cursor.execute('SELECT skypename,fullname,birthday,phone_home,phone_mobile,emails from Accounts')
	xml_root = ET.parse('/'.join(db_file.split('/')[:-1])+'/config.xml').getroot()
	auth_data = xml_root[0][0][0].text # TODO: find out how to decrypt this
	user = SkypeUser()
	user_data = database_cursor.fetchone()
	if user_data[0]:
		user.username = user_data[0]
	if user_data[1]:
		user.actual_name = user_data[1]
	if user_data[2]:
		user.birthday = user_data[2]
	if user_data[3]:
		user.phone_home = user_data[3]
	if user_data[4]:
		user.phone_mobile = user_data[4]
	if user_data[5]:
		user.email = user_data[5]
	return (user, messages)

def verify_os_type():
	if platform.system() != 'Darwin':
		sys.stderr.write('[!] Incompatible operating system\n')
		exit(-1)

def get_db_list():
	db_files = []
	home_dir = os.path.expanduser("~")
	db_dir = home_dir+'/Library/Application Support/Skype'
	for the_dir in os.listdir(db_dir):
		if os.path.isdir(db_dir+'/'+the_dir) and the_dir not in ('DataRv', 'EmoticonCache.bundle', 'shared_dynco', 'shared_httpfe'):
			db_files.append(db_dir+'/'+the_dir+'/main.db')
	return db_files

def main(args):
	html = """
	<!DOCTYPE html>
	<html>
		<head>
			<meta charset='utf-8'>
			<title>SkypeDump Output Table</title>
			<link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
			<link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css">
			<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
			<script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
			<style type="text/css">
			    .sd-table{
			    	margin: 20px;
			    }
			</style>
		</head>
		<body>
			<div class="sd-table">
				<table class="table">
					<thead>
						<tr>
							<th>Skype Username:</th>
							<th>Real Name:</th>
							<th>Birthday:</th>
							<th>Home Phone #:</th>
							<th>Cell Phone #:</th>
							<th>Email:</th>
						</tr>
					</thead>
					<tbody>
						__USER_DATA__
					</tbody>
				</table>
				<table class="table">
					<thead>
						<tr>
							<th>From:</th>
							<th>To:</th>
							<th>Message:</th>
						</tr>
					</thead>
					<tbody>
						__MESSAGE_DATA__
					</tbody>
				</table>
			</div>
		</body>
	</html>
	"""
	user_html = ''
	message_html = ''
	for db_file in get_db_list():
		print "[*] Processing database: %s\n" % (db_file)
		user_info, messages_info = process_skype_database(db_file)
		user_html += user_info.to_html()
		for message in messages_info:
			message_html += message.to_html()
	html = html.replace('__USER_DATA__', user_html)
	html = html.replace('__MESSAGE_DATA__', message_html)
	html = unicodedata.normalize('NFKD', html).encode('ascii', 'ignore')
	html = re.sub(r'[^\x00-\x7F]+', '', html)
	with open('/tmp/skype_db.html', 'w') as f:
		f.write(html)
	webbrowser.open_new_tab('/tmp/skype_db.html')

if __name__ == '__main__':
	main(sys.argv)
