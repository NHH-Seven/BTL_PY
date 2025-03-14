import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QHBoxLayout)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from database_connection import connect_db
import hashlib
import re

class RegisterWindow(QWidget):
    def __init__(self, login_form=None):
        super().__init__()
        self.login_form = login_form
        self.setup_database()
        self.initUI()
    
    def setup_database(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(10) PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL,
                        phone VARCHAR(15),
                        role VARCHAR(20) DEFAULT 'Nhân viên'
                    )
                """)
                conn.commit()
            except Exception as e:
                print(f"Lỗi khi tạo bảng: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def initUI(self):
        self.setWindowTitle("Đăng Ký - Quản Lý Quán Café")
        self.setFixedSize(900, 600)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left side - Register form
        register_frame = QFrame()
        register_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 0px;
            }
        """)
        register_layout = QVBoxLayout(register_frame)
        register_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        register_layout.setSpacing(20)
        register_layout.setContentsMargins(50, 50, 50, 50)
        
        # Register form content
        register_title = QLabel("Đăng Ký Tài Khoản")
        register_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        register_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        register_title.setStyleSheet("color: #1976D2;")
        
        # Form fields
        self.username = QLineEdit()
        self.username.setPlaceholderText("Tên đăng nhập")
        self.username.setMinimumHeight(45)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mật khẩu")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setMinimumHeight(45)
        
        self.confirm = QLineEdit()
        self.confirm.setPlaceholderText("Xác nhận mật khẩu")
        self.confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm.setMinimumHeight(45)
        
        self.name = QLineEdit()
        self.name.setPlaceholderText("Họ và tên")
        self.name.setMinimumHeight(45)
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.email.setMinimumHeight(45)
        
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Số điện thoại")
        self.phone.setMinimumHeight(45)
        
        # Register button
        register_button = QPushButton("ĐĂNG KÝ")
        register_button.setMinimumHeight(45)
        register_button.clicked.connect(self.register)
        
        # Login link
        switch_to_login = QPushButton("Đã có tài khoản? Đăng nhập ngay")
        switch_to_login.clicked.connect(self.show_login)
        
        # Add widgets to register layout
        register_layout.addWidget(register_title)
        register_layout.addWidget(self.username)
        register_layout.addWidget(self.password)
        register_layout.addWidget(self.confirm)
        register_layout.addWidget(self.name)
        register_layout.addWidget(self.email)
        register_layout.addWidget(self.phone)
        register_layout.addWidget(register_button)
        register_layout.addWidget(switch_to_login)
        
        main_layout.addWidget(register_frame, 1)
        
        # Right side - Image
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: #1976D2;
                border-radius: 0px;
            }
        """)
        image_layout = QVBoxLayout(image_frame)
        
        # Add welcome image/icon
        welcome_icon = QLabel("☕")
        welcome_icon.setFont(QFont("Arial", 72))
        welcome_icon.setStyleSheet("color: white;")
        welcome_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_text = QLabel("Tham gia cùng chúng tôi\nQuản Lý Quán Café")
        welcome_text.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        welcome_text.setStyleSheet("color: white;")
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        image_layout.addWidget(welcome_icon)
        image_layout.addWidget(welcome_text)
        main_layout.addWidget(image_frame, 1)
        
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
        
        # Set flat property for login button
        switch_to_login.setFlat(True)
    
    def set_login_form(self, login_form):
        self.login_form = login_form
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone):
        pattern = r'^(0|\+84)\d{9,10}$'
        return re.match(pattern, phone) is not None
    
    def generate_user_id(self, cursor):
        try:
            cursor.execute("SELECT id FROM users WHERE id LIKE 'NV%' ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
        
            if result and result[0]:
                last_id = result[0]
                last_number = int(last_id[2:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            new_id = f"NV{new_number:03d}"
            return new_id
        
        except Exception as e:
            print(f"Lỗi khi tạo mã nhân viên: {str(e)}")
            import random
            return f"NV{random.randint(1, 999):03d}"
    
    def register(self):
        username = self.username.text().strip()
        password = self.password.text()
        confirm = self.confirm.text()
        name = self.name.text().strip()
        email = self.email.text().strip()
        phone = self.phone.text().strip()
        
        # Validation
        if not all([username, password, confirm, name, email, phone]):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
            return
        
        if not self.validate_email(email):
            QMessageBox.warning(self, "Lỗi", "Email không hợp lệ!")
            return
        
        if not self.validate_phone(phone):
            QMessageBox.warning(self, "Lỗi", "Số điện thoại không hợp lệ!\nVui lòng nhập số điện thoại bắt đầu bằng 0 hoặc +84 và có 10-11 số.")
            return
        
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                # Kiểm tra username đã tồn tại
                cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Lỗi", "Tên đăng nhập đã tồn tại!")
                    return
                
                # Kiểm tra email đã tồn tại
                cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Lỗi", "Email đã được sử dụng!")
                    return
                
                # Tạo mã nhân viên mới
                user_id = self.generate_user_id(cursor)
                
                # Tiến hành đăng ký
                hashed_password = self.hash_password(password)
                cursor.execute("""
                    INSERT INTO users (id, username, password, name, email, phone, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, username, hashed_password, name, email, phone, 'Nhân viên'))
                conn.commit()
                
                QMessageBox.information(
                    self, 
                    "Thành công", 
                    f"""Đăng ký thành công!
                    Mã nhân viên của bạn là: {user_id}
                    Vui lòng đăng nhập để tiếp tục."""
                )
                
                # Xóa dữ liệu đã nhập
                for widget in [self.username, self.password, self.confirm, 
                             self.name, self.email, self.phone]:
                    widget.clear()
                
                # Chuyển về màn hình đăng nhập
                self.show_login()
                    
            except Exception as e:
                print(f"Lỗi đăng ký: {str(e)}")
                QMessageBox.warning(
                    self, 
                    "Lỗi", 
                    "Có lỗi xảy ra trong quá trình đăng ký! Vui lòng thử lại."
                )
            finally:
                cursor.close()
                conn.close()
    
    def show_login(self):
        if self.login_form:
            self.login_form.show()
            self.hide()
        else:
            # Import here to avoid circular imports
            from login_form import LoginForm
            self.login_form = LoginForm()
            self.login_form.set_register_window(self)
            self.login_form.show()
            self.hide()

# Standalone test for this module
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    # Make sure database_connection.py is in path
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec())