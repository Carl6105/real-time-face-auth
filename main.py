import sys, cv2, face_recognition
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QInputDialog
)
from PyQt6.QtGui import QFont, QCursor, QMovie, QIcon
from PyQt6.QtCore import Qt

from utils.database import (
    register_user, get_user_by_encoding, update_last_login,
    update_face_encoding, get_login_logs, get_all_users,
    is_user_admin, verify_admin_password, delete_user
)
from utils.logger import log_access
from utils.liveness import detect_blink


def capture_face_preview():
    cap = cv2.VideoCapture(0)
    frame = None
    while True:
        ret, live = cap.read()
        if not ret:
            break
        faces = face_recognition.face_locations(live)
        for (top, right, bottom, left) in faces:
            cv2.rectangle(live, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.imshow("Face Capture - Press SPACE to Capture, ESC to Cancel", live)
        key = cv2.waitKey(1)
        if key == 27:
            break
        elif key == 32:
            frame = live.copy()
            break
    cap.release()
    cv2.destroyAllWindows()
    return frame


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Authenticator")
        self.setWindowIcon(QIcon("assets/lock.png"))
        self.setFixedSize(500, 400)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = self.build_homepage()
        self.stack.addWidget(self.home)

        self.logged_in_user = None

    def build_homepage(self):
        layout = QVBoxLayout()

        title = QLabel("Real Time Face Authentication", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20))
        layout.addWidget(title)

        gif = QMovie("assets/face_scan.gif")
        gif_label = QLabel()
        gif_label.setMovie(gif)
        gif.start()
        layout.addWidget(gif_label, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_register = QPushButton("📝 Register a New Face")
        btn_register.setFixedHeight(40)
        btn_register.clicked.connect(self.register_face)
        layout.addWidget(btn_register)

        btn_login = QPushButton("🔐 Log in with your Face")
        btn_login.setFixedHeight(40)
        btn_login.clicked.connect(self.authenticate_face)
        layout.addWidget(btn_login)

        admin_btn = QLabel("<a href='#'>⚙️ Admin Login</a>")
        admin_btn.setAlignment(Qt.AlignmentFlag.AlignRight)
        admin_btn.setStyleSheet("color: gray; font-size: 12px;")
        admin_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        admin_btn.linkActivated.connect(self.admin_login)
        layout.addWidget(admin_btn)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def register_face(self):
        name, ok = QInputDialog.getText(self, "Name", "Enter your name:")
        if not ok or not name.strip():
            return

        frame = capture_face_preview()
        if frame is None:
            return

        if not detect_blink(frame):
            QMessageBox.warning(self, "Liveness Failed", "Blink required.")
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)
        if encs:
            register_user(name.strip(), encs[0].tolist(), is_admin=False)
            QMessageBox.information(self, "Registered", f"Face registered for {name}.")
        else:
            QMessageBox.warning(self, "Error", "Face not detected.")

    def authenticate_face(self):
        frame = capture_face_preview()
        if frame is None:
            return

        if not detect_blink(frame):
            QMessageBox.warning(self, "Liveness Failed", "Blink required.")
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)
        if not encs:
            QMessageBox.warning(self, "Error", "No Face Detected - Adjust the Camera")
            return

        user = get_user_by_encoding(encs[0])
        if not user:
            QMessageBox.warning(self, "Access Denied", "Unknown User")
            return

        self.logged_in_user = user
        update_last_login(user['_id'])
        log_access(user['_id'])
        self.load_user_success(user)

    def load_user_success(self, user):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("✅ Face Successfully Verified", alignment=Qt.AlignmentFlag.AlignCenter))
        layout.addWidget(QLabel(f"Welcome, {user['name']}!", alignment=Qt.AlignmentFlag.AlignCenter))

        update_btn = QPushButton("🔄 Update Face")
        update_btn.clicked.connect(self.update_user_face)
        layout.addWidget(update_btn)

        widget = QWidget()
        widget.setLayout(layout)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def update_user_face(self):
        if not self.logged_in_user:
            QMessageBox.warning(self, "Error", "No user logged in.")
            return

        frame = capture_face_preview()
        if frame is None:
            return

        if not detect_blink(frame):
            QMessageBox.warning(self, "Liveness Failed", "Blink required.")
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        enc = face_recognition.face_encodings(rgb)
        if not enc:
            QMessageBox.warning(self, "Error", "No Face Detected - Adjust the Camera")
            return

        update_face_encoding(self.logged_in_user['_id'], enc[0].tolist())
        QMessageBox.information(self, "Success", "Your face has been updated.")

    def admin_login(self):
        name, ok1 = QInputDialog.getText(self, "Admin", "Admin name:")
        pwd, ok2 = QInputDialog.getText(self, "Password", "Password:", QLineEdit.EchoMode.Password)
        if not (ok1 and ok2 and name.strip() and pwd.strip()):
            return

        if name.strip() != "Admin":
            QMessageBox.warning(self, "Access Denied", "Only 'Admin' user is allowed.")
            return

        users = get_all_users()
        user = next((u for u in users if u['name'] == 'Admin'), None)

        if not user or not is_user_admin(user) or not verify_admin_password(user, pwd):
            QMessageBox.warning(self, "Access Denied", "Invalid admin credentials.")
            return

        self.load_admin_dashboard()

    def load_admin_dashboard(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("👮 Admin Dashboard", alignment=Qt.AlignmentFlag.AlignCenter))

        table = QTableWidget()
        users = get_all_users()
        table.setRowCount(len(users))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Name", "Last Login", "Total Logins", "View Logs", "Delete"])

        for i, user in enumerate(users):
            logs = get_login_logs(user['_id'])
            last_login = str(logs[-1]['timestamp']) if logs else "Never"

            table.setItem(i, 0, QTableWidgetItem(user['name']))
            table.setItem(i, 1, QTableWidgetItem(last_login))
            table.setItem(i, 2, QTableWidgetItem(str(len(logs))))

            view_btn = QPushButton("📄 View")
            view_btn.setStyleSheet("background-color: #444; color: white; padding: 4px 10px;")
            view_btn.clicked.connect(lambda _, u=user: self.show_login_logs(u))
            table.setCellWidget(i, 3, view_btn)

            if user['name'].lower() != "admin":
                del_btn = QPushButton("🗑️")
                del_btn.setStyleSheet("background-color: #822; color: white; padding: 4px 10px;")
                del_btn.clicked.connect(lambda _, u=user: self.confirm_delete_user(u))
                table.setCellWidget(i, 4, del_btn)

        layout.addWidget(table)
        widget = QWidget()
        widget.setLayout(layout)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def confirm_delete_user(self, user):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{user['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_user(user['_id'])
            QMessageBox.information(self, "Deleted", f"User '{user['name']}' has been removed.")
            self.load_admin_dashboard()

    def show_login_logs(self, user):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"📜 Login Logs for {user['name']}", alignment=Qt.AlignmentFlag.AlignCenter))

        log_table = QTableWidget()
        logs = get_login_logs(user['_id'])
        log_table.setRowCount(len(logs))
        log_table.setColumnCount(1)
        log_table.setHorizontalHeaderLabels(["Timestamp"])

        for i, log in enumerate(logs):
            log_table.setItem(i, 0, QTableWidgetItem(str(log['timestamp'])))

        back_btn = QPushButton("🔙 Back")
        back_btn.clicked.connect(self.load_admin_dashboard)

        layout.addWidget(log_table)
        layout.addWidget(back_btn)
        widget = QWidget()
        widget.setLayout(layout)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("templates/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = MainApp()
    window.show()
    sys.exit(app.exec())