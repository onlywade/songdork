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

SONG_UNKNOWN_MESSAGE = 'Hmm, that doesn\'t sound at all familiar. Try singing it louder next time.'


@app.route('/twilio_callback', methods=['GET'])
def twilio_callback():
    """
    Main entrypoint. (Callback from Twilio upon receipt of SMS message.)
    """
    origin_number = request.args.get('From')    # number the SMS originated from
    partial_lyrics = request.args.get('Body')   # body of SMS, presumed to be song lyrics

    try:
        artist_and_song = find_artist_and_song(partial_lyrics)
        response_message = message_for_artist_and_song(artist_and_song)
    except Exception as e:
        response_message = 'Sorry I am broken. {}'.format(e)

    send_sms(origin_number, response_message)

    return response_message # it doesn't really matter how we respond to the Twilio callback


def find_artist_and_song(lyrics):
    """
    Given a snippet of lyrics, searches lyricsfreak for a suitable match.
    Returns an (artist, song) tuple, or None if no results found.
    """

    # google custom search engine API params
    params = {'key': G_API_KEY,
              'cx': G_CX_ID,
              'q': lyrics}

    response = requests.get(G_SEARCH_URL, params=params)
    results = json.loads(response.content.decode('utf-8'))

    items = results.get('items')
    if items:
        first_hit = items[0]['title']
        return parse_result(first_hit)
    else:
        return None


def message_for_artist_and_song(artist_and_song):
    """
    Given an (artist, song) tuple, returns a nice message about it.
    """
    if artist_and_song:
        artist = artist_and_song[0]
        song = artist_and_song[1]
        return get_random_message_template().format(artist=artist, song=song)
    else:
        return SONG_UNKNOWN_MESSAGE


def get_random_message_template():
    """
    Returns a random result message for interpolating artist/song into.
    """

    templates = [
        'whoah dude i LOOOOVE {artist}! not that song though.',
        'hey that\'s totally {song} by {artist}!!1 sing it again!',
        'oooooo, {song} by {artist}, huh? good one.',
        'oh man, {artist} are the worst. ESPECIALLY {song}.',
        '{song}, by {artist}. what a hit. *sigh*',
        '{artist}, really? you have terrible taste.',
        'yay, {artist} really does the best rendition of {song}, huh.',
        'oh yeah, {song} by that band {artist}, i\'ve always liked that one.',
        'wow, hearing {artist} brings me back to like, 4th grade.',
        'that\'s that song {song} by those guys {artist}, isn\'t it?',
        'hmm sounds like {song} as performed by the great {artist}.',
    ]

    return random.choice(templates)


def parse_result(result_string):
    """
    Given a result entry from the Google search API, returns an (artist, song) tuple or None
    """

    match = re.match('(.*)\ Lyrics\ -\ (.*)', result_string)
    if len(match.groups()) == 2:
        song = match.group(1)
        artist = match.group(2)
        return (artist, song)
    else:
        return None


def send_sms(to, message):
    """
    Just sends a text.
    """
    client = TwilioRestClient(T_SID, T_AUTH_TOKEN)
    client.messages.create(to=to, from_=T_FROM_NO, body=message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
