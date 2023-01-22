import multiprocessing as mp
import time
import speech_recognition as sr
import random

r = sr.Recognizer()

def convertSpeechToText(audio):
    #print("Converting speech to text")
    query = ""
    try:
        query = r.recognize_google(audio)
    except:
        print("Coundn't understand you!")
    print(query)

def record(consumerQueue):
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2)
        #print("Set minimum energy threshold to {}".format(r.energy_threshold))
        print("Say something ...")

        for _ in range(5):
            sleep_for = random.uniform(0.05, 1.0)
            audio = r.listen(source, phrase_time_limit=5)
            print("Adding audio to transcriber ...")
            consumerQueue.put_nowait(audio)
            print("Adding audio to transcriber ... Done")

def recorderStage(q_in, q_out):
    try:
        print("stage1 started")
        q_in.get()
        while True:
            record(q_out)
        print("stage1 finished")
    except Exception as e:
        print("Error in stage1")
        print(e)
    return

def transcriberStage(q_in, q_out):
    print("stage2 started")
    while True:
        print("Waiting for audio ...")
        convertSpeechToText(q_in.get())
    q_out.put("Conversion complete.\n")
    print("stage2 finished")
    return

def main():

    pool = mp.Pool()
    manager = mp.Manager()

    # create managed queues
    q_main_to_recorder = manager.Queue()
    q_recorder_to_transcriber = manager.Queue()
    q_transcriber_to_main = manager.Queue()

    # launch workers, passing them the queues they need
    results_s1 = pool.apply_async(recorderStage, (q_main_to_recorder, q_recorder_to_transcriber))
    results_s2 = pool.apply_async(transcriberStage, (q_recorder_to_transcriber, q_transcriber_to_main))

    # Send a message into the pipeline
    q_main_to_recorder.put("Start recording.\n")

    # Wait for work to complete
    print(q_transcriber_to_main.get()+"Main completed.")

    pool.close()
    pool.join()

    print("All done")

    return

if __name__ == "__main__":
    main()