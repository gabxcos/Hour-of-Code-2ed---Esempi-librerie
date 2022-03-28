"""
Questo progetto è stato tradotto e adattato da questa repository:
https://github.com/adarsh1021/facedetection

Articolo completo qui:
https://towardsdatascience.com/face-detection-in-2-minutes-using-opencv-python-90f89d7c0f81
"""

import cv2 # pip install opencv-python

"""
Guida completa al classificatore Haar feature-based cascade:
https://docs.opencv.org/3.4/db/d28/tutorial_cascade_classifier.html
"""

# Carica il classificatore dalla libreria, usando la matrice di pesi definita da file .xml
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Ottieni output video dalla fotocamera
cap = cv2.VideoCapture(0)
# In alternativa, si può utilizzare un file video:
# cap = cv2.VideoCapture('filename.mp4')

while True:
    # Ottieni il singolo frame di immagine
    _, img = cap.read()
    # Converti in bianco e nero (il modello non opera a colori!)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Trova le facce
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Disegna un rettangolo attorno ad ogni faccia
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    # Mostra a schermo
    cv2.imshow('img', img)
    # Blocca l'esecuzione se si preme il tasto ESC
    k = cv2.waitKey(30) & 0xff # Limita all'ultimo byte con un AND numerico
    if k==27:
        break
# Rilascia l'oggetto VideoCapture
cap.release()