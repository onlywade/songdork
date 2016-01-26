import json
import os
import random
import re

from flask import Flask, request
import requests
from twilio.rest import TwilioRestClient

app = Flask(__name__)
app.debug = True

G_API_KEY = os.getenv('G_API_KEY')
G_CX_ID = os.getenv('G_CX_ID')
G_SEARCH_URL = 'https://www.googleapis.com/customsearch/v1'

T_SID = os.getenv('T_SID')
T_AUTH_TOKEN = os.getenv('T_AUTH_TOKEN')
T_FROM_NO = os.getenv('T_FROM_NO')

app.logger.info('Environment loaded.')


@app.route('/find_song', methods=['GET'])
def find_song():
    from_ = request.args.get('From')
    lyrics = request.args.get('Body')
    if lyrics and len(lyrics) > 5:
        response_message = do_search_request(lyrics)
    else:
        response_message = 'that could be anything man'

    app.logger.info('Sending SMS response: {}'.format(response_message))
    send_sms_response(from_, response_message)

    return response_message


def do_search_request(lyrics):
    params = {'key': G_API_KEY,
              'cx': G_CX_ID,
              'q': lyrics}

    try:
        response = requests.get(G_SEARCH_URL, params=params)
    except Exception as e:
        app.logger.error('Exception during search request: {}'.format(e))
        return 'Sorry I am broken. {}'.format(e)

    return parse_search_response(response)


def parse_search_response(response):
    results = json.loads(response.content.decode('utf-8'))
    items = results.get('items')
    if items:
        first_hit = items[0]['title']
        message = respond_with_hit(first_hit)
    else:
        message = 'Hmm, that doesn\'t sound like anything I know..'

    app.logger.info('Search results resolved to: {}'.format(message))
    return message


def respond_with_hit(result_string):
    match = re.match('(.*)\ Lyrics\ -\ (.*)', result_string)
    if len(match.groups()) == 2:
        song = match.group(1)
        artist = match.group(2)
        message = get_random_template().format(song=song, artist=artist)
    else:
        message = 'Hmm, that doesn\'t sound like anything I know..'

    return message


def get_random_template():

    templates = [
        'whoah dude i LOOOOVE {artist}! not that song though.',
        'hey that\'s totally {song} by {artist}!!1 sing it again!',
        'oooooo, {song} by {artist}, huh? good one.',
        'oh man, {artist} are the worst. ESPECIALLY {song}.',
        '{song}, by {artist}. what a hit. *sigh*',
        '{artist}, really? you have terrible taste.'
    ]

    return random.choice(templates)


def send_sms_response(to, message):
    client = TwilioRestClient(T_SID, T_AUTH_TOKEN)
    client.messages.create(to=to, from_=T_FROM_NO, body=message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
