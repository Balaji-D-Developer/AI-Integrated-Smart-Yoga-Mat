# pose_detection.py
import cv2
import mediapipe as mp
import numpy as np
import configparser

# Key angle names
ANGLE_KEYS = [
    'left_elbow', 'right_elbow', 'left_shoulder', 'right_shoulder',
    'left_knee', 'right_knee'
]

class YogaPoseRecognizer:
    def __init__(self, config_path='pose_details.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.last_pose_correct = False

    def calculate_angle_3d(self, a, b, c):
        """Calculates the angle between three 3D landmarks."""
        a = np.array([a.x, a.y, a.z])
        b = np.array([b.x, b.y, b.z])
        c = np.array([c.x, c.y, c.z])

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)

    def get_all_angles(self, landmarks):
        """Calculates all key angles from 3D world landmarks."""
        lm = landmarks.landmark
        angles = {}

        # Define landmark connections for angle calculation
        angle_definitions = {
            'left_elbow': ('LEFT_SHOULDER', 'LEFT_ELBOW', 'LEFT_WRIST'),
            'right_elbow': ('RIGHT_SHOULDER', 'RIGHT_ELBOW', 'RIGHT_WRIST'),
            'left_shoulder': ('LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_HIP'),
            'right_shoulder': ('RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_HIP'),
            'left_knee': ('LEFT_HIP', 'LEFT_KNEE', 'LEFT_ANKLE'),
            'right_knee': ('RIGHT_HIP', 'RIGHT_KNEE', 'RIGHT_ANKLE')
        }

        for angle_name, (p1, p2, p3) in angle_definitions.items():
            try:
                point1 = lm[getattr(self.mp_pose.PoseLandmark, p1).value]
                point2 = lm[getattr(self.mp_pose.PoseLandmark, p2).value]
                point3 = lm[getattr(self.mp_pose.PoseLandmark, p3).value]
                angles[angle_name] = self.calculate_angle_3d(point1, point2, point3)
            except:
                angles[angle_name] = None
        return angles

    def process_frame(self, frame, pose_name):
        """
        Processes a single video frame to provide real-time feedback for a target pose.
        """
        frame.flags.writeable = False
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        frame.flags.writeable = True

        all_green = True
        
        if results.pose_world_landmarks and pose_name in self.config.sections():
            # Calculate angles using 3D world landmarks for accuracy
            angles = self.get_all_angles(results.pose_world_landmarks)
            thresholds = self.config[pose_name]

            # Draw 2D landmarks on the frame for visualization
            self.mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )

            # Check angles and draw feedback
            for key in ANGLE_KEYS:
                angle = angles.get(key)
                if angle is None:
                    all_green = False
                    continue

                min_val = float(thresholds.get(f"{key}_min", 0))
                max_val = float(thresholds.get(f"{key}_max", 360))
                is_ok = min_val <= angle <= max_val
                
                if not is_ok:
                    all_green = False

                color = (0, 255, 0) if is_ok else (0, 0, 255)
                
                # Get 2D coordinates for displaying text
                lm_2d = results.pose_landmarks.landmark
                joint_name = key.split('_')[0].upper() + '_' + key.split('_')[1].upper()
                joint_landmark = lm_2d[getattr(self.mp_pose.PoseLandmark, joint_name).value]
                x, y = int(joint_landmark.x * frame.shape[1]), int(joint_landmark.y * frame.shape[0])
                
                cv2.putText(
                    frame, f"{int(angle)}", (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
                )
        
        else:
            all_green = False # No landmarks detected or pose not in config

        self.last_pose_correct = all_green
        return frame