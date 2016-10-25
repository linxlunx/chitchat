#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Linggar Primahastoko
# Email: x@linggar.asia

bot_name = "System Bot"

messages = {
	"welcome_message": "===================== Welcome to the Chat Server ======================\n"\
					   "================== You can have some chit chat here ===================\n"\
					   "================ Chit chat with many people in the room ===============\n"\
					   "==== Or you can have a private chat with a person in the same room ====\n"\
					   "=======================================================================\n",
	"input_username": "<< <{}> Please Input Username: ".format(bot_name),
	"duplicate_username": "<< <{}> Username has been registered, please choose another one: ".format(bot_name),
	"bye_message": "<< <{}> Nice to chat with you! Have a good day.\n".format(bot_name),
	"help_message": "You can list help command by using /help command.\n",
	"command_not_detect": "<< <{}> Command not detected, see /help.\n".format(bot_name),
	"help_list_message": "<< <{}> You can use these several commands.\n"\
						 "<< /help => Show this help message\n"\
						 "<< /private => private message with a user in the same room\n"\
						 "<< /quit => disconnect from chat server\n"\
						 "<< /room => create, list, delete room\n"\
						 "<< You can use /<command> help to see the specific command\n".format(bot_name),
	"rooms": {
		"no_sub": "<< <{}> Please type /room help to list all command\n".format(bot_name),
		"help_message": "<< <{}> /room command list\n"\
						"<< /room create <room_name> => Create room\n"\
						"<< /room help => List all commands under /room command\n"\
						"<< /room list => List active rooms\n"\
						"<< /room join <room_name> => Join a room\n"\
						"<< /room users => List users in room\n"\
						"<< /room delete => Delete a room (Admin Only)\n"\
						"<< /room exit => Exit from room (If the user is admin, the second user who join the room will be the admin)\n"\
						"<< /room ban <username> => Ban a user from room (Admin Only)\n"\
						"<< /room unban <username> => Unban a user from room (Admin Only)\n"\
						"<< /room kick <username> => Kick a user from room (Admin Only)\n".format(bot_name),
		"no_room_name": "<< <{}> Please write the room name!\n".format(bot_name),
		"room_exist": "<< <{}> Room is exist, please take another room name!\n".format(bot_name),
		"not_in_joined": "<< <{}> Cannot create room, you are in private chat or room mode!\n".format(bot_name),
		"room_not_exist": "<< <{}> Room is not exist, please choose the existing room!\n".format(bot_name),
		"no_room": "<< <{}> No available rooms for this time.\n".format(bot_name),
		"must_joined": "<< <{}> You must not in private mode or room mode, exit first.\n".format(bot_name),
		"must_in_room": "<< <{}> Enter the room first!\n".format(bot_name),
		"not_admin": "<< <{}> Cannot delete, you are not the admin!\n".format(bot_name),
		"room_delete": "\n<< <{}> Admin is deleting the room, force exit to all user!\n".format(bot_name),
		"no_user_ban": "\n<< <{}> Please choose user to be banned\n".format(bot_name),
		"no_user_unban": "\n<< <{}> Please choose user to be unbanned\n".format(bot_name),
		"no_ban_self": "<< <{}> You cannot ban yourself!\n".format(bot_name),
		"no_self_unban": "\n<< <{}> You cannot ban yourself, so why unban?\n".format(bot_name),
		"already_banned": "\n<< <{}> The user has been already_banned\n".format(bot_name),
		"user_not_banned": "\n<< <{}> This user is not exist in the banned list.\n".format(bot_name),
		"user_banned": "<< <{}> Cannot join, you are banned from this room.\n".format(bot_name),
		"notify_banned": "\n<< <{}> You are banned from the room\n".format(bot_name),
		"choose_user_kick": "<< <{}> Please choose user to be kicked\n".format(bot_name),
		"no_self_kick": "<< <{}> You cannot kick yourself!\n".format(bot_name),
		"user_not_exist": "<< <{}> Cannot find this kind of username in this room.\n".format(bot_name),
	},
	"private": {
		"no_sub": "<< <{}> Please type /private help to list all command.\n".format(bot_name),
		"help_message": "<< <{}> /private command list\n"\
						"<< /private chat <username> => Create a private session with a user (only if you are in the same room)\n"\
						"<< /private confirm <username> => Confirm a private user that invites you to have a private session\n"\
						"<< /private help => List all command under /private command\n"\
						"<< /private exit => Exit from private session\n".format(bot_name),
		"in_private_mode": "<< <{}> You have to exit private mode first to chat with another people.\n".format(bot_name),
		"choose_user": "<< <{}> Please choose the user in the room to have a private chat.\n".format(bot_name),
		"no_invite": "<< <{}> No invitation in private chat, maybe the user wait too long and left the session.\n".format(bot_name),
		"choose_user": "<< <{}> Choose user that invite you to his/her private session.\n".format(bot_name),
		"no_self_chat": "<< <{}> You cannot have a monologue here.\n".format(bot_name),
		"not_in_private": "<< <{}> You are not in private mode.\n".format(bot_name),
	},
	"user_no_exist": "\n<< <{}> User is not exist\n".format(bot_name),
}