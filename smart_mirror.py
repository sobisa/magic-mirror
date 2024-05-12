import tkinter as tk
from tkinter import ttk

import time
from flask import Flask, render_template
import cv2
import face_recognition
import threading
from selenium import webdriver
def recognize():


    known_images = [
        {'name': 'sobhan', 'image_path': "sobhan.jpg"}
    ]

    known_encodings = []
    known_names = []
    check = 2

    for image_data in known_images:
        image = face_recognition.load_image_file(image_data['image_path'])
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            encoding = encodings[0]
            known_encodings.append(encoding)
            known_names.append(image_data['name'])

    # Initialize the webcam
    video_capture = cv2.VideoCapture(0)

    # Initialize the Flask app
    app = Flask(__name__)

    @app.route('/')
    def index():
        if check == 0:
            return render_template('someone.html')
        elif check == 1:
            return render_template('page.html')
        else:
            return render_template('none.html')

    # Run the Flask app in a separate thread
    def run_flask_app():
        app.run(port=5000)

    # Start the Flask app
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Set up the Selenium WebDriver
    url = 'http://127.0.0.1:5000/'
    driver = webdriver.Chrome()  # Assuming you have Chrome WebDriver installed
    driver.get(url)

    # Reload the page every 3 seconds
    def reload_page():
        while True:
            time.sleep(0.5)
            driver.refresh()
            driver.switch_to.window(driver.window_handles[0])  # Switch to the new tab

    # Start the page reload thread
    reload_thread = threading.Thread(target=reload_page)
    reload_thread.start()

    while True:
        # Capture frame-by-frame from the webcam
        ret, frame = video_capture.read()

        # Resize the frame to speed up face recognition
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (OpenCV format) to RGB color (face_recognition format)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find all the faces and their encodings in the frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        if len(face_encodings) == 0:
            check = 2  # Set check to 2 when no faces are detected

        # Iterate over each face in the frame
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare the face encoding with the known encodings
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = 'Unknown'

            # Check if there is a match
            if True in matches:
                match_index = matches.index(True)
                name = known_names[match_index]
                print(name)
                check = 1
            else:
                print('unknown')
                check = 0

        # Break the loop if 'q' is pressed
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     driver.quit()  # Close the Selenium WebDriver
        #     break

    # Release the webcam and destroy the OpenCV windows
    video_capture.release()
    cv2.destroyAllWindows()


root = tk.Tk()
root.geometry("900x500")

# Create a custom style for the button with curved corners
style = ttk.Style()
style.configure("TButton",
                relief="raised",
                borderwidth=50,
                font=("Arial", 12),
                padding=10)
style.map("TButton",
          foreground=[('pressed', 'gray'), ('active', 'blue')],
          background=[('pressed', '!disabled', 'blue'), ('active', 'white')])

# Create the button with curved corners
button = ttk.Button(root, text="Start Mirror", command=recognize, style="TButton")
button.pack()

root.mainloop()