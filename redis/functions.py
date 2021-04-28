# importing the necessary libraries
from tinydb import TinyDB, Query
import redis
import datetime
from datetime import datetime as datetime2
import time
import pprint


# connect to redis server
ip_address = '192.168.1.3'
client = redis.Redis(host = ip_address, port = '6379')


# connect to database files
db_users = TinyDB('users.json')
db_meetings = TinyDB('meetings.json')
db_meeting_instances = TinyDB('meeting_instances.json')
db_eventsLog = TinyDB('eventsLog.json')

# global variables
eventID = 10 #global variable for eventID in database eventsLog


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
        start_date = datetime.datetime.strptime(instance['fromdatetime'], '%Y-%m-%d %H:%M:%S.%f')
        finish_date = datetime.datetime.strptime(instance['todatetime'], '%Y-%m-%d %H:%M:%S.%f')
        # date now must be between the start and end date of the meeting instance
        if ((start_date < datetime.datetime.now()) & (finish_date > datetime.datetime.now() )):
            # add the meetingID to the redis set  @active
            client.sadd('active', instance['meetingID'])


def show_active_meetings():
    """   
    Function that prints the information of active meetings. It iterates through
    the redis set @active and for each different meetingID value there, the information
    of the particular meetingID is printed from the database @meetings
    Returns: -
    """
    query = Query()
    # iterate through all active meetingIDS
    for meeting in client.smembers('active'):
        # print for each meetingID the extended information
        pprint.pprint(db_meetings.search(query.meetingID == meeting.decode('utf-8')))


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
    list_item = current_meetingID + '_message_' + str(userID) + '_' + str(timestamp)
    # append item to list
    client.rpush(list_name, list_item)
    # create hashes of message and userID for item
    client.hset(list_item, 'message', message)
    client.hset(list_item, 'userID', userID)
    # insert action to eventsLog database
    db_eventsLog.insert({'event_id': get_eventID(), 'userID': userID,
                         'event_type': 4, 'timestamp': timestamp})


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
    print('Chat of meeting '+ meetingID + ' :')
    for message  in client.lrange(meetingID+'_messages', 0 , -1):
        message_name = message.decode('utf-8')
        message_sender = client.hget(message_name, 'userID').decode('utf-8')
        message_text = client.hget(message_name, 'message').decode('utf-8')
        print (message_sender + ': ' + message_text)

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
    print('Messages of user '+ str(userID) + ' in meeting ' + meetingID +':')
    for message  in client.lrange(meetingID+'_messages', 0 , -1):
        message_name = message.decode('utf-8')
        message_sender = client.hget(message_name, 'userID').decode('utf-8')
        if (int(message_sender) == userID):
            message_text = client.hget(message_name, 'message').decode('utf-8')
            timestamp = message_name[message_name.rindex('_')+1:]
            date_timestamp = datetime2.fromtimestamp(int(timestamp))
            print (str(date_timestamp.time()) + ' : ' + message_text)


def get_eventID():
    """
    Function that returns a unique eventID used in database eventsLog
    Everytime it is called, it increases by 1 and returns a unique eventID.

    Returns: integer
    """
    global eventID
    eventID = eventID + 1
    return(eventID)




# test functions
activate_meetings()
#show_active_meetings()
#post_message('100', 4,'Hello class')
#time.sleep(1.4)
#post_message('100', 1,'My name is Stef')
#show_chat('100')
show_user_chat('100', 1)

# close connection to database files
db_users.close()
db_meetings.close()
db_meeting_instances.close()
db_eventsLog.close()