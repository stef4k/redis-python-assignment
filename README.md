# Redis-Assignment
Assignment for the course Big Data Management Systems of 4th year spring semester and specifically Redis

## Assignment description

Firstly create by using any type of database:

1. A database of users (userID, name, age, gender, email)
2. A database of meetings (meetingID, title, description, isPublic, audience) with meeting instances (meetingID, orderID, fromdatetime, todatetime) 
3. A database of eventsLog (event_id, userID, event_type, timestamp)

Then create the following functions storing the data in a Redis Server:
* Function: a meeting instance becomes active
* Function: a user can join an active meeting instance – if allowed, his email is in audience*
* Function: a user can leave a meeting*
* Function: show meeting’s current participants
* Function: show active meetings
* Function: when a meeting ends, all participants leave*
* Function: a user can post a chat message*
* Function: show meeting’s chat messages in chronological order
* Function: show for each active meeting when (timestamp) current participants joined
* Function: show for an active meeting and a user his/her chat message

Note: A meeting has audience or it is public. Also, functions with a star in the end, must also insert an event in the database eventsLog.

## Running Application
1. Open the `redis-server.exe` window-server
2. Run the command `python main.py` from cmd
3. Choose from the displayed menu the corresponding function
