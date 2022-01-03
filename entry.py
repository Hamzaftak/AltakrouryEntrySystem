import os
from os import walk
import glob
import numpy as np
import pandas as pd
import face_recognition
import cv2
import datetime
import pdb
import tkinter
from tkinter import *
import tkinter.filedialog as Tkf
from tkinter import messagebox

global images_path 
global video_file 
global table_path 
global res

images_path = 0
video_file = 0
table_path = 0

def browsefunc1():
    global video_file
    video_file = Tkf.askopenfilename(filetypes=(("MP4 files","*.mp4"),("AVI files","*.avi"),("All files","*.*")))
    ent1.insert(tkinter.END, video_file) # add this
    if (images_path and table_path):
        B.config(state="normal")

def browsefunc2():
    global images_path
    count = 0
    images_path = Tkf.askdirectory()
    ent2.insert(tkinter.END, images_path) # add this
    filenames = next(walk(images_path), (None, None, []))[2]
    for thisfile in filenames:
        thistype = thisfile.split(".")[-1]
        if(thistype == "jpg"):
            count +=1
    if len(filenames) == 0:
        images_path = 0
        ent2.delete(0,"end")
        messagebox.showinfo("Error", "There is no images in the images folder")
    elif len(filenames) == count:
        if((var1.get()==1 or video_file) and table_path):
            B.config(state="normal")
    else:
        images_path = 0
        ent2.delete(0,"end")
        messagebox.showinfo("Error", "All files in the images folder must have jpg extension")

def browsefunc3():
    global table_path
    table_path = Tkf.askdirectory()
    ent3.insert(tkinter.END, table_path) # add this
    #if((video_file or var1.get()==1) and images_path):
    if((var1.get()==1 or video_file) and images_path):
        B.config(state="normal")



def choose_webcam():
    if var1.get() == 1 :
        b1.config(state="disable")
        ent1.config(state="disable")
        if (images_path and table_path):
            B.config(state="normal")
    else:
        b1.config(state="normal")
        ent1.config(state="normal")
        if (~(video_file)):
            B.config(state="disable")


def runfunc():
    if var1.get() == 0:
        
        video_capture = cv2.VideoCapture(video_file)
        frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        my_directory = images_path # change this
        #ratio = 0.5 # Change this
        ratios = {
            "Original" : 1,
            "Half" : 0.5,
            "One-fourth" : 0.25
        }
        ratio = ratios[var2.get()]
        try:
            th_time = int(var3.get())
        except ValueError:
            messagebox.showinfo("Error", "The entered time should be integer")
            return
        columns = ["Name","Year", "Month", "Day", "Hour", "Minute", "Second"]
        df = pd.DataFrame(columns=columns)
        reg_names = []
        reg_times = []

        known_face_encodings = []
        known_face_names = []
        for filepath in glob.iglob(my_directory +'/*.jpg'):
            image = face_recognition.load_image_file(filepath)
            full_name = os.path.basename(filepath)
            known_face_names.append(full_name[0:full_name.find('.')])
            image_encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(image_encoding)

        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        for i in range(frame_count):
            # Grab a single frame of video
            ret, frame = video_capture.read()
            small_frame = cv2.resize(frame, (0, 0), fx=ratio, fy=ratio)
            rgb_small_frame = small_frame[:, :, ::-1]
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"
                    # if True in matches:
                    #      first_match_index = matches.index(True)
                    #      name = known_face_names[first_match_index]
            
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index] and np.min(face_distances)<0.5: # Here I added a thrishold
                        name = known_face_names[best_match_index]
                        if name not in reg_names:
                            reg_names.append(name)
                            reg_time = datetime.datetime.now() 
                            reg_times.append(reg_time)
                            df = df.append({'Name': name, "Year": reg_time.year, "Month": reg_time.month, "Day": reg_time.day, "Hour": reg_time.hour, "Minute": reg_time.minute, "Second": reg_time.second}, ignore_index=True)
                        else:
                            for i in range(len(reg_names)):
                                if reg_names[i] == name:
                                    index = i
                            if (datetime.datetime.now() - reg_times[index]).seconds > th_time:
                                reg_names.append(name)
                                reg_time = datetime.datetime.now() 
                                reg_times.append(reg_time)
                                df = df.append({'Name': name, "Year": reg_time.year, "Month": reg_time.month, "Day": reg_time.day, "Hour": reg_time.hour, "Minute": reg_time.minute, "Second": reg_time.second}, ignore_index=True)
                    face_names.append(name)

            process_this_frame = not process_this_frame
    
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= int(1/ratio)
                right *= int(1/ratio)
                bottom *= int(1/ratio)
                left *= int(1/ratio)

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)

            # Hit 'q' on the keyboard to quit! (The error comes rom the next lines)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break    
            # if video_capture.isOpened() == False:
            #     df.to_csv(my_directory + '/times.csv')
            #     break


        # Release handle to the webcam
        df.to_csv(table_path + '/times.csv')
        video_capture.release()
        cv2.destroyAllWindows()
    
    else:

        video_capture = cv2.VideoCapture(0)
        #frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        my_directory = images_path # change this
        #ratio = 0.5 # Change this
        ratios = {
            "Original" : 1,
            "Half" : 0.5,
            "One-fourth" : 0.25
        }
        ratio = ratios[var2.get()]
        try:
            th_time = int(var3.get())
        except ValueError:
            messagebox.showinfo("Error", "The entered time should be integer")
            return
        columns = ["Name","Year", "Month", "Day", "Hour", "Minute", "Second"]
        df = pd.DataFrame(columns=columns)
        reg_names = []
        reg_times = []

        known_face_encodings = []
        known_face_names = []
        for filepath in glob.iglob(my_directory +'/*.jpg'):
            image = face_recognition.load_image_file(filepath)
            full_name = os.path.basename(filepath)
            known_face_names.append(full_name[0:full_name.find('.')])
            image_encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(image_encoding)

        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()
            small_frame = cv2.resize(frame, (0, 0), fx=ratio, fy=ratio)
            rgb_small_frame = small_frame[:, :, ::-1]
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"
                    # if True in matches:
                    #      first_match_index = matches.index(True)
                    #      name = known_face_names[first_match_index]
            
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index] and np.min(face_distances)<0.5: # Here I added a thrishold
                        name = known_face_names[best_match_index]
                        if name not in reg_names:
                            reg_names.append(name)
                            reg_time = datetime.datetime.now() 
                            reg_times.append(reg_time)
                            df = df.append({'Name': name, "Year": reg_time.year, "Month": reg_time.month, "Day": reg_time.day, "Hour": reg_time.hour, "Minute": reg_time.minute, "Second": reg_time.second}, ignore_index=True)
                        else:
                            for i in range(len(reg_names)):
                                if reg_names[i] == name:
                                    index = i
                            if (datetime.datetime.now() - reg_times[index]).seconds > th_time:
                                reg_names.append(name)
                                reg_time = datetime.datetime.now() 
                                reg_times.append(reg_time)
                                df = df.append({'Name': name, "Year": reg_time.year, "Month": reg_time.month, "Day": reg_time.day, "Hour": reg_time.hour, "Minute": reg_time.minute, "Second": reg_time.second}, ignore_index=True)
                    face_names.append(name)

            process_this_frame = not process_this_frame
    
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= int(1/ratio)
                right *= int(1/ratio)
                bottom *= int(1/ratio)
                left *= int(1/ratio)

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)

            # Hit 'q' on the keyboard to quit! (The error comes rom the next lines)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break    
            # if video_capture.isOpened() == False:
            #     df.to_csv(my_directory + '/times.csv')
            #     break


        # Release handle to the webcam
        df.to_csv(table_path + '/times.csv')
        video_capture.release()
        cv2.destroyAllWindows()


root=tkinter.Tk()
root.title("Altakroury Entry System")
var1 = tkinter.IntVar()
global var2 
var2 = tkinter.StringVar()
var2.set("Original")
global var3
var3 = tkinter.StringVar()

ent1=tkinter.Entry(root,font=40)
ent1.grid(row=2,column=2)
b1=tkinter.Button(root,text="Video File",font=40,command=browsefunc1)
b1.grid(row=2,column=4)

c1 = tkinter.Checkbutton(root, text='Webcam',variable=var1, onvalue=1, offvalue=0, command=choose_webcam)
c1.grid(row=2,column=6)

ent2=tkinter.Entry(root,font=40)
ent2.grid(row=4,column=2)
b2=tkinter.Button(root,text="Images Folder",font=40,command=browsefunc2)
b2.grid(row=4,column=4)

ent3=tkinter.Entry(root,font=40)
ent3.grid(row=6,column=2)
b3=tkinter.Button(root,text="Table Path",font=40,command=browsefunc3)
b3.grid(row=6,column=4)

l1 = Label(root, text = "Input resolution ratio",font=25)
l1.grid(row=8,column=2)
d1 = OptionMenu(root, var2, "Original", "Half", "One-fourth")
d1.grid(row=8,column=4)

l2 = Label(root, text = "Time between registrations",font=25)
l2.grid(row=10,column=2)
ent4=tkinter.Entry(root,textvariable=var3,font=40)
#ent4.insert(END, '20')
ent4.grid(row=10,column=4)
l3 = Label(root, text = "seconds",font=25)
l3.grid(row=10,column=6)

B=tkinter.Button(root,text="Run",state="disable",command= runfunc)
B.grid(row=12,column=2)

root.mainloop()


