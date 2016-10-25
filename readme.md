# ChitChat

Simple In Memory Chat Server in Python. You can have group chat and private chat with this chat system. No need a database server.

## Run the server
- Open chat.py, set the host and port (default bind to 0.0.0.0 port 5000).
- Because we only use socket and select library, we don't need to install another dependency.
```
$ python chat.py
<Starting Socket Server: 0.0.0.0:5000>
```

## Run the client
- You can use telnet to connect to the server
```
linx@crawler ~ $ telnet localhost 5000
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
===================== Welcome to the Chat Server ======================
================== You can have some chit chat here ===================
================ Chit chat with many people in the room ===============
==== Or you can have a private chat with a person in the same room ====
=======================================================================
<< <System Bot> Please Input Username:
```
### Rules
- No duplicate username in the server.
- No duplicate room name.
- Room admin is the one who creates the room.
- Admin can ban the user based on the username, although the username is not in the room.
- Admin can kick a user that exists in the room.
- You can have a private chat with the user in the same room.
- If you have a private session, you will leave the room.
- If a user confirm a private session, the user also will leave the room.
- If before the private session, the user is joined to a room. When the user exit from private session, he/she will be back to the room, unless the room is deleted.

### Problem to be solved
- Didn't get notified when a user suddenly disconnect from a server because error connection.

