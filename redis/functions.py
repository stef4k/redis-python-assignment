# importing the necessary libraries
from tinydb import TinyDB, Query
import redis
import datetime
from datetime import datetime as datetime2

# connect to redis server
# ip_address = '192.168.1.3'
ip_address = '127.0.0.1'
client = redis.Redis(host=ip_address, port='6379')


# connect to database files
db_users = TinyDB('users.json')
db_meetings = TinyDB('meetings.json')
db_meeting_instances = TinyDB('meeting_instances.json')
db_eventsLog = TinyDB('eventsLog.json')

# global variables
eventID = 10  # global variable for eventID in database eventsLog


def activate_meetings():
    """
    Function that checks all the meeting instances from the database table 
    meeting instances and activates the ones that should be live at the 
    particular moment (meaning the current date is before the end of the instance 
    and after the start of it). Meeting instances are being activated by
    saving the meetingID inside a set in redis named @active

    Returns: -
    """
    # iterate through all meeting instances in database @meeting_instances
    for instance in db_meeting_instances:
        start_date = datetime.datetime.strptime(
            instance['fromdatetime'], '%Y-%m-%d %H:%M:%S.%f')
        finish_date = datetime.datetime.strptime(
            instance['todatetime'], '%Y-%m-%d %H:%M:%S.%f')
        # date now must be between the start and end date of the meeting instance
        if (start_date < datetime.datetime.now()) & (finish_date > datetime.datetime.now()):
            # add the meetingID to the redis set  @active
            client.sadd('active', instance['meetingID'])


def show_active_meetings():
    """   
    Function that prints the information of active meetings. It iterates through
    the redis set @active and for each different meetingID value there, the information
    of the particular meetingID is printed from the database @meetings
    Returns: -
    """
    # iterate through all active meetingIDS
    for meeting in client.smembers('active'):
        meetingID = meeting.decode('utf-8')
        # print for each meetingID the extended information
        print(meetingID + '| ' + get_meeting_title(meetingID) +
              ': ' + get_meeting_description(meetingID))


def join_meeting(meeting_id, user_id):
    if client.sismember('active', meeting_id):
        participants = meeting_id + '_participants'
        # audience = get_meeting_audience(meeting_id)
        if not get_meeting_publicity(meeting_id):
            if int(user_id) in get_meeting_audience(meeting_id):
                if not client.hexists(participants, user_id):
                    timestamp = round(datetime2.timestamp(datetime2.now()))
                    client.hset(participants, user_id, timestamp)
                    print(get_user_name(user_id), 'just joined', get_meeting_title(meeting_id) + '!')

                    # update event_log
                    insert_eventLog(user_id, 1, timestamp)
                else:
                    print(get_user_name(user_id), 'can not double-join', get_meeting_title(meeting_id) + '.')
                return
            print(get_user_name(user_id), 'is not in the audience of', get_meeting_title(meeting_id) + '.')
            return
        else:
            if not client.hexists(participants, user_id):
                client.hset(participants, user_id, 1)
                print(get_user_name(user_id), 'just joined', get_meeting_title(meeting_id) + '!')
            else:
                print(get_user_name(user_id), 'can not double-join', get_meeting_title(meeting_id) + '.')
            return
    print(get_meeting_title(meeting_id), 'is not an active meeting.')

# to be corrected
def show_meeting_participants(meeting_id):
    meeting = get_meeting_title(meeting_id)
    participants_naming = (meeting + '_participants').encode('utf-8')
    client.hset('meetings', meeting, participants_naming)

    participants_naming = (meeting + '_participants').encode('utf-8')
    audience = get_meeting_audience(meeting_id)
    if audience:
        for user in audience:
            client.sadd(participants_naming, get_user_name(user).encode('utf-8'))

    client.sadd(participants_naming, 'No participants')

    for m in client.hkeys('meetings'):
        print(m.decode('utf-8')+':',
              (' | '.join([name.decode('utf-8') for name in client.smembers(client.hget('meetings', m)) ] ) ) )


def end_meeting():

    pass


def post_message(current_meetingID, userID, message):
    """
    Function that represents a message posting on a meeting. Practically, this 
    function creates or appends to a redis list called 'meetingID_messages' 
    (where meetingID is the meetingID number) a string called 'meetingID_messages_userID_timestamp'
    (where meetingID is the meetingID number, userID is the user's ID and timestamp 
    is the current timestamp) Also a hash is created with the same name 
    @meetingID_messages_timestamp which contains the fields: message  and userID which contain the particular
    message abd userID that sent the message

    Parameters
    ----------
    current_meetingID : string
    userID : int
    message : string, the message sent

    Returns: -

    """
    # unique current timestamp
    timestamp = round(datetime2.timestamp(datetime2.now()))
    # creating the names of the list and name of the message
    list_name = current_meetingID + '_messages'
    list_item = current_meetingID + '_message_' + \
        str(userID) + '_' + str(timestamp)
    # append item to list
    client.rpush(list_name, list_item)
    # create hashes of message and userID for item
    client.hset(list_item, 'message', message)
    client.hset(list_item, 'userID', userID)
    # insert action to eventsLog database
    insert_eventLog(userID, 4, timestamp)


def show_chat(meetingID):
    """
    Functions that prints all the messages of a particular meeting @meetingID
    in a chronological order. This functions iterates through the redis list
    @meetingID_messages and after that for each item list which is also stored 
    as a hash the sender user's ID and message are printed.

    Parameters
    ----------
    meetingID : string

    Returns: -
    """
    print('Chat of meeting ' + meetingID +
          ' :' + '\n----------------------------------------------')
    for message in client.lrange(meetingID+'_messages', 0, -1):
        message_name = message.decode('utf-8')
        message_sender = client.hget(message_name, 'userID').decode('utf-8')
        message_text = client.hget(message_name, 'message').decode('utf-8')
        print(message_sender + ': ' + message_text)
    print('----------------------------------------------')


def show_user_chat(meetingID, userID):
    """
    Function that prints for a particular meeting and user, all of his/her 
    chat meesages in that meeting. It iterates through the list of messages 
    for that particular meeting. For each message, it checks if it was sent by
    the particular user and if so, it prints the time together with the message.

    Parameters
    ----------
    meetingID : string
    userID : int

    Returns: - 
    """
    print('Messages of user ' + str(userID) + ' in meeting ' +
          meetingID + ':' + '\n----------------------------------------------')
    for message in client.lrange(meetingID+'_messages', 0, -1):
        message_name = message.decode('utf-8')
        message_sender = client.hget(message_name, 'userID').decode('utf-8')
        if (int(message_sender) == userID):
            message_text = client.hget(message_name, 'message').decode('utf-8')
            timestamp = message_name[message_name.rindex('_')+1:]
            date_timestamp = datetime2.fromtimestamp(int(timestamp))
            print(str(date_timestamp.time()) + ' : ' + message_text)
    print('----------------------------------------------')


def get_eventID():
    """
    Function that returns a unique eventID used in database eventsLog
    Everytime it is called, it increases by 1 and returns a unique eventID.

    Returns: integer
    """
    global eventID
    eventID = eventID + 1
    return(eventID)


def get_meeting_title(meetingID):
    """
    Function that finds the title of a particular @meetingID inside the database
    of meetings

    Parameters
    ----------
    meetingID : string
    Returns: a string of the title of the particular meeting

    """
    query = Query()
    result = (db_meetings.search(query.meetingID == meetingID))
    title = [r['title'] for r in result]
    return ''.join(title)


def get_meeting_audience(meeting_id):
    query = Query()
    result = (db_meetings.search(query.meetingID == meeting_id))
    return result[0]['audience']


def get_meeting_publicity(meeting_id):
    query = Query()
    result = (db_meetings.search(query.meetingID == meeting_id))
    return result[0]['isPublic']


def get_user_name(userID):
    query = Query()
    result = db_users.search(query['userID'] == str(userID))
    return result[0]['name']


def get_meeting_description(meetingID):
    """
    Function that finds the description of a particular @meetingID inside the database
    of meetings

    Parameters
    ----------
    meetingID : string

    Returns: a string of the description of the particular meeting
    """
    query = Query()
    result = (db_meetings.search(query.meetingID == meetingID))
    description = [r['description'] for r in result]
    return (''.join(description))


def insert_eventLog(userID, event_type, timestamp):
    """
    Function that inserts in the database @eventsLog a particular event
    from a particular user @userID, of a particular @event_type and the particular
    time it happened

    Parameters
    ----------
    userID : int 
    event_type : int , 1 for user joining a meeting, 2 for user leaving a meeting,
                3 for a meeting ending, 4 for a user posting a message

    timestamp : int

    Returns: - 

    """
    db_eventsLog.insert({'event_id': get_eventID(), 'userID': userID,
                         'event_type': event_type, 'timestamp': timestamp})


# Quick test of functions
activate_meetings()
# show_active_meetings()

# User joins meeting
join_meeting('100', 2)
join_meeting('100', 4)
join_meeting('100', 1)
join_meeting('200', 5)

# Show participants of every meeting
# print('---'*15, '\nParticipants of an active meeting:')
# show_meeting_participants('200')
# print('---'*15+'\n')

# Users posts messages
post_message('100', 1, 'Hello')
post_message('100', 3, 'Hello professor')
# time.sleep(1)
# post_message('100', 1, 'Its a me!')
# time.sleep(0.5)
# post_message('100', 1, 'We are good')

# Shows chat of a specific meeting
show_chat('100')

# Shows all messages posted by a single user to a specific meeting
show_user_chat('100', 1)

# print(get_meeting_title('100'))

# close connection to database files
client.flushall()
db_users.close()
db_meetings.close()
db_meeting_instances.close()
db_eventsLog.close()
