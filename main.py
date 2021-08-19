#!/usr/bin/env python3
import json
import os
import textwrap

from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
USER_ID = os.environ["USER_ID"]
GROUP_IDS = os.environ["GROUP_IDS"]

slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, endpoint="/slack/events")

slack_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=slack_token)


def recursive_block_process(elements, cb, accu=None):
    if accu is None:
        accu = []
    for elem in elements:
        accu.append(cb(elem))
        if 'elements' in elem:
            recursive_block_process(elem['elements'], cb, accu)
    return accu


def is_mention(elem):
    if elem['type'] == 'usergroup':
        return elem['usergroup_id'] in GROUP_IDS.split(',')
    elif elem['type'] == 'user':
        return elem['user_id'] == USER_ID
    elif elem['type'] == 'channel':
        return True
    return False


last_timestamp = 0
@slack_events_adapter.on("message")
def message(event_data):
    global last_timestamp
    ts = float(event_data['event']['ts'])
    if ts < last_timestamp:
        return
    last_timestamp = ts
    is_dm = 'im' in event_data['event']['channel_type']
    is_mentioning = False
    if 'blocks' in event_data['event'] and event_data['event']['blocks'] is not None:
        is_mentioning = any(recursive_block_process(event_data['event']['blocks'], is_mention))

    if is_dm or is_mentioning:
        text = '\n'.join(textwrap.wrap(event_data['event']['text'], 31, initial_indent=" ", subsequent_indent=" "))
        user_name = client.users_info(user=event_data['event']['user']).data['user']['real_name']

        channel = client.conversations_info(channel=event_data['event']['channel']).data['channel']
        if is_dm and ('is_mpim' not in channel or not channel['is_mpim']):
            user = channel['user']
            channel_name = client.users_info(user=user).data['user']['real_name']
        elif channel['is_mpim']:
            channel_name = channel['purpose']['value']
        else:
            channel_name = '#' + channel['name']
        try:
            with open('/dev/usb/lp0', encoding='cp437', mode='w') as stream:
                print(f"""=======
by {user_name}
in {channel_name}:
{text}
""", file=stream, flush=True)
        except BaseException as ex:
            print(ex)


# Start the server on port 8774
slack_events_adapter.start(host='0.0.0.0', port=8774)
