import os
import time
import re
from slackclient import SlackClient
import json


# constants
SLACK_BOT_TOKEN = 'xoxb-6911509088-371851564835-8oZ2egTZiDIWjkcCqi5nhmso'
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = 'do'
MENTION_REGEX = '^<@(|[WU].+?)>(.*)'
COMMAND_LIST = ['- *do* [action]', '*help* [command]', '*hello*', '*INC*[number]', '*ADR*[number]']

# initiate Slack Client
# slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack_client = SlackClient(SLACK_BOT_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
# converts a python dict into a json string
#   json_str = json.dumps(py_dict)
# converts a json string into a python dict
#   py_dict = json.loads(json_str)

def parse_bot_commands(slack_events):
    """
    Parses a list of events coming from the Slack RTM API to find bot commands.
    If a bot command is found, this function returns a tuple of command and channel.
    If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event['type'] == 'message' and not 'subtype' in event:
            user_id, message = parse_direct_mention(event['text'])
            if user_id == starterbot_id:
                return message, event['channel']
    return None, None


def parse_direct_mention(message_text):
    """
    Finds a direct metnion (a mention that is at the beginning) in message text and returns
    the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # if first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
    Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = 'Not sure what you mean. Try *{}*.'.format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    # TODO: Better command implementation other than if/else statements. List?
    if command.startswith(EXAMPLE_COMMAND):
        response = 'Sure...write some more code then I can do that!'
    elif command.startswith('help'):
        # TODO: Respond with a list of commands in json format
        pretext = 'Here\'s what I can do for you:\n'
        list_commands = '\n- '.join(COMMAND_LIST)

        response_dict = {
            'attachments': {
                'pretext': pretext,
                'text': list_commands
            }
        }

        # response = json.dumps(response_dict)
        response = pretext + list_commands
    elif command.startswith('hello'):
        payload = {'token':'XXXXXX', 'user':'XXXXXX'}
        # TODO: Retrieve user's name
        # req = requests.get('https://slack.com/api/channels.history', params=payload)
        response = 'Hi! What can I do for you?'
    elif command.startswith('INC') or command.startswith('ADR'):
        response = 'I will be able to check the status of your INC and ADR tickets soon! Hang tight!'

    # Sends the response back to the channel
    slack_client.api_call(
        'chat.postMessage',
        channel=channel,
        text=response or default_response,
        mrkdwn=True,
        # TODO: Create threaded response
        thread_ts=''
    )


if __name__ == '__main__':
    if slack_client.rtm_connect(with_team_state=False):
        print('Starter Bot connected and running!')
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call('auth.test')['user_id']
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print('Connection failed. Exception traceback printed above.')

