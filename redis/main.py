# importing the necessary libraries
import functions
import time
import os


# Main
if not os.path.exists('users.json'):
    # create database
    exec(open("database.py").read())
functions.start()
print('Welcome to Redis Meeting Application')
functions.print_menu()
choice = input()

while (choice != 'X') & (choice != 'x'):
    if (choice == '1'):
        print('Press the meeting ID to activate:')
        functions.print_all_meetings()
        meetingID = input()
        functions.activate_meeting(meetingID)
    if (choice == '2'):
        print('\t\tActive Meetings:')
        functions.show_active_meetings()
    elif (choice == '3'):
        print('Press the meeting ID to join:')
        functions.show_active_meetings()
        meetingID = input()
        if functions.check_meeting_active(meetingID):
            print('Press the user ID to join:')
            functions.print_all_users()
            userID = input()
            functions.join_meeting(meetingID, userID)
        else:
            print('Meeting ' + meetingID + ' is not active')
    elif (choice == '4'):
        print('Press the meeting ID to leave:')
        functions.show_active_meetings()
        meetingID = input()
        if functions.check_meeting_active(meetingID):
            print('Press the user ID to leave:')
            functions.show_meeting_current_participants(meetingID)
            userID = input()
            functions.leave_meeting(meetingID,userID)
        else:
            print('Meeting ' + meetingID + ' is not active')
    elif (choice == '5'):
        print('Press the meeting ID to show participants:')
        functions.show_active_meetings()
        meetingID = input()
        functions.show_meeting_current_participants(meetingID)
    elif (choice == '6'):
        print('Press the meeting ID to end:')
        functions.show_active_meetings()
        meetingID = input()
        functions.end_meeting(meetingID)
    elif (choice == '7'):
        print('Press the meeting ID to post message:')
        functions.show_active_meetings()
        meetingID = input()
        if functions.check_meeting_active(meetingID):
            print('Press the user ID to post a message:')
            functions.show_meeting_current_participants(meetingID)
            userID = input()
            print('Type the message:')
            message = input()
            functions.post_message(meetingID,userID,message)
        else:
            print('Meeting ' + meetingID + ' is not active')
    elif (choice == '8'):
        print('Press the meeting ID to show chat:')
        functions.show_active_meetings()
        meetingID = input()
        functions.show_chat(meetingID)
    elif (choice == '9'):
        functions.show_join_timestamp()
    elif (choice == '10'):
        print('Press the meeting ID to show chat:')
        functions.show_active_meetings()
        meetingID = input()
        if functions.check_meeting_active(meetingID):
            print('Press the user ID to show his/her chat:')
            functions.show_meeting_current_participants(meetingID)
            userID = input()
            functions.show_user_chat(meetingID, userID)
        else:
            print('Meeting ' + meetingID + ' is not active')
    time.sleep(1.5)
    functions.print_menu()
    choice = input()

functions.close()
print('Thank you and goodbye!')


