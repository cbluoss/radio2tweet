#!/usr/bin/env python3
import pyaudio
import audioop
import wave
import speech_recognition as sr
import tweepy

p = pyaudio.PyAudio()
# prints a list with all audio devices
# for i in range(p.get_device_count()):
#   dev = p.get_device_info_by_index(i)
#   print((i,dev['name'],dev['maxInputChannels']))

RATE = 44100  
CHANNELS = 1
FORMAT = pyaudio.paInt16
INPUT_BLOCK_TIME = 0.5
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
THRESHOLD = 600

WAVE_OUTPUT_FILENAME = "temp.wav"

CONSUMER_KEY = 'xxx'#keep the quotes, replace this with your consumer key
CONSUMER_SECRET = 'xxx'#keep the quotes, replace this with your consumer secret key
ACCESS_KEY = 'xxx'#keep the quotes, replace this with your access token
ACCESS_SECRET = 'xxx'#keep the quotes, replace this with your access token secret
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

stream = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input_device_index = 0,
    input = True,
    frames_per_buffer=INPUT_FRAMES_PER_BLOCK)

decode_buffer = []
r = sr.Recognizer()
print ("lets get started")
while True:
	try:
		data = stream.read(INPUT_FRAMES_PER_BLOCK)
		data_level = audioop.rms(data, 2)
		print(("Decode Bufer Length", len(decode_buffer),"RMS",data_level))
		if data_level > THRESHOLD:
			decode_buffer.append(data)
		if data_level <= THRESHOLD and len(decode_buffer) != 0:
			print ("Process as RMS dropped")
			waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
			waveFile.setnchannels(CHANNELS)
			waveFile.setsampwidth(p.get_sample_size(FORMAT))
			waveFile.setframerate(RATE)
			waveFile.writeframes(b''.join(decode_buffer))
			waveFile.close()

			with sr.WavFile(WAVE_OUTPUT_FILENAME) as source:
			    audio = r.record(source) # read the entire WAV file
			# recognize speech using Google Speech Recognition
			try:
			    # for testing purposes, we're just using the default API key
			    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
			    # instead of `r.recognize_google(audio)`
			    api.update_status(status=r.recognize_google(audio))
			    #print("Google Speech Recognition thinks you said " + )
			except sr.UnknownValueError:
			    print("Google Speech Recognition could not understand audio")
			except sr.RequestError as e:
			    print("Could not request results from Google Speech Recognition service; {0}".format(e))

			decode_buffer = []

	except OSError:
		pass
#

