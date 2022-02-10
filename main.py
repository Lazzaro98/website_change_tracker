import hashlib
import smtplib
import ssl
import sys
import time
import webbrowser
from datetime import datetime
from urllib.request import Request, urlopen

USAGE = 'usage: website_change_tracker.py URL [-h] [-receiver_email=test@test.com]\n\t\t\t\t[-sender_email=test2@test.com] [-sender_password=password]\n\t\t\t\t[-youtube_song_url=youtube.com/test]\n\t\t\t\t[-repeat_check_time=TIME_IN_SECONDS]\n\t\t\t\t[-looking_for=STRING_TO_FIND]'
# set these values if you want to be notified by email when the change is detected
RECEIVER_EMAIL = ''
SENDER_PASSWORD = ''
SENDER_EMAIL = ''
# set this value if you want youtube URL to be player when the change is detected
YOUTUBE_SONG_URL = ''
# set the value of the website you want to track
URL = ''
# set the repeat time for checks (5minutes default)
REPEAT_CHECK_TIME = 5
# If you want to detect if certain string appeared on the website, set this value
LOOKING_FOR = ''


# In order to allow less secure logins on your email account
# you need to visit https://www.google.com/settings/security/lesssecureapps
# and enable it
def send_mail(sender_email_, sender_password_, receiver_email_, message_):
    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = sender_email_
    receiver_email = receiver_email_
    password = sender_password_
    message = message_

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def play_song(song_youtube_url=YOUTUBE_SONG_URL):
    webbrowser.open(song_youtube_url)


def track_website_changes(url_=URL, repeat_time=REPEAT_CHECK_TIME, looking_for=LOOKING_FOR):
    url = Request(url_, headers={'User-Agent': 'Mozilla/5.0'})

    response = urlopen(url).read()
    previous_hash = hashlib.sha224(response).hexdigest()
    print("Monitoring for changes...")
    while True:
        time.sleep(int(repeat_time))
        try:
            response = urlopen(url).read()
            current_hash = hashlib.sha224(response).hexdigest()

            if current_hash != previous_hash:
                if looking_for != '':
                    if looking_for in str(response):
                        on_found()
                else:
                    on_change()
            previous_hash = current_hash
        except Exception as e:
            print("Error: " + e)


def on_found():  # if you detect special string appeared on the website
    on_change()  # Signal whatever you want


def on_change():  # What do you want to do after you detected a change. Sending email and opening certain webpage available for now
    # create log
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    log = "[ " + dt_string + " ]" + " Change in " + URL + " detected."

    print(log)

    if SENDER_EMAIL != '' and SENDER_PASSWORD != '' and RECEIVER_EMAIL != '':
        send_mail(SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, log)
    if YOUTUBE_SONG_URL != '':
        play_song()
    # Feel free to add any action


def load_args():
    global URL
    global RECEIVER_EMAIL
    global SENDER_EMAIL
    global SENDER_PASSWORD
    global YOUTUBE_SONG_URL
    global REPEAT_CHECK_TIME
    global LOOKING_FOR

    if len(sys.argv) < 2:
        print("Type URL which you want to track for changes.")
        print(USAGE)
        exit(0)
    if sys.argv[1] == '-h' or sys.argv[1] == '-help':
        print(USAGE)
        exit(0)
    URL = sys.argv[1]
    for i in range(2, len(sys.argv)):
        s = sys.argv[i]
        if 'receiver_email' in s:
            RECEIVER_EMAIL = s.rsplit('receiver_email=', 1)[-1]
        elif 'sender_email' in s:
            SENDER_EMAIL = s.rsplit('sender_email=', 1)[-1]
        elif 'sender_password' in s:
            SENDER_PASSWORD = s.rsplit('sender_password=', 1)[-1]
        elif 'youtube_song_url' in s:
            YOUTUBE_SONG_URL = s.rsplit('youtube_song_url=', 1)[-1]
        elif 'repeat_check_time' in s:
            REPEAT_CHECK_TIME = s.rsplit('-repeat_check_time=', 1)[-1]
        elif 'looking_for' in s:
            LOOKING_FOR = s.rsplit('-looking_for=', 1)[-1]


if __name__ == '__main__':
    load_args()  # if there are no args, this will have no effect
    # play_song('https://www.youtube.com/watch?v=WREobnmYO4M')
    track_website_changes(URL, REPEAT_CHECK_TIME)
