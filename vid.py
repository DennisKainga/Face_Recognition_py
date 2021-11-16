import os
import face_recognition
import cv2
from time import ctime
from tkinter import * 
import tkinter as tk
from tkinter import messagebox
import sqlite3
import pandas as pd
import sys
from datetime import datetime

#CREATE CONNECTION TO DB
conn = sqlite3.connect('example.sql')
c = conn.cursor()
root = Tk()
root.title("FACE RECOGNTION")
KNOWN_FACES_DIR = 'known'

#UNKNOWN_FACES_DIR = 'unknown'
FRAME_THICKNESS = 2
FONT_THICKNESS = 2
TOLERANCE = 0.5
MODEL  = "mtcnn"
known_names=[]
known_faces=[]
number_of_people=[]
unknown_faces=[]
found_faces= []
photos = []
time = ctime()

def exit():
    response = messagebox.askyesno("WARNING","ARE YOU SURE ?")
    if response == 0: #0 if it is responded with yes and 1 if responded with NO
        pass
    else:
        sys.exit()
def markAttendance(name):
    with open('Attendance.csv','r+') as f:
        data = f.readlines()
        nameList = []
        for line in data:
            entry = line.split(',')
            nameList.append(entry[0])
        now = datetime.now()
        dtString =now.strftime('%H:%M:%S')
        tday = datetime.date(datetime.now())
        f.writelines(f'\n{name},{dtString},{tday}')

def fetchFromDB(match):
    names =[]
    names.append(match)
    list2= []
    for name in names:
        list2.extend(name.split())
        try:
            firstName,lastName=list2
        except ValueError:
            firstName,lastName,alias = list2
        c.execute('SELECT * FROM names WHERE fName=? AND lName=?',(firstName,lastName))
        a= c.fetchone()
        print(a)

def refresh_db():
    conn=sqlite3.connect('example.sql')
    c = conn.cursor()
    c.execute("UPDATE names SET fName = UPPER(fName)")
    c.execute("UPDATE names SET lName = UPPER(lName)")
    conn.commit()
    conn.close()
    messagebox.showinfo("SUCCESS","GOOD TO GO !!")

def train_module():
    #LOAD THE KNOWN FACES
    try:
        for names in os.listdir(f"{KNOWN_FACES_DIR}"):    
            for filename in os.listdir (f"{KNOWN_FACES_DIR}/{names}"):
                number_of_people.append(filename)
                image = f"{KNOWN_FACES_DIR}/{names}/{filename}"
                #print(image)
                image = face_recognition.load_image_file(image)
                #print(names)
                try:
                    encoding= face_recognition.face_encodings(image)[0]
                except IndexError:
                    messagebox.showerror("ERROR","Failed to read Face for "f"{names}")
                    break
                known_faces.append(encoding)
                known_names.append(names)
                #messagebox.showinfo("LISTING NAMES ON DB",f"{names}")
    except NotADirectoryError:
        messagebox.showerror("ERROR","PLEASE INSERT ALL IMAGES TO A NAMED FOLDER")
    #print(names)
    if len(known_names) == 0:
        messagebox.showerror("ERROR","NO IDENTIIES FOUND!!")
    elif len(known_names)!=len(number_of_people):#len(next(os.walk(KNOWN_FACES_DIR))):
        messagebox.showerror("ERROR","TRAINING INCOMPLETE")
    else:
    	messagebox.showinfo("SUCCES","TRAINING COMPLETE")
    print(known_names)    	

def recognise():
    video = cv2.VideoCapture(0)
    video.set(3,440)
    video.set(4,300)
    if video == None:
        messagebox.showerror("ERROR","CAN NOT READ VIDEO FILE")
        print("no file loaded")
        sys.exit()
    if len(known_faces) == 0:
        messagebox.showerror("ERROR","TRAIN SYSTEM FIRST")
    else:    
    #LOAD THE UNKNOWN FACES
        while True:
            ret,image = video.read()
            locations = face_recognition.face_locations(image,model=MODEL)
            encodings = face_recognition.face_encodings(image)
            #photos.append(filename)
            unknown_faces.append(encodings)
            #image=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
            for face_encoding,face_location in zip(encodings,locations):
                results = face_recognition.compare_faces(known_faces,face_encoding,TOLERANCE)
                Dist = face_recognition.face_distance(known_faces,face_encoding)
                print(min(Dist))
                match = 'No Match'
                #print(results)
                if True in results:
                    match = known_names[results.index(True)]
                    markAttendance(match)
                    fetchFromDB(match)
                    found_faces.append(match)
                    index = (len(photos))
                    print(f"Match Found For {match}")
                    color = [0,255,0]
                    #YOU CAN USE PANDAS AS WELL df=pd.read_sql_query("SELECT * FROM names WHERE fName='%s' AND lName='%s'"%(firstName,lastName),conn)
                    #print(names)
                    names = []
                    #found = (f"{match}",)
                    conn.commit()
                    #conn.close()
                else:
                    color = [0,0,255]
                top_left = (face_location[3],face_location[0])
                bottom_right = (face_location[1],face_location[2])
                cv2.rectangle(image,top_left,bottom_right,color,FRAME_THICKNESS)
                top_left = (face_location[3], face_location[2])
                bottom_right = (face_location[1], face_location[2]+22)
                cv2.rectangle(image, top_left, bottom_right,color, cv2.FILLED)
                cv2.putText(image, match, (face_location[3]+15, face_location[2]+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), FONT_THICKNESS)
                top_left = (face_location[3],face_location[2])
                bottom_right = (face_location[1],face_location[2]-22)
            cv2.imshow("VIDEO FEED",image)
            if cv2.waitKey(30) == ord('q'):
                #video.release()
                cv2.destroyWindow("VIDEO FEED")
                messagebox.showinfo("END","Video Feed Stopped")
                break
        #conn.close()
def database_configure():
        database = Toplevel()
        database.title("DataBase Configuration")
        def submit():
            conn = sqlite3.connect('example.sql')
            c = conn.cursor()
            #INSERT INTO THE TABLE
            c.execute("INSERT INTO names VALUES (:fName,:lName,:Residence,:idNumber,:birthPlace,:phoneNumber)",
                    {   
                        'fName':fName.get(),
                        'lName':lName.get(),
                        'Residence':Residence.get(),
                        'idNumber':idNumber.get(),
                        'birthPlace':birthPlace.get(),
                        'phoneNumber':phoneNumber.get()
                        })
            conn.commit()
            conn.close()

            #CLEAR THE TEXT BOXES
            fName.delete(0,END)
            lName.delete(0,END)
            Residence.delete(0, END)
            idNumber.delete(0,END)
            birthPlace.delete(0,END)
            phoneNumber.delete(0,END)

        #CREATE TEXT BOXES
        fName = Entry(database,width=30)
        fName.grid(row=0,column=1,padx=0,pady=10)
        lName = Entry(database,width=30)
        lName.grid(row=1,column=1,padx=0,pady=10)
        Residence = Entry(database,width=30)
        Residence.grid(row=2,column=1,padx=0,pady=10)
        idNumber = Entry(database,width=30)
        idNumber.grid(row=3,column=1,padx=10,pady=10)
        birthPlace = Entry(database,width=30)
        birthPlace.grid(row=4,column=1,padx=10,pady=10)
        phoneNumber = Entry(database,width=30)
        phoneNumber.grid(row=5,column=1,padx=10,pady=10)
        #CREATE TEXT BOX LABELS
        fName_label = Label(database,text="FIRST NAME")
        fName_label.grid(row=0,column=0)
        lName_label = Label(database,text="LAST NAME")
        lName_label.grid(row=1,column=0)
        Residence_label = Label(database,text="RESIDENCE")
        Residence_label.grid(row=2,column=0)
        idNumber_label = Label(database,text="ID NUMBER")
        idNumber_label.grid(row=3,column=0)
        birthPlace_label = Label(database,text="PLACE OF BIRTH")
        birthPlace_label.grid(row=4,column=0)
        phoneNumber_label = Label(database,text="PHONE NUMBER")
        phoneNumber_label.grid(row=5,column=0)

        #CREATE BUTTONS

        button_submit = Button(database,text="SUBMIT",command=submit,padx=50)
        button_submit.grid(row=6 , column=0)
def submit():
    conn = sqlite3.connect('example.sql')
    c = conn.cursor()
    #INSERT INTO THE TABLE
    c.execute("INSERT INTO names VALUES (:fName,:lName,:Residence,:idNumber,:birthPlace,:phoneNumber)",
            {   
                'fName':fName.get(),
                'lName':lName.get(),
                'Residence':Residence.get(),
                'idNumber':idNumber.get(),
                'birthPlace':birthPlace.get(),
                'phoneNumber':phoneNumber.get()
                })
    conn.commit()
    conn.close()

    #CLEAR THE TEXT BOXES
    fName.delete(0,END)
    lName.delete(0,END)
    Residence.delete(0, END)
    idNumber.delete(0,END)
    birthPlace.delete(0,END)
    phoneNumber.delete(0,END)

#CEATE TEXT BOXES
def getNewIdentities():
    dataset = tk.Tk()
    dataset.title("DATASET")
    #dataset.geometry('100x100')
    tk.Label(dataset,text="FIRST NAME").grid(row=0)
    tk.Label(dataset,text="LAST NAME").grid(row=1)
    firstName=tk.Entry(dataset)
    lastName=tk.Entry(dataset)
    firstName.grid(row=0,column=1)
    lastName.grid(row=1,column=1)
    def startStreaming():
        cap=cv2.VideoCapture(0)
        cap.set(3,640)
        cap.set(4,480)
        faceCascade = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')
        name = ('%s %s' % (firstName.get(),lastName.get() ))
        print(len(name))
        path ='known'
        print(name)
        if len(name) == 0 or len(name)==1:
            messagebox.showerror("ERROR","FILL THE FIELDS WITH NAMES")
        else:
            try:
                os.mkdir(path+"/"+name)
            except FileExistsError:
                print(f"{name } IS ALREADY IN DATABASE")
                sys.exit()
            count = 0
            firstName.delete(0,END)
            lastName.delete(0,END)
            while True:
                ret,img = cap.read()
                gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                faces=faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(30,30),
                flags=cv2.CASCADE_SCALE_IMAGE
                )
                #print(faces)
                for (x,y,w,h) in faces:
                    cv2.rectangle(gray,(x,y),(x+w,y+h),(0,255,0),2)
                    count+=1
                    h+=10
                    w+=10
                    cv2.imwrite(os.path.join(path,f"{name}/{str(count)}.jpg"),img[y:y+h,x:x+w])
                    cv2.imshow('DataSet',gray)
                    #roi_gray = gray[y:y+h,x:x+w]
                    #roi_color =img[y:y+h,x:x+w]
                k = cv2.waitKey(25)
                if k == 27:
                    break
                    cv2.destroyWindow("DataSet")
                    cap.release()
                elif count>=30:
                    cv2.destroyWindow("DataSet")
                    cap.release()
                    break
        cap.release()
        cv2.destroyAllWindows()

    def abortCapture():
        dataset.destroy()
    tk.Button(dataset, text="START CAPTURE",command=startStreaming).grid(row=3,column=0)
    tk.Button(dataset, text="ABORT",command=abortCapture).grid(row=3,column=2)
fName = Entry(root,width=30)
fName.grid(row=0,column=6,padx=0,pady=10)
lName = Entry(root,width=30)
lName.grid(row=1,column=6,padx=0,pady=10)
Residence = Entry(root,width=30)
Residence.grid(row=2,column=6,padx=0,pady=10)
idNumber = Entry(root,width=30)
idNumber.grid(row=3,column=6,padx=10,pady=10)
birthPlace = Entry(root,width=30)
birthPlace.grid(row=4,column=6,padx=10,pady=10)
phoneNumber = Entry(root,width=30)
phoneNumber.grid(row=5,column=6,padx=10,pady=10)
#CREATE TEXT BOX LABELS
fName_label = Label(root,text="FIRST NAME")
fName_label.grid(row=0,column=5)
lName_label = Label(root,text="LAST NAME")
lName_label.grid(row=1,column=5)
Residence_label = Label(root,text="RESIDENCE")
Residence_label.grid(row=2,column=5)
idNumber_label = Label(root,text="ID NUMBER")
idNumber_label.grid(row=3,column=5)
birthPlace_label = Label(root,text="PLACE OF BIRTH")
birthPlace_label.grid(row=4,column=5)
phoneNumber_label = Label(root,text="PHONE NUMBER")
phoneNumber_label.grid(row=5,column=5)
#CREATE BUTTONS
button_submit = Button(root,text="SUBMIT",command=submit,padx=10,pady=5)
button_submit.grid(row=6 , column=6,columnspan=5)
button_execute = Button(root,text="TRAIN", command=train_module,bg='green', padx=100,pady=40)
button_recognise = Button(root,text="RECOGNISE",command=recognise,bg='blue',padx=100,pady=40)
button_refresh_db = Button(root,text="Refresh Data Base",command=refresh_db,padx=50,pady=20)
button_get_new_data = Button(root,text="ADD PERSONAL",command=getNewIdentities,padx=50,pady=20)
button_exit = Button(root,text="EXIT SYSTEM", command=exit,bg='red',padx=100,pady=9)
button_database_configuration = Button(root,text="ADD RECORD",command=database_configure,bg='blue',padx=40,pady=10)
button_recognise.grid(row=0,column=1)
button_execute.grid(row=0 , column=0)
button_refresh_db.grid(row=1,column=0)
button_get_new_data.grid(row=1,column=1)
button_database_configuration.grid(row=2,column=0)
button_exit.grid(row=4, column=0)
root.mainloop()
