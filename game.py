# file: game.py
import cv2
import time
import random
import mediapipe as mp
import math
import numpy as np
import os
import sys
from index import save_score

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)

curr_Frame = 0
prev_Frame = 0
delta_time = 0

next_Time_to_Spawn = 0
Speed = [0, 5]
Fruit_Size = 30
Spawn_Rate = 1
Score = 0
Lives = 15
Difficulty_level = 1
game_Over = False

slash = np.array([[]], np.int32)
slash_Color = (255, 255, 255)
slash_length = 19
w = h = 0
Fruits = []

def Spawn_Fruits():
    fruit = {}
    random_x = random.randint(15, 600)
    random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    fruit["Color"] = random_color
    fruit["Curr_position"] = [random_x, 440]
    fruit["Next_position"] = [0, 0]
    Fruits.append(fruit)

def Fruit_Movement(Fruits, speed):
    global Lives
    for fruit in Fruits[:]:
        if fruit["Curr_position"][1] < 20 or fruit["Curr_position"][0] > 650:
            Lives -= 1
            Fruits.remove(fruit)
        cv2.circle(img, tuple(fruit["Curr_position"]), Fruit_Size, fruit["Color"], -1)
        fruit["Next_position"][0] = fruit["Curr_position"][0] + speed[0]
        fruit["Next_position"][1] = fruit["Curr_position"][1] - speed[1]
        fruit["Curr_position"] = fruit["Next_position"]

def distance(a, b):
    return int(math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2))

def show_game_over_screen(img):
    cv2.rectangle(img, (150, 200), (500, 300), (0, 0, 0), -1)
    cv2.putText(img, "GAME OVER", (180, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
    cv2.rectangle(img, (180, 320), (320, 370), (0, 255, 0), -1)
    cv2.putText(img, "Play Again", (190, 355), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.rectangle(img, (330, 320), (470, 370), (0, 0, 255), -1)
    cv2.putText(img, "Exit", (370, 355), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def mouse_callback(event, x, y, flags, param):
    global game_Over
    if event == cv2.EVENT_LBUTTONDOWN and game_Over:
        if 180 <= x <= 320 and 320 <= y <= 370:
            cv2.destroyAllWindows()
            os.execl(sys.executable, sys.executable, "game.py")
        elif 330 <= x <= 470 and 320 <= y <= 370:
            cv2.destroyAllWindows()
            exit()

cap = cv2.VideoCapture(0)
cv2.namedWindow("img")
cv2.setMouseCallback("img", mouse_callback)

while cap.isOpened():
    success, img = cap.read()
    if not success:
        print("skipping frame")
        continue

    h, w, c = img.shape
    img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
    img.flags.writeable = False
    results = hands.process(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            for id, lm in enumerate(hand_landmarks.landmark):
                if id == 8:
                    index_pos = (int(lm.x * w), int(lm.y * h))
                    cv2.circle(img, index_pos, 18, slash_Color, -1)
                    slash = np.append(slash, index_pos)

                    while len(slash) >= slash_length:
                        slash = np.delete(slash, len(slash) - slash_length, 0)

                    for fruit in Fruits[:]:
                        d = distance(index_pos, fruit["Curr_position"])
                        if d < Fruit_Size:
                            Score += 100
                            slash_Color = fruit["Color"]
                            Fruits.remove(fruit)

    if Score % 1000 == 0 and Score != 0:
        Difficulty_level = int((Score / 1000) + 1)
        Spawn_Rate = Difficulty_level * 4 / 5
        Speed[0] *= Difficulty_level
        Speed[1] = int(5 * Difficulty_level / 2)

    if Lives <= 0:
        game_Over = True

    slash_draw = slash.reshape((-1, 1, 2))
    cv2.polylines(img, [slash_draw], False, slash_Color, 15, 0)

    curr_Frame = time.time()
    delta_Time = curr_Frame - prev_Frame
    FPS = int(1 / delta_Time) if delta_Time > 0 else 0

    cv2.putText(img, "FPS : " + str(FPS), (int(w * 0.82), 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 250, 0), 2)
    cv2.putText(img, "Score: " + str(Score), (int(w * 0.35), 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 5)
    cv2.putText(img, "Level: " + str(Difficulty_level), (int(w * 0.01), 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 150), 5)
    cv2.putText(img, "Lives remaining : " + str(Lives), (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    prev_Frame = curr_Frame

    if not game_Over:
        if time.time() > next_Time_to_Spawn:
            Spawn_Fruits()
            next_Time_to_Spawn = time.time() + (1 / Spawn_Rate)
        Fruit_Movement(Fruits, Speed)
    else:
        save_score(Score)
        show_game_over_screen(img)

    cv2.imshow("img", img)
    if cv2.waitKey(5) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
