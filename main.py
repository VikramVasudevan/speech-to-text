import multiprocessing as mp
import time
import speech_recognition as sr
import random
import signal
import sys

r = sr.Recognizer()
pool = None
fh = open("notes.txt", "w+")

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

def closeResources():
    fh.close()
    pool.close()

def convertSpeechToText(audio):
    #print("Converting speech to text")
    query = ""
    try:
        query = r.recognize_google(audio)
    except:
        print("Coundn't understand you!")
    print(query)
    fh.write(query+". \n")

def record(transcriberQueue):
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2)
        #print("Set minimum energy threshold to {}".format(r.energy_threshold))
        print("Say something ...")

        while True:
            audio = r.listen(source, phrase_time_limit=5)
            print("Adding audio to transcriber ...")
            transcriberQueue.put_nowait(audio)
            print("Adding audio to transcriber ... Done")

def recorderStage(q_in, q_out):
    try:
        print("recorderStage started")
        q_in.get()
        record(q_out)
        print("recorderStage finished")
    except Exception as e:
        print("Error in recorderStage")
        print(e)
    return

def transcriberStage(q_in, q_out):
    print("Hello")
    try:
        print("transcriberStage started")
        while True:
            print("Waiting for audio ...")
            convertSpeechToText(q_in.get())
        q_out.put("Transcribing complete.\n")
        print("transcriberStage finished")
    except Exception as e:
        print("Error in transcriberStage")
        print(e)
        
    return

def main():
    print("Real-time Transcriber Started ...")
    pool = mp.Pool()
    manager = mp.Manager()

    # create managed queues
    q_main_to_recorder = manager.Queue()
    q_recorder_to_transcriber = manager.Queue()
    q_transcriber_to_main = manager.Queue()

    # launch workers, passing them the queues they need
    print("Creating worker for recorder ...")
    results_s1 = pool.apply_async(recorderStage, (q_main_to_recorder, q_recorder_to_transcriber))
    print(results_s1.ready())
    print("Creating worker for transcriber ...")
    results_s2 = pool.apply_async(transcriberStage, (q_recorder_to_transcriber, q_transcriber_to_main))
    print(results_s2.ready())

    print("Initiating recording process ...")
    # Send a message into the pipeline
    q_main_to_recorder.put("Start recording.\n")

    print("Awaiting process completion ...")
    # Wait for work to complete
    print(q_transcriber_to_main.get()+"Main completed.")

    pool.close()
    pool.join()
    
    print("All done")

    return

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
