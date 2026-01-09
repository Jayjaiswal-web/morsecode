"""
Integrated Home UI - Main Entry Point
Connects to enrollment and sign-in interfaces
"""
import tkinter as tk
from tkinter import font, messagebox
import subprocess
import sys
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Theme colors
BG_COLOR = "#0f172a"
PRIMARY_BTN = "#38bdf8"
TEXT_COLOR = "#e5e7eb"
SUBTEXT_COLOR = "#94a3b8"
BTN_TEXT = "#111827"
ACCENT = "#22c55e"

def open_enrollment():
    """Open the enrollment interface"""
    try:
        # Try different possible filenames
        possible_files = [
            "enrollment_ui (1).py",
            "enrollment_ui.py",
            "integrated_enrollment_ui.py"
        ]
        
        enrollment_file = None
        for filename in possible_files:
            filepath = os.path.join(BASE_DIR, filename)
            if os.path.exists(filepath):
                enrollment_file = filepath
                break
        
        if enrollment_file:
            # Don't destroy root - just hide it
            root.withdraw()
            
            # Open enrollment in same process
            subprocess.Popen([sys.executable, enrollment_file])
            
            # Show root again after some delay (or you can close it)
            # root.after(1000, lambda: root.deiconify())
        else:
            messagebox.showerror(
                "File Not Found",
                "Could not find enrollment_ui.py file.\n\n"
                "Please ensure the file is in the same directory."
            )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open enrollment:\n{str(e)}")

def open_signin():
    """Open the sign-in interface"""
    try:
        # Try different possible filenames
        possible_files = [
            "signin_ui (1).py",
            "signin_ui.py",
            "integrated_signin_ui.py"
        ]
        
        signin_file = None
        for filename in possible_files:
            filepath = os.path.join(BASE_DIR, filename)
            if os.path.exists(filepath):
                signin_file = filepath
                break
        
        if signin_file:
            # Don't destroy root - just hide it
            root.withdraw()
            
            # Open sign-in in same process
            subprocess.Popen([sys.executable, signin_file])
            
            # Show root again after some delay (or you can close it)
            # root.after(1000, lambda: root.deiconify())
        else:
            messagebox.showerror(
                "File Not Found",
                "Could not find signin_ui.py file.\n\n"
                "Please ensure the file is in the same directory."
            )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open sign-in:\n{str(e)}")

def show_stats():
    """Show user statistics"""
    stats_window = tk.Toplevel(root)
    stats_window.title("User Statistics")
    stats_window.geometry("600x400")
    stats_window.configure(bg=BG_COLOR)
    
    # Import Firebase
    try:
        from firebase_admin import db
        
        # Get all users
        ref = db.reference('users')
        users = ref.get()
        
        if users:
            # Title
            tk.Label(
                stats_window,
                text="Registered Users",
                font=("Helvetica", 20, "bold"),
                fg=TEXT_COLOR,
                bg=BG_COLOR
            ).pack(pady=20)
            
            # Create scrollable frame
            canvas = tk.Canvas(stats_window, bg=BG_COLOR, highlightthickness=0)
            scrollbar = tk.Scrollbar(stats_window, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Display users
            for username, data in users.items():
                user_frame = tk.Frame(scrollable_frame, bg="#1e293b", relief="solid", borderwidth=1)
                user_frame.pack(pady=8, padx=20, fill="x")
                
                tk.Label(
                    user_frame,
                    text=f"👤 {username}",
                    font=("Helvetica", 13, "bold"),
                    fg=ACCENT,
                    bg="#1e293b"
                ).pack(anchor="w", padx=15, pady=(10, 5))
                
                decoded = data.get('decoded_word', 'N/A')
                pattern_count = data.get('pattern_count', 0)
                
                profile = data.get('biometric_profile', {})
                consistency = profile.get('consistency_score', 0)
                
                metrics = data.get('enrollment_metrics', {})
                accuracy = metrics.get('pattern_accuracy', 0)
                
                info_text = f"Password: {decoded} | Patterns: {pattern_count} | "
                info_text += f"Accuracy: {accuracy:.1%} | Consistency: {consistency:.1%}"
                
                tk.Label(
                    user_frame,
                    text=info_text,
                    font=("Helvetica", 10),
                    fg=SUBTEXT_COLOR,
                    bg="#1e293b"
                ).pack(anchor="w", padx=15, pady=(0, 10))
            
            canvas.pack(side="left", fill="both", expand=True, padx=20)
            scrollbar.pack(side="right", fill="y")
            
        else:
            tk.Label(
                stats_window,
                text="No users registered yet",
                font=("Helvetica", 14),
                fg=SUBTEXT_COLOR,
                bg=BG_COLOR
            ).pack(expand=True)
    
    except Exception as e:
        tk.Label(
            stats_window,
            text=f"Error loading statistics:\n{str(e)}",
            font=("Helvetica", 12),
            fg="#ef4444",
            bg=BG_COLOR
        ).pack(expand=True)

# Main window
root = tk.Tk()
root.title("Morse Tap Authentication")
root.geometry("1000x600")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

# Fonts
title_font = font.Font(family="Helvetica", size=32, weight="bold")
subtitle_font = font.Font(family="Helvetica", size=14)
button_font = font.Font(family="Helvetica", size=14, weight="bold")
small_font = font.Font(family="Helvetica", size=11)

# Main frame
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(expand=True)

# Logo/Icon
tk.Label(
    main_frame,
    text="🔐",
    font=("Helvetica", 60),
    fg=PRIMARY_BTN,
    bg=BG_COLOR
).pack(pady=(0, 20))

# Title
tk.Label(
    main_frame,
    text="Morse Tap Authentication",
    fg=TEXT_COLOR,
    bg=BG_COLOR,
    font=title_font
).pack(pady=(0, 10))

# Subtitle
tk.Label(
    main_frame,
    text="Biometric authentication through rhythm patterns",
    fg=SUBTEXT_COLOR,
    bg=BG_COLOR,
    font=subtitle_font
).pack(pady=(0, 50))

# Button frame
btn_frame = tk.Frame(main_frame, bg=BG_COLOR)
btn_frame.pack(pady=20)

# Sign Up button
signup_btn = tk.Button(
    btn_frame,
    text="📝 Sign Up",
    font=button_font,
    bg=PRIMARY_BTN,
    fg=BTN_TEXT,
    width=18,
    height=2,
    relief="flat",
    command=open_enrollment,
    cursor="hand2",
    activebackground="#0ea5e9",
    activeforeground=BTN_TEXT
)
signup_btn.grid(row=0, column=0, padx=15)

# Sign In button
signin_btn = tk.Button(
    btn_frame,
    text="🔓 Sign In",
    font=button_font,
    bg=PRIMARY_BTN,
    fg=BTN_TEXT,
    width=18,
    height=2,
    relief="flat",
    command=open_signin,
    cursor="hand2",
    activebackground="#0ea5e9",
    activeforeground=BTN_TEXT
)
signin_btn.grid(row=0, column=1, padx=15)

# Stats button (smaller, secondary)
stats_btn = tk.Button(
    main_frame,
    text="📊 View Statistics",
    font=small_font,
    bg="#1e293b",
    fg=TEXT_COLOR,
    width=20,
    relief="flat",
    command=show_stats,
    cursor="hand2"
)
stats_btn.pack(pady=25)

# Feature highlights
features_frame = tk.Frame(main_frame, bg=BG_COLOR)
features_frame.pack(pady=30)

features = [
    ("🎵", "Rhythm-Based"),
    ("🔒", "Highly Secure"),
    ("⚡", "Fast Login")
]

for icon, text in features:
    feature_box = tk.Frame(features_frame, bg=BG_COLOR)
    feature_box.pack(side="left", padx=25)
    
    tk.Label(
        feature_box,
        text=icon,
        font=("Helvetica", 24),
        bg=BG_COLOR
    ).pack()
    
    tk.Label(
        feature_box,
        text=text,
        font=("Helvetica", 11),
        fg=SUBTEXT_COLOR,
        bg=BG_COLOR
    ).pack()

# Footer
footer_frame = tk.Frame(root, bg=BG_COLOR)
footer_frame.pack(side="bottom", pady=20)

tk.Label(
    footer_frame,
    text="DotDash Labs • Biometric Authentication Research",
    fg=SUBTEXT_COLOR,
    bg=BG_COLOR,
    font=("Helvetica", 10)
).pack()

tk.Label(
    footer_frame,
    text="Tap • Rhythm • Authenticate",
    fg="#64748b",
    bg=BG_COLOR,
    font=("Helvetica", 9, "italic")
).pack()

# Hover effects
def on_enter(e, button, color):
    button['background'] = color

def on_leave(e, button, color):
    button['background'] = color

signup_btn.bind("<Enter>", lambda e: on_enter(e, signup_btn, "#0ea5e9"))
signup_btn.bind("<Leave>", lambda e: on_leave(e, signup_btn, PRIMARY_BTN))

signin_btn.bind("<Enter>", lambda e: on_enter(e, signin_btn, "#0ea5e9"))
signin_btn.bind("<Leave>", lambda e: on_leave(e, signin_btn, PRIMARY_BTN))

stats_btn.bind("<Enter>", lambda e: on_enter(e, stats_btn, "#334155"))
stats_btn.bind("<Leave>", lambda e: on_leave(e, stats_btn, "#1e293b"))

# Handle window close
def on_closing():
    """Handle window close event"""
    root.destroy()
    # Make sure all child processes are also terminated
    sys.exit(0)

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start application
root.mainloop()
