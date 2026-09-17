# AI Squat Virtual Assistant

An AI-powered real-time squat assistant built using **Python, OpenCV, MediaPipe, NumPy, and pyttsx3**. The system uses webcam-based pose estimation to detect squats, calculate knee and hip angles, count valid repetitions, identify partial squats, and provide real-time voice and visual feedback.

## Features

* 🎥 Real-time webcam-based pose detection
* 🦴 Human pose estimation using MediaPipe
* 📐 Knee and hip angle calculation
* 🔢 Automatic squat repetition counting
* ✅ Valid squat depth detection
* ⚠️ Partial squat detection
* 🔊 Voice feedback using text-to-speech
* ⏱️ Workout timer
* 📊 Real-time display of:

  * Knee angle
  * Hip angle
  * Number of repetitions
  * Current position
  * Squat feedback
  * Workout time
* 👤 Automatically selects the more visible side of the body

## How It Works

The system follows these steps:

1. The webcam captures the user's video.
2. MediaPipe Pose detects the body landmarks.
3. The shoulder, hip, knee, and ankle landmarks are extracted.
4. Knee and hip angles are calculated.
5. The system selects the side of the body with better landmark visibility.
6. The current squat position is determined.
7. The system checks whether the required squat depth has been reached.
8. A repetition is counted only when the user reaches the required depth and returns to the standing position.
9. Voice feedback is provided for correct depth and partial repetitions.

## Squat Detection Logic

### Standing Position

The user is considered to be standing when:

```text
Knee Angle >= 160°
Hip Angle   >= 160°
```

### Required Squat Depth

A squat reaches the required depth when:

```text
Knee Angle <= 120°
Hip Angle   <= 125°
```

Both conditions must be satisfied for a valid repetition.

### Partial Squat

If the user returns to the standing position without reaching the required depth, the repetition is classified as a partial repetition and is **not counted**.

Example feedback:

```text
Partial rep. Go deeper.
Partial rep. Go lower.
Partial rep. Go deeper with your hips.
```

## Technologies Used

| Technology | Purpose                             |
| ---------- | ----------------------------------- |
| Python     | Main programming language           |
| OpenCV     | Webcam capture and visual interface |
| MediaPipe  | Human pose estimation               |
| NumPy      | Mathematical calculations           |
| pyttsx3    | Voice feedback                      |

## Project Structure

```text
AI-Squat-Virtual-Assistant/
│
├── squat_assistant.py
├── requirements.txt
├── README.md
├── .gitignore
├── .gitattributes

```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/AI-Squat-Virtual-Assistant.git
cd AI-Squat-Virtual-Assistant
```

### 2. Create a Virtual Environment

For Windows:

```powershell
python -m venv myenv
```

Activate it:

```powershell
.\myenv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Requirements

The project requires:

```text
opencv-python
mediapipe
numpy
pyttsx3
```

## Running the Project

Run:

```bash
python squat_assistant.py
```

The webcam window will open automatically.

### Usage

1. Stand sideways to the webcam.
2. Keep your complete body visible.
3. Start performing squats.
4. The system will detect your movement.
5. Reach the required depth.
6. Return to the standing position.
7. A valid repetition will be counted.
8. Press **Q** to exit.

## Voice Feedback

The assistant provides voice feedback such as:

```text
Squat assistant started.

Stand sideways and keep your full body visible.

Good depth.

Partial rep. Go deeper.

Partial rep. Go lower.

Good! Rep completed.
```

A cooldown mechanism is used to prevent the same feedback from being spoken repeatedly.

## On-Screen Interface

The application displays:

```text
Knee Angle: 118
Hip Angle: 121
REPS: 5
Position: DOWN
Feedback: GOOD DEPTH
Required: Knee <= 120, Hip <= 125
Time: 01:32
Press Q to quit
```

## System Workflow

```text
Webcam
   ↓
Video Frame
   ↓
MediaPipe Pose Detection
   ↓
Body Landmarks
   ↓
Knee & Hip Angle Calculation
   ↓
Visible Side Selection
   ↓
Squat Depth Detection
   ↓
State Detection
   ↓
Valid / Partial Squat
   ↓
Rep Counter + Voice Feedback
```

## Current Configuration

| Parameter                  |     Value |
| -------------------------- | --------: |
| Standing Knee Angle        |      160° |
| Standing Hip Angle         |      160° |
| Required Knee Angle        |      120° |
| Required Hip Angle         |      125° |
| Voice Feedback Cooldown    | 2 seconds |
| Rep Cooldown               |  1 second |
| MediaPipe Model Complexity |         1 |
| Detection Confidence       |       0.5 |
| Tracking Confidence        |       0.5 |

## Limitations

The accuracy of the system can depend on:

* Camera position
* Lighting conditions
* Body visibility
* Camera angle
* Occlusion of body parts
* Clothing
* Distance from the camera
* Multiple people appearing in the frame

The current implementation is primarily intended for a **side-view squat**.


## Disclaimer

This project is intended for educational and demonstration purposes. It is not a medical or professional fitness assessment system.


Built with Python and computer vision for real-time exercise assistance.
