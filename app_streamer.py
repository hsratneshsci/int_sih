import time
import cv2
import numpy as np
import mss
import subprocess
import psutil
from flask import Flask, Response, render_template, request
import pygetwindow as gw

app = Flask(__name__)

# Paths to additional applications
application_paths = {
    "app1": r"C:\Path\To\Application1.exe",
    "app2": r"C:\Path\To\Application2.exe",
    "app3": r"C:\Path\To\Application3.exe",
    "app4": r"C:\Path\To\Application4.exe",
    "app5": r"C:\Path\To\Application5.exe",
}

# Command to launch scrcpy with specific attributes
scrcpy_command = r"scrcpy\scrcpy.exe"


#scrcpy_command = r"scrcpy\scrcpy.exe --crop=2000:1600:20:350 --angle 15 --video-bit-rate 4M --max-size 1024"

# Title of the application window to track
capture_window_title = "SM-M307F"
#capture_window_title = "Quest 3"

def is_application_running(name):
    """
    Check if an application is already running.
    """
    for proc in psutil.process_iter(['name']):
        if name.lower() in proc.info['name'].lower():
            return True
    return False

def launch_scrcpy():
    """
    Launch scrcpy with the specified command if it is not already running.
    """
    if not is_application_running("scrcpy"):
        print(f"Launching scrcpy with command: {scrcpy_command}")
        subprocess.Popen(scrcpy_command, shell=True)
    else:
        print("scrcpy is already running!")

def launch_application(app_path):
    """
    Launch the specified application if it is not already running.
    """
    app_name = app_path.split("\\")[-1]
    if not is_application_running(app_name):
        print(f"Launching application: {app_path}")
        subprocess.Popen(app_path, shell=True)
    else:
        print(f"{app_name} is already running!")

def find_window_region(title):
    """
    Find the position and size of the window with the given title.
    """
    windows = gw.getWindowsWithTitle(title)
    if windows:
        window = windows[0]
        return {
            "top": window.top,
            "left": window.left,
            "width": window.width,
            "height": window.height
        }
    return None

def capture_screen_dynamic(title):
    """
    Capture a specific window's content dynamically based on its current position and size.
    """
    with mss.mss() as sct:
        prev_region = None
        while True:
            region = find_window_region(title)
            if not region:
                print("Window not found! Relaunching scrcpy...")
                launch_scrcpy()
                time.sleep(1)
                continue

            if prev_region != region:
                print(f"Window region updated: {region}")
                prev_region = region

            frame = np.array(sct.grab(region))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

            time.sleep(0.02)

def get_system_metrics():
    """
    Gather system metrics (CPU, memory, disk usage).
    """
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        'cpu_usage': cpu_usage,
        'memory_usage': memory.percent,
        'disk_usage': disk.percent
    }

@app.route("/")
def index():
    """
    Main dashboard page.
    """
    return render_template("dashboard.html", apps=application_paths)

@app.route("/launch/<app_key>")
def launch(app_key):
    """
    Launch an application based on the key.
    """
    if app_key in application_paths:
        app_path = application_paths[app_key]
        launch_application(app_path)
        return f"Application {app_key} launched!", 200
    elif app_key == "scrcpy":
        launch_scrcpy()
        return "scrcpy launched with specific attributes!", 200
    else:
        return "Invalid application key!", 404

@app.route("/metrics")
def metrics():
    """
    Endpoint to retrieve system metrics in JSON format.
    """
    metrics_data = get_system_metrics()
    return metrics_data

@app.route("/video_feed")
def video_feed():
    """
    Endpoint for serving the video stream.
    """
    return Response(capture_screen_dynamic(capture_window_title), 
                    mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    # Launch scrcpy application with specific attributes
    launch_scrcpy()

    # Start Flask server
    app.run(debug=True, host="0.0.0.0", port=5000)
