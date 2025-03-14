from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QHBoxLayout)
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtCore import Qt
from database_connection import connect_db
import hashlib
import sys
import globals

class LoginForm(QWidget):
    def __init__(self, onLoginSuccess=None):
        super().__init__()
        self.onLoginSuccess = onLoginSuccess
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Đăng Nhập - Quản Lý Quán Café")
        self.setFixedSize(900, 600)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left side - Image
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: #1976D2;
                border-radius: 0px;
            }
        """)
        image_layout = QVBoxLayout(image_frame)
        
        # Add logo or welcome image
        logo_label = QLabel("☕")
        logo_label.setFont(QFont("Arial", 72))
        logo_label.setStyleSheet("color: white;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_text = QLabel("Chào mừng đến với\nQuản Lý Quán Café")
        welcome_text.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        welcome_text.setStyleSheet("color: white;")
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        image_layout.addWidget(logo_label)
        image_layout.addWidget(welcome_text)
        main_layout.addWidget(image_frame, 1)
        
        # Right side - Login form
        login_frame = QFrame()
        login_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 0px;
            }
        """)
        login_layout = QVBoxLayout(login_frame)
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.setSpacing(20)
        login_layout.setContentsMargins(50, 50, 50, 50)
        
        # Login form content
        login_title = QLabel("Đăng Nhập")
        login_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_title.setStyleSheet("color: #1976D2;")
        
        # Username input
        self.username = QLineEdit()
        self.username.setPlaceholderText("Tên đăng nhập")
        self.username.setMinimumHeight(45)
        
        # Password input
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mật khẩu")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setMinimumHeight(45)
        
        # Login button
        login_button = QPushButton("ĐĂNG NHẬP")
        login_button.setMinimumHeight(45)
        login_button.clicked.connect(self.login)
        
        # Register link
        self.register_window = None
        switch_to_register = QPushButton("Chưa có tài khoản? Đăng ký ngay")
        switch_to_register.clicked.connect(self.show_register)
        
        # Add widgets to login layout
        login_layout.addWidget(login_title)
        login_layout.addWidget(self.username)
        login_layout.addWidget(self.password)
        login_layout.addWidget(login_button)
        login_layout.addWidget(switch_to_register)
        
        main_layout.addWidget(login_frame, 1)
        
        # Apply styles
        self.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #1976D2;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton[flat=true] {
                background: none;
                border: none;
                color: #1976D2;
                font-weight: normal;
                text-decoration: underline;
            }
            QPushButton[flat=true]:hover {
                color: #1565C0;
            }
        """)
        
        # Set flat property for register button
        switch_to_register.setFlat(True)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self):
        username = self.username.text()
        password = self.hash_password(self.password.text())
        
        if not username or not self.password.text():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT id, name, role 
                    FROM users 
                    WHERE username = %s AND password = %s
                """, (username, password))
                user = cursor.fetchone()
                
                if user:
                    # Save current user ID to global variable
                    globals.current_user_id = user[0]
                    
                    # Call the onLoginSuccess callback
                    if self.onLoginSuccess:
                        self.onLoginSuccess()
                    self.hide()
                else:
                    QMessageBox.warning(self, "Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!")
            finally:
                cursor.close()
                conn.close()
    
    def set_register_window(self, register_window):
        self.register_window = register_window
    
    def show_register(self):
        if self.register_window:
            self.register_window.show()
            self.hide()
        else:
            # Import here to avoid circular imports
            from register_form import RegisterWindow
            self.register_window = RegisterWindow()
            self.register_window.set_login_form(self)
            self.register_window.show()
            self.hide()
        
    def closeEvent(self, event):
        sys.exit()

# Standalone test for this module
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = LoginForm()
    window.show()
    sys.exit(app.exec())