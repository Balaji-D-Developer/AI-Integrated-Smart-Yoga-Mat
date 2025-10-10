# add_pose.py
import cv2
import mediapipe as mp
import configparser
import os
from pose_detection import YogaPoseRecognizer # <-- IMPORT THE UPDATED CLASS

def measure_pose():
    """Capture angles and frame for a new pose via camera feed."""
    recognizer = YogaPoseRecognizer()
    cap = cv2.VideoCapture(0)

    captured_angles = None
    captured_clean_frame = None
    print("Hold the desired pose. Press 's' to save or 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        clean_frame = frame.copy()
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = recognizer.pose.process(image_rgb)
        angles = {}

        if results.pose_world_landmarks:
            # Use the recognizer's method to get 3D angles
            angles = recognizer.get_all_angles(results.pose_world_landmarks)

            # Draw 2D landmarks for visualization
            recognizer.mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, recognizer.mp_pose.POSE_CONNECTIONS
            )

            # Overlay angle text for feedback during capture
            for key, val in angles.items():
                if val is None: continue
                joint_name = key.split('_')[0].upper() + '_' + key.split('_')[1].upper()
                lm_2d = results.pose_landmarks.landmark
                joint_lm = lm_2d[getattr(recognizer.mp_pose.PoseLandmark, joint_name).value]
                x = int(joint_lm.x * frame.shape[1])
                y = int(joint_lm.y * frame.shape[0])
                cv2.putText(frame, f"{key}:{int(val)}", (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        cv2.putText(frame, "Press 's' to save, 'q' to quit",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('Add New Pose', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s') and angles:
            captured_angles = {k: v for k, v in angles.items() if v is not None}
            if captured_angles:
                captured_clean_frame = clean_frame
                print("\nPose captured successfully!")
                break
            else:
                print("Could not capture valid angles. Try again.")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured_angles, captured_clean_frame

def add_pose_to_ini(angles, clean_frame, tolerance=10):
    if not angles or clean_frame is None:
        print("No valid data captured. Exiting.")
        return

    pose_name = input("Enter new pose name (e.g., TrianglePose_Yoga): ").strip()
    if not pose_name:
        print("Pose name cannot be empty.")
        return

    config_path = 'pose_details.ini'
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path)

    if pose_name in config.sections():
        overwrite = input(f"Pose '{pose_name}' already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return

    config[pose_name] = {}
    for key, val in angles.items():
        config[pose_name][f"{key}_min"] = str(max(0, val - tolerance))
        config[pose_name][f"{key}_max"] = str(val + tolerance)

    with open(config_path, 'w') as f:
        config.write(f)
    print(f"Pose '{pose_name}' saved to {config_path}.")

    img_dir = os.path.join('static', 'poses')
    os.makedirs(img_dir, exist_ok=True)
    filename = f"{pose_name.lower()}.png"
    img_path = os.path.join(img_dir, filename)
    cv2.imwrite(img_path, clean_frame)
    print(f"Reference image saved to {img_path}.")

if __name__ == '__main__':
    angles, clean_frame = measure_pose()
    if angles:
        add_pose_to_ini(angles, clean_frame)