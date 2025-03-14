from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHBoxLayout, QFrame, QGridLayout, QScrollArea, QPushButton,
    QFileDialog, QMessageBox, QSizePolicy)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QSize
from database_connection import connect_db
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from datetime import datetime
from decimal import Decimal

class StatisticsCard(QFrame):
    def __init__(self, title, value, unit=""):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                border: 1px solid #E0E0E0;
            }
            QLabel {
                color: #333;
            }
        """)
        layout = QVBoxLayout(self)
        
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Arial", 12))
        
        value_label = QLabel(f"{value:,} {unit}")
        value_label.setObjectName("valueLabel")
        value_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.setContentsMargins(15, 15, 15, 15)

class StatisticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.top_products = []
        self.summary_data = {}
        self.initUI()
        self.loadStatistics()
    
    def initUI(self):
        # Main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # Remove border
        
        # Create container widget for scroll area
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(20)
        self.container_layout.setContentsMargins(10, 10, 10, 20)  # Add extra bottom margin
        
        # Header with title and export button
        header_layout = QHBoxLayout()
        title = QLabel("Thống Kê Cửa Hàng")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #333;")
        header_layout.addWidget(title)
        
        # Export button
        self.export_btn = QPushButton("Xuất Excel")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b3d;
            }
        """)
        self.export_btn.setMinimumWidth(120)
        self.export_btn.clicked.connect(self.exportToExcel)
        header_layout.addWidget(self.export_btn)
        header_layout.setStretchFactor(title, 3)
        header_layout.setStretchFactor(self.export_btn, 1)
        self.container_layout.addLayout(header_layout)
        
        # Statistics Cards in Grid Layout
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        self.cards = {
            'total_products': StatisticsCard("Tổng số sản phẩm", 0, "sản phẩm"),
            'total_customers': StatisticsCard("Tổng số khách hàng", 0, "khách hàng"),
            'total_revenue': StatisticsCard("Tổng doanh thu", 0, "VNĐ"),
            'total_inventory': StatisticsCard("Tổng hàng tồn kho", 0, "sản phẩm")
        }
        
        positions = [(i, j) for i in range(2) for j in range(2)]
        for (card_name, card), position in zip(self.cards.items(), positions):
            cards_layout.addWidget(card, *position)
        
        self.container_layout.addLayout(cards_layout)
        
        # Charts Section
        charts_frame = QFrame()
        charts_frame.setFrameShape(QFrame.Shape.StyledPanel)
        charts_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        charts_layout = QVBoxLayout(charts_frame)
        charts_layout.setContentsMargins(15, 15, 15, 15)
        
        # Charts Title
        charts_title = QLabel("Biểu Đồ Phân Tích")
        charts_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        charts_layout.addWidget(charts_title)
        
        # Create matplotlib figures with larger size
        self.figure1 = Figure(figsize=(12, 8), dpi=100)  # Increased figure size
        self.ax1 = self.figure1.add_subplot(121)
        self.ax2 = self.figure1.add_subplot(122)
        
        self.canvas1 = FigureCanvas(self.figure1)
        self.canvas1.setMinimumHeight(400)  # Set minimum height for charts
        self.canvas1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        charts_layout.addWidget(self.canvas1)
        
        self.container_layout.addWidget(charts_frame)
        
        # Detailed Statistics Table in a frame
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.StyledPanel)
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
            QTableWidget {
                border: none;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        table_label = QLabel("Chi Tiết Top 5 Sản Phẩm")
        table_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        table_layout.addWidget(table_label)
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels([
            "Danh Mục", "Số Lượng", "Doanh Thu", "Tỷ Lệ (%)"
        ])
        self.stats_table.setMinimumHeight(200)  # Ensure table has minimum height
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setStyleSheet("alternate-background-color: #f5f5f5;")
        table_layout.addWidget(self.stats_table)
        
        self.container_layout.addWidget(table_frame)
        
        # Add a spacer widget at the bottom to ensure everything is scrollable
        spacer = QWidget()
        spacer.setMinimumHeight(20)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.container_layout.addWidget(spacer)
        
        # Set up scroll area and finish layout
        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)
    
    def loadStatistics(self):
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            # Tổng số sản phẩm
            cursor.execute("SELECT COUNT(*), SUM(stock) FROM products")
            product_count, total_stock = cursor.fetchone()
            product_count = int(product_count or 0)
            total_stock = int(total_stock or 0)
            
            # Cập nhật các card
            self.cards['total_products'].findChild(QLabel, "valueLabel").setText(f"{product_count:,} sản phẩm")
            self.cards['total_inventory'].findChild(QLabel, "valueLabel").setText(f"{total_stock:,} sản phẩm")
            
            # Tổng số khách hàng từ bảng users
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
            customer_count = int(cursor.fetchone()[0] or 0)
            self.cards['total_customers'].findChild(QLabel, "valueLabel").setText(f"{customer_count:,} khách hàng")
            
            # Tổng doanh thu (giả định từ giá * số lượng)
            cursor.execute("SELECT SUM(price * stock) FROM products")
            total_revenue = cursor.fetchone()[0] or 0
            total_revenue = float(total_revenue) if isinstance(total_revenue, Decimal) else total_revenue
            self.cards['total_revenue'].findChild(QLabel, "valueLabel").setText(f"{int(total_revenue):,} VNĐ")
            
            # Lưu dữ liệu tổng quan để xuất Excel
            self.summary_data = {
                'total_products': product_count,
                'total_inventory': total_stock,
                'total_customers': customer_count,
                'total_revenue': total_revenue
            }
            
            # Data for charts
            cursor.execute("""
                SELECT name, stock, price * stock as revenue, price 
                FROM products 
                ORDER BY revenue DESC 
                LIMIT 5
            """)
            self.top_products = cursor.fetchall()
            
            # Update pie chart
            names = [p[0] for p in self.top_products]
            revenues = [float(p[2]) if isinstance(p[2], Decimal) else p[2] for p in self.top_products]
            self.ax1.clear()
            wedges, texts, autotexts = self.ax1.pie(
                revenues, 
                labels=names,
                autopct='%1.1f%%',
                textprops={'fontsize': 10},
                wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
            )
            # Make pie chart labels more readable
            for text in texts:
                text.set_fontsize(9)
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_weight('bold')
                
            self.ax1.set_title('Top 5 Sản Phẩm theo Doanh Thu', fontsize=12, pad=15)
            
            # Update bar chart
            stocks = [p[1] for p in self.top_products]
            self.ax2.clear()
            bars = self.ax2.bar(
                names, 
                stocks,
                color='#4CAF50',
                edgecolor='white',
                linewidth=1
            )
            
            # Add data labels on top of bars
            for bar in bars:
                height = bar.get_height()
                self.ax2.text(
                    bar.get_x() + bar.get_width()/2., 
                    height + 0.1,
                    f'{int(height):,}',
                    ha='center', 
                    va='bottom',
                    fontsize=9
                )
                
            self.ax2.set_title('Số Lượng Tồn Kho của Top 5 Sản Phẩm', fontsize=12, pad=15)
            self.ax2.tick_params(axis='x', rotation=45, labelsize=9)
            self.ax2.tick_params(axis='y', labelsize=9)
            self.ax2.spines['top'].set_visible(False)
            self.ax2.spines['right'].set_visible(False)
            self.ax2.set_axisbelow(True)
            self.ax2.grid(axis='y', linestyle='--', alpha=0.7)
            
            self.figure1.tight_layout(pad=3.0)  # Increased padding
            self.canvas1.draw()
            
            # Update table
            self.stats_table.setRowCount(len(self.top_products))
            total_rev = sum(revenues)
            total_rev = float(total_rev) if total_rev else 1  # Avoid division by zero
            
            for i, (name, stock, revenue, price) in enumerate(self.top_products):
                revenue = float(revenue) if isinstance(revenue, Decimal) else revenue
                
                # Format cells and add data
                name_item = QTableWidgetItem(name)
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
                stock_item = QTableWidgetItem(f"{stock:,}")
                stock_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                revenue_item = QTableWidgetItem(f"{int(revenue):,} VNĐ")
                revenue_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                percentage_item = QTableWidgetItem(f"{(revenue / total_rev) * 100:.1f}%")
                percentage_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                self.stats_table.setItem(i, 0, name_item)
                self.stats_table.setItem(i, 1, stock_item)
                self.stats_table.setItem(i, 2, revenue_item)
                self.stats_table.setItem(i, 3, percentage_item)
            
            # Format table appearance
            self.stats_table.horizontalHeader().setStretchLastSection(True)
            self.stats_table.setColumnWidth(0, 200)  # Name column
            self.stats_table.setColumnWidth(1, 100)  # Stock column
            self.stats_table.setColumnWidth(2, 150)  # Revenue column
            
        except Exception as e:
            print(f"Lỗi khi tải thống kê: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def exportToExcel(self):
        try:
            # Chọn vị trí và tên file
            file_name, _ = QFileDialog.getSaveFileName(
                self, 
                "Xuất báo cáo Excel", 
                f"Báo_Cáo_Doanh_Thu_{datetime.now().strftime('%d-%m-%Y')}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if not file_name:
                return  # Người dùng đã hủy
            
            # Tạo file Excel với pandas
            with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Định dạng tiêu đề
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4CAF50',
                    'color': 'white',
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1
                })
                
                # Định dạng số liệu
                number_format = workbook.add_format({
                    'num_format': '#,##0',
                    'align': 'right'
                })
                
                # Định dạng tiền tệ
                currency_format = workbook.add_format({
                    'num_format': '#,##0 "VNĐ"',
                    'align': 'right'
                })
                
                # Định dạng phần trăm
                percent_format = workbook.add_format({
                    'num_format': '0.0%',
                    'align': 'right'
                })
                
                # ---- Sheet 1: Tổng Quan ----
                df_summary = pd.DataFrame({
                    'Chỉ số': ['Tổng số sản phẩm', 'Tổng hàng tồn kho', 'Tổng số khách hàng', 'Tổng doanh thu'],
                    'Giá trị': [
                        self.summary_data['total_products'],
                        self.summary_data['total_inventory'],
                        self.summary_data['total_customers'],
                        self.summary_data['total_revenue']
                    ],
                    'Đơn vị': ['sản phẩm', 'sản phẩm', 'khách hàng', 'VNĐ']
                })
                
                df_summary.to_excel(writer, sheet_name='Tổng Quan', index=False)
                
                # Định dạng Sheet Tổng Quan
                sheet1 = writer.sheets['Tổng Quan']
                sheet1.set_column('A:A', 20)
                sheet1.set_column('B:B', 15)
                sheet1.set_column('C:C', 15)
                
                # Thêm định dạng cho tiêu đề
                for col_num, value in enumerate(df_summary.columns.values):
                    sheet1.write(0, col_num, value, header_format)
                
                # Định dạng giá trị
                for i in range(len(df_summary)):
                    if i == 3:  # Dòng doanh thu
                        sheet1.write(i+1, 1, df_summary.iloc[i, 1], currency_format)
                    else:
                        sheet1.write(i+1, 1, df_summary.iloc[i, 1], number_format)
                
                # ---- Sheet 2: Chi Tiết Sản Phẩm ----
                if self.top_products:
                    # Tạo dataframe từ top_products
                    product_data = []
                    total_rev = sum(float(p[2]) for p in self.top_products)
                    
                    for name, stock, revenue, price in self.top_products:
                        product_data.append({
                            'Tên sản phẩm': name,
                            'Tồn kho': stock,
                            'Đơn giá': price,
                            'Doanh thu': revenue,
                            'Tỷ lệ': revenue / total_rev
                        })
                    
                    df_products = pd.DataFrame(product_data)
                    df_products.to_excel(writer, sheet_name='Chi Tiết Sản Phẩm', index=False)
                    
                    # Định dạng Sheet Chi Tiết
                    sheet2 = writer.sheets['Chi Tiết Sản Phẩm']
                    sheet2.set_column('A:A', 30)
                    sheet2.set_column('B:B', 15)
                    sheet2.set_column('C:C', 15)
                    sheet2.set_column('D:D', 20)
                    sheet2.set_column('E:E', 15)
                    
                    # Thêm định dạng cho tiêu đề
                    for col_num, value in enumerate(df_products.columns.values):
                        sheet2.write(0, col_num, value, header_format)
                    
                    # Định dạng giá trị
                    for i in range(len(df_products)):
                        sheet2.write(i+1, 1, df_products.iloc[i, 1], number_format)
                        sheet2.write(i+1, 2, df_products.iloc[i, 2], currency_format)
                        sheet2.write(i+1, 3, df_products.iloc[i, 3], currency_format)
                        sheet2.write(i+1, 4, df_products.iloc[i, 4], percent_format)
            
            QMessageBox.information(self, "Xuất Excel thành công", 
                                   f"Đã xuất báo cáo thành công đến:\n{file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi xuất Excel", 
                               f"Đã xảy ra lỗi khi xuất báo cáo: {str(e)}")