# import all the package we need in DL
import datetime
import os
import time
import wave

import cv2
import imutils
import librosa
import numpy as np
import pandas as pd

# audio preprocessing
import pyaudio

# keras API
import tensorflow as tf
from keras.models import load_model, Model
from scipy.stats import zscore
from keras import backend as K
from keras.layers import Conv2D, MaxPooling2D, BatchNormalization, Flatten, LSTM
from keras.layers import Input, Dense, Dropout, Activation, TimeDistributed
from keras.utils import img_to_array

import requests
import numpy as np
import cv2
import os
import threading
from sklearn import preprocessing

from speech_recognition import speechEmotionRecognition

from flask import Flask, request
import webbrowser

app = Flask(__name__)

from sendwechat import SendAPI

EMOTIONS = ["ANGRY", "DISGUST", "FEAR", "HAPPY", "SAD", "SURPRISED",
            "NEUTRAL"]

global video_preds, audio_preds, _status_

_status_ = 'NONE'


def run_video(video_file_path):
    # parameters for loading data and images
    detection_model_path = './models/haarcascade_frontalface_default.xml'
    emotion_model_path = './models/_mini_XCEPTION.102-0.66.hdf5'
    face_detection = cv2.CascadeClassifier(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False)

    # feelings_faces = []
    # for index, emotion in enumerate(EMOTIONS):
    # feelings_faces.append(cv2.imread('emojis/' + emotion + '.png', -1))

    # starting video streaming

    camera = cv2.VideoCapture(video_file_path)  # 此处路径改为视频路径
    fps = camera.get(cv2.CAP_PROP_FPS)
    cycle_num = 0
    preds = [0, 0, 0, 0, 0, 0, 0]
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detection.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                                flags=cv2.CASCADE_SCALE_IMAGE)

        canvas = np.zeros((250, 300, 3), dtype="uint8")
        frameClone = frame.copy()
        if len(faces) > 0:
            faces = sorted(faces, reverse=True,
                           key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
            # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
            # the ROI for classification via the CNN
            roi = gray[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (64, 64))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)
            preds = preds + emotion_classifier.predict(roi)[0]
            cycle_num = cycle_num + 1
            # print('Average probability:')
            # print(preds / cycle_num)
            label = EMOTIONS[preds.argmax()]
            # print('result=' + label)
            # emotion_probability = np.max(preds)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    return preds


def run_audio(audio_file_path):
    # loading the model
    model_sub_dir = os.path.join('./models/MODEL_CNN_LSTM.hdf5')
    audio = speechEmotionRecognition(model_sub_dir)

    # Predict emotion in voice at each time step
    step = 1  # in sec
    sample_rate = 16000  # in kHz

    # calling the predicted emotion method
    emotions, timestamp = audio.predict_emotion_from_file(audio_file_path, chunk_step=step * sample_rate,
                                                          predict_proba=False)
    audio.prediction_to_csv(emotions, os.path.join("./results/audio_emotions_emotion.txt"), mode='w')

    # emotion memory
    audio.prediction_to_csv(emotions, os.path.join("./results/audio_emotions_other.txt"), mode='a')

    # Get most common emotion during the interview
    major_emotion = max(set(emotions), key=emotions.count)
    # Calculate emotion distribution
    emotion_dist = [int(100 * emotions.count(emotion) / len(emotions)) for emotion in audio._emotion.values()]
    if emotion_dist is None:
        emotion_dist = [0, 0, 0, 0, 0, 0, 0]
    emotion_dist[4], emotion_dist[6] = emotion_dist[6], emotion_dist[4]
    emotion_dist[5], emotion_dist[4] = emotion_dist[4], emotion_dist[5]
    df = pd.DataFrame(emotion_dist, index=audio._emotion.values(), columns=['VALUE']).rename_axis('EMOTION')
    df.to_csv(os.path.join('./results/audio_emotions_dist.txt'), sep=',')

    # print(major_emotion)
    # print(emotion_dist)
    return emotion_dist


def video_record():
    global video_preds, _status_

    headers = {"content-type": "application/json"}

    # print(time.time())

    record_res = requests.get("http://192.168.0.105:8080/record", headers=headers)

    print("Video record response code: ", record_res.status_code)

    video_res = requests.get("http://192.168.0.105:8080/video", headers=headers, stream=True)

    print("Video download response code: ", video_res.status_code)

    video_file_path = './records/my_video.h264'

    if video_res.status_code == 200:
        with open(video_file_path, 'wb') as f:
            f.write(video_res.content)
        f.close()
    else:
        print("Error making request")

    cap = cv2.VideoCapture(video_file_path)
    if not cap.isOpened():
        os._exit(-1)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 对象创建成功后isOpened()将返回true
    while True:
        # 一帧一帧的捕获
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('frame', frame)

        cv2.waitKey(int(1000 / fps))

    cap.release()
    cv2.destroyAllWindows()

    _status_ = 'RECOGNIZING'
    video_preds = run_video(video_file_path)
    # print("video predictions: ", video_preds)


def audio_record():
    global audio_preds
    # print(time.time())

    audio = speechEmotionRecognition()

    audio_file_path = './records/my_audio.wav'

    rec_duration = 10  # in sec

    # recording the voice
    audio.voice_recording(audio_file_path, duration=rec_duration)

    print("audio record finished")

    audio_preds = run_audio(audio_file_path)
    # print("audio predictions: ", audio_preds)
    # return audio_preds


def checking():
    """0: 'Angry',
      1: 'Disgust',
      2: 'Fear',
      3: 'Happy',
      4: 'Neutral',
      5: 'Sad',
      6: 'Surprised"""

    emotion_dist = pd.read_csv('./results/audio_emotions_dist.txt')
    sum_x = 0

    for i in range(3,6):
        x = int(emotion_dist.loc[i][1])
        sum_x = sum_x + x

    if sum_x < 50:
        print('potential negative emotion warning')

    data = emotion_dist.to_dict('dict')
    value = data['VALUE']

    danger_rate = value[0] + value[2] + value[1]

    if danger_rate > 50:
        print('potential danger warning')
        i = datetime.datetime.now()
        hour = i.hour
        minute = i.minute + 1
        webbrowser.open('http://192.168.0.105:8080/monitor')
        SendAPI.sendWeChat('WARNING')
        # send_message = 'Your-children-might-in-danger-please-check-on-the-camera'
        # message(send_message, hour, minute)
        # Video()
        # sys.exit(0)


@app.route('/run', methods=['GET'])
def run():
    global video_preds, audio_preds, _status_

    result = ''

    mod = request.args.get('mod') if request.args.get('mod') else '0'

    if mod == '1':

        audio_thread = threading.Thread(target=audio_record)

        _status_ = 'RECORDING'

        audio_thread.start()

        video_record()

        time.sleep(1)

        video_preds = (video_preds - np.min(video_preds)) / (np.max(video_preds) - np.min(video_preds) + 0.001)
        audio_preds = (audio_preds - np.min(audio_preds)) / (np.max(audio_preds) - np.min(audio_preds) + 0.001)

    elif mod == '2':

        _status_ = 'RECORDING'

        audio_record()

        audio_preds = (audio_preds - np.min(audio_preds)) / (np.max(audio_preds) - np.min(audio_preds) + 0.001)
        video_preds = audio_preds

    print("video predictions: ", video_preds)
    print("audio predictions: ", audio_preds)

    combined_preds = (video_preds + audio_preds) / 2

    result = EMOTIONS[np.argmax(combined_preds)]

    if mod == '1':
        SendAPI.sendWeChat(result)
    elif mod == '2':
        checking()

    headers = {"content-type": "application/json"}

    parameters = {'result': result}

    res = requests.get("http://192.168.0.105:8080/result", headers=headers, params=parameters)

    print("Response code: ", res.status_code)

    if res.status_code == 200:
        print("Return result: ", res.text)
    else:
        print("Error making request: ", res.text)

    _status_ = 'END'

    # for [video_prob, audio_prob, emotion] in [video_preds, audio_preds, EMOTIONS]:
    #     video_dict[emotion] = video_prob
    #     audio_dict[emotion] = audio_prob

    # video_file_path = './records/my_video.h264'
    # audio_file_path = './records/my_audio.wav'

    show_result = "Emotion Recognitions Result: " + result
    return show_result, 200


@app.route('/status', methods=['GET'])
def status():
    global _status_

    return _status_, 200


if __name__ == '__main__':
    # webbrowser.open('http://192.168.0.105:8080/monitor')
    app.run(host="0.0.0.0", port=8080)
    # label = 'SURPRISED'
    # SendAPI.sendWeChat(label)
