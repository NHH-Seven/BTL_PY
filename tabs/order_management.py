from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QLineEdit, 
                              QPushButton, QHBoxLayout, QTableWidgetItem, QHeaderView,
                              QComboBox, QDateEdit, QMessageBox, QDialog, QGridLayout)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, QDate
from database_connection import connect_db
from datetime import datetime, timedelta

class OrderDetailDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.parent = parent  # Store parent reference for refreshing the table later
        self.setWindowTitle(f"Chi tiết đơn hàng #{order_id}")
        self.setMinimumSize(600, 400)
        self.initUI()
        self.loadOrderDetails()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Order information section
        info_container = QWidget()
        info_container.setStyleSheet("""
            background-color: #E3F2FD;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        """)
        info_layout = QGridLayout(info_container)
        
        # Info labels
        self.id_label = QLabel(f"Mã đơn hàng: #{self.order_id}")
        self.id_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        self.customer_label = QLabel("Khách hàng: ")
        self.phone_label = QLabel("Số điện thoại: ")
        self.date_label = QLabel("Ngày đặt: ")
        self.status_label = QLabel("Phương thức thanh toán: ")
        self.total_label = QLabel("Tổng tiền: ")
        self.total_label.setStyleSheet("color: #d35400; font-weight: bold;")
        
        info_layout.addWidget(self.id_label, 0, 0, 1, 2)
        info_layout.addWidget(self.customer_label, 1, 0)
        info_layout.addWidget(self.phone_label, 1, 1)
        info_layout.addWidget(self.date_label, 2, 0)
        info_layout.addWidget(self.status_label, 2, 1)
        info_layout.addWidget(self.total_label, 3, 0, 1, 2)
        
        layout.addWidget(info_container)
        
        # Order items table
        items_label = QLabel("Sản phẩm trong đơn hàng:")
        items_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(items_label)
        
        self.items_table = QTableWidget(0, 5)
        self.items_table.setHorizontalHeaderLabels([
            "Mã SP", "Tên sản phẩm", "Đơn giá", "Số lượng", "Thành tiền"
        ])
        
        # Adjust column widths
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Price
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Quantity
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Total
        
        self.items_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #E3F2FD;
                padding: 5px;
                border: 1px solid #BBDEFB;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.items_table)
        
        # Button container for all buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        
        # Edit button
        edit_button = QPushButton("Sửa")
        edit_button.setStyleSheet("""
            background-color: #FFA000;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        edit_button.clicked.connect(self.editOrder)
        
        # Delete button
        delete_button = QPushButton("Xóa")
        delete_button.setStyleSheet("""
            background-color: #F44336;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        delete_button.clicked.connect(self.deleteOrder)
        
        # Close button
        close_button = QPushButton("Đóng")
        close_button.setStyleSheet("""
            background-color: #1976D2;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        close_button.clicked.connect(self.accept)
        
        # Add all buttons to layout with some space
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addWidget(button_container)
        
    def loadOrderDetails(self):
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get order information
                cursor.execute("""
                    SELECT customer_name, phone_number, order_date, status, total_amount
                    FROM orders
                    WHERE id = %s
                """, (self.order_id,))
                
                order_info = cursor.fetchone()
                if not order_info:
                    QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin đơn hàng!")
                    self.close()
                    return
                
                customer_name, phone, date, status, total = order_info
                
                # Format date
                date_obj = date
                if isinstance(date, str):
                    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                
                # Update labels
                self.customer_label.setText(f"Khách hàng: {customer_name}")
                self.phone_label.setText(f"Số điện thoại: {phone}")
                self.date_label.setText(f"Ngày đặt: {formatted_date}")
                self.status_label.setText(f"Phương thức thanh toán: {status}")
                self.total_label.setText(f"Tổng tiền: {format(total, ',.0f')} VNĐ")
                
                # Get order items - FIX: Thay đổi oi.unit_price thành oi.price (hoặc tên cột chính xác)
                cursor.execute("""
                    SELECT oi.product_id, p.name, oi.price, oi.quantity, (oi.price * oi.quantity) as item_total
                    FROM order_items oi
                    JOIN products p ON p.id = oi.product_id
                    WHERE oi.order_id = %s
                """, (self.order_id,))
                
                items = cursor.fetchall()
                
                # Populate items table
                self.items_table.setRowCount(len(items))
                
                for row_idx, item in enumerate(items):
                    product_id, name, price, quantity, item_total = item
                    
                    # Create table items
                    id_item = QTableWidgetItem(str(product_id))
                    name_item = QTableWidgetItem(name)
                    price_item = QTableWidgetItem(f"{format(price, ',.0f')} VNĐ")
                    quantity_item = QTableWidgetItem(str(quantity))
                    total_item = QTableWidgetItem(f"{format(item_total, ',.0f')} VNĐ")
                    
                    # Set alignment
                    id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    quantity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    
                    # Set items to table
                    self.items_table.setItem(row_idx, 0, id_item)
                    self.items_table.setItem(row_idx, 1, name_item)
                    self.items_table.setItem(row_idx, 2, price_item)
                    self.items_table.setItem(row_idx, 3, quantity_item)
                    self.items_table.setItem(row_idx, 4, total_item)
                
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể tải chi tiết đơn hàng: {str(e)}")
            finally:
                conn.close()
                
    # Implement edit function
    def editOrder(self):
        # This is a placeholder - you'll need to implement an order editing dialog
        QMessageBox.information(self, "Sửa đơn hàng", 
                               f"Chức năng sửa đơn hàng #{self.order_id} đang được phát triển.")
        # Here you would open an EditOrderDialog or similar
        
    # Implement delete function
    def deleteOrder(self):
        # Ask for confirmation before deleting
        reply = QMessageBox.question(self, "Xác nhận xóa", 
                                    f"Bạn có chắc chắn muốn xóa đơn hàng #{self.order_id}?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = connect_db()
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    # First delete order items (foreign key constraint)
                    cursor.execute("DELETE FROM order_items WHERE order_id = %s", (self.order_id,))
                    
                    # Then delete the order
                    cursor.execute("DELETE FROM orders WHERE id = %s", (self.order_id,))
                    
                    # Commit the transaction
                    conn.commit()
                    
                    QMessageBox.information(self, "Thành công", 
                                           f"Đã xóa đơn hàng #{self.order_id}")
                    
                    # Refresh the order list in parent widget
                    if self.parent and hasattr(self.parent, 'refreshAfterPayment'):
                        self.parent.refreshAfterPayment()
                    
                    # Close dialog
                    self.accept()
                    
                except Exception as e:
                    conn.rollback()
                    QMessageBox.warning(self, "Lỗi", f"Không thể xóa đơn hàng: {str(e)}")
                finally:
                    conn.close()

class OrderManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadOrders()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Quản Lý Đơn Hàng")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976D2; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Filter section
        filter_container = QWidget()
        filter_container.setStyleSheet("""
            background-color: #F5F5F5;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        """)
        filter_layout = QVBoxLayout(filter_container)
        
        # Search filters
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm theo tên hoặc số điện thoại...")
        self.search_input.setStyleSheet("padding: 8px;")
        
        self.payment_filter = QComboBox()
        self.payment_filter.addItems(["Tất cả", "Tiền mặt", "Chuyển khoản"])
        self.payment_filter.setStyleSheet("padding: 8px;")
        
        # Date range
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Từ ngày:"))
        
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.from_date)
        
        date_layout.addWidget(QLabel("Đến ngày:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.to_date)
        
        search_button = QPushButton("Tìm kiếm")
        search_button.setStyleSheet("""
            background-color: #2196F3;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        search_button.clicked.connect(self.loadOrders)
        
        reset_button = QPushButton("Làm mới")
        reset_button.setStyleSheet("""
            background-color: #FF9800;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        reset_button.clicked.connect(self.resetFilters)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.payment_filter)
        search_layout.addWidget(search_button)
        search_layout.addWidget(reset_button)
        
        filter_layout.addLayout(search_layout)
        filter_layout.addLayout(date_layout)
        
        layout.addWidget(filter_container)
        
        # Order table
        self.order_table = QTableWidget(0, 7)  # Added one more column for detail button
        self.order_table.setHorizontalHeaderLabels([
            "Mã ĐH", "Tên KH", "Số điện thoại", "Ngày Đặt", "Tổng Tiền", "Trạng Thái", "Chi tiết"
        ])
        
        # Adjust column widths
        header = self.order_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Phone
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Total
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Detail button
        
        self.order_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #E3F2FD;
                padding: 5px;
                border: 1px solid #BBDEFB;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.order_table)
        
        # Summary section
        summary_widget = QWidget()
        summary_widget.setStyleSheet("""
            background-color: #FAFAFA;
            border-radius: 5px;
            padding: 10px;
        """)
        summary_layout = QHBoxLayout(summary_widget)
        
        self.total_orders_label = QLabel("Tổng số đơn hàng: 0")
        self.total_revenue_label = QLabel("Tổng doanh thu: 0 VNĐ")
        self.total_revenue_label.setStyleSheet("font-weight: bold; color: #2E7D32;")
        
        summary_layout.addWidget(self.total_orders_label)
        summary_layout.addStretch()
        summary_layout.addWidget(self.total_revenue_label)
        
        layout.addWidget(summary_widget)
    
    def resetFilters(self):
        self.search_input.clear()
        self.payment_filter.setCurrentIndex(0)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.to_date.setDate(QDate.currentDate())
        self.loadOrders()
    
    def loadOrders(self):
        # Clear current table
        self.order_table.setRowCount(0)
        
        # Get filter values
        search_text = self.search_input.text().strip()
        payment_method = self.payment_filter.currentText()
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        
        # Add one day to to_date to include the entire day
        to_date_obj = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
        to_date = to_date_obj.strftime("%Y-%m-%d")
        
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Build query with filters
                query = """
                    SELECT id, customer_name, phone_number, order_date, total_amount, status
                    FROM orders
                    WHERE order_date BETWEEN %s AND %s
                """
                params = [from_date, to_date]
                
                # Add search filter if provided
                if search_text:
                    query += " AND (customer_name ILIKE %s OR phone_number ILIKE %s)"
                    search_pattern = f"%{search_text}%"
                    params.extend([search_pattern, search_pattern])
                
                # Add payment method filter if not "All"
                if payment_method != "Tất cả":
                    query += " AND status = %s"
                    params.append(payment_method)
                
                # Order by date descending (newest first)
                query += " ORDER BY order_date DESC"
                
                cursor.execute(query, params)
                orders = cursor.fetchall()
                
                # Populate table
                self.order_table.setRowCount(len(orders))
                
                total_revenue = 0
                
                for row_idx, order in enumerate(orders):
                    order_id, name, phone, date, amount, status = order
                    
                    # Format date
                    date_obj = date
                    if isinstance(date, str):
                        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                    formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                    
                    # Add to total revenue
                    total_revenue += float(amount)
                    
                    # Create table items
                    id_item = QTableWidgetItem(str(order_id))
                    name_item = QTableWidgetItem(name)
                    phone_item = QTableWidgetItem(phone)
                    date_item = QTableWidgetItem(formatted_date)
                    amount_item = QTableWidgetItem(f"{format(amount, ',.0f')} VNĐ")
                    status_item = QTableWidgetItem(status)
                    
                    # Set alignment
                    id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Set background color based on payment method
                    if status == "Tiền mặt":
                        status_item.setBackground(QColor("#E8F5E9"))  # Light green
                    else:
                        status_item.setBackground(QColor("#E3F2FD"))  # Light blue
                    
                    # Set items to table
                    self.order_table.setItem(row_idx, 0, id_item)
                    self.order_table.setItem(row_idx, 1, name_item)
                    self.order_table.setItem(row_idx, 2, phone_item)
                    self.order_table.setItem(row_idx, 3, date_item)
                    self.order_table.setItem(row_idx, 4, amount_item)
                    self.order_table.setItem(row_idx, 5, status_item)
                    
                    # Add detail button
                    detail_btn = QPushButton("Xem")
                    detail_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #1976D2;
                            color: white;
                            border-radius: 3px;
                            padding: 3px 8px;
                        }
                        QPushButton:hover {
                            background-color: #1565C0;
                        }
                    """)
                    # Using lambda to pass the order_id to the function
                    detail_btn.clicked.connect(lambda checked, oid=order_id: self.showOrderDetail(oid))
                    
                    self.order_table.setCellWidget(row_idx, 6, detail_btn)
                
                # Update summary labels
                self.total_orders_label.setText(f"Tổng số đơn hàng: {len(orders)}")
                self.total_revenue_label.setText(f"Tổng doanh thu: {format(total_revenue, ',.0f')} VNĐ")
                
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu đơn hàng: {str(e)}")
            finally:
                conn.close()
    
    def showOrderDetail(self, order_id):
        detail_dialog = OrderDetailDialog(order_id, self)
        detail_dialog.exec()
        
    # Thêm phương thức mới để cập nhật bảng sau khi thanh toán
    def refreshAfterPayment(self, order_id=None):
        """Cập nhật bảng đơn hàng sau khi thanh toán thành công"""
        self.loadOrders()
        
        # Nếu order_id được cung cấp, tự động mở chi tiết đơn hàng
        if order_id:
            self.showOrderDetail(order_id)