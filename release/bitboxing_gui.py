import bbtp
import bitboxing_data as bbdata
from bitboxing_sender import BitboxingSender
import cv2 as cv
import json
from PIL import Image, ImageTk
import pyzbar.pyzbar as pyzbar
import socket
import tkinter as tk
from tkinter import font as tkfont
import tkinter.messagebox as messagebox

IP = "127.0.0.1"
PORT = 9999
VERSION = "0.1"

class Frame(tk.Frame):
    def __init__(self, parent, controller, *args):
        tk.Frame.__init__(self, parent)
        self.controller = controller
    
    def on_load(self, *args):
        pass

class BitboxingGui(tk.Tk):
    def __init__(self, width, height, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.width = width
        self.height = height
        self.font_title = tkfont.Font(family='Helvetica', size=18, weight="bold")
        self.font_fixed = tkfont.Font(family="Courier", size="14")
        
        frames = tk.Frame(self)
        frames.pack(side="top", fill="both", expand=True)
        frames.grid_rowconfigure(0, weight=1)
        frames.grid_columnconfigure(0, weight=1)
        
        self.sender = None

        self.frames = {}
        for F in [Login, MainMenu, Scanner, PuzzleMenu, MyScore, Leaderboard]:
            name = F.__name__
            frame = F(parent=frames, controller=self)
            self.frames[name] = frame
            
            frame.grid(row=0, column=0, sticky="nsew")

        self.title("Bitboxing")
        self.geometry(f"{self.width}x{height}")
        
        self.load("Login")

    def load(self, name, *args):
        frame = self.frames[name]
        frame.on_load(*args)
        frame.tkraise()
    
    def make_request(self, msg):
        """
        Sends a request to the server and fetches a response.

        @param {str} msg BBTP request
        @return {str}    BBTP response
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))
        
        bbtp.send_msg(s, msg)
        msg = bbtp.receive_msg(s)
        
        s.close()

        return bbtp.parse_response(msg)
    
    def unknown_error(self):
        messagebox.showerror(title="Error", message="An unknown error has occurred.")

class Login(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, controller)
        
        tk.Label(self, text="Login", font=controller.font_title).pack(side="top", fill="x", pady=10)

        tk.Label(self, text="Username").pack()
        entry_username = tk.Entry(self)
        entry_username.pack()
        self.username = entry_username
            
        tk.Label(self, text="Password").pack()
        entry_password = tk.Entry(self)
        entry_password.pack()
        self.password = entry_password

        tk.Button(self, text="Login", command=lambda: self.login()).pack()
    
    def on_load(self, *args):
        self.username.delete(0, tk.END)
        self.username.insert(0, "")

        self.password.delete(0, tk.END)
        self.password.insert(0, "")

        self.controller.sender = None
    
    def login(self):
        username = self.username.get()
        password = self.password.get()
        sender = BitboxingSender(username, VERSION)
        response = self.controller.make_request(sender.handle_login(password))

        if response[0] == bbtp.STATUS_UNAUTHENTICATED:
            response = self.controller.make_request(sender.handle_register(password))

            if response[0] == bbtp.STATUS_OK:
                response = self.controller.make_request(sender.handle_login(password))
        
        if response[0] == bbtp.STATUS_OK:
            self.controller.sender = sender
            self.controller.load("MainMenu")
        elif response[0] == bbtp.STATUS_INCORRECT:
            messagebox.showerror(title="Login Error", message="Invalid password!")
            self.controller.sender = None
        else:
            self.controller.unknown_error()
            self.controller.sender = None

class MainMenu(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, controller)
        
        list_options = tk.Listbox(self)
        list_options.insert(0, "Scanner")
        list_options.insert(1, "My score")
        list_options.insert(2, "Leaderboard")
        list_options.insert(3, "Log out")
        list_options.pack()
        self.options = list_options

        btn_select = tk.Button(self, text="Go", command=lambda: self.select())
        btn_select.pack()
    
    def select(self):
        selection = self.options.curselection()
        if len(selection) == 1:
            option = selection[0]
            if option == 0:
                self.controller.load("Scanner")
            elif option == 1:
                self.controller.load("MyScore")
            elif option == 2:
                self.controller.load("Leaderboard")
            elif option == 3:
                self.controller.load("Login")
            else:
                messagebox.showinfo(title="Option", message=f"You chose option #{selection[0]}")

class Scanner(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, controller)

        self.camera = cv.VideoCapture(0)
        self.code = ""

        tk.Label(self, text="Scan QR Code", font=controller.font_title).pack(side="top", fill="x", pady=10)
        
        scanner = tk.Label(self)
        scanner.pack()
        self.scanner = scanner

        tk.Button(self, text="Cancel", command=lambda: controller.load("MainMenu")).pack()

    def scan(self):
        _, frame = self.camera.read()
        img = Image.fromarray(cv.cvtColor(cv.flip(frame, 1), cv.COLOR_BGR2RGBA))
        self.scanner.imgtk = ImageTk.PhotoImage(image=img)
        self.scanner.configure(image=self.scanner.imgtk)
        
        self.code = ""
        decoded = pyzbar.decode(frame)
        for x in decoded:
            self.code = x.data.decode()
        
        self.scanner.after(10, self.scan if self.code == "" else self.stop_scan)

    def stop_scan(self):
        self.scanner.configure(image="")

        sender = self.controller.sender
        response = self.controller.make_request(sender.handle_find(self.code))

        if response[0] == bbtp.STATUS_OK or response[0] == bbtp.STATUS_WITHOUT_CHANGE:
            self.controller.load("PuzzleMenu", self.code, response[1])
        elif response[0] == bbtp.STATUS_NOT_FOUND:
            self.code = ""
            messagebox.showwarning("QR Scanner Error", "Invalid QR code.")
            self.scanner.after(10, self.scan)
        else:
            self.controller.unknown_error()
    
    def on_load(self, *args):
        self.scan()

class PuzzleMenu(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, controller)
        
        
        tk.Label(self, text="Puzzle", font=controller.font_title).pack(side="top", fill="x", pady=10)
        
        lbl_question = tk.Label(self, text="")
        lbl_question.pack()
        self.question = lbl_question
        
            
        btn_hint = tk.Button(self, text="Hint?", command=self.show_hint)
        btn_hint.place(x=200, y=200)

        lbl_hint = tk.Label(self, text="")
        lbl_hint.place(x=300, y=200)
        self.hint = lbl_hint
        
        btn_solve = tk.Button(self, text="Solve", command=self.solve)
        btn_solve.place(x=200, y=275)

        entry_guess = tk.Entry(self)
        entry_guess.place(x=300, y=275)
        self.guess = entry_guess

        btn_leaderboard = tk.Button(self, text="Leaderboard", command=self.show_leaderboard)
        btn_leaderboard.place(x=200, y=350)

        lbl_leaderboard = tk.Label(self, text="", font=self.controller.font_fixed, justify=tk.LEFT)
        lbl_leaderboard.place(x=200, y=425)
        self.leaderboard = lbl_leaderboard

        tk.Button(self, text="Go Back", command=lambda: self.controller.load("MainMenu")).pack(side=tk.BOTTOM)
        
        self.code = ""
    
    def on_load(self, *args):
        self.question["text"] = ""
        self.hint["text"] = ""
        self.guess.delete(0, tk.END)
        self.leaderboard["text"] = ""

        self.code = args[0]
        self.question["text"] = args[1]
    
    def show_hint(self):
        sender = self.controller.sender
        response = self.controller.make_request(sender.handle_hint(self.code))
        
        if response[0] == bbtp.STATUS_OK:
            self.hint["text"] = response[1]
        elif response[0] == bbtp.STATUS_OUT_OF_ORDER:
            self.warning_already_solved()
        else:
            self.controller.unknown_error()
    
    def solve(self):
        sender = self.controller.sender
        response = self.controller.make_request(sender.handle_solve(self.code, self.guess.get()))

        if response[0] == bbtp.STATUS_OK:
            messagebox.showinfo("Puzzle", "Correct!")
        elif response[0] == bbtp.STATUS_INCORRECT:
            messagebox.showwarning("Puzzle", "Sorry, that is not correct.")
        elif response[0] == bbtp.STATUS_OUT_OF_ORDER:
            self.warning_already_solved()
        else:
            self.controller.unknown_error()
    
    def warning_already_solved(self):
        messagebox.showwarning("Puzzle", "You have already solved this puzzle!")
    
    def show_leaderboard(self):
        sender = self.controller.sender
        response = self.controller.make_request(sender.handle_cache_leaderboard(self.code))

        if response[0] == bbtp.STATUS_OK:
            self.leaderboard["text"] = self.format_leaderboard(response[1])
        else:
            self.controller.unknown_error()

    def format_leaderboard(self, msg):
        leaderboard = json.loads(msg)
        
        s = ""
        for i in range(len(leaderboard)):
            s += f"{i + 1}\t{leaderboard[i]}\n"
        
        return s

class Leaderboard(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, controller)
        
        tk.Label(self, text="Leaderboard", font=controller.font_title).pack(side="top", fill="x", pady=10)

        lbl_response = tk.Label(self, text="", font=self.controller.font_fixed, justify=tk.LEFT)
        lbl_response.pack()
        self.response = lbl_response

        tk.Button(self, text="Go Back", command=lambda: self.controller.load("MainMenu")).pack(side=tk.BOTTOM)

    def format_leaderboard(self, msg):
        leaderboard = [bbdata.PlayerScore.from_dict(x) for x in json.loads(msg)]

        s = "".ljust(4) + "  " + "Player".ljust(40) + "  " + "Finds".ljust(6) + "  " + "Solves".ljust(6) + "\n"
        for i in range(len(leaderboard)):
            x = leaderboard[i]
            s += str(i + 1).ljust(4) + "  " + x.player().ljust(40) + "  " + str(x.finds()).ljust(6) + "  " + str(x.solves()).ljust(6) + "\n"
        
        return s
    
    def on_load(self, *args):
        self.response["text"] = ""
        sender = self.controller.sender
        response = self.controller.make_request(sender.handle_leaderboard())

        if response[0] == bbtp.STATUS_OK:
            self.response["text"] = self.format_leaderboard(response[1])
        elif response[0] == bbtp.STATUS_EXCEPTION:
            messagebox.showerror("Leaderboard Error", response[1])
        else:
            self.controller.unknown_error()

class MyScore(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, controller)

        tk.Label(self, text="My Score", font=controller.font_title).pack(side="top", fill="x", pady=10)
        
        lbl_response = tk.Label(self, text="", font=self.controller.font_fixed, justify=tk.LEFT)
        lbl_response.pack()
        self.response = lbl_response

        tk.Button(self, text="Go Back", command=lambda: self.controller.load("MainMenu")).pack(side=tk.BOTTOM)

    def format_my_score(self, msg):
        score = bbdata.PlayerScore.from_dict(json.loads(msg))
        
        s = f"Finds:  {score.finds()}\n" + \
            f"Solves: {score.solves()}\n"
        
        return s
    
    def on_load(self, *args):
        self.response["text"] = ""
        sender = self.controller.sender
        response = self.controller.make_request(sender.handle_score(sender.id()))

        if response[0] == bbtp.STATUS_OK:
            self.response["text"] = self.format_my_score(response[1])
        elif response[0] == bbtp.STATUS_EXCEPTION:
            messagebox.showerror("My Score Error", response[1])
        else:
            self.controller.unknown_error()
    
if __name__ == "__main__":
    app = BitboxingGui(800, 600)
    app.mainloop()