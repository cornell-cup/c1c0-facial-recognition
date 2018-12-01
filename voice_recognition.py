import speech_recognition as sr
import client

#obtain audio from the microphone

while(True):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("It's up. Say something!")
        audio = r.listen(source)

    #recognize speech using Google Speech Recognition
    try:
        print("I thinks you said " + r.recognize_google(audio))
        if (r.recognize_google(audio)=="check in"):
            client.main()

    except sr.UnknownValueError:
        print("I could not understand audio")
    except sr.RequestError as e:
        print("I could not request results from Google Speech Recognition service; {0}".format(e))
