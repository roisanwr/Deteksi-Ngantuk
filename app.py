from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance as dist
import pygame
import os

app = Flask(__name__)

# =============================================================================
# 1. KONFIGURASI & SETUP AUDIO
# =============================================================================

EAR_THRESHOLD = 0.25 
EAR_CONSEC_FRAMES = 20  
MAR_THRESHOLD = 0.7 
MAR_CONSEC_FRAMES = 15  

# Inisialisasi Audio
pygame.mixer.init()

# Load Audio (Path absolut agar aman)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path_alarm = os.path.join(BASE_DIR, "alarm.mp3")
path_song = os.path.join(BASE_DIR, "song1.mp3")

try:
    sound_drowsy = pygame.mixer.Sound(path_alarm)
    sound_yawn = pygame.mixer.Sound(path_song)
    print("[INFO] Audio berhasil dimuat!")
except Exception as e:
    print(f"[ERROR] File Audio tidak ditemukan: {e}")
    # Kita buat dummy sound agar tidak error saat run, tapi tidak ada suara
    sound_drowsy = pygame.mixer.Sound(buffer=bytearray()) 
    sound_yawn = pygame.mixer.Sound(buffer=bytearray())

channel_drowsy = pygame.mixer.Channel(0)
channel_yawn = pygame.mixer.Channel(1)

# Indeks Landmark
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
MOUTH_CALC_IDX = [13, 14, 78, 308] 
INNER_LIPS_DRAW = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 
                   324, 318, 402, 317, 14, 87, 178, 88, 95]

# MediaPipe Setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Global Kamera
cap = cv2.VideoCapture(0)

def calculate_ear(eye_points):
    A = dist.euclidean(eye_points[1], eye_points[5])
    B = dist.euclidean(eye_points[2], eye_points[4])
    C = dist.euclidean(eye_points[0], eye_points[3])
    return (A + B) / (2.0 * C)

def calculate_mar(mouth_points):
    A = dist.euclidean(mouth_points[0], mouth_points[1]) 
    B = dist.euclidean(mouth_points[2], mouth_points[3]) 
    if B == 0: return 0
    return A / B

def generate_frames():
    drowsy_counter = 0
    yawn_counter = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mesh_points = np.array([np.multiply([p.x, p.y], [w, h]).astype(int) for p in face_landmarks.landmark])

                left_eye = mesh_points[LEFT_EYE_IDX]
                right_eye = mesh_points[RIGHT_EYE_IDX]
                mouth_calc = mesh_points[MOUTH_CALC_IDX]
                mouth_draw = mesh_points[INNER_LIPS_DRAW]

                left_ear = calculate_ear(left_eye)
                right_ear = calculate_ear(right_eye)
                avg_ear = (left_ear + right_ear) / 2.0
                mar = calculate_mar(mouth_calc)

                # Visualisasi
                cv2.polylines(frame, [left_eye], True, (0, 255, 255), 1)
                cv2.polylines(frame, [right_eye], True, (0, 255, 255), 1) 
                cv2.polylines(frame, [mouth_draw], True, (255, 255, 255), 1)

                # --- LOGIKA SUARA (Server Side) ---
                if avg_ear < EAR_THRESHOLD:
                    drowsy_counter += 1
                else:
                    drowsy_counter = 0
                    # if channel_drowsy.get_busy(): channel_drowsy.stop() # Opsional

                if drowsy_counter >= EAR_CONSEC_FRAMES:
                    cv2.putText(frame, "!!! WAKE UP !!!", (50, h // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
                    
                    if not channel_drowsy.get_busy():
                        channel_drowsy.play(sound_drowsy)
                        if channel_yawn.get_busy(): channel_yawn.stop()

                elif mar > MAR_THRESHOLD:
                    yawn_counter += 1
                else:
                    yawn_counter = 0

                if yawn_counter >= MAR_CONSEC_FRAMES:
                    cv2.putText(frame, "Take a Rest", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
                    
                    if not channel_yawn.get_busy() and not channel_drowsy.get_busy():
                        channel_yawn.play(sound_yawn)

                # Info Data
                cv2.putText(frame, f"EAR: {avg_ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"MAR: {mar:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Encode Frame ke JPEG agar bisa dikirim ke Browser
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield frame dalam format MJPEG stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)