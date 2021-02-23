# Speech-to-Text with Twilio and AssemblyAI

If you want to start building conversational IVRs and you want to bring your own speech to text engine, this will get you started.

## Technologies:
- [Twilio](www.twilio.com/referral/IqqOOI)
- [AssemblyAI](https://app.assemblyai.com/dashboard/)
- [Python Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Redis](https://redis.io/)

## Flow
1. Call comes in to Twilio number which sends a webhok to the `/welcome` endpoint
2. Return TwiML to greet caller and record snippet of voice
3. `CallSid` is added to Redis set to inform the `/welcome` endpoint that we are waiting for the recording to be processed
4. Twilio processes recording and sends webhook to `/process_recording `endpoint
5. `/process_recording` downloads the wav file
6. The recording is converted to base64 and has it's headers stripped as required by AssemblyAI
7. `POST` request sent to AssemblyAI with base64 payload. Returns JSON object with transcription
8. Loop through list of text to get only the words
9. Return a new list containing the spoken words
10. Word list is converted to string and is added to Redis
11. `CallSid` is removed from Redis set so that the call can continue
12. `/welcome` endpoint gets text from Redis using the `CallSid` stored in the session variable
13. Echos the callers words using TwiML <Say>
14. Call disconnects
