#!/usr/bin/env python3
import pyaudio
import audioop
import wave
import speech_recognition as sr
import tweepy

INTERACTIVE = True
DEMO_MODE = True

RATE = 44100
CHANNELS = 1
FORMAT = pyaudio.paInt16
INPUT_BLOCK_TIME = 0.5
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
THRESHOLD = 600
INPUT_DEVICE = 0

WAVE_OUTPUT_FILENAME = "file.wav"

LANG = "de"
G_API_KEY = ""

# Twitter API Settings/Keyss
CONSUMER_KEY = 'xxx'
CONSUMER_SECRET = 'xxx'
ACCESS_KEY = 'xxx'
ACCESS_SECRET = 'xxx'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

p = pyaudio.PyAudio()

if INTERACTIVE:
    LANG = input("Expected language (default is %s):" % LANG)
    print("Select input device")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print((i, dev['name'], dev['maxInputChannels']))
    INPUT_DEVICE = int(input("Use device id (default is %i )" % INPUT_DEVICE))
    CHANNELS = int(input("Input channels (default is %i)" % CHANNELS))
    DEMO_MODE = eval(input("Demo mode? (True/False) "))


stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input_device_index=INPUT_DEVICE,
    input=True,
    frames_per_buffer=INPUT_FRAMES_PER_BLOCK)

decode_buffer = []
r = sr.Recognizer()
print("RELEASE THE KRAKEN!")
while True:
    try:
        data = stream.read(INPUT_FRAMES_PER_BLOCK)
        data_level = audioop.rms(data, 2)
        print(("Current decode buffer %2.1f sec" % (INPUT_BLOCK_TIME*len(decode_buffer)), "Curent RMS", data_level))
        if data_level > THRESHOLD:
            decode_buffer.append(data)
        if data_level <= THRESHOLD and len(decode_buffer) != 0:
            print("Process as RMS dropped")
            waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(p.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(decode_buffer))
            waveFile.close()

            with sr.WavFile(WAVE_OUTPUT_FILENAME) as source:
                audio = r.record(source)  # read the entire WAV file
            # recognize speech using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                if DEMO_MODE:
                    print(r.recognize_google(audio, language=LANG))
                else:
                    api.update_status(
                        status=r.recognize_google(audio, language=LANG))
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google SR service; {0}".format(e))

            decode_buffer = []  # reset buffer
    except OSError:
        pass
