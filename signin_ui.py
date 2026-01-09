"""
Integrated Sign-In UI with Backend Authentication
Connects sign-in interface with Firebase and biometric matching
"""
import tkinter as tk
from tkinter import messagebox
import time
import numpy as np

# Backend imports
from tap_listener import TapListener
from optimized_feature_extractor import OptimizedFeatureExtractor as FeatureExtractor
from matcher import Matcher
from rhythm_analyzer import RhythmAnalyzer

# Firebase imports
import firebase_admin
from firebase_admin import credentials, db
import os

# =============================
# FIREBASE SETUP
# =============================
KEY_PATH = "fresh key.json"
DB_URL = "https://morse-code-36b13-default-rtdb.asia-southeast1.firebasedatabase.app/"

os.environ["GOOGLE_CLOUD_DISABLE_GRPC"] = "true"
os.environ["NO_GCE_CHECK"] = "true"

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred, {'databaseURL': DB_URL, 'httpTimeout': 30})
        print("✅ Firebase Connected")
    except Exception as e:
        print(f"❌ Firebase Error: {e}")

# =============================
# DATABASE HELPERS
# =============================
def get_user_profile(username):
    """Retrieve user profile from Firebase"""
    try:
        ref = db.reference(f'users/{username}')
        return ref.get()
    except Exception as e:
        print(f"⚠️ DB Read Error: {e}")
        return None

# =============================
# THEME COLORS
# =============================
BG_COLOR = "#0f172a"
PRIMARY_BTN = "#38bdf8"
TEXT_COLOR = "#FFFFFF"
SUBTEXT_COLOR = "#94a3b8"
BTN_TEXT = "#111827"
INPUT_BG = "#020617"
SUCCESS = "#22c55e"
ERROR = "#ef4444"
SURFACE = "#1e293b"

# =============================
# MAIN APPLICATION CLASS
# =============================
class SignInApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign In - Morse Authentication")
        self.root.geometry("900x600")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        # Backend components
        self.extractor = FeatureExtractor(dot_dash_threshold_ratio=2.0)
        self.matcher = Matcher(use_dynamic_threshold=True, metric='euclidean')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the complete UI"""
        # Main frame
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(expand=True)
        
        # Title
        tk.Label(
            frame,
            text="Secure Sign In",
            font=("Helvetica", 28, "bold"),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=(0, 10))
        
        tk.Label(
            frame,
            text="Authenticate with your unique rhythm pattern",
            font=("Helvetica", 12),
            fg=SUBTEXT_COLOR,
            bg=BG_COLOR
        ).pack(pady=(0, 40))
        
        # Username input
        tk.Label(
            frame,
            text="Username",
            font=("Helvetica", 13, "bold"),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(anchor="w", padx=250)
        
        self.username_entry = tk.Entry(
            frame,
            font=("Helvetica", 14),
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            width=32,
            relief="flat",
            highlightbackground=PRIMARY_BTN,
            highlightthickness=2
        )
        self.username_entry.pack(pady=(8, 35), ipady=8)
        
        # Info card
        info_frame = tk.Frame(frame, bg=SURFACE, relief="solid", borderwidth=1)
        info_frame.pack(pady=20, padx=80, fill="x")
        
        tk.Label(
            info_frame,
            text="🎵 Tap Your Pattern",
            font=("Helvetica", 14, "bold"),
            fg=PRIMARY_BTN,
            bg=SURFACE
        ).pack(pady=(15, 5))
        
        tk.Label(
            info_frame,
            text="After entering username, you'll tap your enrolled pattern.\n"
            "Use SPACEBAR to tap, ESC when finished.",
            font=("Helvetica", 11),
            fg=SUBTEXT_COLOR,
            bg=SURFACE,
            justify="center"
        ).pack(pady=(0, 15))
        
        # Authenticate button
        tk.Button(
            frame,
            text="AUTHENTICATE",
            font=("Helvetica", 14, "bold"),
            bg=PRIMARY_BTN,
            fg=BTN_TEXT,
            width=22,
            height=2,
            relief="flat",
            command=self.start_authentication,
            cursor="hand2"
        ).pack(pady=25)
        
        # Status label
        self.status_label = tk.Label(
            frame,
            text="",
            font=("Helvetica", 12),
            bg=BG_COLOR
        )
        self.status_label.pack(pady=15)
        
        # Footer
        tk.Label(
            self.root,
            text="Biometric rhythm authentication • DotDash Labs",
            fg=SUBTEXT_COLOR,
            bg=BG_COLOR,
            font=("Helvetica", 10)
        ).pack(side="bottom", pady=20)
    
    def start_authentication(self):
        """Start the authentication process"""
        username = self.username_entry.get().strip()
        
        # Validation
        if not username:
            messagebox.showerror("Error", "Please enter your username")
            return
        
        self.status_label.config(text="Loading user profile...", fg=SUBTEXT_COLOR)
        self.root.update()
        
        # Fetch user data
        user_data = get_user_profile(username)
        
        if not user_data:
            self.status_label.config(text="", fg=TEXT_COLOR)
            messagebox.showerror(
                "User Not Found",
                f"Username '{username}' does not exist.\n\n"
                "Please check your username or enroll first."
            )
            return
        
        # Extract profile
        profile = user_data.get('biometric_profile')
        if not profile:
            messagebox.showerror(
                "Error",
                "User profile is corrupted. Please re-enroll."
            )
            return
        
        password_info = {
            'morse_code': user_data.get('morse_code', ''),
            'decoded': user_data.get('decoded_word', ''),
            'total_elements': user_data.get('total_elements', 0)
        }
        
        # Show pattern to user
        msg = f"Welcome back, {username}!\n\n"
        msg += f"Your password: {password_info['decoded']}\n"
        msg += f"Morse pattern: {password_info['morse_code']}\n\n"
        msg += "Press OK, then tap your pattern using SPACEBAR.\n"
        msg += "Press ESC when finished."
        
        messagebox.showinfo("Tap Your Pattern", msg)
        
        # Record tapping
        self.status_label.config(text="⏺ Recording your pattern...", fg=PRIMARY_BTN)
        self.root.update()
        
        listener = TapListener()
        listener.start()
        presses, gaps = listener.get_sequences()
        
        if not presses:
            self.status_label.config(text="", fg=TEXT_COLOR)
            messagebox.showwarning("No Input", "No tapping pattern detected. Please try again.")
            return
        
        # Authenticate
        self.authenticate_pattern(username, presses, gaps, profile)
    
    def authenticate_pattern(self, username, presses, gaps, profile):
        """Authenticate the tapped pattern"""
        self.status_label.config(text="🔐 Authenticating...", fg=SUBTEXT_COLOR)
        self.root.update()
        
        try:
            # Extract features from test pattern
            test_vector = self.extractor.extract(presses, gaps)
            
            # Perform multi-metric authentication
            results = self.matcher.authenticate_with_multiple_metrics(test_vector, profile)
            
            # Get results
            final_decision = results['final_decision']
            avg_confidence = results.get('avg_confidence', 0)
            votes = results.get('votes', '0/3')
            
            # Show results
            if final_decision:
                self.status_label.config(text="✓ Authentication Successful", fg=SUCCESS)
                
                # Detailed success message
                details = f"Access Granted for {username}\n\n"
                details += f"Confidence: {avg_confidence:.1%}\n"
                details += f"Consensus: {votes} metrics agreed\n\n"
                details += "Individual Metrics:\n"
                for metric, data in results.items():
                    if metric not in ['final_decision', 'avg_confidence', 'votes']:
                        status = "✓" if data['accepted'] else "✗"
                        details += f"  {status} {metric.capitalize()}: {data['confidence']:.1%}\n"
                
                messagebox.showinfo("Authentication Successful", details)
                
                # Here you could open the main application
                # subprocess.Popen([sys.executable, "dotdash_ui.py"])
                # self.root.destroy()
                
            else:
                self.status_label.config(text="✗ Authentication Failed", fg=ERROR)
                
                # Detailed failure message
                details = f"Access Denied\n\n"
                details += f"Confidence: {avg_confidence:.1%}\n"
                details += f"Consensus: {votes} metrics agreed\n\n"
                details += "Your rhythm pattern didn't match the enrolled profile.\n\n"
                details += "Individual Metrics:\n"
                for metric, data in results.items():
                    if metric not in ['final_decision', 'avg_confidence', 'votes']:
                        status = "✓" if data['accepted'] else "✗"
                        details += f"  {status} {metric.capitalize()}: {data['confidence']:.1%}\n"
                
                messagebox.showerror("Authentication Failed", details)
        
        except Exception as e:
            self.status_label.config(text="✗ Authentication Error", fg=ERROR)
            messagebox.showerror(
                "Error",
                f"Authentication failed due to an error:\n\n{str(e)}"
            )
            print(f"Authentication error: {e}")

# =============================
# RUN APPLICATION
# =============================
if __name__ == "__main__":
    root = tk.Tk()
    app = SignInApp(root)
    root.mainloop()
