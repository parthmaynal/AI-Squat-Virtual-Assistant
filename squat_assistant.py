import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import time
import threading
import queue


# =========================
# VOICE SYSTEM
# =========================

engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("volume", 1.0)

voice_queue = queue.Queue()


def voice_worker():
    while True:
        message = voice_queue.get()

        if message is None:
            break

        try:
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print("Voice error:", e)

        voice_queue.task_done()


voice_thread = threading.Thread(
    target=voice_worker,
    daemon=True
)

voice_thread.start()


def speak(message):
    voice_queue.put(message)


# =========================
# ANGLE CALCULATION
# =========================

def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    denominator = (
        np.linalg.norm(ba) *
        np.linalg.norm(bc)
    )

    if denominator == 0:
        return 0

    cosine_angle = np.dot(ba, bc) / denominator

    cosine_angle = np.clip(
        cosine_angle,
        -1.0,
        1.0
    )

    angle = np.degrees(
        np.arccos(cosine_angle)
    )

    return angle


# =========================
# MEDIAPIPE
# =========================

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# =========================
# CAMERA
# =========================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Could not open webcam.")
    exit()


# =========================
# SQUAT THRESHOLDS
# =========================

# Standing position
KNEE_UP = 160
HIP_UP = 160

# Required squat depth
KNEE_DOWN = 120
HIP_DOWN = 125

# Voice timing
FEEDBACK_COOLDOWN = 2.0

# Rep timing
REP_COOLDOWN = 1.0


# =========================
# VARIABLES
# =========================

count = 0

position = "UP"

reached_depth = False

feedback = "READY"

last_feedback_time = 0
last_rep_time = 0

start_time = time.time()


# =========================
# START MESSAGE
# =========================

speak("Squat assistant started.")
speak("Stand sideways and keep your full body visible.")


# =========================
# MAIN LOOP
# =========================

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:

        print("ERROR: Could not read webcam.")
        break


    # Mirror image
    frame = cv2.flip(frame, 1)


    # Convert BGR -> RGB
    image = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    image.flags.writeable = False

    results = pose.process(image)

    image.flags.writeable = True


    # =========================
    # PERSON DETECTED
    # =========================

    if results.pose_landmarks:

        landmarks = results.pose_landmarks.landmark


        # =========================
        # LEFT SIDE
        # =========================

        ls = landmarks[
            mp_pose.PoseLandmark.LEFT_SHOULDER
        ]

        lh = landmarks[
            mp_pose.PoseLandmark.LEFT_HIP
        ]

        lk = landmarks[
            mp_pose.PoseLandmark.LEFT_KNEE
        ]

        la = landmarks[
            mp_pose.PoseLandmark.LEFT_ANKLE
        ]


        # =========================
        # RIGHT SIDE
        # =========================

        rs = landmarks[
            mp_pose.PoseLandmark.RIGHT_SHOULDER
        ]

        rh = landmarks[
            mp_pose.PoseLandmark.RIGHT_HIP
        ]

        rk = landmarks[
            mp_pose.PoseLandmark.RIGHT_KNEE
        ]

        ra = landmarks[
            mp_pose.PoseLandmark.RIGHT_ANKLE
        ]


        # =========================
        # KNEE ANGLES
        # =========================

        left_knee_angle = calculate_angle(

            [lh.x, lh.y],
            [lk.x, lk.y],
            [la.x, la.y]
        )


        right_knee_angle = calculate_angle(

            [rh.x, rh.y],
            [rk.x, rk.y],
            [ra.x, ra.y]
        )


        # =========================
        # HIP ANGLES
        # =========================

        left_hip_angle = calculate_angle(

            [ls.x, ls.y],
            [lh.x, lh.y],
            [lk.x, lk.y]
        )


        right_hip_angle = calculate_angle(

            [rs.x, rs.y],
            [rh.x, rh.y],
            [rk.x, rk.y]
        )


        # =========================
        # CHOOSE VISIBLE SIDE
        # =========================

        left_visibility = (

            ls.visibility +
            lh.visibility +
            lk.visibility +
            la.visibility
        ) / 4


        right_visibility = (

            rs.visibility +
            rh.visibility +
            rk.visibility +
            ra.visibility
        ) / 4


        if left_visibility >= right_visibility:

            knee_angle = left_knee_angle
            hip_angle = left_hip_angle

        else:

            knee_angle = right_knee_angle
            hip_angle = right_hip_angle


        current_time = time.time()


        # =========================
        # DEPTH CONDITIONS
        # =========================

        good_depth = (

            knee_angle <= KNEE_DOWN
            and
            hip_angle <= HIP_DOWN
        )


        standing = (

            knee_angle >= KNEE_UP
            and
            hip_angle >= HIP_UP
        )


        # =========================
        # START MOVING DOWN
        # =========================

        if position == "UP" and not standing:

            position = "GOING_DOWN"

            reached_depth = False

            feedback = "GOING DOWN"


        # =========================
        # GOING DOWN
        # =========================

        if position == "GOING_DOWN":

            # Both knee and hip reached required depth
            if good_depth:

                reached_depth = True

                position = "DOWN"

                feedback = "GOOD DEPTH"


                if (
                    current_time - last_feedback_time
                    >= FEEDBACK_COOLDOWN
                ):

                    speak("Good depth.")

                    last_feedback_time = current_time


            # Not deep enough
            else:

                feedback = "PARTIAL - GO DEEPER"


                if (
                    current_time - last_feedback_time
                    >= FEEDBACK_COOLDOWN
                ):

                    # Both are too high
                    if (
                        knee_angle > KNEE_DOWN
                        and
                        hip_angle > HIP_DOWN
                    ):

                        speak(
                            "Partial rep. Go deeper."
                        )

                    # Knee is limiting
                    elif knee_angle > KNEE_DOWN:

                        speak(
                            "Partial rep. Go lower."
                        )

                    # Hip is limiting
                    elif hip_angle > HIP_DOWN:

                        speak(
                            "Partial rep. Go deeper with your hips."
                        )

                    last_feedback_time = current_time


        # =========================
        # DOWN POSITION
        # =========================

        if position == "DOWN":

            reached_depth = True

            feedback = "GOOD DEPTH"


        # =========================
        # RETURN TO STANDING
        # =========================

        if standing:


            # Valid completed squat
            if (
                position == "DOWN"
                and
                reached_depth
            ):

                if (
                    current_time - last_rep_time
                    >= REP_COOLDOWN
                ):

                    count += 1

                    last_rep_time = current_time

                    position = "UP"

                    reached_depth = False

                    feedback = "GOOD REP"

                    speak(
                        f"Good! Rep {count} completed."
                    )


            # Partial squat
            elif position == "GOING_DOWN":

                position = "UP"

                reached_depth = False

                feedback = "PARTIAL REP - NOT COUNTED"


                if (
                    current_time - last_feedback_time
                    >= FEEDBACK_COOLDOWN
                ):

                    speak(
                        "Partial rep. Go deeper. Rep not counted."
                    )

                    last_feedback_time = current_time


            elif position == "UP":

                feedback = "READY"


        # =========================
        # DRAW SKELETON
        # =========================

        mp_drawing.draw_landmarks(

            frame,

            results.pose_landmarks,

            mp_pose.POSE_CONNECTIONS
        )


        # =========================
        # DISPLAY INFORMATION
        # =========================

        cv2.putText(

            frame,

            f"Knee Angle: {int(knee_angle)}",

            (20, 35),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 255),

            2
        )


        cv2.putText(

            frame,

            f"Hip Angle: {int(hip_angle)}",

            (20, 70),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 255),

            2
        )


        cv2.putText(

            frame,

            f"REPS: {count}",

            (20, 115),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.9,

            (0, 255, 0),

            2
        )


        cv2.putText(

            frame,

            f"Position: {position}",

            (20, 155),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.65,

            (255, 255, 0),

            2
        )


        cv2.putText(

            frame,

            f"Feedback: {feedback}",

            (20, 195),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0, 255, 255),

            2
        )


        cv2.putText(

            frame,

            f"Required: Knee <= {KNEE_DOWN}, Hip <= {HIP_DOWN}",

            (20, 235),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (255, 255, 255),

            2
        )


    # =========================
    # NO PERSON
    # =========================

    else:

        cv2.putText(

            frame,

            "NO PERSON DETECTED",

            (20, 40),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (0, 0, 255),

            2
        )


    # =========================
    # TIMER
    # =========================

    elapsed_time = int(
        time.time() - start_time
    )

    minutes = elapsed_time // 60

    seconds = elapsed_time % 60


    cv2.putText(

        frame,

        f"Time: {minutes:02d}:{seconds:02d}",

        (20, 275),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.7,

        (255, 255, 255),

        2
    )


    cv2.putText(

        frame,

        "Press Q to quit",

        (20, frame.shape[0] - 20),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.65,

        (255, 255, 255),

        2
    )


    # =========================
    # SHOW CAMERA
    # =========================

    cv2.imshow(

        "AI Squat Virtual Assistant",

        frame
    )


    # Quit with Q
    if cv2.waitKey(10) & 0xFF == ord("q"):

        break


# =========================
# CLEANUP
# =========================

cap.release()

cv2.destroyAllWindows()

pose.close()

voice_queue.put(None)


# =========================
# FINAL RESULT
# =========================

print()

print("==============================")

print("WORKOUT FINISHED")

print("==============================")

print(f"Total Squats: {count}")

print(
    f"Workout Time: "
    f"{elapsed_time // 60:02d}:"
    f"{elapsed_time % 60:02d}"
)

print("==============================")