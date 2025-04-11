import cv2 
import time               # useful for calculating the FPS rate
import random             # for spawning "fruits" at random positions and random colours
import mediapipe as mp    # for hand detection and tracking
import math               # for various mathematical calculations
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)


curr_Frame = 0
prev_Frame = 0
delta_time = 0

next_Time_to_Spawn = 0   # variable to compute the time to spawn a "fruit".
Speed = [0,5]            # Speed vector along the x , y axis
Fruit_Size = 30          # radius of the circle representing the fruit
Spawn_Rate = 1           # Spawning rate of "fruits" (Per second) initially at 1 fruit /s
Score = 0                # Score initially at 0
Lives = 15               # number of Lives initially at 15
Difficulty_level= 1      # Difficulty level which will increase according to Score, initially at 1
game_Over=False          # Whether the game is lost , initially false ofc.

slash = np.array([[]],np.int32)   # a numpy array of arrays in order to keep track of the index finger positions in order to draw a curve representing the slash
slash_Color=(255,255,255)         # initial slash color : white
slash_length= 19                  # number of points to keep track of

w=h=0       # to store width and height of the frame
Fruits=[]   # the list to keep track of the "fruits" on screen


def Spawn_Fruits():
 fruit = {}
 random_x = random.randint(15,600)                                                   # x position of the fruit randomly generated
 random_color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))  # Colour of the fruit randomly generated
 #cv2.circle(img,(random_x,440),Fruit_Size,random_color,-1)                           # uncomment to test the of spawning the fruit as a circle on random x position and on a 440 y position
 fruit["Color"] = random_color                                                       
 fruit["Curr_position"]=[random_x,440]
 fruit["Next_position"] = [0,0]
 Fruits.append(fruit)


def Fruit_Movement(Fruits, speed):
    global Lives

    for fruit in Fruits:
        if (fruit["Curr_position"][1]) < 20 or (fruit["Curr_position"][0]) > 650:
            Lives = Lives - 1
            # print(Lives)
            print("removed ", fruit)
            Fruits.remove(fruit)

        cv2.circle(img, tuple(fruit["Curr_position"]), Fruit_Size, fruit["Color"], -1)
        fruit["Next_position"][0] = fruit["Curr_position"][0] + speed[0]  # + speed[0] #* delta_time
        fruit["Next_position"][1] = fruit["Curr_position"][1] - speed[1]  # * delta_time

        fruit["Curr_position"] = fruit["Next_position"]

        # print(len(Fruits))


def distance(a, b):
    x1 = a[0]
    y1 = a[1]

    x2 = b[0]
    y2 = b[1]

    d = math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))
    return int(d)


cap = cv2.VideoCapture(0)           # we set our pc webcam as our input
while(cap.isOpened()):              # while the webcam is opened
    success , img = cap.read()      # capture images
    if not success:
        print("skipping frame")
        continue
    h, w, c = img.shape             # get the dimensions of our image 
    
    img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)  # we flip the img bc it's initially mirrored and convert it from BGR to RGB in order to process it correctly with mediapipe
    img.flags.writeable = False     # To improve performance, optionally mark the image as not writeable to pass by reference.
    results = hands.process(img)    # launch the detection and tracking process on our img and store the results in "results"
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) # reconvert the img to its initial BGR Color space
    
    if results.multi_hand_landmarks:                          #if a hand is detected
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(                        # draw the landmarks 
                img,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            #**************************************************************************************
            for id , lm in enumerate(hand_landmarks.landmark): 
                if id == 8:                                       # id = 8 corresponds with the tip of the index finger
                    index_pos=(int(lm.x * w) ,int(lm.y * h))      # store the position of the index figer along the x and y axis
                                                                  # each hand is represented as a list of 21 hand landmarks and each landmark is composed of x, y and z. x and y are normalized to [0.0, 1.0] by the image width and height respectively. 
                                                                  #so in order to get the correct position we mutiply the x and y by the width and height of our image
                    cv2.circle(img,index_pos,18,slash_Color,-1)   
                    #slash=np.delete(slash,0)
                    slash=np.append(slash,index_pos)              # apped the position of the index in a numpy array

                    while len(slash) >= slash_length:             # keep the length of the slash array constant
                        slash = np.delete(slash , len(slash) -slash_length , 0)

                    for fruit in Fruits:                              
                        d= distance(index_pos,fruit["Curr_position"])           #calculate the distance between the index finger tip and each of the fruits
                        cv2.putText(img,str(d),fruit["Curr_position"],cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0),2,3)
                        if(d < Fruit_Size):                                     # if distance < size of the fruit the the fruit is "cut"
                            Score= Score + 100                                  # the score increments by 100
                            slash_Color = fruit["Color"]                        # the slash takes the color of the last fruit "cut"
                            Fruits.remove(fruit)                                # remove the fruit that was cut from the list of fruits


            #***********************************************************************************************************
  
    if Score % 1000 ==0 and Score != 0:        #each time the score is a multiple of 1000 (1000 , 2000 etc ..)
        Difficulty_level = (Score / 1000) + 1    # Difficulty level increments by 1 for every 1000 score
        Difficulty_level= int(Difficulty_level)  # convert it to integer value
        print(Difficulty_level)
        Spawn_Rate =  Difficulty_level * 4/5     # Spawn rate increases by 80 %
        Speed[0] = Speed[0] * Difficulty_level   
        Speed[1] = int(5 * Difficulty_level /2) # speed increases by 250 %
        print(Speed)

#*****************************************************************************
#*****************************************************************************

    if(Lives<=0):  # if u run out of lives the game is over
        game_Over=True

    slash=slash.reshape((-1,1,2))                     # reshape the slash array in order to draw a polyline a visualize the slash
    cv2.polylines(img,[slash],False,slash_Color,15,0) # draw the slash

    curr_Frame = time.time()
    delta_Time = curr_Frame - prev_Frame
    FPS = int(1/delta_Time)                 #calculating the fps
    cv2.putText(img,"FPS : " +str(FPS),(int(w*0.82),50),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,250,0),2)                 #printing the fps on the screen
    cv2.putText(img,"Score: "+str(Score),(int(w*0.35),90),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),5)                 #printing the score on the screen
    cv2.putText(img,"Level: "+str(Difficulty_level),(int(w*0.01),90),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,150),5)    #printing the Level on the screen
    cv2.putText(img,"Lives remaining : " + str(Lives), (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)  #printing remaining lives on the screen


    prev_Frame = curr_Frame

    #***********************************************************
    if not (game_Over):                               # if the game is still not over then keep spawning and moving the fruits
        if  (time.time() > next_Time_to_Spawn):       
            Spawn_Fruits()
            next_Time_to_Spawn = time.time() + (1 / Spawn_Rate)

        Fruit_Movement(Fruits,Speed)


    else:                                     # if game is over then print it and clear all the fruits
        cv2.putText(img, "GAME OVER", (int(w * 0.1), int(h * 0.6)), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 3)
        Fruits.clear()
        
    cv2.imshow("img", img)                    #display the resulting image

    if cv2.waitKey(5) & 0xFF == ord("q"):     # the "q" button to quit
        break

cap.release()                                 # release the webcam
cv2.destroyAllWindows()
