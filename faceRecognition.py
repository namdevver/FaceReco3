import face_recognition
import cv2
import pickle
import os
import time
import numpy as np
import tempfile
from tqdm import tqdm
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from time import sleep
import tkinter as tk
import tkinter as tk2
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import *
from tkinter import ttk
from tkinter.ttk import Progressbar, Style
from datetime import datetime
from pathlib import Path
import logging as log
import sys
import glob
import os
from termcolor import colored
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import smtplib

gauth = GoogleAuth()
drive = GoogleDrive(gauth)
#sys.path.append(os.getcwd())

# class: Dlib Face Unlock
# Purpose: This class will update the encoded known face if the directory has changed
# as well as encoding a face from a live feed to compare the face to allow the facial recognition
# to be integrated into the system
# Methods: ID
class Dlib_Face_Unlock:
    def __init__(self):
        try:
            with open(r'C:\Users\barry\PycharmProjects\face_rec\labels.pickle', 'rb') as self.f:
                self.og_labels = pickle.load(self.f)
            print(self.og_labels)
        # error checking
        except FileNotFoundError:

            print("No label.pickle file detected, will create required pickle files")

        # this will be used to for selecting the photos
        self.current_id = 0
        # creating a blank ids dictionary
        self.labels_ids = {}
        # this is the directory where all the users are stored
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.image_dir = os.path.join(self.BASE_DIR, 'images')
        for self.root, self.dirs, self.files in os.walk(self.image_dir):
            # checking each folder in the images directory
            for self.file in self.files:
                # looking for any png or jpg files of the users
                if self.file.endswith('png') or self.file.endswith('jpg'):
                    # getting the folder name, as the name of the folder will be the user
                    self.path = os.path.join(self.root, self.file)
                    self.label = os.path.basename(os.path.dirname(self.path)).replace(' ', '-').lower()
                    if not self.label in self.labels_ids:
                        # adding the user into the labels_id dictionary
                        self.labels_ids[self.label] = self.current_id
                        self.current_id += 1
                        self.id = self.labels_ids[self.label]

        print(self.labels_ids)
        # this is compare the new label ids to the old label ids dictionary seeing if their has been any new users or old users
        # being added to the system, if there is no change then nothing will happen
        self.og_labels = 0
        toolbar_width = 40

        s = Style(root)
        # add the label to the progressbar style
        s.layout("LabeledProgressbar",
                 [('LabeledProgressbar.trough',
                   {'children': [('LabeledProgressbar.pbar',
                                  {'side': 'right', 'sticky': 'ns'}),
                                 ("LabeledProgressbar.label",  # label inside the bar
                                  {"sticky": ""})],
                    'sticky': 'nswe'})])

        p = Progressbar(root, orient="horizontal", length=300,
                        style="LabeledProgressbar")
        p.grid()

        # change the text of the progressbar,
        # the trailing spaces are here to properly center the text
        s.configure("LabeledProgressbar", text="0%")

        if self.labels_ids != self.og_labels:
            # if the dictionary change then the new dictionary will be dump into the pickle file
            with open('labels.pickle', 'wb') as self.file:
                pickle.dump(self.labels_ids, self.file)

            self.known_faces = []
            for self.i in self.labels_ids:

                noOfImgs = len([filename for filename in os.listdir('images/' + mssv.get() + self.i)
                                                        if os.path.isfile(os.path.join('images/' + mssv.get() +
                                                                                       self.i, filename))])
                print("Dang load ", end='')
                print(noOfImgs, end='')
                print(" hinh cua ", end='')
                print(self.i)

                # setup toolbar
                sys.stdout.write("[%s]" % (" " * toolbar_width))
                sys.stdout.flush()
                sys.stdout.write("\b" * (toolbar_width + 1))  # return to start of line, after '['

                for imgNo in range(1, (noOfImgs + 1)):
                    self.directory = os.path.join(self.image_dir, self.i, str(imgNo) + '.png')
                    self.img = face_recognition.load_image_file(self.directory)
                    self.img_encoding = face_recognition.face_encodings(self.img)[0]
                    self.known_faces.append([self.i, self.img_encoding])
                    #sf = self.directory.count(self.image_dir)
                    #sfd = self.directory.count(self.i)

                    time.sleep(0.1)  # do real work here
                    # update the bar
                    percent = str(round((imgNo/noOfImgs)*100))
                    percent2 = str("Dang load " + str(imgNo) + "/" + str(noOfImgs) + "anh cua " + self.i)
                    p.step((noOfImgs/imgNo)/1.22)
                    s.configure("LabeledProgressbar", text="{0}".format(percent2))
                    root.update()
                    sys.stdout.write(colored(percent + "% ","green"))
                    sys.stdout.flush()

                sys.stdout.write("]\n")

            print(self.known_faces)
            print("No Of Imgs" + str(len(self.known_faces)))

            with open('KnownFace.pickle', 'wb') as self.known_faces_file:
                pickle.dump(self.known_faces, self.known_faces_file)
        else:
            with open(r'CC:\Users\barry\PycharmProjects\face_rec\KnownFace.pickle', 'rb') as self.faces_file:
                self.known_faces = pickle.load(self.faces_file)
            print(self.known_faces)

    # Method: ID
    # Purpose:This is method will be used to create a live feed .i.e turning on the devices camera
    # then the live feed will be used to get an image of the user and then encode the users face
    # once the users face has been encoded then it will be compared to in the known faces
    # therefore identifying the user
    def ID(self):
        # turning on the camera to get a photo of the user frame by frame
        self.cap = cv2.VideoCapture(0)
        # seting the running variable to be true to allow me to known if the face recog is running
        self.running = True
        self.face_names = []
        while self.running == True:
            # taking a photo of the frame from the camera
            self.ret, self.frame = self.cap.read()
            # resizing the frame so that the face recog module can read it
            self.small_frame = cv2.resize(self.frame, (0, 0), fx=0.5, fy=0.5)
            # converting the image into black and white
            self.rgb_small_frame = self.small_frame[:, :, ::-1]
            if self.running:
                # searching the black and white image for a face
                self.face_locations = face_recognition.face_locations(self.frame)

                # if self.face_locations == []:
                #     Dlib_Face_Unlock.ID(self)
                # it will then encode the face into a matrix
                self.face_encodings = face_recognition.face_encodings(self.frame, self.face_locations)
                # creating a names list to append the users identify into
                self.face_names = []
                # looping through the face_encoding that the system made
                for self.face_encoding in self.face_encodings:
                    # looping though the known_faces dictionary
                    for self.face in self.known_faces:
                            # using the compare face method in the face recognition module
                            self.matches = face_recognition.compare_faces([self.face[1]], self.face_encoding)
                            print(self.matches)
                            self.name = 'Unknown'
                            # compare the distances of the encoded faces
                            self.face_distances = face_recognition.face_distance([self.face[1]], self.face_encoding)

                            # uses the numpy module to comare the distance to get the best match
                            self.best_match = np.argmin(self.face_distances)
                            print(self.best_match)
                            print('This is the match in best match', self.matches[self.best_match])

                            if self.matches[self.best_match] == True:
                                self.running = False
                                self.face_names.append(self.face[0])
                                break
                            next
            print("The best match(es) is" + str(self.face_names))
            self.cap.release()
            cv2.destroyAllWindows()
            break
        return self.face_names


"""
dfu = Dlib_Face_Unlock()
dfu.ID()
"""



def draw():
    cascPath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)
    log.basicConfig(filename='webcam.log', level=log.INFO)

    cam = cv2.VideoCapture(0)
    anterior = 0

    # Capture frame-by-frame
    ret, frame = cam.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    if anterior != len(faces):
        anterior = len(faces)
        log.info("faces: "+str(len(faces))+" at "+str(datetime.now()))
    draw()

def register():
    # Create images folder
    if not os.path.exists("images"):
        os.makedirs("images")
    # Create folder of person (IF NOT EXISTS) in the images folder
    if mssv!=None:
        Path("images/" + mssv.get() + "-" + name.get()).mkdir(parents=True, exist_ok=True)
    else:
        Path("images/" + name.get()).mkdir(parents=True, exist_ok=True)
    # Obtain the number of photos already in the folder
    if mssv != None:
        numberOfFile = len([filename for filename in os.listdir('images/' + mssv.get() + name.get())
                        if os.path.isfile(os.path.join('images/' + mssv.get() + name.get(), filename))])
    else:
        numberOfFile = len([filename for filename in os.listdir('images/' + name.get())
                            if os.path.isfile(os.path.join('images/' + name.get(), filename))])

    # Add 1 because we start at 1
    numberOfFile += 1
    # Take a photo code
    cam = cv2.VideoCapture(0)

    cv2.namedWindow("test")

    while True:
        ret, frame = cam.read()

        anterior = 0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cascPath = "haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(cascPath)
        log.basicConfig(filename='webcam.log', level=log.INFO)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if anterior != len(faces):
            anterior = len(faces)
            log.info("faces: " + str(len(faces)) + " at " + str(datetime.now()))

        cv2.imshow("test", frame)
        if not ret:
            break
        k = cv2.waitKey(1)


        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            cam.release()
            cv2.destroyAllWindows()
            break
        elif k % 256 == 32:
            # SPACE pressed

                img_name = str(numberOfFile) + ".png"
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                os.replace(str(numberOfFile) + ".png", "images/" + mssv.get().lower() + "-" +
                           name.get().lower() + "/" + str(numberOfFile) + ".png")
                numberOfFile += 1
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    raiseFrame(loginFrame)


# Passing in the model
def login():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Log In")

    while True:
        ret, frame = cam.read()

        anterior = 0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cascPath = "haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(cascPath)
        log.basicConfig(filename='webcam.log', level=log.INFO)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if anterior != len(faces):
            anterior = len(faces)
            log.info("faces: " + str(len(faces)) + " at " + str(datetime.now()))
        cv2.imshow("Log In", frame)

        if not ret:
            break
        k = cv2.waitKey(1)

        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            cam.release()
            cv2.destroyAllWindows()
            break
        elif k % 256 == 32:
            # SPACE pressed
            cam.release()
            cv2.destroyAllWindows()
            break

    # After someone has registered, the face scanner needs to load again with the new face
    dfu = Dlib_Face_Unlock()

    # Will return the user's name as a list, will return an empty list if no matches
    user = dfu.ID()
    if user == []:
        messagebox.showerror("Alert", "Face Not Recognised")
        return
    loggedInUser.set(user[0])
    num1 = loggedInUser.get()
    outfile = open('checkin.txt', 'a')
    outfile.write("\nUser %s logged in at %s" % (num1,datetime.now()))

    now = datetime.now()
    date_time = now.strftime("%m%d%Y")
    if not os.path.exists("Diem-danh"):
        os.makedirs("Diem-danh")
    # Create folder of person (IF NOT EXISTS) in the images folder
    Path("Diem-danh/" + date_time).mkdir(parents=True, exist_ok=True)
    imag_name = "Diem-danh/" + str(date_time) + "/" + num1 + ".png"
    cv2.imwrite(imag_name, frame)
    print("Da luu file diem danh {} !".format(imag_name))

    upload_file_list = ["Diem-danh/" + str(date_time) + "/" + num1 + ".png"]
    for upload_file in upload_file_list:
        gfile = drive.CreateFile({'parents': [{'id': '1E0zWiUKmeAqa6JMiacmCMXrMhRzkPCvA'}]})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(upload_file)
        gfile.Upload()  # Upload the file.

    os.replace("Diem-danh/" + str(date_time) + "/" + num1 + ".png", "Diem-danh/" + str(date_time) + "/" + num1 + ".png")
    #subprocess.Popen(r'explorer "C:/Users/NAM/PycharmProjects/faceR/Diem-danh/"' + str(date_time))

    raiseFrame(userMenuFrame)

master = Tk()
master.title = 'Custom Email App'

def report():
    # Functions
    def send():
        try:
            username = temp_username.get()
            password = temp_password.get()
            to = temp_receiver.get()
            subject = temp_subject.get()
            body = temp_body.get()
            if username == "" or password == "" or to == "" or subject == "" or body == "":
                notif.config(text="All fields required", fg="red")
                return
            else:
                finalMessage = 'Subject: {}\n\n{}'.format(subject, body)
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(username, password)
                server.sendmail(username, to, finalMessage)
                notif.config(text="Email has been sent successfully", fg="green")
        except:
            notif.config(text="Error sending email", fg="red")

    def reset():
        usernameEntry.delete(0, 'end')
        passwordEntry.delete(0, 'end')
        receiverEntry.delete(0, 'end')
        subjectEntry.delete(0, 'end')
        bodyEntry.delete(0, 'end')

    # Labels
    Label(master, text="Custom Email App", font=('Calibri', 15)).grid(row=0, sticky=N)
    Label(master, text="Please use the form below to send an email", font=('Calibri', 11)).grid(row=1, sticky=W, padx=5,
                                                                                                pady=10)

    Label(master, text="Email", font=('Calibri', 11)).grid(row=2, sticky=W, padx=5)
    Label(master, text="Password", font=('Calibri', 11)).grid(row=3, sticky=W, padx=5)
    Label(master, text="To", font=('Calibri', 11)).grid(row=4, sticky=W, padx=5)
    Label(master, text="Subject", font=('Calibri', 11)).grid(row=5, sticky=W, padx=5)
    Label(master, text="Body", font=('Calibri', 11)).grid(row=6, sticky=W, padx=5)
    notif = Label(master, text="", font=('Calibri', 11), fg="red")
    notif.grid(row=7, sticky=S)

    # Storage
    temp_username = StringVar()
    temp_password = StringVar()
    temp_receiver = StringVar()
    temp_subject = StringVar()
    temp_body = StringVar()

    # Entries
    usernameEntry = Entry(master, textvariable=temp_username)
    usernameEntry.grid(row=2, column=0)
    passwordEntry = Entry(master, show="*", textvariable=temp_password)
    passwordEntry.grid(row=3, column=0)
    receiverEntry = Entry(master, textvariable=temp_receiver)
    receiverEntry.grid(row=4, column=0)
    subjectEntry = Entry(master, textvariable=temp_subject)
    subjectEntry.grid(row=5, column=0)
    bodyEntry = Entry(master, textvariable=temp_body)
    bodyEntry.grid(row=6, column=0)

    # Buttons
    Button(master, text="Send", command=send).grid(row=7, sticky=W, pady=15, padx=5)
    Button(master, text="Reset", command=reset).grid(row=7, sticky=W, padx=45, pady=40)

    # Mainloop
    master.mainloop()

    raiseFrame(reportFrame)

# Tkinter
root = tk.Tk()
root.title("Face Login Example")
# Frames
loginFrame = tk.Frame(root)
regFrame = tk.Frame(root)
userMenuFrame = tk.Frame(root)
reportFrame = tk.Frame(root)

# Define Frame List
frameList = [loginFrame, regFrame, userMenuFrame, reportFrame]
# Configure all Frames
for frame in frameList:
    frame.grid(row=0, column=0, sticky='news')
    frame.configure(bg='white')

def OpenDir():
    num11 = loggedInUser.get()
    subprocess.Popen(r'explorer "C:\Users\NAM\PycharmProjects\faceR\images\"' + num11)

def raiseFrame(frame):
    frame.tkraise()

def regFrameRaiseFrame():
    raiseFrame(regFrame)

def logFrameRaiseFrame():
    raiseFrame(loginFrame)

def reportFrameRaiseFrame():
    raiseFrame(reportFrame)

# Tkinter Vars
# Stores user's name when registering
name = tk.StringVar()
mssv = tk.StringVar()
# Stores user's name when they have logged in
loggedInUser = tk.StringVar()

tk.Label(loginFrame, text="Nhận diện khuôn mặt", font=("Courier", 60), bg="white").grid(row=1, column=1, columnspan=5)
loginButton = tk.Button(loginFrame, text="Điểm danh", bg="Cyan", font=("Arial", 30), command=login)
loginButton.grid(row=2, column=5)
reportButton = tk.Button(reportFrame, text="Báo lỗi", bg="Red", font=("Arial", 30), command=report)
reportButton.grid(row=2, column=3)
regButton = tk.Button(loginFrame, text="Đăng ký", command=regFrameRaiseFrame, bg="green", font=("Arial", 30))
regButton.grid(row=2, column=1)

tk.Label(regFrame, text="Register", font=("Courier", 60), bg="white").grid(row=1, column=1, columnspan=5)
tk.Label(regFrame, text="Nhập MSSV : ", font=("Arial", 30), bg="white").grid(row=2, column=1)
nameEntry = tk.Entry(regFrame, textvariable=mssv, font=("Arial", 30)).grid(row=2, column=2)
tk.Label(regFrame, text="Nhập tên : ", font=("Arial", 30), bg="white").grid(row=3, column=1)
nameEntry = tk.Entry(regFrame, textvariable=name, font=("Arial", 30)).grid(row=3, column=2)
registerButton = tk.Button(regFrame, text="Register", command=register, bg="white", font=("Arial", 30))
registerButton.grid(row=4, column=2)

tk.Label(userMenuFrame, text="Hello, ", font=("Courier", 20), bg="white").grid(row=1, column=1)
tk.Label(userMenuFrame, textvariable=loggedInUser, font=("Courier", 20), bg="white", fg="red").grid(row=1, column=2)
tk.Label(userMenuFrame, text="Logged in at", font=("Courier", 20), bg="white").grid(row=2, column=1)
tk.Label(userMenuFrame, text=" %s" % (datetime.now()), font=("Courier", 20), bg="white").grid(row=2, column=2)
tk.Button(userMenuFrame, text="All photos", font=("Arial", 30), command=OpenDir).grid(row=3, column=1)
tk.Button(userMenuFrame, text="Back", font=("Arial", 30), command=logFrameRaiseFrame).grid(row=3, column=2)

# Load Faces
#dfu = Dlib_Face_Unlock()
raiseFrame(loginFrame)
root.mainloop()

