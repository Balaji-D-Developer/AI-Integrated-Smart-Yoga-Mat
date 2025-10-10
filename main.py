# main.py
import os
import threading
import time

import cv2
import serial
from flask import (
    Flask, Response, render_template, session,
    redirect, url_for, request, jsonify
)
from pose_detection import YogaPoseRecognizer # <-- IMPORT THE UPDATED CLASS

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24) # <-- Use a secure, random key

# Initialize pose recognizer
recognizer = YogaPoseRecognizer(config_path='pose_details.ini')

# Serial port handle (will be set in serial_thread)
ser = None
SERIAL_PORT = 'COM3' # <-- Consider moving to a config file

def init_serial():
    """Attempt to open the serial port once."""
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)
        print(f'✅ Serial port {SERIAL_PORT} opened successfully')
    except serial.SerialException as e:
        ser = None
        print(f'❌ Warning: could not open serial port {SERIAL_PORT}: {e}')

def serial_thread():
    """Background thread: open serial and optionally read."""
    init_serial()
    while True:
        time.sleep(1) # Keep thread alive, can add read logic if needed

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        # Shuffle poses for variety, or keep them ordered
        all_poses = list(recognizer.config.sections())
        session['today_poses']        = all_poses[:3] # Taking first 3 for simplicity
        session['current_pose_index'] = 0
        session['correct_poses']      = 0
        session['wrong_poses']        = 0
        return redirect(url_for('pose'))
    return render_template('start.html')

@app.route('/pose')
def pose():
    idx = session.get('current_pose_index', 0)
    poses = session.get('today_poses', [])
    
    if idx >= len(poses):
        return redirect(url_for('summary'))
        
    pose_name = poses[idx]
    ref_img = url_for('static', filename=f'poses/{pose_name.lower()}.png')
    return render_template('pose.html', pose=pose_name, reference_image=ref_img)

@app.route('/video_feed')
def video_feed():
    idx = session.get('current_pose_index', 0)
    pose_name = session['today_poses'][idx]
    return Response(
        stream_frames(pose_name),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def stream_frames(pose_name):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Delegate all processing to the recognizer class
        annotated_frame = recognizer.process_frame(frame, pose_name)

        ret2, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret2:
            continue

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
        )

    cap.release()

@app.route('/pose_complete', methods=['POST'])
def pose_complete():
    # The final check relies on the last state updated by process_frame
    correct = recognizer.last_pose_correct

    if correct:
        session['correct_poses'] += 1
    else:
        session['wrong_poses'] += 1
        # Send signal over serial on wrong pose
        if ser and ser.is_open:
            try:
                data = b'*0#'
                print(f"→ Writing to serial: {data}")
                ser.write(data)
            except Exception as e:
                print(f"❌ Serial write failed: {e}")
        else:
            print("⚠️ Serial port not open; skipping write")

    session['current_pose_index'] += 1
    if session['current_pose_index'] < len(session.get('today_poses', [])):
        next_url = url_for('pose')
    else:
        next_url = url_for('summary')

    return jsonify({'next_url': next_url, 'correct': correct})

@app.route('/summary')
def summary():
    total   = len(session.get('today_poses', []))
    correct = session.get('correct_poses', 0)
    wrong   = session.get('wrong_poses', 0)
    calories = correct * 5 # Simple calculation

    # Diet plan logic
    if correct <= 1: diet = 'High-protein, low-carb diet plan.'
    elif correct == 2: diet = 'Balanced diet with moderate calories.'
    else: diet = 'High-fiber, moderate-protein diet.'

    all_poses = list(recognizer.config.sections())
    next_day_poses = all_poses[3:] if len(all_poses) > 3 else []

    return render_template(
        'summary.html',
        total=total, correct=correct, wrong=wrong,
        calories=calories, diet=diet, next_day_poses=next_day_poses
    )

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        t = threading.Thread(target=serial_thread, daemon=True)
        t.start()
    app.run(debug=True)