from dotenv import load_dotenv
from flask import Flask, session, request
import os
from flask.helpers import url_for
import redis
from twilio.twiml.voice_response import VoiceResponse
import requests
import redis
import base64

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
app = Flask(__name__)
app.secret_key = SECRET_KEY
red = redis.Redis('localhost')


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    response = VoiceResponse()
    print(str(session.items()))
    if session.get('welcome') is None:
        caller = request.form.get('Caller')
        call_sid = request.form.get('CallSid')
        session['caller'] = caller
        session['call_sid'] = call_sid
        session['welcome'] = False
        session['loops'] = 0
        response.say('Welcome! What would you like to talk about today?')
        response.record(max_length=15, recording_status_callback_event="completed",
                        recording_status_callback=url_for('process_recording'), play_beep=False)
        session['welcome'] = True
        red.sadd("waiting", call_sid)
    elif red.sismember("waiting", session['call_sid']):
        print("Waiting for Assembly AI to return text")
        response.pause(1)
        response.redirect(url_for('welcome'))
    else:
        text = red.get(session['call_sid']).decode("utf-8")
        response.say(text)
        response.hangup()
    session['loops'] = session.get('loops') + 1
    print(f"LOOPS: {session['loops']}")
    return str(response)


@app.route('/process_recording', methods=['POST'])
def process_recording():
    call_sid = request.form.get('CallSid')
    recording_url = request.form.get('RecordingUrl')
    recording_sid = request.form.get('RecordingSid')

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCT_SID}/Recordings/{recording_sid}"

    headers = {
        'Authorization': f'Basic {os.environ.get("TWILIO_BASIC_AUTH")}'
    }

    response = requests.request("GET", url, headers=headers)
    with open(f"{recording_sid}.wav", "wb") as recording:
        recording.write(response.content)

    api_token = os.environ.get('ASSEMBLY_AI_TOKEN')
    headers = {'authorization': api_token}

    data = base64.b64encode(open(f"{recording_sid}.wav", "rb").read()[
                            44:]).decode("utf-8")

    json_data = {'audio_data': data}

    response = requests.post(
        'https://api.assemblyai.com/v2/stream', json=json_data, headers=headers)
    ai_data = response.json()
    words = ai_data['words']
    word_list = []
    for _ in words:
        word_list.append(_['text'])

    red.srem("waiting", call_sid)
    red.set(call_sid, " ".join(word_list))
    return 'OK', 200


def send_to_transcribe(recording):
    # TODO: format wav file and send to AssemblyAI. Return text
    pass
