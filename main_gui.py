import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import subprocess
from PIL import Image, ImageTk
import webbrowser

# Base directory for resolving relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")
        
        # Load and set window icon (optional)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Custom style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)
        self.style.configure('Title.TLabel', font=('Helvetica', 24, 'bold'), 
                           background='#2c3e50', foreground='#ecf0f1')
        self.style.configure('Subtitle.TLabel', font=('Helvetica', 12), 
                           background='#2c3e50', foreground='#bdc3c7')
        
        # Header Frame
        self.header_frame = tk.Frame(root, bg='#2c3e50')
        self.header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Title and subtitle
        self.title_label = ttk.Label(self.header_frame, text="Face Recognition", 
                                   style='Title.TLabel')
        self.title_label.pack()
        
        self.subtitle_label = ttk.Label(self.header_frame, 
                                       text="Attendance System", 
                                       style='Subtitle.TLabel')
        self.subtitle_label.pack()
        
        # Main content frame
        self.main_frame = tk.Frame(root, bg='#34495e', bd=2, relief=tk.RIDGE)
        self.main_frame.pack(padx=40, pady=20, fill=tk.BOTH, expand=True)
        
        # Create the 4-box layout (with images)
        self.create_box_layout()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, 
                                  relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add menu
        self.create_menu()
    
    def create_box_layout(self):
        # Create a frame for the 4 image buttons
        boxes_frame = tk.Frame(self.main_frame, bg='#34495e')
        boxes_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Configure grid weights
        boxes_frame.grid_rowconfigure(0, weight=1)
        boxes_frame.grid_rowconfigure(1, weight=1)
        boxes_frame.grid_columnconfigure(0, weight=1)
        boxes_frame.grid_columnconfigure(1, weight=1)
        
        # Define the 4 images with their functions
        box_data = [
            {"text": "1. Student Registration", "command": self.register_student, "image": os.path.join(BASE_DIR, "images/student.jpg")},
            {"text": "2. Train Data", "command": self.train_model, "image": os.path.join(BASE_DIR, "images/train_data.jpg")},
            {"text": "3. Take Attendance", "command": self.start_recognition, "image": os.path.join(BASE_DIR, "images/face_detector.png")},
            {"text": "4. View Attendance", "command": self.view_records, "image": os.path.join(BASE_DIR, "images/attendance.jpg")}
        ]
        
        self.images = []  # keep references so images are not garbage-collected
        
        for i, data in enumerate(box_data):
            row = i // 2
            col = i % 2
            
            frame = tk.Frame(boxes_frame, bg='#34495e')
            frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
            
            # Load and resize image
            try:
                img = Image.open(data["image"])
                img = img.resize((200, 130))  # adjust image size
                photo = ImageTk.PhotoImage(img)
                self.images.append(photo)
            except Exception as e:
                photo = None
            
            # Create image button + text label in vertical layout
            if photo:
                btn = tk.Button(frame, image=photo, command=data["command"], 
                                bg='#34495e', bd=0, activebackground='#34495e', cursor="hand2")
                btn.pack(pady=(5, 2))   # spacing between top and text
                
            lbl = tk.Label(frame, text=data["text"], bg='#34495e', fg="white", 
                           font=("Helvetica", 13, "bold"))
            lbl.pack(pady=(0, 10))   # space below label
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Register Student", command=self.register_student)
        file_menu.add_command(label="Train Model", command=self.train_model)
        file_menu.add_command(label="Start Attendance", command=self.start_recognition)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _run_script(self, script_name):
        """Run a Python script as a non-blocking subprocess"""
        script_path = os.path.join(BASE_DIR, script_name)
        try:
            subprocess.Popen(
                [sys.executable, script_path],
                cwd=BASE_DIR
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {script_name}: {str(e)}")
            self.status_var.set(f"Error launching {script_name}")
    
    def register_student(self):
        self.status_var.set("Launching student registration...")
        self.root.update()
        self._run_script("register.py")
        self.status_var.set("Student registration window opened")
    
    def train_model(self):
        self.status_var.set("Launching model training...")
        self.root.update()
        self._run_script("train_model.py")
        self.status_var.set("Model training launched")
    
    def start_recognition(self):
        self.status_var.set("Launching attendance recognition...")
        self.root.update()
        self._run_script("recognize.py")
        self.status_var.set("Attendance recognition launched")
    
    def view_records(self):
        self.status_var.set("Launching attendance records viewer...")
        self.root.update()
        self._run_script("records.py")
        self.status_var.set("Records viewer opened")
    
    def show_docs(self):
        webbrowser.open("https://github.com/yourusername/face-recognition-attendance/docs")
    
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        
        tk.Label(about_window, text="Face Recognition Attendance System", 
                font=('Helvetica', 16, 'bold')).pack(pady=20)
        
        tk.Label(about_window, text="Version 2.0", font=('Helvetica', 12)).pack()
        tk.Label(about_window, text="\nDeveloped by Your Name\n\n", 
                font=('Helvetica', 12)).pack()
        
        tk.Label(about_window, text="© 2023 All Rights Reserved", 
                font=('Helvetica', 10)).pack(side=tk.BOTTOM, pady=10)
        
        close_btn = ttk.Button(about_window, text="Close", command=about_window.destroy)
        close_btn.pack(pady=10)
    
    def exit_app(self):
        answer = messagebox.askyesno("Exit Confirmation", 
                                   "Are you sure you want to exit the application?",
                                   icon='question')
        if answer:
            self.status_var.set("Exiting application...")
            self.root.update()
            try:
                self.root.destroy()
            except:
                os._exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceSystem(root)
    root.mainloop()
