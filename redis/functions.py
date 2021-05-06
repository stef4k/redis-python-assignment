# importing the necessary libraries
from tinydb import TinyDB, Query
import redis
import datetime
from datetime import datetime as datetime2
import time
import os

# connect to redis server
ip_address = '127.0.0.1'
client = redis.Redis(host=ip_address, port='6379')


# check if databases exist
if not os.path.exists('users.json'):
    # create database
    exec(open("database.py").read())
else:
    # connect to database files
    db_users = TinyDB('users.json')
    db_meetings = TinyDB('meetings.json')
    db_meeting_instances = TinyDB('meeting_instances.json')
    db_eventsLog = TinyDB('eventsLog.json')


# global variables
eventID = 7  # global variable for eventID in database eventsLog


def activate_meeting(meetingID):
    """
    Function that checks the particular meeting instance from the database table 
    meeting instances and activates the meeting with @meetingID if it should be live at 
    particular moment (meaning the current date is before the end of the instance 
    and after the start of it). The meeting instances is being activated by
    saving the meetingID inside a set in redis named @active

    Returns: -
    """
    if not check_meeting_exists(meetingID):
        print('Meeting with ID ' + meetingID + ' not found in database')
    elif client.sismember('active', meetingID):
        print(get_meeting_title(meetingID) + ' meeting already active')
    else:
        # iterate through all meeting instances in database @meeting_instances
        for instance in db_meeting_instances:
            if instance['meetingID'] == meetingID:
                start_date = datetime.datetime.strptime(
                    instance['fromdatetime'], '%Y-%m-%d %H:%M:%S.%f')
                finish_date = datetime.datetime.strptime(
                    instance['todatetime'], '%Y-%m-%d %H:%M:%S.%f')
                # date now must be between the start and end date of the meeting instance
                if (start_date < datetime.datetime.now()) & (finish_date > datetime.datetime.now()):
                    # add the meetingID to the redis set  @active
                    client.sadd('active', instance['meetingID'])
                    print('Meeting instance for ' + get_meeting_title(meetingID) +
                          ' activated!')
                    return
        print('No meeting instance for ' + get_meeting_title(meetingID) + 
              ' planned for this moment')


def show_active_meetings():
    """   
    Function that prints the information of active meetings. It iterates through
    the redis set @active and for each different meetingID value there, the information
    of the particular meetingID is printed from the database @meetings.
    If active meetings are found in the set @active, a relative message is printed.
    Returns: -
    """
    # iterate through all active meetingIDS
    for meeting in client.smembers('active'):
        meetingID = meeting.decode('utf-8')
        # print for each meetingID the extended information
        print(meetingID + '| ' + get_meeting_title(meetingID) +
              ': ' + get_meeting_description(meetingID))
    if len(client.smembers('active')) == 0:
        print('No active meetings at the moment.')


def join_meeting(meeting_id, user_id):
    if client.sismember('active', meeting_id):
        participants = meeting_id + '_participants'
        # audience = get_meeting_audience(meeting_id)
        if not get_meeting_publicity(meeting_id):
            if user_id in get_meeting_audience(meeting_id):
                if not client.hexists(participants, user_id):
                    timestamp = round(datetime2.timestamp(datetime2.now()))
                    client.hset(participants, user_id, timestamp)
                    print('{user} just joined {meeting}!'
                          .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))

                    # update event log
                    insert_eventLog(user_id, 1, timestamp)
                else:
                    print(get_user_name(user_id), '{user} can not double-join {meeting}.'
                          .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))
                return
            print('{user} is not in the audience of {meeting}.'
                  .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))
            return
        else:
            if not client.hexists(participants, user_id):
                timestamp = round(datetime2.timestamp(datetime2.now()))
                client.hset(participants, user_id, timestamp)
                print('{user} just joined {meeting}!'
                      .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))

                # update event log
                insert_eventLog(user_id, 1, timestamp)
            else:
                print('{user} is already participating at {meeting}.'
                      .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))
            return
    print(meeting_id + ' {meeting} is not an active meeting.'.format(meeting=get_meeting_title(meeting_id), ))


def leave_meeting(meeting_id, user_id):
    if client.sismember('active', meeting_id):
        if client.hexists(meeting_id + '_participants', user_id):
            client.hdel(meeting_id + '_participants', user_id)

            # update event log
            timestamp = round(datetime2.timestamp(datetime2.now()))
            insert_eventLog(user_id, 2, timestamp)
            print('{user} just left {meeting}.'
                  .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))

        else:
            print('{user} is not currently participating at {meeting}.'
                  .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))
        return
    print(meeting_id + ' {meeting} is not an active meeting.'.format(meeting=get_meeting_title(meeting_id)))


def show_meeting_current_participants(meeting_id):
    participants = meeting_id + '_participants'
    if client.sismember('active', meeting_id):
        if client.hlen(participants) != 0:
            print('Participants of {meeting_title}:'.format(meeting_title=get_meeting_title(meeting_id)), end='| ')
            for user in client.hkeys(participants):
                print('#'+user.decode('utf-8'), get_user_name(user.decode('utf-8')), end=' | ')
            print()
        else:
            print('Nobody participates at {meeting_title} yet.'.format(meeting_title=get_meeting_title(meeting_id)))
        return
    print(meeting_id + ' {meeting} is not an active meeting.'.format(meeting=get_meeting_title(meeting_id)))


def show_join_timestamp():
    if client.scard('active') != 0:
        for meeting in client.smembers('active'):
            participants = meeting.decode('utf-8') + '_participants'
            print('{meeting} has {length} participants.'
                  .format(meeting=get_meeting_title(meeting.decode('utf-8')), length=client.hlen(participants)))

            if client.hlen(participants) != 0:
                print('\n'.join(
                    ['#{user_id} {user_name}: joined at {timestamp}'
                        .format(user_id=user.decode('utf-8'),
                                user_name=get_user_name(user.decode('utf-8')),
                                timestamp=datetime2.fromtimestamp(int(client.hget(participants, user).decode('utf-8')))
                                )
                     for user in client.hkeys(participants)
                     ]))
            print()
        return

    print('There are no active meetings at the moment.')


def end_meeting(meeting_id):
    if client.sismember('active', meeting_id):
        participants = meeting_id + '_participants'
        if client.hlen(participants) != 0:
            for user in client.hkeys(participants).copy():
                # update event log for the participants
                timestamp = round(datetime2.timestamp(datetime2.now()))
                insert_eventLog(user.decode('utf-8'), 3, timestamp)
                client.hdel(participants, user)

        # update event log for the meeting
        timestamp = round(datetime2.timestamp(datetime2.now()))
        insert_eventLog(3, None, timestamp)
        client.srem('active', meeting_id)
        print('{meeting} just ended.'.format(meeting=get_meeting_title(meeting_id)))
        return
    print(meeting_id + ' ' + get_meeting_title(meeting_id), 'is not active at the moment.')


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
    userID : string
    message : string, the message sent

    Returns: -

    """
    if not client.hget(current_meetingID+'_participants', userID):
        print('User ' + str(userID) + ' has not joined meeting of ' +
              get_meeting_title(current_meetingID))
    else:
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
        print('Successfully posted message')


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
    if check_meeting_exists(meetingID):
        print('Chat of meeting ' + get_meeting_title(meetingID) +
              ' :')
        for message in client.lrange(meetingID+'_messages', 0, -1):
            message_name = message.decode('utf-8')
            message_sender = client.hget(message_name, 'userID').decode('utf-8')
            message_text = client.hget(message_name, 'message').decode('utf-8')
            print(get_user_name(message_sender) + ': ' + message_text)
    else:
        print('Meeting with ID ' + meetingID + ' not found in database')


def show_user_chat(meetingID, userID):
    """
    Function that prints for a particular meeting and user, all of his/her 
    chat meesages in that meeting. It iterates through the list of messages 
    for that particular meeting. For each message, it checks if it was sent by
    the particular user and if so, it prints the time together with the message.

    Parameters
    ----------
    meetingID : string
    userID : string

    Returns: - 
    """
    # meeting is not active
    if not client.hget(meetingID+'_participants', userID):
        print('User ' + str(userID) + ' has not joined meeting of ' +
              get_meeting_title(meetingID))
    else:
        print('Messages of user ' + get_user_name(userID) + ' in meeting ' +
              get_meeting_title(meetingID) + ':')
        for message in client.lrange(meetingID+'_messages', 0, -1):
            message_name = message.decode('utf-8')
            message_sender = client.hget(message_name, 'userID').decode('utf-8')
            if (message_sender == userID):
                message_text = client.hget(message_name, 'message').decode('utf-8')
                timestamp = message_name[message_name.rindex('_')+1:]
                date_timestamp = datetime2.fromtimestamp(int(timestamp))
                print(str(date_timestamp.time()) + ' : ' + message_text)


def get_eventID():
    """
    Function that returns a unique eventID used in database eventsLog
    Everytime it is called, it increases by 1 and returns a unique eventID.

    Returns: integer
    """
    global eventID
    eventID = eventID + 1
    return (eventID)


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
    return ''.join(description)


def insert_eventLog(userID, event_type, timestamp):
    """
    Function that inserts in the database @eventsLog a particular event
    from a particular user @userID, of a particular @event_type and the particular
    time it happened

    Parameters
    ----------
    userID : string 
    event_type : int , 1 for user joining a meeting, 2 for user leaving a meeting,
                3 for a meeting ending, 4 for a user posting a message

    timestamp : int

    Returns: - 

    """
    db_eventsLog.insert({'event_id': get_eventID(), 'userID': userID,
                         'event_type': event_type, 'timestamp': timestamp})


def check_meeting_active(meetingID):
    """
    Function that checks if the meeting with @meetingID is active (meaning is
    inside the redis set @active). Returns true if meeting is active

    Parameters
    ----------
    meetingID : string

    Returns: boolean
    """
    if client.sismember('active', meetingID):
        return True
    else:
        return False
    

    

def check_meeting_exists(meetingID):
    """
    Function that checks if a meeting with @meetingID exists in the database 
    meetings

    Parameters
    ----------
    meetingID : str that contains the meeting ID we want to check

    Returns: boolean

    """
    query = Query()
    result = db_meetings.search(query.meetingID == meetingID)
    if len(result) > 0:
        return True
    else:
        return False

def print_menu():
    """
    Functions that prints the menu of the meeting application

    Returns: -

    """
    print('---'*15)
    print('\t\tMenu:\nPress:\n1: Activate a meeting instance\n' +
      '2: Show active meetings\n3: Join an active meeting' +
      '\n4: Leave a meeting\n5: Show meetings current participants\n' +
      '6: End a meeting\n7: Post a chat message\n' +
      '8: Show the chat of a meeting\n9: Show for active meetings when current participants joined\n' +
      '10: Show the messages of a user in a active meeting\nX: Exit application')
    print('---'*15)

    
def print_all_users():
    """
    Function that prints all users IDs, name and age from db_users

    Returns: -
    """
    for user in db_users:
        print(user['userID'] + '| ' + user['name'] + ', ' + str(user['age'])\
              + ' years old')

def print_all_meetings():
    """
    Function that prints all meeting IDs, title and description from db_meetings

    Returns: -
    """
    for meeting in db_meetings:
        print(meeting['meetingID'] + '| ' + meeting['title'] + ': ' + 
              meeting['description'])


# Main
print('Welcome to Redis Meeting Application')
print_menu()
choice = input()

while (choice != 'X') & (choice != 'x'):
    if (choice == '1'):
        print('Press the meeting ID to activate:')
        print_all_meetings()
        meetingID = input()
        activate_meeting(meetingID)
    if (choice == '2'):
        print('\t\tActive Meetings:')
        show_active_meetings()
    elif (choice == '3'):
        print('Press the meeting ID to join:')
        show_active_meetings()
        meetingID = input()
        print('Press the user ID to join:')
        print_all_users()
        userID = input()
        join_meeting(meetingID, userID)
    elif (choice == '4'):
        print('Press the meeting ID to leave:')
        show_active_meetings()
        meetingID = input()
        if check_meeting_active(meetingID):
            print('Press the user ID to leave:')
            show_meeting_current_participants(meetingID)
            userID = input()
            leave_meeting(meetingID,userID)
        else:
            print('Meeting ' + meetingID + ' is not active')
    elif (choice == '5'):
        print('Press the meeting ID to show participants:')
        show_active_meetings()
        meetingID = input()
        show_meeting_current_participants(meetingID)
    elif (choice == '6'):
        print('Press the meeting ID to end:')
        show_active_meetings()
        meetingID = input()
        end_meeting(meetingID)
    elif (choice == '7'):
        print('Press the meeting ID to post message:')
        show_active_meetings()
        meetingID = input()
        if check_meeting_active(meetingID):
            print('Press the user ID to post a message:')
            show_meeting_current_participants(meetingID)
            userID = input()
            print('Type the message:')
            message = input()
            post_message(meetingID,userID,message)
        else:
            print('Meeting ' + meetingID + ' is not active')
    elif (choice == '8'):
        print('Press the meeting ID to show chat:')
        show_active_meetings()
        meetingID = input()
        show_chat(meetingID)
    elif (choice == '9'):
        show_join_timestamp()
    elif (choice == '10'):
        print('Press the meeting ID to show chat:')
        show_active_meetings()
        meetingID = input()
        if check_meeting_active(meetingID):
            print('Press the user ID to show his/her chat:')
            show_meeting_current_participants(meetingID)
            userID = input()
            show_user_chat(meetingID, int(userID))
        else:
            print('Meeting ' + meetingID + ' is not active')
    time.sleep(1.5)
    print_menu()
    choice = input()


print('Thank you and goodbye!')

# close connection to database files
client.flushall()
db_users.close()
db_meetings.close()
db_meeting_instances.close()
db_eventsLog.close()
