import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QStackedWidget, QHBoxLayout, QPushButton, QButtonGroup, QLabel, QFrame,
    QMessageBox, QMenu, QDialog)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt

from database_connection import connect_db
from styles import Styles

# Import UI components - remove LoginForm import
from ui.user_dialogs import UserProfileDialog, ChangePasswordDialog
from login_form import LoginForm

# Import globals
import globals

# Import tabs
from tabs.dashboard_tab import DashboardTab
from tabs.sales import SalesTab
from tabs.product_management import ProductManagementTab
from tabs.employee_management import EmployeeManagementTab
from tabs.order_management import OrderManagementTab
from tabs.statisticss import StatisticsTab
# Import CartTab ngay từ đầu
from tabs.cart import CartTab

class CafeManagementUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản Lý Quán Café")
        self.setMinimumSize(1400, 900)
        
        # Khởi chạy form đăng nhập trước
        self.showLoginForm()
    
    def showLoginForm(self):
        self.login_form = LoginForm(onLoginSuccess=self.initializeMainUI)
        self.login_form.show()
    
    def initializeMainUI(self):
        try:
            # Lấy thông tin người dùng hiện tại từ CSDL dựa trên ID đã lưu trong globals
            print(f"Initializing UI with user_id: {globals.current_user_id}")
            self.current_user = self.getUserInfo()
            if not self.current_user:
                print("Failed to get user info")
                return
        
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
        
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0, 0, 0, 0)
        
            self.createHeader(main_layout)
            self.createContent(main_layout)
            self.setStyleSheet(Styles.MAIN_STYLE)
        
            # Hiển thị cửa sổ chính
            self.show()
            
            print("Main UI initialized and shown")
        except Exception as e:
            print(f"Error initializing main UI: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def createHeader(self, layout):
        header_frame = QFrame()
        header_frame.setStyleSheet("""
        QFrame {
            background-color: #1976D2;
            padding: 0px;
        }
        QLabel {
            color: white;
        }
        QPushButton {
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: normal;
        }
        QPushButton:hover {
            background-color: #1565C0;
        }
        QPushButton:checked {
            background-color: #0D47A1;
            font-weight: bold;
        }
        #userButton, #cartButton {
            padding: 5px 15px;
            background-color: #1565C0;
            border-radius: 5px;
            margin: 5px;
        }
        #userButton:hover, #cartButton:hover {
            background-color: #0D47A1;
        }
    """)
    
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(0)
        header_layout.setContentsMargins(0, 0, 0, 0)
    
        # Top bar với logo và user info
        top_bar = QHBoxLayout()
    
        logo_label = QLabel("QUẢN LÝ QUÁN CAFÉ")
        logo_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        logo_label.setStyleSheet("padding: 10px 20px;")
        top_bar.addWidget(logo_label)
    
        top_bar.addStretch()
    
        # Add cart button
        self.cart_button = QPushButton("🛒 Giỏ hàng")
        self.cart_button.setObjectName("cartButton")
        self.cart_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cart_button.clicked.connect(self.openCart)
        top_bar.addWidget(self.cart_button)
    
        self.user_button = QPushButton(f"👤 {self.current_user['name']} ({self.current_user['role']})")
        self.user_button.setObjectName("userButton")
        self.user_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.user_button.clicked.connect(self.showUserMenu)
        top_bar.addWidget(self.user_button)
    
        header_layout.addLayout(top_bar)
    
        # Menu bar
        menu_bar = QHBoxLayout()
        menu_bar.setSpacing(0)
        menu_bar.setContentsMargins(20, 0, 20, 0)
    
        self.nav_buttons = []
        nav_items = [
            ("🏠 Trang Chủ", 0),
            ("🛒 Oder", 1),
            ("📋 Quản Lý Sản Phẩm", 2),
            ("👤 Quản Lý Nhân Viên", 3),
            ("📦 Quản Lý Đơn Hàng", 4),
            ("📊 Thống Kê", 5)
        ]
    
        button_group = QButtonGroup(self)
        button_group.setExclusive(True)
    
        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, x=index: self.content_stack.setCurrentIndex(x))
            button_group.addButton(btn)
            menu_bar.addWidget(btn)
            self.nav_buttons.append(btn)
    
        self.nav_buttons[0].setChecked(True)
    
        header_layout.addLayout(menu_bar)
        layout.addWidget(header_frame)

    def showUserMenu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #1976D2;
                color: white;
            }
        """)
    
        profile_action = menu.addAction("👤 Thông tin cá nhân")
        change_password_action = menu.addAction("🔑 Đổi mật khẩu")
        menu.addSeparator()
        logout_action = menu.addAction("🚪 Đăng xuất")
    
        profile_action.triggered.connect(self.showProfile)
        change_password_action.triggered.connect(self.showChangePassword)
        logout_action.triggered.connect(self.logout)
    
        menu.exec_(QCursor.pos())

    def openCart(self):
        # Chuyển đến tab giỏ hàng
        self.content_stack.setCurrentIndex(self.cart_tab_index)
    
        # Bỏ chọn tất cả các nút điều hướng
        for button in self.nav_buttons:
            button.setChecked(False)

    def createContent(self, layout):
        self.content_stack = QStackedWidget()
    
        # Khởi tạo CartTab trước
        self.cart_tab = CartTab()
    
        self.tabs = [
            DashboardTab(),
            SalesTab(),
            ProductManagementTab(),
            EmployeeManagementTab(),
            OrderManagementTab(),
            StatisticsTab()
        ]
    
        # Set CartTab cho SalesTab
        self.tabs[1].setCartTab(self.cart_tab)
    
        # Thêm các tab vào stack
        for tab in self.tabs:
            self.content_stack.addWidget(tab)
    
        # Thêm CartTab vào cuối
        self.content_stack.addWidget(self.cart_tab)
        self.cart_tab_index = self.content_stack.count() - 1
    
        layout.addWidget(self.content_stack)

    def getUserInfo(self):
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                # Lấy user_id từ biến toàn cục đã lưu khi đăng nhập
                user_id = globals.current_user_id
            
                cursor.execute("""
                SELECT id, username, name, email, phone, role
                FROM users
                WHERE id = %s
                """, (user_id,))
                user = cursor.fetchone()
                if user:
                    return {
                    "id": user[0],
                    "username": user[1],
                    "name": user[2],
                    "email": user[3],
                    "phone": user[4],
                    "role": user[5]
                }
            except Exception as e:
                print(f"Error fetching user info: {str(e)}")
            finally:
                conn.close()

        # Return default user info if database connection fails
        return {
            "id": "Unknown",
            "username": "unknown",
            "name": "Unknown User",
            "role": "User",
            "email": "unknown@example.com",
            "phone": "N/A"
        }

    def showProfile(self):
        dialog = UserProfileDialog(self.current_user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh user info
            self.current_user = self.getUserInfo()
            self.user_button.setText(f"👤 {self.current_user['name']} ({self.current_user['role']})")

    def showChangePassword(self):
        dialog = ChangePasswordDialog(self.current_user["id"], self)
        dialog.exec()

    def logout(self):
        reply = QMessageBox.question(self, 'Xác nhận', 
                                    'Bạn có chắc chắn muốn đăng xuất?',
                                    QMessageBox.StandardButton.Yes | 
                                    QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No)
    
        if reply == QMessageBox.StandardButton.Yes:
            # Xóa thông tin người dùng hiện tại
            globals.current_user_id = None
        
            # Đóng cửa sổ hiện tại và hiển thị form đăng nhập
            self.hide()
            self.showLoginForm()
    # Thay đổi trong main.py
    def showLoginForm(self):
        self.login_form = LoginForm(onLoginSuccess=lambda: print("Login successful") or self.initializeMainUI())
        self.login_form.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CafeManagementUI()
    sys.exit(app.exec())