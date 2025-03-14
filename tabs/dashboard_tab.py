from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QSizePolicy, QGridLayout, QSpacerItem)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt

from database_connection import connect_db

class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Tiêu đề trang chủ
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("TRANG CHỦ QUẢN LÝ QUÁN CAFE")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #1976D2; margin: 10px;")
        title_layout.addWidget(title_label)
        
        # Phần giới thiệu về quán cafe
        intro_text = """
        <p style='font-size: 16px; line-height: 1.6; text-align: center;'>
        Chào mừng đến với phần mềm quản lý quán cafe của chúng tôi! 
        Hệ thống này giúp bạn quản lý hiệu quả các hoạt động kinh doanh, 
        từ bán hàng, quản lý sản phẩm, đến quản lý nhân viên và thống kê doanh thu.
        </p>
        """
        intro_label = QLabel(intro_text)
        intro_label.setWordWrap(True)
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(intro_label)
        
        main_layout.addWidget(title_frame)
        
        # Thống kê tổng quan
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        # Tạo các widget thống kê
        self.stats_widgets = []
        stats_info = [
            ("💰 Doanh Thu Hôm Nay", "0 VND", self.getDailyRevenue),
            ("📦 Đơn Hàng Hôm Nay", "0", self.getDailyOrders),
            ("📊 Doanh Thu Tháng Này", "0 VND", self.getMonthlyRevenue),
            ("🛒 Tổng Đơn Hàng", "0", self.getTotalOrders)
        ]
        
        row, col = 0, 0
        for title, default_value, update_func in stats_info:
            stats_widget = self.createStatsWidget(title, default_value)
            stats_grid.addWidget(stats_widget, row, col)
            self.stats_widgets.append((stats_widget, update_func))
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        main_layout.addLayout(stats_grid)
        
        # Thêm khoảng trống ở cuối
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Cập nhật dữ liệu thống kê
        self.updateStats()
    
    def createStatsWidget(self, title, value):
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
        """)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        widget.setMinimumHeight(150)
        
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14))
        title_label.setStyleSheet("color: #555;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: #1976D2; margin-top: 10px;")
        layout.addWidget(value_label)
        
        return widget
    
    def updateStats(self):
        # Cập nhật giá trị cho từng widget thống kê
        for widget, update_func in self.stats_widgets:
            value = update_func()
            value_label = widget.findChild(QLabel, "", Qt.FindChildOption.FindDirectChildrenOnly)
            if value_label and value_label.font().pointSize() > 20:  # Xác định đúng label giá trị
                value_label.setText(value)
    
    def getDailyRevenue(self):
        # Lấy doanh thu hôm nay từ CSDL
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COALESCE(SUM(total_amount), 0) 
                    FROM orders 
                    WHERE DATE(order_date) = CURDATE()
                """)
                result = cursor.fetchone()
                if result and result[0]:
                    return f"{int(result[0]):,} VND"
            except Exception as e:
                print(f"Error getting daily revenue: {str(e)}")
            finally:
                conn.close()
        return "0 VND"
    
    def getMonthlyRevenue(self):
        # Lấy doanh thu tháng này từ CSDL
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COALESCE(SUM(total_amount), 0) 
                    FROM orders 
                    WHERE YEAR(order_date) = YEAR(CURDATE()) 
                    AND MONTH(order_date) = MONTH(CURDATE())
                """)
                result = cursor.fetchone()
                if result and result[0]:
                    return f"{int(result[0]):,} VND"
            except Exception as e:
                print(f"Error getting monthly revenue: {str(e)}")
            finally:
                conn.close()
        return "0 VND"
    
    def getDailyOrders(self):
        # Lấy số đơn hàng hôm nay từ CSDL
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM orders 
                    WHERE DATE(order_date) = CURDATE()
                """)
                result = cursor.fetchone()
                if result:
                    return str(result[0])
            except Exception as e:
                print(f"Error getting daily orders: {str(e)}")
            finally:
                conn.close()
        return "0"
    
    def getTotalOrders(self):
        # Lấy tổng số đơn hàng từ CSDL
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM orders")
                result = cursor.fetchone()
                if result:
                    return str(result[0])
            except Exception as e:
                print(f"Error getting total orders: {str(e)}")
            finally:
                conn.close()
        return "0"