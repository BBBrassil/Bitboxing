import tkinter as tk
import cv2 as cv
from PIL import Image, ImageTk
import pyzbar.pyzbar as pyzbar

width, height = 800, 600
camera = None
scanner = None
code = ""

btn = None

def scan():
    global code
    global scanner
    
    _, frame = camera.read()
    img = Image.fromarray(cv.cvtColor(cv.flip(frame, 1), cv.COLOR_BGR2RGBA))
    scanner.imgtk = ImageTk.PhotoImage(image=img)
    scanner.configure(image=scanner.imgtk)
    
    code = ""
    decoded = pyzbar.decode(frame)
    for x in decoded:
        code = x.data.decode()
    
    scanner.after(10, scan if code == "" else stop_scan)

def stop_scan():
    print(code)
    scanner.configure(image="")

window = tk.Tk()
window.geometry(f"{width}x{height}")

camera = cv.VideoCapture(0)

btn = tk.Button(window, text="Scan QR Code", command=scan)
btn.pack()

scanner = tk.Label(window)
scanner.pack()

window.mainloop()