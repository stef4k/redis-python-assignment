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

# loop for menu reappearance
while (choice != 'X') & (choice != 'x'):
    # activate corresponding function based on input
    if choice == '1':
        functions.print_all_meetings()
        meetingID = input('Press the meeting ID to activate it: ')
        functions.activate_meeting(meetingID)
    elif choice == '2':
        print('\t\tActive Meetings:')
        functions.show_active_meetings()
    elif choice == '3':
        if functions.show_active_meetings():
            meetingID = input('Press the meeting ID to join: ')
            if functions.check_meeting_exists(meetingID):
                if functions.check_meeting_active(meetingID):
                    functions.print_all_users()
                    userID = input('Press the user ID to join: ')
                    functions.join_meeting(meetingID, userID)
                else:
                    print('Meeting ' + meetingID + ' is not active at the moment.')
            else:
                print('Meeting with ID {meeting_id} does not exist in database.'
                      .format(meeting_id=meetingID))
    elif choice == '4':
        if functions.show_active_meetings():
            meetingID = input('Press the meeting ID to leave: ')
            if functions.check_meeting_exists(meetingID):
                if functions.check_meeting_active(meetingID):
                    if functions.show_meeting_current_participants(meetingID):
                        userID = input('Press the user ID to leave: ')
                        functions.leave_meeting(meetingID, userID)
                else:
                    print('Meeting ' + meetingID + ' is not active.')
            else:
                print('Meeting with ID {meeting_id} does not exist in database.'
                      .format(meeting_id=meetingID))
    elif choice == '5':
        if functions.show_active_meetings():
            meetingID = input('Press the meeting ID to show participants: ')
            if functions.check_meeting_exists(meetingID):
                functions.show_meeting_current_participants(meetingID)
            else:
                print('Meeting with ID {meeting_id} does not exist in database.'
                      .format(meeting_id=meetingID))
    elif choice == '6':
        if functions.show_active_meetings():
            meetingID = input('Press the meeting ID to end: ')
            functions.end_meeting(meetingID)
    elif choice == '7':
        if functions.show_active_meetings():
            meetingID = input('Press the meeting ID to post message: ')
            if functions.check_meeting_exists(meetingID):
                if functions.check_meeting_active(meetingID):
                    if functions.show_meeting_current_participants(meetingID):
                        userID = input('Type the user ID to post a message: ')
                        if functions.check_user_exists(userID):
                            message = input('Type the message: ')
                            functions.post_message(meetingID, userID, message)
                        else:
                            print('User with ID {user_id} does not exist in database.'
                                  .format(user_id=userID))
                else:
                    print('Meeting ' + meetingID + ' is not active')
            else:
                print('Meeting with ID {meeting_id} does not exist in database.'
                      .format(meeting_id=meetingID))
    elif choice == '8':
        if functions.show_active_meetings():
            meetingID = input('Press the meeting ID to show chat: ')
            functions.show_chat(meetingID)
    elif choice == '9':
        functions.show_join_timestamp()
    elif choice == '10':
        if functions.show_active_meetings():
            meetingID = input('Press the meeting ID to show chat: ')
            if functions.check_meeting_exists(meetingID):
                if functions.check_meeting_active(meetingID):
                    if functions.show_meeting_current_participants(meetingID):
                        userID = input('Press the user ID to show his/her chat: ')
                        functions.show_user_chat(meetingID, userID)
                else:
                    print('Meeting ' + meetingID + ' is not active')
            else:
                print('Meeting with ID {meeting_id} does not exist in database.'
                      .format(meeting_id=meetingID))
    time.sleep(1.5)
    functions.print_menu()
    choice = input()

functions.close()
print('Thank you and goodbye!')