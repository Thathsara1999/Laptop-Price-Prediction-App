import cv2
import mediapipe as mp
import pyautogui
import pygetwindow as gw
import time
import threading
import tkinter as tk
from tkinter import Toplevel
from PIL import Image, ImageTk
import psutil


def set_window_always_on_top(window_name):
    while True:
        try:
            window = gw.getWindowsWithTitle(window_name)[0]
            window.activate()
            window.alwaysOnTop = True
            break
        except IndexError:
            time.sleep(0.1)


def show_error_message(message):
    error_window = Toplevel(root)
    error_window.title("Error")
    error_label = tk.Label(error_window, text=message, fg="red", font=("Helvetica", 12))
    error_label.pack(pady=10, padx=10)
    ok_button = tk.Button(error_window, text="OK", command=error_window.destroy, font=("Helvetica", 12, "bold"), padx=10, pady=5)
    ok_button.pack(pady=10)
    error_window.transient(root)
    error_window.grab_set()
    root.wait_window(error_window)


def show_success_message(message):
    success_window = Toplevel(root)
    success_window.title("Success")
    success_label = tk.Label(success_window, text=message, fg="green", font=("Helvetica", 12))
    success_label.pack(pady=10, padx=10)
    ok_button = tk.Button(success_window, text="OK", command=success_window.destroy, font=("Helvetica", 12, "bold"), padx=10, pady=5)
    ok_button.pack(pady=10)
    success_window.transient(root)
    success_window.grab_set()
    root.wait_window(success_window)


def start_virtual_mouse():

    is_powerpoint_running = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() in ['powerpnt.exe', 'powerpoint', 'powerpnt']:
            is_powerpoint_running = True
            break

    if not is_powerpoint_running:
        show_error_message("Running program is not PowerPoint application")
        return

    cap = cv2.VideoCapture(0)
    hand_detector = mp.solutions.hands.Hands()
    drawing_utils = mp.solutions.drawing_utils


    window_name = 'Hand Gesture Controlling'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 600, 450)


    screen_width, screen_height = pyautogui.size()
    frame_width, frame_height = 600, 450
    cv2.moveWindow(window_name, 0, screen_height - frame_height)


    boundary_line_y = 300


    thread = threading.Thread(target=set_window_always_on_top, args=(window_name,))
    thread.start()

    status = ""

    while True:

        power_point_window = None
        for window in gw.getWindowsWithTitle('PowerPoint'):
            if window.title.startswith('PowerPoint'):
                power_point_window = window
                break

        if power_point_window and power_point_window.isMinimized:
            show_error_message("PowerPoint is minimized. Gestures are disabled.")
            time.sleep(1)
            continue

        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = hand_detector.process(rgb_frame)
        hands = output.multi_hand_landmarks

        if hands:

            hand = hands[0]
            drawing_utils.draw_landmarks(frame, hand)
            landmarks = hand.landmark


            finger_tips_ids = [4, 8, 12, 16, 20]
            finger_mcp_ids = [2, 5, 9, 13, 17]
            fingers_up = []

            for tip_id, mcp_id in zip(finger_tips_ids, finger_mcp_ids):
                tip_y = landmarks[tip_id].y
                mcp_y = landmarks[mcp_id].y
                if tip_y < mcp_y:
                    fingers_up.append(True)
                else:
                    fingers_up.append(False)


            thumb_up = fingers_up[0] and not any(fingers_up[1:])


            all_fingers_up = all(fingers_up)


            hand_y = int(landmarks[8].y * frame_height)
            is_teacher_area = hand_y < boundary_line_y


            if is_teacher_area:

                if thumb_up:
                    pyautogui.press('left')
                    status = "Previous"
                    pyautogui.sleep(1)


                elif all_fingers_up:
                    pyautogui.press('right')
                    status = "Next"
                    pyautogui.sleep(1)

            else:
                status = "Student Area"

        else:
            status = ""


        cv2.line(frame, (0, boundary_line_y), (frame_width, boundary_line_y), (255, 0, 0), 2)


        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow(window_name, frame)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def test_gesture_control():
    test_window = Toplevel(root)
    test_window.title("Test Hand Gesture Control")
    boundary_line_y = 300
    frame_width, frame_height = 650, 600

    image_paths = ["./img/1.jpg", "./img/2.jpg", "./img/3.jpg"]
    images = [Image.open(path).resize((400, 300)) for path in image_paths]
    photos = [ImageTk.PhotoImage(image) for image in images]

    current_image = tk.Label(test_window)
    current_image.pack()

    def update_image(index):
        current_image.config(image=photos[index])
        current_image.image = photos[index]

    update_image(0)
    image_index = [0]

    def gesture_control():
        cap = cv2.VideoCapture(0)
        window_name = "Gesture Control Test"

        hand_detector = mp.solutions.hands.Hands()
        drawing_utils = mp.solutions.drawing_utils
        status = ""

        while True:
            _, frame = cap.read()
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = hand_detector.process(rgb_frame)
            hands = output.multi_hand_landmarks

            if hands:

                hand = hands[0]
                drawing_utils.draw_landmarks(frame, hand)
                landmarks = hand.landmark


                finger_tips_ids = [4, 8, 12, 16, 20]
                finger_mcp_ids = [2, 5, 9, 13, 17]
                fingers_up = []

                for tip_id, mcp_id in zip(finger_tips_ids, finger_mcp_ids):
                    tip_y = landmarks[tip_id].y
                    mcp_y = landmarks[mcp_id].y
                    if tip_y < mcp_y:
                        fingers_up.append(True)
                    else:
                        fingers_up.append(False)


                thumb_up = fingers_up[0] and not any(fingers_up[1:])


                all_fingers_up = all(fingers_up)

                hand_y = int(landmarks[8].y * frame_height)
                is_teacher_area = hand_y < boundary_line_y

                if is_teacher_area:
                    if thumb_up:
                        image_index[0] = (image_index[0] - 1) % len(photos)
                        update_image(image_index[0])
                        status = "Previous"
                        pyautogui.sleep(1)


                    elif all_fingers_up:
                        image_index[0] = (image_index[0] + 1) % len(photos)
                        update_image(image_index[0])
                        status = "Next"
                        pyautogui.sleep(1)
                else:
                    status = "Student Area"
            else:
                status = ""


            cv2.line(frame, (0, boundary_line_y), (frame_width, boundary_line_y), (255, 0, 0), 2)
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            cv2.imshow(window_name, frame)


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


        test_window.destroy()

        show_success_message("Now you can control your slide in PowerPoint presentation")

    threading.Thread(target=gesture_control).start()


#frontend

root = tk.Tk()
root.title("Start Hand Gesture Presentation")

start_button = tk.Button(root, text="Start", command=start_virtual_mouse, font=("Helvetica", 12, "bold"), padx=10, pady=10)
start_button.pack(pady=20)

test_button = tk.Button(root, text="Test", command=test_gesture_control, font=("Helvetica", 12, "bold"), padx=10, pady=10)
test_button.pack(pady=20)

gestures_label = tk.Label(root, text="Use the following hand gestures to control the presentation:", font=("Helvetica", 14))
gestures_label.pack(pady=10)

gesture_image_frame1 = tk.Frame(root, bg='white')
gesture_image_frame1.pack(pady=30)


gesture_left_image = Image.open("./img/thumbsUp.jpg")
gesture_right_image = Image.open("./img/raise5Fingers.jpg")

gesture_left_image = gesture_left_image.resize((100, 100))
gesture_right_image = gesture_right_image.resize((100, 100))

gesture_left_tk = ImageTk.PhotoImage(gesture_left_image)
gesture_right_tk = ImageTk.PhotoImage(gesture_right_image)


gesture_left_label = tk.Label(gesture_image_frame1, image=gesture_left_tk, bg='black')
gesture_left_label.grid(row=0, column=0, padx=20)
gesture_left_text = tk.Label(gesture_image_frame1, text="Go Previous", font=("Helvetica", 12), bg='white')
gesture_left_text.grid(row=1, column=0, padx=20)


gesture_right_label = tk.Label(gesture_image_frame1, image=gesture_right_tk, bg='black')
gesture_right_label.grid(row=0, column=1, padx=20)
gesture_right_text = tk.Label(gesture_image_frame1, text="Go Next", font=("Helvetica", 12), bg='white')
gesture_right_text.grid(row=1, column=1, padx=20)

gestures_tips = tk.Label(root, text="\tTips: \n\t > Use Right hand to control easily. \n\t > Before Click the Start Button, Open The PowerPoint Presentation. \n\t > if you need to quit, click on video frame (Gesture control test or Hand Gesture controling window) \n\t and press 'q' letter. \n\t > You can check sliding is working or not by clicking on Test button. \n\t > When sliding in powerpoint, do hand gestures above the blue boundary line. \n ", font=("Helvetica", 8), justify='left')
gestures_tips.pack(pady=10)

root.mainloop()