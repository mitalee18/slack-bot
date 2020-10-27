import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

#storing path of .env file in env_path, '.' in Path signifies current directory
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

#configure flask
app = Flask(__name__)

# set adapter - to handle the events sent to it by the slack api & send events to the below server ie app
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

#connecting to slack webclient
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
#get user id of bot to avoid his messages to be posted on channel
BOT_ID = client.api_call('auth.test')['user_id']

#dictionary to store key= userid & values = number of messages
message_counts = {}

#function to handle events
@slack_event_adapter.on('message')
def message(payload):
    # print(payload)
    event = payload.get('event', {})
    user_id = event.get('user')
    channel_id = event.get('channel')
    text = event.get('text')
    if BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1
        #post message in below channel., (bot should already be installed in our channel)
        client.chat_postMessage(channel=channel_id, text=text)

#make a new endpoint to be called when a command is called
@app.route('/message_count', methods=['POST'])
def message_count():
    #get request fom post request form since it was not sent as a payload
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_c = message_counts.get(user_id, 0) #if you don't find user id then return 0
    print("message count: {}".format(message_c))
    client.chat_postMessage(channel=channel_id, text="message count: {}".format(message_c))

    return Response(), 200
#run flask application
if __name__ == "__main__":
    app.run(debug=True) #debug true will not run entire app if we import the file & don't run directly