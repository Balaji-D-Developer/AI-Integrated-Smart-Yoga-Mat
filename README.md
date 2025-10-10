# AI-Powered Yoga Pose Trainer

This project is a full-stack web application that acts as a personal yoga trainer. It uses your webcam to provide real-time analysis and feedback on your yoga poses, helping you improve your form and track your progress.

## Features

* **Real-Time Pose Analysis**: Utilizes Google's MediaPipe library to detect 33 body landmarks and calculate key joint angles in 3D for high-precision analysis.
* **Instant Visual Feedback**: Overlays colored markers and angle data directly onto your live video feed. Green indicates correct alignment, while red highlights areas that need adjustment.
* **Workout Sessions**: Guides you through a series of yoga poses, each with a 60-second timer to hold the position.
* **Performance Summary**: After each session, you receive a summary of your performance, including the number of correct/incorrect poses, estimated calories burned, and a personalized diet suggestion.
* **Extensible Pose Library**: Comes with a utility script that allows you to add new yoga poses to the system. Simply hold a pose, and the script will capture the required angles and save it for future sessions.
* **Hardware Integration**: Sends a signal over a serial port when a pose is performed incorrectly, allowing for integration with a physical feedback device like a vibration motor.
* **Audio Feedback**: Uses the browser's speech synthesis to provide audio confirmation when a pose is completed correctly or incorrectly.

## Tech Stack

* **Backend**: Python, Flask, OpenCV, MediaPipe, NumPy, PySerial
* **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript (Fetch API)
* **Configuration**: INI files (ConfigParser)

## Setup and Installation

1.  **Prerequisites**:
    * Python 3.8+
    * An available COM port for hardware integration (optional).

2.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/your-username/ai-yoga-trainer.git](https://github.com/your-username/ai-yoga-trainer.git)
    cd ai-yoga-trainer
    ```

3.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install Dependencies**:
    Create a `requirements.txt` file with the following content:
    ```
    Flask
    opencv-python
    mediapipe
    numpy
    pyserial
    ```
    Then, install the packages:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Hardware (Optional)**:
    * Connect your microcontroller (e.g., Arduino) to your computer.
    * Open `main.py` and update the `SERIAL_PORT` variable to your device's COM port.
    ```python
    SERIAL_PORT = 'COM3' # <-- Change this to your port, e.g., '/dev/ttyUSB0' on Linux
    ```

## Usage

1.  **Add New Poses (Recommended First Step)**:
    * To populate the system with poses, run the `add_pose.py` script.
        ```bash
        python add_pose.py
        ```
    * A window with your webcam feed will appear. Hold the desired yoga pose.
    * Press the **'s'** key to save the pose angles and reference image.
    * Press **'q'** to quit.
    * You will be prompted in the terminal to enter a name for the pose (e.g., `WarriorPose_Yoga`).
    * The pose data will be saved to `pose_details.ini`, and a reference image will be saved in the `static/poses/` directory.

2.  **Start the Yoga Session**:
    * Run the main application.
        ```bash
        python main.py
        ```
    * Open your web browser and navigate to `http://127.0.0.1:5000`.
    * Click the "Start Today's Session" button to begin your workout.
    * Follow the on-screen instructions, holding each pose for the duration of the timer.
    * At the end of the session, your summary will be displayed.

## File Structure


├── main.py              # Main Flask application, handles routing and session logic.
├── pose_detection.py    # Core computer vision module for pose analysis.
├── add_pose.py          # Utility script to add new poses to the system.
├── pose_details.ini     # Configuration file storing angle data for each pose.
├── templates/           # HTML templates for the web interface.
│   ├── base.html
│   ├── start.html
│   ├── pose.html
│   └── summary.html
└── static/              # Static assets.
└── poses/           # Directory for reference images of the poses.
