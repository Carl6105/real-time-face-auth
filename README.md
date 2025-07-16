# 🔐 Real-Time Face Authentication App

A modern, secure face authentication desktop application built with **Python**, **PyQt6**, **OpenCV**, and **face_recognition**. It includes real-time face detection with liveness checks, secure admin login, face updates, and full user activity logging with a stylish and interactive UI.

---

## ✨ Features

- 👤 **Face Registration** – Register users securely with liveness (blink) detection.
- 🔐 **Face Login** – Authenticate using face recognition with anti-spoofing.
- 🔄 **Update Face** – Logged-in users can re-register or update their face data.
- 👮 **Admin Dashboard** – Admin can:
  - View all users.
  - See last login and login counts.
  - View detailed login logs.
  - Delete users (excluding admin).
- ⚠️ **Anti-Spoofing** – Uses blink detection to prevent photo/video attacks.
- 🎨 **Modern UI** – Custom-styled with QSS, icons, and animation support.
- 📦 **MongoDB Backend** – All users and logs stored securely in a MongoDB database.

---

## 📁 Folder Structure
📦Real-Time Face Authenticator
┣ 📁assets
┃ ┣ face_scan.gif
┃ ┗ lock.png
┣ 📁utils
┃ ┣ database.py
┃ ┣ liveness.py
┃ ┗ logger.py
┣ 📁templates
┃ ┗ style.qss
┣ main.py
┗ README.md

---

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Carl6105/real-time-face-auth
```

### 2. Install Dependencies
```
pip install -r requirements.txt
```

If you don't have a requirements.txt, here are the essential packages:
```
pip install pyqt6 opencv-python face_recognition pymongo numpy
```
💡 Ensure you also have dlib installed (used by face_recognition). This may require Visual Studio Build Tools on Windows or Xcode tools on macOS.

### 3. Setup MongoDB
Use MongoDB Atlas or install MongoDB locally.
Update the connection string in utils/database.py:
client = MongoClient("mongodb://localhost:27017")

### ▶️ Running the App
```
python main.py
```

### 🧪 Usage Guide

➕ Register Face
Click on "Register a New Face".4

Enter your name.

Blink once when prompted and press Space to capture.

You’ll see a success message.


🔓 Login with Face
Click on "Log in with your Face".

Blink when prompted, press Space, and your face will be recognized.


🔄 Update Face
After successful login, click "🔄 Update Face" to re-capture your face.


👮 Admin Login
Click "Admin Login".

Enter the admin username and password.

See all registered users, logs, and manage them.


⚙️ Customization
Update styling via templates/style.qss.

Modify icons/animations in the assets/ folder.

Extend user roles in utils/database.py.


🤝 Contribution
Contributions are welcome! Feel free to submit issues or pull requests for improvements.


📜 License
MIT License. Feel free to use, modify, and distribute.


📧 Contact
Created by S Mohammed Aadil

📩 shaikaadil60@gmail.com

🌐 https://carl6105.github.io/my-portfolio/
