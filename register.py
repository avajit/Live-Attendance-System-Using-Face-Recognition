import os
import cv2
import dlib
import numpy as np
import urllib.request
import bz2
from PIL import Image, ImageEnhance, ImageTk
import face_recognition
from imutils import face_utils
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class StudentRegistrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Registration System")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Initialize variables
        self.camera_active = False
        self.cap = None
        self.count = 0
        self.use_landmarks = False
        self.predictor = None
        self.face_detector = None
        self.full_save_path = ""
        
        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create UI components
        self.create_registration_form()
        self.create_camera_feed()
        self.create_status_bar()
        
        # Check for shape predictor
        self.check_shape_predictor()
    
    def create_registration_form(self):
        """Create the registration form elements"""
        form_frame = ttk.LabelFrame(self.main_frame, text="Student Information", padding=10)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Form fields
        fields = [
            ("Enrollment Number:", "enroll_entry"),
            ("Full Name:", "name_entry"),
            ("Save Location:", "save_path_entry")
        ]
        
        for i, (label_text, entry_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(form_frame)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5)
            setattr(self, entry_name, entry)
        
        # Set default save location
        self.save_path_entry.insert(0, "student_images")
        
        # Browse button
        ttk.Button(form_frame, text="Browse...", command=self.browse_save_location).grid(
            row=2, column=2, padx=5, sticky=tk.W)
        
        # Buttons frame
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Registration", command=self.start_registration)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_registration, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        ttk.Label(form_frame, text="Progress:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.progress_bar = ttk.Progressbar(form_frame, orient=tk.HORIZONTAL, length=200, 
                                          mode='determinate', maximum=100)
        self.progress_bar.grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=5)
        
        # Image counter
        self.image_counter = ttk.Label(form_frame, text="Images captured: 0/100")
        self.image_counter.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
    
    def create_camera_feed(self):
        """Create the camera feed elements"""
        camera_frame = ttk.LabelFrame(self.main_frame, text="Camera Feed", padding=10)
        camera_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.camera_label = ttk.Label(camera_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = ttk.Label(
            camera_frame,
            text="1. Face the camera directly\n"
                 "2. Ensure good lighting\n"
                 "3. Try different angles",
            justify=tk.LEFT
        )
        instructions.pack(fill=tk.X, pady=5)
    
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def browse_save_location(self):
        """Open dialog to select save location"""
        path = filedialog.askdirectory()
        if path:
            self.save_path_entry.delete(0, tk.END)
            self.save_path_entry.insert(0, path)
    
    def check_shape_predictor(self):
        """Check if shape predictor is available"""
        predictor_path = "shape_predictor_68_face_landmarks.dat"
        
        if os.path.exists(predictor_path):
            self.initialize_landmark_detector(predictor_path)
            return
        
        answer = messagebox.askyesno(
            "Download Required",
            "The facial landmark predictor file is missing (37MB). Download now?"
        )
        
        if answer:
            self.download_shape_predictor()
        else:
            self.status_var.set("Using basic face detection (no landmarks)")
            self.use_landmarks = False
    
    def initialize_landmark_detector(self, predictor_path):
        """Initialize the facial landmark detector"""
        try:
            self.predictor = dlib.shape_predictor(predictor_path)
            self.face_detector = dlib.get_frontal_face_detector()
            self.use_landmarks = True
            self.status_var.set("Ready (with facial landmarks)")
        except Exception as e:
            self.use_landmarks = False
            self.status_var.set(f"Error initializing predictor: {str(e)}")
    
    def download_shape_predictor(self):
        """Download the facial landmark predictor"""
        predictor_url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
        bz2_path = "shape_predictor_68_face_landmarks.dat.bz2"
        dat_path = "shape_predictor_68_face_landmarks.dat"
        
        try:
            self.status_var.set("Downloading facial landmark predictor (37MB)...")
            self.root.update()
            
            # Download the file
            urllib.request.urlretrieve(predictor_url, bz2_path)
            
            # Extract the bz2 file
            with open(dat_path, 'wb') as new_file, bz2.BZ2File(bz2_path, 'rb') as file:
                for data in iter(lambda: file.read(100 * 1024), b''):
                    new_file.write(data)
            
            # Clean up
            os.remove(bz2_path)
            
            # Initialize the detector
            self.initialize_landmark_detector(dat_path)
            messagebox.showinfo("Success", "Facial landmark predictor downloaded successfully!")
            
        except Exception as e:
            self.use_landmarks = False
            self.status_var.set(f"Error downloading predictor: {str(e)}")
            messagebox.showerror("Error", f"Failed to download predictor: {str(e)}")
    
    def validate_inputs(self):
        """Validate user inputs before starting registration"""
        enroll = self.enroll_entry.get().strip()
        name = self.name_entry.get().strip()
        save_path = self.save_path_entry.get().strip()
        
        if not enroll or not name:
            messagebox.showerror("Error", "Both enrollment number and name are required!")
            return False
        
        if not save_path:
            messagebox.showerror("Error", "Please select a save location!")
            return False
        
        return True
    
    def initialize_camera(self):
        """Initialize the camera with optimal settings"""
        # self.cap = cv2.VideoCapture("http://192.168.137.149:8080:<port>/video")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open camera!")
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.6)
        
        return True
    
    def create_student_directory(self):
        """Create directory for student images"""
        enroll = self.enroll_entry.get().strip()
        name = self.name_entry.get().strip()
        save_path = self.save_path_entry.get().strip()
        
        folder_name = f"{enroll}_{name.replace(' ', '_')}"
        self.full_save_path = os.path.join(save_path, folder_name)
        os.makedirs(self.full_save_path, exist_ok=True)
    
    def start_registration(self):
        """Start the registration process"""
        if not self.validate_inputs():
            return
        
        if not self.initialize_camera():
            return
        
        self.create_student_directory()
        
        # Initialize registration state
        self.camera_active = True
        self.count = 0
        self.progress_bar['value'] = 0
        self.image_counter.config(text="Images captured: 0/100")
        
        # Update UI state
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.status_var.set("Registration in progress...")
        self.update_camera_feed()
    
    def stop_registration(self):
        """Stop the registration process"""
        self.camera_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Update UI state
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Show completion message
        self.status_var.set(f"Registration complete. {self.count} images saved in: {self.full_save_path}")
        messagebox.showinfo("Complete", f"Registration complete!\n{self.count} images saved.")
    
    def detect_faces(self, rgb_frame):
        """Detect faces in the frame using the appropriate method"""
        if self.use_landmarks and self.count < 100:
            # Convert to grayscale for dlib (most reliable format)
            gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
            faces = self.face_detector(gray, 1)
            if not faces:
                face_locations = face_recognition.face_locations(rgb_frame)
                faces = [dlib.rectangle(left, top, right, bottom) 
                        for (top, right, bottom, left) in face_locations]
        else:
            face_locations = face_recognition.face_locations(rgb_frame)
            faces = [(top, right, bottom, left) for (top, right, bottom, left) in face_locations]
        
        return faces
    
    def process_face(self, frame, face):
        """Process a detected face and save if conditions are met"""
        if self.use_landmarks:
            (x, y, w, h) = face_utils.rect_to_bb(face)
        else:
            (top, right, bottom, left) = face
            x, y, w, h = left, top, right-left, bottom-top
        
        # Add padding to the face region
        padding = 30
        x, y = max(0, x-padding), max(0, y-padding)
        w, h = w+padding*2, h+padding*2
        
        face_img = frame[y:y+h, x:x+w]
        
        if face_img.size == 0:
            return False
        
        # Only save if face is properly detected and we haven't reached the limit
        if w > 100 and h > 100 and self.count < 100:
            self.save_face_image(face_img)
            return True
        
        return False
    
    def save_face_image(self, face_img):
        """Save the face image with quality enhancements"""
        self.count += 1
        img_path = os.path.join(self.full_save_path, f"{self.count}.jpg")
        
        # Convert to PIL Image for enhancements
        pil_img = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
        
        # Apply image enhancements
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(1.3)
        
        enhancer = ImageEnhance.Sharpness(pil_img)
        pil_img = enhancer.enhance(1.2)
        
        # Convert back to OpenCV format and save as grayscale
        enhanced_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        gray_img = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(img_path, gray_img)
        
        # Update progress
        self.progress_bar['value'] = self.count
        self.image_counter.config(text=f"Images captured: {self.count}/100")
    
    def update_camera_feed(self):
        """Update the camera feed with face detection"""
        if not self.camera_active or not self.cap:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            return
        
        # Convert to RGB for face detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = self.detect_faces(rgb_frame)
        
        for face in faces:
            # Process each face
            face_processed = self.process_face(frame, face)
            
            # Draw rectangle around face
            if self.use_landmarks:
                (x, y, w, h) = face_utils.rect_to_bb(face)
            else:
                (top, right, bottom, left) = face
                x, y, w, h = left, top, right-left, bottom-top
            
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"#{self.count}", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        # Display the frame
        self.display_frame(frame)
        
        # Schedule next update or stop if done
        if self.camera_active:
            if self.count >= 100:
                self.stop_registration()
            else:
                self.root.after(20, self.update_camera_feed)
    
    def display_frame(self, frame):
        """Convert and display the OpenCV frame in Tkinter"""
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(image=img)
        
        self.camera_label.imgtk = img
        self.camera_label.configure(image=img)


def main():
    root = tk.Tk()
    app = StudentRegistrationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()