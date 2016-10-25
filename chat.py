#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Linggar Primahastoko
# Email: x@linggar.asia

import socket
import select
import time
from templates import messages, bot_name

class Chat:
	def __init__(self):
		# set variables
		self.RECV_BUFFER = 4096
		self.HOST = "0.0.0.0"
		self.PORT = 5000
		self.CONNECTION_LIST = []

		self.clients = {}
		self.users = {}
		self.status = ["JOINED", "ROOM", "PM"]
		self.rooms = {}
		self.before_status = {}
		self.private_status = {}
		self.private_messages = {}

		# root command
		self.commands = {
			"/quit": self.quit_chat,
			"/help": self.list_help,
			"/room" : self.room_method,
			"/private": self.private_method,
		}

		# command under room mode
		self.room_commands = {
			"help": self.room_help,
			"create": self.room_create,
			"list": self.room_list,
			"join": self.room_join,
			"users": self.room_users,
			"delete": self.room_delete,
			"exit": self.room_exit,
			"ban": self.room_ban,
			"unban": self.room_unban,
			"kick": self.room_kick,
		}

		# command under private mode
		self.private_commands = {
			"help": self.private_help,
			"chat": self.private_chat,
			"confirm": self.private_confirm,
			"exit": self.private_exit,
		}

		# set server socket
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind((self.HOST, self.PORT))
		self.server_socket.listen(10)

		# append connection
		self.CONNECTION_LIST.append(self.server_socket)
		print "<Starting Socket Server: {}:{}>".format(self.HOST, self.PORT)

	# NEW CLIENT, LIST HELP, QUIT
	def new_client(self):
		"""
		Welcoming new client
		Send welcome message and input username prompt
		"""
		sockfd, addr = self.server_socket.accept()
		self.CONNECTION_LIST.append(sockfd)
		print "<Client connected: ({}:{})>".format(addr[0], addr[1])

		if sockfd not in self.clients:
			self.clients[sockfd] = [addr, None]
			self.send_private(sockfd, messages["welcome_message"])
			self.send_private(sockfd, messages["input_username"])

		return addr

	def list_help(self, sock, msg):
		"""
		Help List Method
		"""
		self.send_private(sock, messages["help_list_message"])

	def quit_chat(self, sock, msg):
		"""
		Quit chat method, remove the user from all array and dict
		"""
		if self.users[self.clients[sock][1]]["status"] == self.status[2]:
			self.private_exit(sock, msg)
		self.send_private(sock, messages["bye_message"])
		self.users.pop(self.clients[sock][1])
		if self.clients[sock][1] in self.private_status:
			self.private_status.pop(self.clients[sock][1])
		self.clients.pop(sock)
		sock.close()
		self.CONNECTION_LIST.remove(sock)
	###########

	# MESSAGE HANDLING
	def handle_message(self, sock, data):
		"""
		Handle message method
		Receive message and process it
		"""
		msg = data.rstrip()
		# If it is a new client, send welcome message and input username prompt
		if self.clients[sock][1] == None:
			if msg not in self.users:
				self.users[msg] = {}
				self.users[msg]["status"] = self.status[0]
				self.users[msg]["sock"] = sock
				self.clients[sock][1] = msg
				self.send_private(sock, "<< <{}> Welcome {}. {}".format(bot_name, msg, messages["help_message"]))
				self.send_private(sock, ">> ")
			else:
				# If username is exist, send duplicate message, choose another username
				self.send_private(sock, messages["duplicate_username"])
		else:
			# If message start with /, then it is a command
			if msg.startswith("/"):
				cmd = msg.split()[0]
				if cmd in self.commands:
					self.commands[cmd](sock, msg)
				else:
					self.send_private(sock, messages["help_message"])
			else:
				# Check if a status is joined status
				if self.users[self.clients[sock][1]]["status"] == self.status[0]:
					self.send_private(sock, messages["help_message"])
				# if status is in room mode, send room prompt and send the message to all users under same room
				elif self.users[self.clients[sock][1]]["status"] == self.status[1]:
					if len(msg) != 0:
						room_msg = "\n<< <{}> {}\n".format(self.clients[sock][1], msg)
						self.send_room(sock, room_msg)
						self.send_room(sock, "room {}>> ".format(self.users[self.clients[sock][1]]["room"]))
				# if status in private mode, send notify to the user related to private message, only send message to the private session
				elif self.users[self.clients[sock][1]]["status"] == self.status[2]:
					if len(msg) != 0:
						if not self.private_status[self.clients[sock][1]]["confirmed"]:
							self.private_messages[self.private_status[self.clients[sock][1]]["friend"]][self.clients[sock][1]].append(msg)

							notify_private = "\n<< <{}> You get a private message from {}, type /private confirm {} to enter private session\n".format(bot_name, self.clients[sock][1], self.clients[sock][1])
							self.send_private(self.users[self.private_status[self.clients[sock][1]]["friend"]]["sock"], notify_private)
							self.send_prompt(self.users[self.private_status[self.clients[sock][1]]["friend"]]["sock"], msg)
						else:
							chat_msg = "\n<< <{}> {}\n".format(self.clients[sock][1], msg)
							self.send_private(self.users[self.private_status[self.clients[sock][1]]["friend"]]["sock"], chat_msg)
							self.send_prompt(self.users[self.private_status[self.clients[sock][1]]["friend"]]["sock"], msg)

			self.send_prompt(sock, msg)

	def send_prompt(self, sock, msg):
		"""
		Check the status and send prompt based it's mode
		"""
		if msg != "/quit":
			if self.users[self.clients[sock][1]]["status"] == self.status[0]:
				self.send_private(sock, ">> ")
			elif self.users[self.clients[sock][1]]["status"] == self.status[1]:
				self.send_private(sock, "room {}>> ".format(self.users[self.clients[sock][1]]["room"]))
			elif self.users[self.clients[sock][1]]["status"] == self.status[2]:
				self.send_private(sock, "private {}>> ".format(self.private_status[self.clients[sock][1]]["friend"]))

	def send_private(self, sock, message):
		"""
		Send message to one client
		"""
		for socket in self.CONNECTION_LIST:
			if socket == sock:
				try:
					socket.send(message)
				except:
					socket.close()
					self.CONNECTION_LIST.remove(socket)

	def broadcast(self, sock, message):
		"""
		Send message to all clients that connected to the server
		"""
		for socket in self.CONNECTION_LIST:
			if socket != self.server_socket and socket != sock:
				try:
					socket.send(message)
				except:
					socket.close()
					self.CONNECTION_LIST.remove(socket)

	def send_room(self, sock, message):
		"""
		Send message to all users under the same room
		"""
		room_name = self.users[self.clients[sock][1]]["room"]
		for user in self.rooms[room_name]["users"]:
			socket = self.users[user]["sock"]
			if socket != self.server_socket and socket != sock:
				try:
					socket.send(message)
				except:
					socket.close()
					self.CONNECTION_LIST.remove(socket)

	############

	# ROOMS
	def room_method(self, sock, msg):
		"""
		Handle commands under /room command
		"""
		if len(msg.split()) == 1:
			self.send_private(sock, messages["rooms"]["no_sub"])
		else:
			cmd = msg.split()[1]
			# Check if command in room commands
			if cmd in self.room_commands:
				self.room_commands[cmd](sock, msg)
			else:
				self.send_private(sock, messages["command_not_detect"])

	def room_help(self, sock, msg):
		"""
		Room command help list
		"""
		self.send_private(sock, messages["rooms"]["help_message"])

	def room_create(self, sock, msg):
		"""
		Create Room Method
		"""
		# Status must in joined mode, not room or private mode
		if self.users[self.clients[sock][1]]["status"] != self.status[0]:
			self.send_private(sock, messages["rooms"]["not_in_joined"])
		else:
			if len(msg.split()) < 3:
				self.send_private(sock, messages["rooms"]["no_room_name"])
			else:
				room_name = msg.split()[2]
				if room_name in self.rooms:
					self.send_private(sock, messages["rooms"]["room_exist"])
				else:
					# Create New Room
					self.users[self.clients[sock][1]]["status"] = self.status[1]
					self.users[self.clients[sock][1]]["room"] = room_name
					self.rooms[room_name] = {}
					self.rooms[room_name]['admin'] = self.clients[sock][1]
					self.rooms[room_name]['users'] = [self.clients[sock][1]]
					self.rooms[room_name]['banned'] = []
					print "<{} create room {}>".format(self.clients[sock][1], room_name)

	def room_list(self, sock, msg):
		"""
		List Rooms
		"""
		if not self.rooms:
			self.send_private(sock, messages["rooms"]["no_room"])
		else:
			all_rooms = "".join(["*{} ({})\n".format(i, len(self.rooms[i]["users"])) for i in self.rooms])
			rooms_available = "<< <{}> All available rooms:\n{}".format(bot_name, all_rooms)
			self.send_private(sock, rooms_available)

	def room_join(self, sock, msg):
		"""
		Join Room Method
		"""
		if self.users[self.clients[sock][1]]["status"] != self.status[0]:
			self.send_private(sock, messages["rooms"]["must_joined"])
		else:
			if len(msg.split()) < 3:
				self.send_private(sock, messages["rooms"]["no_room_name"])
			else:
				room_name = msg.split()[2]
				if room_name not in self.rooms:
					self.send_private(sock, messages["rooms"]["room_not_exist"])
				else:
					# If banned, cannot join room
					if self.clients[sock][1] in self.rooms[room_name]["banned"]:
						self.send_private(sock, messages["rooms"]["user_banned"])
					else:
						self.users[self.clients[sock][1]]["status"] = self.status[1]
						self.users[self.clients[sock][1]]["room"] = room_name
						self.rooms[room_name]["users"].append(self.clients[sock][1])

						# Broadcast to all users under same room
						join_room_msg = "\n<< <{}> {} is joining the room.\n".format(bot_name, self.clients[sock][1])
						self.send_room(sock, join_room_msg)
						self.send_room(sock, "room {}>> ".format(room_name))

						print "<{} join room {}>".format(self.clients[sock][1], room_name)

	def room_users(self, sock, msg):
		"""
		List all users under rooms
		"""
		if self.users[self.clients[sock][1]]["status"] != self.status[1]:
			self.send_private(sock, messages["rooms"]["must_in_room"])
		else:
			room_name = self.users[self.clients[sock][1]]["room"]
			all_users = []
			for user in self.rooms[room_name]["users"]:
				all_users.append("*{}\n".format(user) if user != self.rooms[room_name]["admin"] else "*{} (admin)\n".format(user))
			users_available = "<< <{}> All available users in this room:\n{}".format(bot_name, ''.join(all_users))
			self.send_private(sock, users_available)

	def room_delete(self, sock, msg):
		"""
		Delete room method
		"""
		if self.users[self.clients[sock][1]]["status"] != self.status[1]:
			self.send_private(sock, messages["rooms"]["must_in_room"])
		else:
			room_name = self.users[self.clients[sock][1]]["room"]
			if self.rooms[room_name]["admin"] != self.clients[sock][1]:
				self.send_private(sock, messages["rooms"]["not_admin"])
			else:
				# If admin deleted the room, it will kick all users under the rooms
				self.send_room(sock, messages["rooms"]["room_delete"])
				for user in self.rooms[room_name]["users"]:
					self.users[user]["status"] = self.status[0]
					self.users[user].pop("room")
					if self.rooms[room_name]["admin"] != user:
						self.send_prompt(self.users[user]["sock"], msg)
				self.rooms.pop(room_name)
				print "<{} delete room {}>".format(self.clients[sock][1], room_name)

	def room_exit(self, sock, msg):
		"""
		Exit room method
		"""
		if self.users[self.clients[sock][1]]["status"] != self.status[1]:
			self.send_private(sock, messages["rooms"]["must_in_room"])
		else:
			room_name = self.users[self.clients[sock][1]]["room"]
			# Check if admin
			if self.rooms[room_name]["admin"] == self.clients[sock][1]:
				# If there is only admin, it will be deleting the room
				if len(self.rooms[room_name]["users"]) == 1:
					self.room_delete(sock, msg)
				else:
					# if there are more than 1 users in the room, the second user will be the admin
					message = "\n<< <{}> {} left the room, new admin is {}\n".format(bot_name, self.clients[sock][1], self.rooms[room_name]["users"][1])
					self.send_room(sock, message)
					self.send_room(sock, "room {}>> ".format(room_name))
					del self.rooms[room_name]["users"][0]
					self.rooms[room_name]["admin"] = self.rooms[room_name]["users"][0]

					self.users[self.clients[sock][1]]["status"] = self.status[0]
					self.users[self.clients[sock][1]].pop("room")
			else:
				message = "\n<< <{}> {} left the room\n".format(bot_name, self.clients[sock][1])
				self.send_room(sock, message)
				self.send_room(sock, "room {}>> ".format(room_name))
				user_index = self.rooms[room_name]["users"].index(self.clients[sock][1])
				del self.rooms[room_name]["users"][user_index]
				self.users[self.clients[sock][1]]["status"] = self.status[0]
				self.users[self.clients[sock][1]].pop("room")
			
			print "<{} left room {}>".format(self.clients[sock][1], room_name)

	def room_ban(self, sock, msg):
		"""
		Ban a user.
		User can be banned by a username.
		User can be banned although he/she is not in the room
		"""
		if self.users[self.clients[sock][1]]["status"] != self.status[1]:
			self.send_private(sock, messages["rooms"]["must_in_room"])
		else:
			room_name = self.users[self.clients[sock][1]]["room"]
			if self.rooms[room_name]["admin"] != self.clients[sock][1]:
				self.send_private(sock, messages["rooms"]["not_admin"])
			else:
				if len(msg.split()) < 3:
					self.send_private(sock, messages["rooms"]["no_user_ban"])
				else:
					user_to_ban = msg.split()[2]
					if user_to_ban not in self.users:
						self.send_private(sock, messages["user_not_exist"])
					else:
						if user_to_ban == self.clients[sock][1]:
							self.send_private(sock, messages["rooms"]["no_ban_self"])
						else:
							if user_to_ban in self.rooms[room_name]["banned"]:
								self.send_private(sock, messages["rooms"]["already_banned"])
							else:
								if user_to_ban in self.rooms[room_name]["users"]:
									user_index = self.rooms[room_name]["users"].index(user_to_ban)
									del self.rooms[room_name]["users"][user_index]

									self.users[user_to_ban]["status"] = self.status[0]
									self.users[user_to_ban].pop("room")

								self.rooms[room_name]["banned"].append(user_to_ban)

								message = "\n<< <{}> {} is banned from this room.\n".format(bot_name, user_to_ban)
								self.send_room(sock, message)
								self.send_room(sock, "room {}>> ".format(room_name))
								message_banned = "\n<< <{}> You are banned from the room {}.\n".format(bot_name, room_name)
								self.send_private(self.users[user_to_ban]["sock"], message_banned)
								self.send_prompt(self.users[user_to_ban]["sock"], msg)

								print "<{} banned {} from room {}>".format(self.clients[sock][1], user_to_ban, room_name)

	def room_unban(self, sock, msg):
		"""
		Unban User Method
		"""
		if self.users[self.clients[sock][1]]["status"] != self.status[1]:
			self.send_private(sock, messages["rooms"]["must_in_room"])
		else:
			room_name = self.users[self.clients[sock][1]]["room"]
			if self.rooms[room_name]["admin"] != self.clients[sock][1]:
				self.send_private(sock, messages["rooms"]["not_admin"])
			else:
				if len(msg.split()) < 3:
					self.send_private(sock, messages["rooms"]["no_user_unban"])
				else:
					user_to_unban = msg.split()[2]
					if user_to_unban == self.clients[sock][1]:
						self.send_private(sock, messages["rooms"]["no_self_unban"])
					else:
						if user_to_unban not in self.rooms[room_name]["banned"]:
							self.send_private(sock, messages["rooms"]["user_not_banned"])
						else:
							user_index = self.rooms[room_name]["banned"].index(user_to_unban)
							del self.rooms[room_name]["banned"][user_index]

							message = "\n<< <{}> The Admin have already granted the access to you room {}\n".format(bot_name, room_name)
							self.send_private(self.users[user_to_unban]["sock"], message)

	def room_kick(self, sock, msg):
		"""
		Kick User
		"""
		if self.users[self.clients[sock][1]]["status"] != self.status[1]:
			self.send_private(sock, messages["rooms"]["must_in_room"])
		else:
			room_name = self.users[self.clients[sock][1]]["room"]
			if self.rooms[room_name]["admin"] != self.clients[sock][1]:
				self.send_private(sock, messages["rooms"]["not_admin"])
			else:
				if len(msg.split()) < 3:
					self.send_private(sock, messages["rooms"]["choose_user_kick"])
				else:
					user_to_kicked = msg.split()[2]
					if user_to_kicked == self.clients[sock][1]:
						self.send_private(sock, messages["rooms"]["no_self_kick"])
					else:
						# Check if user is in the room, cannot kick if there is no related username in the room
						if user_to_kicked not in self.rooms[room_name]["users"]:
							self.send_private(sock, messages["rooms"]["user_not_exist"])
						else:
							user_index = self.rooms[room_name]["users"].index(user_to_kicked)
							del self.rooms[room_name]["users"][user_index]

							self.users[user_to_kicked]["status"] = self.status[0]
							self.users[user_to_kicked].pop("room")

							message = "\n<< <{}> Admin kick {} from room.\n".format(bot_name, user_to_kicked)
							self.send_room(sock, message)
							self.send_room(sock, "room {}>> ".format(room_name))

							notify_kick = "\n<< <{}> You have been kicked from room {}.\n".format(bot_name, room_name)
							self.send_private(self.users[user_to_kicked]["sock"], notify_kick)
							self.send_prompt(self.users[user_to_kicked]["sock"], msg)

							print "<{} kick {} from room {}>".format(self.clients[sock][1], user_to_kicked, room_name)
	###########

	# PRIVATE
	def private_method(self, sock, msg):
		"""
		Handle the private command
		"""
		if len(msg.split()) == 1:
			self.send_private(sock, messages["private"]["no_sub"])
		else:
			cmd = msg.split()[1]
			if cmd in self.private_commands:
				self.private_commands[cmd](sock, msg)
			else:
				self.send_private(sock, messages["command_not_detect"])

	def private_chat(self, sock, msg):
		"""
		Private chat method
		"""
		# Must in same room if you want to invite a person to a private chat
		if self.users[self.clients[sock][1]]["status"] != self.status[1]:
			self.send_private(sock, messages["rooms"]["must_in_room"])
		else:
			if self.users[self.clients[sock][1]]["status"] == self.status[2]:
				self.send_private(sock, messages["private"]["in_private_mode"])
			else:
				if len(msg.split()) != 3:
					self.send_private(sock, messages["private"]["choose_user"])  
				else:
					room_name = self.users[self.clients[sock][1]]["room"]
					user_to_chat = msg.split()[2]

					if user_to_chat == self.clients[sock][1]:
						self.send_private(sock, messages["private"]["no_self_chat"])
					else:
						if user_to_chat not in self.rooms[room_name]["users"]:
							self.send_private(sock, messages["rooms"]["user_not_exist"])
						else:
							# Exit the room and set user mode to private mode
							self.before_status[self.clients[sock][1]] = {}
							self.before_status[self.clients[sock][1]]["status"] = self.users[self.clients[sock][1]]["status"]
							if self.users[self.clients[sock][1]]["status"] == self.status[1]:
								self.before_status[self.clients[sock][1]]["room"] = room_name
								self.room_exit(sock, msg)

							self.users[self.clients[sock][1]]["status"] = self.status[2]

							self.private_status[self.clients[sock][1]] = {}
							self.private_status[self.clients[sock][1]]["friend"] = user_to_chat
							self.private_status[self.clients[sock][1]]["confirmed"] = False

							# Add message to array if invited user didn't confirm the private session
							# Messages will be delivered after invited user confirm the private session
							if user_to_chat not in self.private_messages:
								self.private_messages[user_to_chat] = {}
								if self.clients[sock][1] not in self.private_messages[user_to_chat]:
									self.private_messages[user_to_chat][self.clients[sock][1]] = []

							# Notify an invited user that there is an invitation
							notify_private = "\n<< <{}> You get a private message from {}, type /private confirm {} to enter private session\n".format(bot_name, self.clients[sock][1], self.clients[sock][1])
							self.send_private(self.users[user_to_chat]["sock"], notify_private)
							self.send_prompt(self.users[user_to_chat]["sock"], msg)

	def private_confirm(self, sock, msg):
		"""
		Confirm private session
		"""
		if self.clients[sock][1] not in self.private_messages:
			self.send_private(sock, messages["private"]["no_invite"])
		else:
			if len(msg.split()) != 3:
				self.send_private(sock, messages["private"]["choose_user"])
			else:
				user_to_confirm = msg.split()[2]
				if user_to_confirm == self.clients[sock][1]:
					self.send_private(sock, messages["private"]["no_self_chat"])
				else:
					if user_to_confirm not in self.private_status:
						self.send_private(sock, messages["private"]["no_invite"])
					else:
						if self.private_status[user_to_confirm]["friend"] != self.clients[sock][1]:
							self.send_private(sock, messages["private"]["no_invite"])
						else:
							# Set Confirmation
							self.private_status[self.clients[sock][1]] = {}
							self.private_status[self.clients[sock][1]]["friend"] = user_to_confirm
							self.private_status[self.clients[sock][1]]["confirmed"] = True

							self.private_status[user_to_confirm]["confirmed"] = True

							self.before_status[self.clients[sock][1]] = {}
							self.before_status[self.clients[sock][1]]["status"] = self.users[self.clients[sock][1]]["status"]
							# Exit from room if user is in the room
							if self.users[self.clients[sock][1]]["status"] == self.status[1]:
								room_name = self.users[self.clients[sock][1]]["room"]
								self.before_status[self.clients[sock][1]]["room"] = room_name
								self.room_exit(sock, msg)

							self.users[self.clients[sock][1]]["status"] = self.status[2]

							# Receive all pending message related to private session
							for mess in self.private_messages[self.clients[sock][1]][user_to_confirm]:
								pm = "<< <{}> {}\n".format(user_to_confirm, mess)
								self.send_private(sock, pm)

							self.private_messages[self.clients[sock][1]].pop(user_to_confirm)


	def private_help(self, sock, msg):
		self.send_private(sock, messages["private"]["help_message"])

	def private_exit(self, sock, msg):
		"""
		Exit from Private Session
		"""
		if self.users[self.clients[sock][1]]["status"] != self.status[2]:
			self.send_private(sock, messages["private"]["not_in_private"])
		else:
			if self.private_status[self.clients[sock][1]]["friend"] in self.private_status:
				friend_name = self.private_status[self.clients[sock][1]]["friend"]

				# Notify to other user for leaving a private session
				msg_left = "\n<< <{}> {} left a private chat.\n".format(bot_name, self.clients[sock][1])
				self.send_private(self.users[friend_name]["sock"], msg_left)
				self.private_status.pop(self.private_status[self.clients[sock][1]]["friend"])

				# If the user is in the room before, he/she will be joining the room again
				self.users[friend_name]["status"] = self.before_status[friend_name]["status"]
				if self.users[friend_name]["status"] == self.status[1]:
					room_name = self.before_status[friend_name]["room"]
					if room_name in self.rooms:
						self.users[friend_name]["status"] = self.status[0]
						join_msg = "/room join {}".format(room_name)
						self.room_join(self.users[friend_name]["sock"], join_msg)
						self.send_prompt(self.users[friend_name]["sock"], msg)
					else:
						self.users[friend_name]["status"] = self.status[0]
				self.before_status.pop(friend_name)

			self.private_status.pop(self.clients[sock][1])
			self.users[self.clients[sock][1]]["status"] = self.before_status[self.clients[sock][1]]["status"]
			if self.users[self.clients[sock][1]]["status"] == self.status[1]:
				room_name = self.before_status[self.clients[sock][1]]["room"]
				if room_name in self.rooms:
					self.users[self.clients[sock][1]]["status"] = self.status[0]
					join_msg = "/room join {}".format(room_name)
					self.room_join(self.users[self.clients[sock][1]]["sock"], join_msg)
				else:
					self.users[self.clients[sock][1]]["status"] = self.status[0]
			self.before_status.pop(self.clients[sock][1])

	######################

	# RUN!
	def run(self):
		while True:
			read_sockets, write_sockets, error_sockets = select.select(self.CONNECTION_LIST, [], [])
			for sock in read_sockets:
				if sock == self.server_socket:
					self.new_client()
				else:
					try:
						data = sock.recv(self.RECV_BUFFER)
						if data:
							self.handle_message(sock, data)
					except socket.error, err:
						sock.close()
						self.CONNECTION_LIST.remove(sock)
						continue
			# We need sleep here, so the application won't eat high cpu and memory resources when doing forever loop
			time.sleep(0.2)

		self.server_socket.close()


if __name__ == "__main__":
	chat = Chat()
	chat.run()

