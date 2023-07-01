import csv
import datetime
import os
import random
import sys
import webbrowser
from PyQt5.QtWidgets import *
import sqlite3
from PyQt5.QtGui import * 
from PyQt5.QtPrintSupport import * 
from fpdf import FPDF
from tkcalendar import Calendar, DateEntry
from datetime import datetime
from time import strftime
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from fpdf import FPDF as ArabicPDF
from PyQt5.QtCore import *
from PyQt5.QtSql import *
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from os import startfile
from subprocess import Popen, PIPE
import win32api
import win32print




conn = sqlite3.connect('StorDB.db')
c= conn.cursor()
result = c.execute("""CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            password TEXT NOT NULL,
                            role TEXT NOT NULL,
                            can_add_products INTEGER DEFAULT 0,
                            can_edit_products INTEGER DEFAULT 0,
                            can_delete_products INTEGER DEFAULT 0,
                            trial_end_date TEXT NOT NULL
                            )""")

result1 = c.execute("""CREATE TABLE IF NOT EXISTS products(
                                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                product_name TEXT NOT NULL,
                                product_stok TEXT NOT NULL,
                                product_co_stoke TEXT NOT NULL,
                                product_cp TEXT NOT NULL,
                                product_sp TEXT NOT NULL,
                                product_totalcp TEXT NOT NULL,
                                product_totalsp TEXT NOT NULL,
                                product_assumed_profid TEXT NOT NULL,
                                product_vendor TEXT NOT NULL,
                                product_vendor_ph TEXT NOT NULL
                                )""")

result2 = c.execute("""CREATE TABLE IF NOT EXISTS invoices (
                                invoice_number INTEGER PRIMARY KEY AUTOINCREMENT, 
                                total_price TEXT NOT NULL,
                                Phone TEXT NOT NULL,
                                Name TEXT NOT NULL,
                                Address TEXT NOT NULL,
                                sale_date TEXT
                                )""")

result3 = c.execute('''CREATE TABLE IF NOT EXISTS cart_items (
                                id INTEGER PRIMARY KEY,
                                invoice_id INTEGER,
                                product_name TEXT,
                                price REAL,
                                quantity INTEGER,
                                discount REAL,
                                total_price REAL,
                                sale_date TEXT,
                                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
                                )''')


result4 = c.execute("""CREATE TABLE IF NOT EXISTS add_customer (
                                phone_customer TEXT NOT NULL PRIMARY KEY, 
                                name_customer TEXT NOT NULL,
                                address_customer TEXT NOT NULL
                                )""")
                               
result5 = c.execute("""CREATE TABLE IF NOT EXISTS suppliers (
                                id INTEGER PRIMARY KEY, 
                                name TEXT NOT NULL,
                                address TEXT NOT NULL,
                                Phone_suppliers TEXT NOT NULL,
                                numper_bill_Suppliers TEXT NOT NULL,
                                how_much_bill TEXT NOT NULL,
                                term_value TEXT NOT NULL,
                                method_of_payment TEXT NOT NULL,
                                Been_paid TEXT NOT NULL
                                )""")
                               

result6 = c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                product_name TEXT NOT NULL UNIQUE,
                                available_quantity INTEGER NOT NULL,
                                minimum_quantity INTEGER NOT NULL
                               )''')




day_date = datetime.datetime.now().date()
string = time.strftime('%H:%M:%S %p')

class POS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1200, 1024)
        self.setWindowTitle("ادارة المخزن الرئيسى")
        self.initUI()

    def initUI(self):
        # تصميم واجهة المستخدم
            # تحديد لون الخلفية

        # إضافة العناصر الأخرى
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.gridLayout = QGridLayout(self.centralWidget)
        
        self.centralWidget.setAutoFillBackground(True)
        p = self.centralWidget.palette()
        p.setColor(self.centralWidget.backgroundRole(), QColor(251, 251, 251))
        self.centralWidget.setPalette(p)
        
        # self.Hello = QLabel('مرحبا بك في برنامج إدارة المخزن الرئيسي', self.centralWidget)
       

        # self.Hello.setAlignment(Qt.AlignCenter)
        # self.gridLayout.addWidget(self.Hello, 0, 0)
        # # ----------------- Label -----------------      

        menubarSupplier = self.menuBar()
        fileMenuSupplier = menubarSupplier.addMenu('القائمة')
        editMenu = menubarSupplier.addMenu('Edit')

        storemangAct = QAction('موردين', self)
        storemangAct.triggered.connect(self.show_Supplier)
        fileMenuSupplier.addAction(storemangAct)

        repAct = QAction('تقارير', self)
        repAct.triggered.connect(self.show_totalsell)
        # newuserAct.setShortcut('Ctrl+S')
        fileMenuSupplier.addAction(repAct)

        repAct = QAction('شاشة البيع', self)
        repAct.triggered.connect(self.show_Sell_screen)
        # newuserAct.setShortcut('Ctrl+S')
        fileMenuSupplier.addAction(repAct)

        copyAct = QAction('Copy', self)
        editMenu.addAction(copyAct)


        self.id_label = QLabel('رقم المنتج', self)
        self.id_label.move(15, 50)  
        self.id_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.name_label = QLabel('اسم الصنف', self)
        self.name_label.move(15, 80)  
        self.name_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.stok_label = QLabel('الكمية', self)
        self.stok_label.move(15, 110)  
        self.stok_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.co_stoke_label = QLabel('نوع الكمية', self)
        self.co_stoke_label.move(15, 140)  
        self.co_stoke_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.cp_label = QLabel('سعر الشراء', self)
        self.cp_label.move(335, 50)  
        self.cp_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.sp_label = QLabel('سعر البيع', self)
        self.sp_label.move(335, 80)  
        self.sp_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.vendor_label = QLabel('اسم المورد', self)
        self.vendor_label.move(335, 110)  
        self.vendor_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.vendor_ph_label = QLabel('هاتف المورد', self)
        self.vendor_ph_label.move(335, 140)  
        self.vendor_ph_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        # ----------------- LineEdit -----------------
        self.id_le = QLineEdit(self)
        self.id_le.move(120, 55) 
        self.id_le.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;")        
        self.name_le = QLineEdit(self)
        self.name_le.move(120, 85) 
        self.name_le.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
        
        self.stok_le = QLineEdit(self)
        self.stok_le.move(120, 115) 
        self.stok_le.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 

        self.co_stok_le = QComboBox(self)
        self.co_stok_le.addItems(['عدد', 'كيلو', 'متر', 'كرتونة', 'كيس', 'علبة'])
        self.co_stok_le.move(120, 145)
        # self.co_stok_le.setStyleSheet("font-size: 14px; min-width: 200px; \
        #                           max-width: 300px; min-height:10px; max-height: 20px;") 

        self.cp_le = QLineEdit(self)
        self.cp_le.move(440, 55) 
        self.cp_le.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
        
        self.sp_le = QLineEdit(self)
        self.sp_le.move(440, 85) 
        self.sp_le.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
        
        self.vendor_le = QLineEdit(self)
        self.vendor_le.move(440, 115) 
        self.vendor_le.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
        
        self.vendor_ph_le = QLineEdit(self)
        self.vendor_ph_le.move(440, 145) 
        self.vendor_ph_le.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
        # ----------------- Button -----------------
        self.save_button = QPushButton('حفظ', self)
        self.save_button.move(60, 180) 
        self.save_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")

        self.upd_item_button = QPushButton('تعديل', self)
        self.upd_item_button.move(220, 180) 
        self.upd_item_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")

        self.delete_button = QPushButton('حذف', self)
        self.delete_button.move(370, 180) 
        self.delete_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")

        self.search_item_button = QPushButton('بحث', self)
        self.search_item_button.move(540, 180) 
        self.search_item_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        
        self.show_button = QPushButton('عرض', self)
        self.show_button.move(60, 230) 
        self.show_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; min-width: 550px; \
                                  max-width: 650px; min-height:10px; max-height: 20px; padding: 8px 16px; border-radius: 4px;")
        
        self.exit_button = QPushButton('خروج', self)
        self.exit_button.move(60, 650) 
        self.exit_button.setStyleSheet("background-color: #CA1D2B; color: white; font-size: 12px; font-weight: bold; min-width: 550px; \
                                  max-width: 650px; min-height:10px; max-height: 20px; padding: 8px 16px; border-radius: 4px;")
        # ----------------- Table -----------------
        self.table = QTableWidget(self)
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels(
            ['رقم المنتج', 'اسم الصنف', 'الكمية', 'نوع الكمية', 'سعر الشراء', 'سعر البيع', 'إجمالى سعر الشراء', 'إجمالى سعر البيع', 'الربحية','اسم المورد', 'هاتف المورد'])
        self.table.setGeometry(5,285,1100,350)
        self.table.setStyleSheet("background-color: white; alternate-background-color: #1D82CA; color: black; border: 1px solid #ccc; font-size: 12px;"
                         "QTableView::item:selected{background-color: #907AB3; }")

        self.total_cp_label = QLabel(self)
        self.total_cp_label.setAlignment(Qt.AlignRight)
        self.total_cp_label.setGeometry(900, 740, 190, 20)

        self.total_sp_label = QLabel(self)
        self.total_sp_label.setAlignment(Qt.AlignRight)
        self.total_sp_label.setGeometry(900, 770, 190, 20)  

        self.total_assumed_profid_label = QLabel(self)
        self.total_assumed_profid_label.setAlignment(Qt.AlignRight)
        self.total_assumed_profid_label.setGeometry(900, 800, 190, 20)  

        # ----------------- Connect -----------------
        self.save_button.clicked.connect(self.save_product)
        self.show_button.clicked.connect(self.show_data)
        self.delete_button.clicked.connect(self.delete_data)
        self.exit_button.clicked.connect(self.exit_app)
        self.search_item_button.clicked.connect(self.search_product)
        self.upd_item_button.clicked.connect(self.update_product)

    # def delete_data(self):
    #     # حذف البيانات
    #     if self.table.selectionModel().hasSelection():
    #         rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
    #         count = 0
    #         for row in rows:
    #             count += 1
    #             self.table.removeRow(row)
    #         with open('data.csv', 'r', newline='', encoding='utf-8') as file:
    #             reader = csv.reader(file)
    #             data = [row for i, row in enumerate(reader) if i not in rows]
    #         with open('data.csv', 'w', newline='', encoding='utf-8') as file:
    #             writer = csv.writer(file)
    #             writer.writerows(data)

    def exit_app(self):
        # إغلاق التطبيق
        self.close()


        # ----------------- Fun -----------------

    def update_product(self):
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()

        product_id = self.id_le.text()
        name = self.name_le.text()
        stok = float(self.stok_le.text())
        co_stoke = self.co_stok_le.currentText()
        cp = float(self.cp_le.text())
        sp = float(self.sp_le.text())
        vendor = self.vendor_le.text()
        vendor_ph = self.vendor_ph_le.text()
        totalcp = cp * stok
        totalsp = sp * stok
        assumed_profid = (totalsp - totalcp)

        result1 = '''UPDATE products SET product_name=?, product_stok=?, product_co_stoke=?, product_cp=?, product_sp=?, product_totalcp=?, product_totalsp=?, product_assumed_profid=?,product_vendor=?,product_vendor_ph=? WHERE product_id=?'''
        c.execute(result1, (name, stok, co_stoke, cp, sp, totalcp, totalsp,assumed_profid, vendor, vendor_ph, product_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, 'Success', 'تم تحديث المنتج بنجاح!')
    def search_product(self):
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()
        product_id = self.id_le.text()

        c.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        data = c.fetchone()
        if data:
            self.name_le.setText(data[1])
            self.stok_le.setText(str(data[2]))
            self.co_stok_le.setCurrentText(data[3])
            self.cp_le.setText(str(data[4]))
            self.sp_le.setText(str(data[5]))
            self.vendor_le.setText(data[9])
            self.vendor_ph_le.setText(data[10])
        else:
            QMessageBox.warning(self, "Warning", "لا يوجد منتج بهذا الرقم")

        conn.commit()
        conn.close()
    def save_product(self):
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()

        id = self.id_le.text()
        name = self.name_le.text()
        stok = float(self.stok_le.text())
        co_stoke = self.co_stok_le.currentText()
        cp = float(self.cp_le.text())
        sp = float(self.sp_le.text())
        vendor = self.vendor_le.text()
        vendor_ph = self.vendor_ph_le.text()

        totalcp = cp * stok
        totalsp = sp * stok
        assumed_profid = (totalsp - totalcp)

        if id == '' or name == '' or stok == '' or co_stoke == '' or cp == '' or sp == '' or vendor == '' or vendor_ph =='':
            QMessageBox.warning(self, "Warning","برجاء ادخال البيانات كاملة")

        else:
            result1 = '''INSERT INTO products (product_id, product_name, product_stok, product_co_stoke, product_cp, product_sp,product_totalcp,product_totalsp, product_assumed_profid,product_vendor,product_vendor_ph)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ? ,?,?,?)'''
            c.execute(result1, (id, name, stok, co_stoke, cp, sp,totalcp,totalsp,assumed_profid,vendor,vendor_ph))            
        # conn = sqlite3.connect('Users.db')
        # result = c.execute()
            c.execute("SELECT available_quantity FROM inventory WHERE product_name=?", (name,))
            old_quantity = c.fetchone()
            if old_quantity:
                   new_quantity = int(old_quantity[0]) + int(stok)
                   c.execute("UPDATE inventory SET available_quantity=? WHERE product_name=?", (new_quantity, name))
                   if new_quantity <= 5:
                       QMessageBox.warning(self, 'تحذير', 'الكمية المتوفرة من المنتج تقترب من الحد الأدنى')
            else:
                   c.execute("INSERT INTO inventory (product_name, available_quantity, minimum_quantity) VALUES (?, ?, ?)", (name, stok, 0))




            conn.commit()
            conn.close()
            self.show_data()
            QMessageBox.information(self, 'Success', 'Product has been added successfully!')



  
    
    def delete_data(self):
        global MyData
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            product_id = self.table.item(selected_row, 0).text()
            # conn = sqlite3.connect('Users.db')
            result1 = "DELETE FROM products WHERE product_id = ?"
            c.execute(result1, (product_id,))

            self.table.removeRow(selected_row)
            QMessageBox.information(self, 'Success', 'تم حذف المنتج بنجاح!')
        else:
            QMessageBox.warning(self, 'Error', 'يرجى تحديد المنتج المراد حذفه')
        conn.commit()
        conn.close()
    def search_data(self):
        global MyData
        # conn = sqlite3.connect('Users.db')
        # cur = conn.cursor()
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()
        search_text = self.id_le.text()

        result1 = "SELECT * FROM products WHERE product_id LIKE ?"
        c.execute(result1, ('%'+search_text+'%',))
        MyData = c.fetchall()

        self.table.setRowCount(0)
        for row in MyData:
            self.table.insertRow(self.table.rowCount())
            for column, item in enumerate(row):
                self.table.setItem(
                    self.table.rowCount() - 1, column, QTableWidgetItem(str(item))
                )
        conn.commit()
        conn.close()

    def show_data(self):
        global MyData
        # conn = sqlite3.connect('Users.db')
        # cur = conn.cursor()
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        MyData = c.fetchall()
        total1 = 0
        total2 = 0
        total3 = 0
        
        self.table.setRowCount(0)
        for row in MyData:
            self.table.insertRow(self.table.rowCount())
            for column, item in enumerate(row):
                self.table.setItem(
                    self.table.rowCount() - 1, column, QTableWidgetItem(str(item))
                )
                if column == 6:
                    total1 += float(item)
                if column == 7:
                    total2 += float(item)
                if column == 8:
                    total3 += float(item)
        # set the total sales label
        self.total_cp_label.setText('إجمالى سعر الشراء:' + str(total1))
        self.total_cp_label.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold;border-radius: 4px;")

        self.total_sp_label.setText('إجمالى سعر البيع:' + str(total2))
        self.total_sp_label.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold;border-radius: 4px;")        

        self.total_assumed_profid_label.setText('إجمالـــــى الربحية:' + str(total3))
        self.total_assumed_profid_label.setStyleSheet("background-color: #1D82CA; color: white;font-size: 12px; font-weight: bold;border-radius: 4px;")



        conn.commit()
        conn.close()

    def show_Sell_screen(self):
        self.Sell_screen_window = Sell_screen()
        self.Sell_screen_window.show()
    def show_Supplier(self):
        self.POS_window = Supplier()
        self.POS_window.show()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.show_totalsell()
    def show_totalsell(self):
        self.totalsell_window = SalesReport()
        self.totalsell_window.show()

class Sell_screen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('شاشة البيع')
        self.setGeometry(0, 0, 1200, 1024)
        self.setStyleSheet("color: #34495E")
        self.initUI()

    def initUI(self):
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.sell_screen = QGridLayout(self.centralWidget)
        
        font = QFont("Tajawal", 11,)
        # color_font = "#8E44AD"

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('القائمة الرئيسية')
        editMenu = menubar.addMenu('Edit')

        storeAct = QAction('المخزون', self)
        storeAct.triggered.connect(self.show_POS)
        fileMenu.addAction(storeAct)

        # newuserAct = QAction('مستخدم جديد', self)
        # # storeAct.triggered.connect(self.show_newuser_screen)
        # # newuserAct.setShortcut('Ctrl+S')
        # fileMenu.addAction(newuserAct)

        # # newuserAct = QAction('إدارة الموردين', self)
        # # # storeAct.triggered.connect(self.show_SupplierManagement_screen)
        # # # newuserAct.setShortcut('Ctrl+S')
        # # fileMenu.addAction(newuserAct)

        # exitAct = QAction('Exit', self)
        # exitAct.setShortcut('Ctrl+Q')
        # exitAct.triggered.connect(self.close)
        # fileMenu.addAction(exitAct)

        # copyAct = QAction('Copy', self)
        # editMenu.addAction(copyAct)

        # cutAct = QAction('Cut', self)
        # editMenu.addAction(cutAct)

        # pasteAct = QAction('Paste', self)
        # editMenu.addAction(pasteAct)

        # self.setGeometry(300, 300, 300, 200)
        # self.setWindowTitle('Menu Example')
        # self.show()
        self.datetime_label = QLabel(self)
        self.current_datetime = QDateTime.currentDateTime()
        self.datetime_label.setText(self.current_datetime.toString())
        self.datetime_label.move(50, 20) 
        self.datetime_label.setStyleSheet("font-size: 12px; font-weight: bold;min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
        # self.datetime_label.setStyleSheet("font-size: 12px; font-weight: bold;min-width: 200px; \
        #                           max-width: 300px; min-height:10px; max-height: 20px;") 
        # إنشاء مؤشر زمني
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000) # تحديث الوقت كل ثانية

    # دالة تحديث الوقت

        self.welcome_app_label = QLabel('Welcome To Easy P.O.S',self)
        self.welcome_app_label.move(500, 20)
        self.welcome_app_label.setStyleSheet("font-size: 12px; font-weight: bold;min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 

        self.serch_items_lineEdit = QLineEdit(self)
        self.serch_items_lineEdit.move(850, 180)
        self.serch_items_lineEdit.returnPressed.connect(self.show_sell_items_data)
        self.serch_items_lineEdit.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
        
        self.search_button = QPushButton("بحث", self)
        self.search_button.move(740, 175)
        self.search_button.setFont(font)
        self.search_button.clicked.connect(self.show_sell_items_data)
        self.search_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")

        self.delete_button = QPushButton("مسح", self)
        self.delete_button.move(635, 175)
        self.delete_button.setFont(font)
        self.delete_button.clicked.connect(self.delete_data_sell)
        self.delete_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")

        self.phone_cust_bill = QLabel('رقـم التليفون',self)
        self.phone_cust_bill.move(50, 80)
        self.phone_cust_bill.setFont(font)
        self.phone_cust_bill.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.phone_cust_bill_lineEdit = QLineEdit(self)
        self.phone_cust_bill_lineEdit.move(155, 85)
        self.phone_cust_bill_lineEdit.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 

        self.name_cust_bill = QLabel('أسم العميل',self)
        self.name_cust_bill.move(50, 110)
        self.name_cust_bill.setFont(font)
        self.name_cust_bill.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.name_cust_bill_lineEdit = QLineEdit(self)
        self.name_cust_bill_lineEdit.move(155, 115)
        self.name_cust_bill_lineEdit.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 

        self.address_cust_bill = QLabel('العنوان',self)
        self.address_cust_bill.move(50, 140)
        self.address_cust_bill.setFont(font)
        self.address_cust_bill.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.address_cust_bill_lineEdit = QLineEdit(self)
        self.address_cust_bill_lineEdit.move(155, 145)
        self.address_cust_bill_lineEdit.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 400px; \
                                  max-width: 500px; min-height:10px; max-height: 20px;") 

        self.serch_cust_button = QPushButton("بحث", self)
        self.serch_cust_button.move(380, 80)
        self.serch_cust_button.setFont(font)
        self.serch_cust_button.clicked.connect(self.Search_customer)
        self.serch_cust_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")

        self.save_cust_button = QPushButton("حفظ", self)
        self.save_cust_button.move(380, 115)
        self.save_cust_button.setFont(font)
        self.save_cust_button.clicked.connect(self.save_customer)
        self.save_cust_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")

        self.name_product_label = QLabel('',self)
        self.name_product_label.move(100, 200)
        self.name_product_label.setFont(font)
        self.name_product_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.price_product_label = QLabel('',self)
        self.price_product_label.move(100, 230)
        self.price_product_label.setFont(font)
        self.price_product_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.quantity_l = QLabel("الكميـــــة",self)
        self.quantity_l.move(200, 300)
        self.quantity_l.setFont(font)
        self.quantity_l.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.discount_l = QLabel("الخصــــم", self)
        self.discount_l.move(200, 330)
        self.discount_l.setFont(font)
        self.discount_l.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.quantity_entry = QLineEdit('1',self)
        self.quantity_entry.move(100, 300)
        
        self.discount_entry = QLineEdit('0',self)
        self.discount_entry.move(100, 330)

        self.add_button = QPushButton("إضافة", self)
        self.add_button.move(100, 380)
        self.add_button.setFont(font)
        self.add_button.clicked.connect(self.add_to_cart)
        self.add_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")

        self.cart_table = QTableWidget(self)
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(['المنتج', 'السعر', 'الكمية', 'الخصم', 'الإجمالي'])
        self.cart_table.setGeometry(450,210,600,400)
        self.cart_table.setFont(font)
        self.cart_table.setStyleSheet("background-color: white; alternate-background-color: #1D82CA; color: black; border: 1px solid #ccc; font-size: 12px;"
                         "QTableView::item:selected{background-color: #907AB3; }")

        self.total_l = QLabel("الإجمالي:", self)
        self.total_l.move(950, 630)
        self.total_l.setFont(font)
        self.total_l.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.total_entry = QLineEdit(self)
        self.total_entry.move(900, 635)
        self.total_entry.setReadOnly(True)
        self.total_entry.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 50px; \
                                  max-width: 100px; min-height:10px; max-height: 20px;") 

        self.checkout_button = QPushButton("إنهاء العملية", self)
        self.checkout_button.move(100, 415)
        self.checkout_button.setFont(font)
        self.checkout_button.clicked.connect(self.save_invoice)
        self.checkout_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        self.show()

    
    def show_POS(self):
        self.POS_window = Login()
        self.POS_window.show()
 
    def Search_customer(self):
        # conn = sqlite3.connect('Users.db')
        # cur = conn.cursor()
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()
        search_customer = self.phone_cust_bill_lineEdit.text()

        result4 = "SELECT phone_customer, name_customer, address_customer FROM add_customer WHERE phone_customer =?"
        c.execute(result4, (search_customer,))
        result4 = c.fetchall()

        # result = c.execute("SELECT phone_customer, name_customer, address_customer FROM add_customer").fetchone()

        for r in  result4:
            # Set QLineEdit values to retrieved data
            self.phone_cust_bill_lineEdit.setText(str(r[0]))
            self.name_cust_bill_lineEdit.setText(str(r[1]))
            self.address_cust_bill_lineEdit.setText(str(r[2]))

        # conn.close()
        conn.commit()
        conn.close()

    def save_customer(self):
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()
        phone_customer = self.phone_cust_bill_lineEdit.text()
        name_customer = self.name_cust_bill_lineEdit.text()
        address_customer = self.address_cust_bill_lineEdit.text()


        if phone_customer == '' or name_customer == '' or address_customer == '':
            QMessageBox.warning(self, "Warning","برجاء ادخال البيانات كاملة")

        else:
            result4 = '''INSERT INTO add_customer (phone_customer, name_customer, address_customer)
                    VALUES (?, ?, ?)'''
            c.execute(result4, (phone_customer, name_customer, address_customer))            
        # conn = sqlite3.connect('Users.db')
        # result = c.execute()

            conn.commit()
            conn.close()
            # self.show_data()
            QMessageBox.information(self, 'Success', 'Product has been added successfully!')

    def show_sell_items_data(self):
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()
        product_id = self.serch_items_lineEdit.text()
        c.execute("SELECT * FROM products WHERE product_id=?", (product_id,))
        data = c.fetchone()
        if data:
            self.name_product_label.setText(f"{data[1]}")
            self.price_product_label.setText(f"{data[5]}")
        else:
            self.name_product_label.setText("المنتج غير موجود")
            self.price_product_label.setText("")

        conn.commit()
        conn.close()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.add_to_cart()
    def add_to_cart(self):
        product_name = self.name_product_label.text()
        quantity = self.quantity_entry.text()
        discount = self.discount_entry.text()
        price = float(self.price_product_label.text().split(":")[-1])
        total_price = (price * int(quantity)) - float(discount)
        
        self.cart_table.insertRow(self.cart_table.rowCount())
        row_position = self.cart_table.rowCount()
        self.cart_table.setItem(row_position - 1, 0, QTableWidgetItem(product_name))
        self.cart_table.setItem(row_position - 1, 1, QTableWidgetItem(str(price)))
        self.cart_table.setItem(row_position - 1, 2, QTableWidgetItem(quantity))
        self.cart_table.setItem(row_position - 1, 3, QTableWidgetItem(discount))
        self.cart_table.setItem(row_position - 1, 4, QTableWidgetItem(str(total_price)))
        self.calculate_total_price()
        # self.serch_items_lineEdit.clear()
        self.serch_items_lineEdit.focusNextChild()
        
    def calculate_total_price(self):
        total_price = 0
        for row in range(self.cart_table.rowCount()):
            total_price += float(self.cart_table.item(row, 4).text())

        self.total_entry.setText(str(total_price))

    def save_invoice(self):
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()
    
        # insert the invoice data into the database
        invoice_number = random.randint(1000, 10000)
        total_price = float(self.total_entry.text())
        Phone = self.phone_cust_bill_lineEdit.text()  
        Name = self.name_cust_bill_lineEdit.text()  
        Address = self.address_cust_bill_lineEdit.text() 
        c.execute("INSERT INTO invoices (invoice_number, total_price, Name, Phone, Address,sale_date) VALUES (?, ?, ?, ?, ?, ?)", (invoice_number, total_price,Phone,Name,Address,day_date))
        invoice_id = c.lastrowid
    
        # insert the cart items into the database
        for row in range(self.cart_table.rowCount()):
            product_name = self.cart_table.item(row, 0).text()
            price = float(self.cart_table.item(row, 1).text())
            quantity = int(self.cart_table.item(row, 2).text())
            discount = float(self.cart_table.item(row, 3).text())
            total_price = float(self.cart_table.item(row, 4).text())
    
            # check if the required quantity is available in the stock
            c.execute("SELECT product_stok FROM products WHERE product_name = ?", (product_name,))
            current_stock = c.fetchone()[0]
            if current_stock < str(quantity):
                QMessageBox.warning(self, "Error", f"كمية {product_name} المتاحة في المخزن غير كافية لإكمال هذه العملية!")
                conn.rollback()
                return
    
            # deduct the sold quantity from the stock
            new_stock = float(current_stock) - float(quantity)
            c.execute("UPDATE products SET product_stok = ? WHERE product_name = ?", (new_stock, product_name))
    
            c.execute("INSERT OR REPLACE INTO cart_items (invoice_id, product_name, price, quantity, discount, total_price,sale_date) VALUES (?, ?, ?, ?, ?, ?, ?)", (invoice_id, product_name, price, quantity, discount, total_price,day_date))
            # QMessageBox.Ok(self, "تم إنشاء الفاتورة بنجاح.")
    
        conn.commit()
        conn.close()
        self.name_product_label.clear()
        self.price_product_label.clear()
        self.serch_items_lineEdit.clear()
        self.total_entry.clear()            
        self.phone_cust_bill_lineEdit.clear()  
        self.name_cust_bill_lineEdit.clear()  
        self.address_cust_bill_lineEdit.clear()  
        # write the cart items
        self.serch_items_lineEdit.focusNextChild()

        # generate the PDF invoice
        self.generate_invoice_pdf(invoice_number)
    
        # print a message to confirm that the invoice has been created
    
        # open the generated PDF file
        webbrowser.open_new(f"invoice_{invoice_number}.pdf")
    # def generate_invoice_pdf(self, invoice_number):
        
    def generate_invoice_pdf(self, invoice_number):
            # get the invoice data from the database
            conn = sqlite3.connect('StorDB.db')
            c = conn.cursor()
            c.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
            invoice_data = c.fetchone()
            c.execute("SELECT * FROM cart_items WHERE invoice_id = ?", (invoice_data[0],))
            cart_data = c.fetchall()
            conn.commit()
            conn.close()

            # create the PDF invoice
            pdf = ArabicPDF()
            pdf.add_page()
            pdf.set_arabic_font()

            # write the invoice header
            pdf.cell(200, 10, txt="Invoice", ln=1, align="C")
            pdf.cell(200, 10, txt=f"No.Invoice: {invoice_data[0]}", ln=1, align="C")
            pdf.cell(200, 10, txt=f"Date: {invoice_data[5]}", ln=1, align="C")
            pdf.cell(200, 10, txt=f"Total: {invoice_data[1]} E.L", ln=1, align="C")
            pdf.cell(200, 10, txt=f"Phone Customer: {invoice_data[2]}", ln=1, align="C")
            pdf.cell(200, 10, txt=f"Name Customer: {invoice_data[3]}", ln=1, align="C")
            pdf.cell(200, 10, txt=f"Address Customer: {invoice_data[4]} ", ln=1, align="C")

            pdf.cell(200, 10, txt="", ln=1, align="C")
            pdf.cell(200, 10, txt="", ln=1, align="C")

            pdf.cell(50, 10, txt="Product", border=1, align="C")
            pdf.cell(30, 10, txt="Price", border=1, align="C")
            pdf.cell(30, 10, txt="Quantity", border=1, align="C")
            pdf.cell(30, 10, txt="Discount", border=1, align="C")
            pdf.cell(30, 10, txt="Total", border=1, align="C")
            pdf.ln()

            # loop through all rows in the cart table and add them to the PDF
            for row in range(self.cart_table.rowCount()):
                product_name = self.cart_table.item(row, 0).text()
                price = float(self.cart_table.item(row, 1).text())
                quantity = int(self.cart_table.item(row, 2).text())
                discount = float(self.cart_table.item(row, 3).text())
                total_price = float(self.cart_table.item(row, 4).text())

                pdf.cell(50, 10, txt=product_name, border=1, align="C")
                pdf.cell(30, 10, txt=str(price), border=1, align="C")
                pdf.cell(30, 10, txt=str(quantity), border=1, align="C")
                pdf.cell(30, 10, txt=str(discount), border=1, align="C")
                pdf.cell(30, 10, txt=str(total_price), border=1, align="C")
                pdf.ln()

            # create the directory for the invoice if it doesn't exist
            directory = "D:/invoicePOS/" + str(day_date) + "/"
            if not os.path.exists(directory):
                os.makedirs(directory)

            # save the invoice as a PDF file
            with open(f"{directory}invoice_{invoice_number}.pdf",'wb') as f:
                f.write(pdf.output(f"invoice_{invoice_number}.pdf").encode("utf-8"))
                os.startfile("print")
                f.close()
            self.cart_table.clearContents()
            self.cart_table.setRowCount(0)
   


    def delete_data_sell(self):
        selected_row = self.cart_table.currentRow()
        if selected_row >= 0:
            self.cart_table.removeRow(selected_row)
            self.calculate_total_price()
    def update_time(self):
        self.current_datetime = QDateTime.currentDateTime()
        self.datetime_label.setText(self.current_datetime.toString("التاريخ yyyy-MM-dd الوقت hh:mm ap "))

class ArabicPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_font('Amiri', '', 'Amiri-Regular.ttf', uni=True, )
    
    def set_arabic_font(self):
        self.set_font('Amiri', '', 11,)
        
class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 300, 150)

        self.username_label = QLabel('Username:')
        self.username_edit = QLineEdit()
        self.password_label = QLabel('Password:')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton('Login')
        self.login_btn.clicked.connect(self.check_login)
        self.signup_btn = QPushButton('Sign up')
        self.signup_btn.clicked.connect(self.show_signup)

        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.username_label)
        hbox1.addWidget(self.username_edit)
        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.password_label)
        hbox2.addWidget(self.password_edit)
        vbox.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.login_btn)
        hbox3.addWidget(self.signup_btn)
        vbox.addLayout(hbox3)

        self.setLayout(vbox)

        # self.conn = sqlite3.connect('users.db')
        # self.cur = self.conn.cursor()
        # self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
        #                     id INTEGER PRIMARY KEY AUTOINCREMENT,
        #                     username TEXT NOT NULL,
        #                     password TEXT NOT NULL
        #                 )""")
        # self.conn.commit()


    def check_login(self):
        global MyData
        username = self.username_edit.text()
        password = self.password_edit.text()

        result = "SELECT * FROM users WHERE username = ? AND password = ?"
        c.execute(result, (username, password))
        MyData = c.fetchone()

        if MyData:
            user_type = MyData[3] # تحديد نوع المستخدم من سجل قاعدة البيانات
            if user_type == 'User':
                self.hide()
                self.main_window = Sell_screen()
                self.main_window.show()
            else:
                self.hide()
                self.sell_window =POS()
                self.sell_window.show()
        else:
            QMessageBox.warning(self, "Login failed", "Invalid username or password.")

    # def check_login(self):
    #     global MyData
    #     username = self.username_edit.text()
    #     password = self.password_edit.text()

    #     result = "SELECT * FROM users WHERE username = ? AND password = ?"
    #     c.execute(result, (username, password))
    #     MyData = c.fetchone()




    #     if MyData:
    #         self.hide()
    #         self.main_window = Sell_screen()
    #         self.main_window.show()
    #     else:
    #         QMessageBox.warning(self, "Login failed", "Invalid username or password.")
        







        
    def show_signup(self):
        self.signup_window = Signup()
        self.signup_window.show()

class Signup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('تسجيل جديد')
        self.setGeometry(100, 100, 300, 150)
        
        self.username_label = QLabel('Username:')
        self.username_edit = QLineEdit()
        self.password_label = QLabel('Password:')
        self.password_edit = QLineEdit()
        self.password_ok_label = QLabel('Password:')
        self.password_ok_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_ok_edit.setEchoMode(QLineEdit.Password)

        self.role_label = QLabel('Role:')
        self.role_combobox = QComboBox()
        self.role_combobox.addItems(['User', 'Admin'])

        self.can_add_products_checkbox = QCheckBox('Can add products')
        self.can_edit_products_checkbox = QCheckBox('Can edit products')
        self.can_delete_products_checkbox = QCheckBox('Can delete products')

        self.signup_btn = QPushButton('Sign up')
        self.signup_btn.clicked.connect(self.signup)

        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.username_label)
        hbox1.addWidget(self.username_edit)
        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.password_label)
        hbox2.addWidget(self.password_edit)
        hbox2.addWidget(self.password_ok_edit)
        vbox.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.role_label)
        hbox3.addWidget(self.role_combobox)
        vbox.addLayout(hbox3)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.can_add_products_checkbox)
        hbox4.addWidget(self.can_edit_products_checkbox)
        hbox4.addWidget(self.can_delete_products_checkbox)
        vbox.addLayout(hbox4)

        vbox.addWidget(self.signup_btn)

        self.setLayout(vbox)

    def check_trial_period_on_start(self):
        username = self.username_edit.text()
        result = "SELECT trial_end_date FROM users WHERE username = ?"
        c.execute(result, (username,))
        trial_end_date = c.fetchone()[0]
    
        if trial_end_date < datetime.datetime.now():
            QMessageBox.warning(self, "Trial period ended", "Your trial period has ended. Please subscribe to continue using the application.")
            QApplication.quit()
        else:
            QMessageBox.information(self, "Welcome", "Welcome, "+ username + "! Your trial ends on " + trial_end_date.strftime('%Y-%m-%d') + ".")
            
    def signup(self):
        global MyData
        username = self.username_edit.text()
        password = self.password_edit.text()
        password_Ok = self.password_ok_edit.text()
        role= self.role_combobox.currentText()
        can_add_products = 1 if self.can_add_products_checkbox.isChecked() else 0
        can_edit_products = 1 if self.can_edit_products_checkbox.isChecked() else 0
        can_delete_products = 1 if self.can_delete_products_checkbox.isChecked() else 0
    
        if password != password_Ok:
            QMessageBox.warning(self, "Sign up failed", "Warning.")
            return
    
        if not username or not password_Ok:
            QMessageBox.warning(self, "Sign up failed", "Username and password cannot be empty.")
            return
    
        result = "SELECT *from users WHERE username = ?"
        c.execute(result, (username,))
        MyData = c.fetchone()
    
        if MyData:
            QMessageBox.warning(self, "Sign up failed", "Username already exists.")
        else:
            # Calculate trial end date (30 days from today)
            trial_end_date = datetime.datetime.now() + datetime.timedelta(days=5)
    
            # Insert new user into database with trial end date and specified permissions
            result = "INSERT INTO users (username, password, role, can_add_products, can_edit_products, can_delete_products, trial_end_date) VALUES (?, ?, ?, ?, ?, ?, ?)"
            c.execute(result, (username, password, role, can_add_products, can_edit_products, can_delete_products, trial_end_date))
            conn.commit()
            conn.close()
    
            # Show success message
            QMessageBox.information(self, "Sign up successful", "Welcome, " + username + "! Your trial ends on " + trial_end_date.strftime('%Y-%m-%d') + ".")
    
            # Check trial period
            self.check_trial_period_on_start()
    
        conn.commit()
        conn.close()
    
    #     self.username_label = QLabel('Username:')
    #     self.username_edit = QLineEdit()
    #     self.password_label = QLabel('Password:')
    #     self.password_edit = QLineEdit()
    #     self.password_ok_label = QLabel('Password:')
    #     self.password_ok_edit = QLineEdit()
    #     self.password_edit.setEchoMode(QLineEdit.Password)
    #     self.password_ok_edit.setEchoMode(QLineEdit.Password)

    #     self.role_label = QLabel('Role:')
    #     self.role_combobox = QComboBox()
    #     self.role_combobox.addItems(['User', 'Admin'])

    #     self.signup_btn = QPushButton('Sign up')
    #     self.signup_btn.clicked.connect(self.signup)

    #     vbox = QVBoxLayout()
    #     hbox1 = QHBoxLayout()
    #     hbox1.addWidget(self.username_label)
    #     hbox1.addWidget(self.username_edit)
    #     vbox.addLayout(hbox1)

    #     hbox2 = QHBoxLayout()
    #     hbox2.addWidget(self.password_label)
    #     hbox2.addWidget(self.password_edit)
    #     hbox2.addWidget(self.password_ok_edit)
    #     vbox.addLayout(hbox2)

    #     hbox3 = QHBoxLayout()
    #     hbox3.addWidget(self.role_label)
    #     hbox3.addWidget(self.role_combobox)
    #     vbox.addLayout(hbox3)

    #     vbox.addWidget(self.signup_btn)

    #     self.setLayout(vbox)

    # def signup(self):
    #     global MyData
    #     username = self.username_edit.text()
    #     password = self.password_edit.text()
    #     password_Ok = self.password_ok_edit.text()
    #     role = self.role_combobox.currentText()

    #     if password != password_Ok:
    #         QMessageBox.warning(self, "Sign up failed", "Warning.")
    #         return

    #     if not username or not password_Ok:
    #         QMessageBox.warning(self, "Sign up failed", "Username and password cannot be empty.")
    #         return

    #     result = "SELECT *from users WHERE username = ?"
    #     c.execute(result, (username,))
    #     MyData = c.fetchone()

    #     if MyData:
    #         QMessageBox.warning(self, "Sign up failed", "Username already exists.")
    #     else:
    #         # Calculate trial end date (30 days from today)
    #         trial_end_date = datetime.datetime.now() + datetime.timedelta(days=30)

    #         # Insert new user into database with trial end date
    #         result = "INSERT INTO users (username, password, role, trial_end_date) VALUES (?, ?, ?, ?)"
    #         c.execute(result, (username, password, role, trial_end_date))
    #         conn.commit()
    #         conn.close()

    #         # Show success message
    #         QMessageBox.information(self, "Sign up successful", "Welcome, " + username + "! Your trial ends on " + trial_end_date.strftime('%Y-%m-%d') + ".")
  
  
    # def signup(self):
    #     global MyData
    #     username = self.username_edit.text()
    #     password = self.password_edit.text()
    #     password_Ok = self.password_ok_edit.text()
    #     role = self.role_combobox.currentText()

    #     if password != password_Ok:
    #         QMessageBox.warning(self, "Sign up failed", "Warning.")
    #         return

    #     if not username or not password_Ok:
    #         QMessageBox.warning(self, "Sign up failed", "Username and password cannot be empty.")
    #         return
        
    #     result = "SELECT * FROM users WHERE username = ?"
    #     c.execute(result, (username,))
    #     MyData = c.fetchone()

    #     if MyData:
    #         QMessageBox.warning(self, "Sign up failed", "Username already exists.")
    #     else:
    #         result = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
    #         c.execute(result, (username, password, role))
    #         conn.commit()
    #         conn.close()
    #         QMessageBox.information(self, "Sign up successful", "Welcome, " + username + "!")

class Supplier(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ادارة الموردين')
        self.setGeometry(0, 0, 1200, 1024)

        self.name_Supplier_label = QLabel('أسم المورد', self)
        self.name_Supplier_label.move(15, 50)
        self.name_Supplier_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.name_Supplier_input = QLineEdit(self)
        self.name_Supplier_input.move(120, 55)
        self.name_Supplier_input.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
        
        self.address_Supplier_label = QLabel('العنوان', self)
        self.address_Supplier_label.move(15, 80)
        self.address_Supplier_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.address_Supplier_input = QLineEdit(self)
        self.address_Supplier_input.move(120, 85)
        self.address_Supplier_input.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
        
        self.phonr_Supplier = QLabel('التليفون', self)
        self.phonr_Supplier.move(15, 110)
        self.phonr_Supplier.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.phone_Supplier_input = QLineEdit(self)
        self.phone_Supplier_input.move(120, 115 )
        self.phone_Supplier_input.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
        
        self.bill_supplier_label = QLabel(' رقــم الفاتورة', self)
        self.bill_supplier_label.move(15, 140)
        self.bill_supplier_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.bill_Supplier_input = QLineEdit(self)
        self.bill_Supplier_input.move(120, 145)
        self.bill_Supplier_input.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 

        self.sall_bill_supplier_label = QLabel(' قيمة الفاتورة', self)
        self.sall_bill_supplier_label.move(335, 50)
        self.sall_bill_supplier_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.sall_bill_Supplier_input = QLineEdit(self)
        self.sall_bill_Supplier_input.move(440, 55)
        self.sall_bill_Supplier_input.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 
   
        self.Been_paid_supplier_label = QLabel(' تـم دفـع', self)
        self.Been_paid_supplier_label.move(335, 80)
        self.Been_paid_supplier_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.Been_paid_Supplier_input = QLineEdit(self)
        self.Been_paid_Supplier_input.move(440, 85)
        self.Been_paid_Supplier_input.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc; font-size: 14px; min-width: 200px; \
                                  max-width: 300px; min-height:10px; max-height: 20px;") 

        self.combo_supplier_bill_label = QLabel('نـــوع الفاتورة', self)
        self.combo_supplier_bill_label.move(335, 110)
        self.combo_supplier_bill_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.combo_supplier_bill_input = QComboBox(self)
        self.combo_supplier_bill_input.addItems(['شراء', 'بيع'])
        self.combo_supplier_bill_input.move(440, 115)

        self.combo_supp_label = QLabel('السداد', self)
        self.combo_supp_label.move(335, 140)
        self.combo_supp_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.combo_supp_input = QComboBox(self)
        self.combo_supp_input.addItems(['نقدآ', 'أجل'])
        self.combo_supp_input.move(440, 145)

        self.add_Supplier_button = QPushButton('حفظ', self)
        self.add_Supplier_button.move(60, 180)
        self.add_Supplier_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        self.add_Supplier_button.clicked.connect(self.add_supplier)

        self.show_Supplier_button = QPushButton('عرض', self)
        self.show_Supplier_button.move(60, 230)
        self.show_Supplier_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; min-width: 550px; \
                                  max-width: 650px; min-height:10px; max-height: 20px; padding: 8px 16px; border-radius: 4px;")
        self.show_Supplier_button.clicked.connect(self.show_supplier_data)
        
        self.search_Supplier_button = QPushButton('بحث', self)
        self.search_Supplier_button.move(370, 180) 
        self.search_Supplier_button.clicked.connect(self.search_supplier)
        self.search_Supplier_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")

        self.edit_Supplier_button = QPushButton('تعديل', self)
        self.edit_Supplier_button.move(220, 180) 
        self.edit_Supplier_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        self.edit_Supplier_button.clicked.connect(self.modify_supplier)

        self.delete_Supplier_button = QPushButton('مسح', self)
        self.delete_Supplier_button.move(520, 180) 
        self.delete_Supplier_button.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        self.delete_Supplier_button.clicked.connect(self.delete_supplier)

        self.exit_Supplier_button = QPushButton('خروج', self)
        self.exit_Supplier_button.move(60, 650) 
        self.exit_Supplier_button.setStyleSheet("background-color: #CA1D2B; color: white; font-size: 12px; font-weight: bold; min-width: 550px; \
                                  max-width: 650px; min-height:10px; max-height: 20px; padding: 8px 16px; border-radius: 4px;")
        self.exit_Supplier_button.clicked.connect(self.exit_app)

        self.supplier_table = QTableWidget(self)
        self.supplier_table.setColumnCount(9)
        self.supplier_table.setHorizontalHeaderLabels(['ID ', 'أسم المورد', 'العنوان', 'التليفون', ' رقــم الفاتورة', ' قيمة الفاتورة','المتبقى','نوع الفاتورة','تم دفع'])
        self.supplier_table.setGeometry(5,285,800,350)
        self.supplier_table.setStyleSheet("background-color: white; alternate-background-color: #1D82CA; color: black; border: 1px solid #ccc; font-size: 12px;"
                         "QTableView::item:selected{background-color: #907AB3; }")

        self.total_remaining_amount_label = QLabel(self)
        self.total_remaining_amount_label.setAlignment(Qt.AlignRight)
        self.total_remaining_amount_label.setGeometry(900, 740, 190, 20)



    def add_supplier(self):
        global MyData
        # """Add a new supplier to the database"""
        name = self.name_Supplier_input.text()
        address = self.address_Supplier_input.text()
        phone = self.phone_Supplier_input.text()
        bill_num = self.bill_Supplier_input.text()
        bill_value = self.sall_bill_Supplier_input.text()
        remaining_amount = str(float(bill_value) - float(self.Been_paid_Supplier_input.text()))

        term_value = self.combo_supp_input.currentText()
        method_of_payment = self.combo_supplier_bill_input.currentText()
        been_paid = self.Been_paid_Supplier_input.text()
        
        c.execute("INSERT INTO suppliers (name, address, Phone_suppliers, numper_bill_Suppliers, how_much_bill, term_value, method_of_payment, Been_paid)VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, address, phone, bill_num, bill_value, remaining_amount, method_of_payment, been_paid))
        # Clear the input fields and refresh the table
        conn.commit()
        conn.close
        self.clear_inputs()
        self.show_supplier_data()

    def show_supplier_data(self):
        global MyData
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()
        # """Retrieve and display all supplier data in the table"""

        c.execute("SELECT * FROM suppliers")
        MyData = c.fetchall()
        totalremaining_amount = 0

        self.supplier_table.setRowCount(0)
        for row in MyData:
            self.supplier_table.insertRow(self.supplier_table.rowCount())
            for column, item in enumerate(row):
                self.supplier_table.setItem(
                    self.supplier_table.rowCount() - 1, column, QTableWidgetItem(str(item))
                )
                if column == 6:
                        totalremaining_amount += float(item)

        # set the total sales label
        self.total_remaining_amount_label.setText('إجمالى المديونية:' + str(totalremaining_amount))
        self.total_remaining_amount_label.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold;border-radius: 4px;")
        conn.commit()
        conn.close
    
    def search_supplier(self):
        # """Retrieve and display supplier data that matches the user's search query"""
        name = self.name_Supplier_input.text()
        cursor = c.execute("SELECT * FROM suppliers WHERE name=?", (name,))
        data = cursor.fetchone()

        if data:
            self.supplier_table.setRowCount(0)
            self.supplier_table.insertRow(0)
            for column_number, column_data in enumerate(data):
                self.supplier_table.setItem(0, column_number, QTableWidgetItem(str(column_data)))
        else:
            QMessageBox.warning(self, "Error", "Supplier not found.")
        conn.commit()
        conn.close
    def delete_supplier(self):
        # """Delete the selected supplier's data from the database"""
        selected_row = self.supplier_table.currentRow()
        if selected_row >= 0:
            supplier_id = self.supplier_table.item(selected_row, 0).text()

            c.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
            # Clear the input fields and refresh the table
            self.clear_inputs()
            self.show_supplier_data()
        else:
            QMessageBox.warning(self, "Error", "Please select a supplier to delete.")
        conn.commit()
        conn.close
    def clear_inputs(self):
        # """Clear all input fields"""
        self.name_Supplier_input.clear()
        self.address_Supplier_input.clear()
        self.phone_Supplier_input.clear()
        self.bill_Supplier_input.clear()
        self.sall_bill_Supplier_input.clear()
        self.Been_paid_Supplier_input.clear()

    def modify_supplier(self):
        global MyData
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()
        # """Modify the selected supplier's data in the database"""
        selected_row = self.supplier_table.currentRow()
        if selected_row >= 0:
            supplier_id = self.supplier_table.item(selected_row, 0).text()
            name = self.name_Supplier_input.text()
            address = self.address_Supplier_input.text()
            phone = self.phone_Supplier_input.text()
            bill_num = self.bill_Supplier_input.text()
            bill_value = self.sall_bill_Supplier_input.text()
            been_paid = self.Been_paid_Supplier_input.text()
            if been_paid != '' and bill_value != '':
                remaining_amount = str(float(bill_value) - float(been_paid))
            else:
                remaining_amount = ''
    
            term_value = self.combo_supp_input.currentText()
            method_of_payment = self.combo_supplier_bill_input.currentText()
            c.execute("UPDATE suppliers SET name=?, address=?, Phone_suppliers=?, numper_bill_Suppliers=?, how_much_bill=?, term_value=?, method_of_payment=?, Been_paid=? WHERE id=?", (name, address, phone, bill_num, bill_value, remaining_amount, method_of_payment, been_paid, supplier_id))
            # Clear the input fields and refresh the table
            conn.commit()
            conn.close()
            self.clear_inputs()
            self.show_supplier_data()
        else:
           QMessageBox.warning(self,"Error", "Please select a supplier to modify.")
    # The `modify_supplier` method retrieves the ID of the selected supplier from the table, and then retrieves the modified data entered by the user from the input fields. It then updates the corresponding row in the `suppliers` table using a SQL `UPDATE` statement with a `WHERE` clause that specifies the ID of the supplier to modify. Finally, it clears the input fields and refreshes the table by calling the `clear_inputs` and `show_supplier_data` methods.

    # Note that as with the other methods, this code assumes that the database connection has already been established prior to the method being called.



        # self.combo_supp_input.setStyleSheet("font-size: 14px; min-width: 200px; \
                                #   max-width: 300px; min-height:10px; max-height: 20px;")
                
        # self.search_Supplier_label = QLabel('Search:', self)
        # self.search_Supplier_label.move(50, 360,)
        # self.search_Supplier_label.setStyleSheet("font-size: 12px; font-weight: bold;")

        # self.search_Supplier_input = QLineEdit(self)
        # self.search_Supplier_input.move(100, 360,)
        # self.search_Supplier_input.textChanged.connect(self.search_supplier)



    

    # def create_connection(self):
    #     self.conn = sqlite3.connect('suppliers.db')
    #     self.cur = self.conn.cursor()
    #     self.cur.execute('CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY, name TEXT, address TEXT, account TEXT)')
    # def add_supplier(self):
    #     # """Add a new supplier to the database"""
    #     name = self.name_Supplier_input.text()
    #     address = self.address_Supplier_input.text()
    #     phone = self.phone_Supplier_input.text()
    #     bill_num = self.bill_Supplier_input.text()
    #     bill_value = self.sall_bill_Supplier_input.text()
    #     remaining_amount = str(float(bill_value) - float(self.Been_paid_Supplier_input.textContinued:

    #     term_value = self.combo_supp_input.currentText()
    #     method_of_payment = self.combo_supplier_bill_input.currentText()
    #     been_paid = self.Been_paid_Supplier_input.text()
    #     with conn:
    #         conn.execute("""INSERT INTO suppliers (name, address, Phone_suppliers, numper_bill_Suppliers, how_much_bill, term_value, method_of_payment, Been_paid)
    #                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (name, address, phone, bill_num, bill_value, term_value, method_of_payment, been_paid))
    #     # Clear the input fields and refresh the table
    #     self.clear_inputs()
    #     self.show_supplier_data()
    # # def add_supplier(self):
        
    # #     name = self.name_Supplier_input.text()
    # #     address = self.address_Supplier_input.text()
    # #     phone = self.phone_Supplier_input.text()
    # #     bill_supplier = self.bill_Supplier_input.text()
    # #     sall_bill_supplier = self.sall_bill_Supplier_input.text()
    # #     Been_paid_supplier = self.Been_paid_Supplier_input.text()
    # #     combo_supplier_bill = self.combo_supplier_bill_input.currentText()
    # #     combo_supp = self.combo_supp_input.currentText()
    # #     term_value = (float(sall_bill_supplier)-(float(Been_paid_supplier)))

    # #     if name == '' or address == '' or phone == '' or bill_supplier == '' or sall_bill_supplier == '' or Been_paid_supplier == '':
    # #         QMessageBox.warning(self, 'Error', 'يرجى ادخال البيانات')
    # #         qury = c.execute('INSERT INTO suppliers (name, address, Phone_suppliers, numper_bill_Suppliers, how_much_bill, term_value, method_of_payment,Been_paid) VALUES (?, ?, ? ,? ,? ,? ,? ,? ,?)', (name, address, phone,bill_supplier,sall_bill_supplier,term_value,Been_paid_supplier,combo_supplier_bill,combo_supp))
    # #         conn.commit()
    # #         # self.show_supplier_data()
    # #         row_count = self.supplier_table.rowCount()
    # #         self.supplier_table.setRowCount(row_count + 1)

    # #         supplier_id = str(qury.lastrowid)
    # #         self.supplier_table.setItem(row_count, 0, QTableWidgetItem(supplier_id))
    # #         self.supplier_table.setItem(row_count, 1, QTableWidgetItem(name))
    # #         self.supplier_table.setItem(row_count, 2, QTableWidgetItem(address))
    # #         self.supplier_table.setItem(row_count, 3, QTableWidgetItem(phone))
    # #         self.supplier_table.setItem(row_count, 4, QTableWidgetItem(bill_supplier))
    # #         self.supplier_table.setItem(row_count, 5, QTableWidgetItem(sall_bill_supplier))
    # #         self.supplier_table.setItem(row_count, 6, QTableWidgetItem(Been_paid_supplier))
    # #         self.supplier_table.setItem(row_count, 7, QTableWidgetItem(combo_supplier_bill))
    # #         self.supplier_table.setItem(row_count, 8, QTableWidgetItem(combo_supp))

    # #         self.name_Supplier_input.setText('')
    # #         self.address_Supplier_input.setText('')
    # #         self.phone_Supplier_input.setText('')
    # #         self.bill_Supplier_input.setText('')
    # #         self.sall_bill_Supplier_input.setText('')
    # #         self.Been_paid_Supplier_input.setText('')
    # #         self.combo_supplier_bill_input.setText('')
    # #         self.combo_supp_input.setText('')

    # def edit_supplier(self):
    #     selected_row = self.supplier_table.currentRow()
    #     if selected_row >= 0:
    #         id_item = self.supplier_table.item(selected_row, 0)
    #         supplier_id = int(id_item.text())
    #         name_item = self.supplier_table.item(selected_row, 1)
    #         name = name_item.text()
    #         address_item = self.supplier_table.item(selected_row, 2)
    #         address = address_item.text()
    #         phone_item = self.supplier_table.item(selected_row, 3)
    #         phone = phone_item.text()
    #         bill_supplier_item = self.supplier_table.item(selected_row, 4)
    #         bill_supplier = bill_supplier_item.text()
    #         sall_bill_supplier_item = self.supplier_table.item(selected_row, 5)
    #         sall_bill_supplier = sall_bill_supplier_item.text()
    #         Been_paid_supplier_item = self.supplier_table.item(selected_row, 6)
    #         Been_paid_supplier = Been_paid_supplier_item.text()
    #         combo_supplier_bill_item = self.supplier_table.item(selected_row, 6)
    #         combo_supplier_bill = combo_supplier_bill_item.text()
    #         combo_supp_item = self.supplier_table.item(selected_row, 7)
    #         combo_supp = combo_supp_item.text()

    #         new_name, ok = QInputDialog.getText(self, 'تعديل اسم المورد', 'ادخل اسم المورد:', QLineEdit.Normal, name)
    #         if ok:
    #             new_address, ok = QInputDialog.getText(self, 'تعديل عنوان المورد', 'ادخل عنوان المورد:', QLineEdit.Normal, address)
    #             if ok:
    #                 new_phone, ok = QInputDialog.getText(self, 'تعديل تليفون المورد', 'ادخل تليفون المورد:', QLineEdit.Normal, phone)
    #                 if ok:
    #                     new_bill_supplier, ok = QInputDialog.getText(self, 'تعديل  رقم فاتورة المورد', 'ادخل رقم فاتورة المورد:', QLineEdit.Normal, bill_supplier)
    #                     if ok:
    #                         new_sall_bill_supplier, ok = QInputDialog.getText(self, 'تعديل قيمة الفاتورة', 'ادخل قيمة الفاتورة :', QLineEdit.Normal, sall_bill_supplier)
    #                         if ok:
    #                             new_Been_paid_supplier, ok = QInputDialog.getText(self, 'تعديل  قيمة الدفع', 'ادخل  قيمة الدفع:', QLineEdit.Normal, Been_paid_supplier)
    #                             if ok:
    #                                 new_combo_supplier_bill, ok = QInputDialog.getText(self, 'تعديل  نوع السداد', 'ادخل نوع السداد:', QLineEdit.Normal, combo_supplier_bill)
    #                                 if ok:
    #                                     new_combo_supp, ok = QInputDialog.getText(self, 'تعديل  نوع السداد', 'ادخل نوع السداد:', QLineEdit.Normal, combo_supp)
    #                                     # if ok:
                    
    #             conn = sqlite3.connect('StorDB.db')
    #             c = conn.cursor()
    #             c.execute('UPDATE suppliers SET name = ?, address = ?, account = ? numper_bill_Suppliers=?, how_much_bill=?, term_value=?, method_of_payment=?, Been_paid=? WHERE id=?', (new_name, new_address, new_phone, new_bill_supplier, new_sall_bill_supplier, new_Been_paid_supplier, new_combo_supplier_bill, new_combo_supp,supplier_id))
    #             conn.commit()
    #             c.close()
    #             name_item.setText(new_name)
    #             address_item.setText(new_address)
    #             phone_item.setText(new_phone)
    #             bill_supplier_item.setText(new_bill_supplier)
    #             sall_bill_supplier_item.setText(new_sall_bill_supplier)
    #             Been_paid_supplier_item.setText(new_Been_paid_supplier)
    #             combo_supplier_bill_item.setText(new_combo_supplier_bill)
    #             combo_supp_item.setText(new_combo_supp)

    #             QMessageBox.information(self, 'Success', 'تم تحديث بيانات المورد بنجاح!')
    #         else:
    #             QMessageBox.warning(self, 'Error', 'يرجى تحديد مورد للتعديل')
    # def show_supplier_data(self):
    #     global MyData
    #     # conn = sqlite3.connect('Users.db')
    #     # cur = conn.cursor()
    #     conn = sqlite3.connect('StorDB.db')
    #     c = conn.cursor()
    #     c.execute("SELECT * FROM products")
    #     MyData = c.fetchall()
    #     total1 = 0
    #     total2 = 0
    #     total3 = 0
        
    #     self.supplier_table.setRowCount(0)
    #     for row in MyData:
    #         self.supplier_table.insertRow(self.supplier_table.rowCount())
    #         for column, item in enumerate(row):
    #             self.supplier_table.setItem(
    #                 self.supplier_table.rowCount() - 1, column, QTableWidgetItem(str(item))
                # )
    #             if column == 6:
    #                 total1 += float(item)
    #             if column == 7:
    #                 total2 += float(item)
    #             if column == 8:
    #                 total3 += float(item)
    #    self.total_cp_label.setText('إجمالى سعر الشراء:' + str(total1))
    #     self.total_cp_label.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold;border-radius: 4px;")

    #     self.total_sp_label.setText('إجمالى سعر البيع:' + str(total2))
    #     self.total_sp_label.setStyleSheet("background-color: #1D82CA; color: white; font-size: 12px; font-weight: bold;border-radius: 4px;")        

    #     self.total_assumed_profid_label.setText('إجمالـــــى الربحية:' + str(total3))
    #     self.total_assumed_profid_label.setStyleSheet("background-color: #1D82CA; color: white;font-size: 12px; font-weight: bold;border-radius: 4px;")




    # def delete_supplier(self):
    #     selected_row = self.supplier_table.currentRow()
    #     if selected_row >= 0:
    #         id_item = self.supplier_table.item(selected_row, 0)
    #         supplier_id = int(id_item.text())
    #         c.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
    #         conn.commit()
    #         self.supplier_table.removeRow(selected_row)
    #     else:
    #         print('No supplier selected')

    # def search_supplier(self):
    #     text = self.name_Supplier_input.text()
    #     if text:
    #         c.execute('SELECT * FROM suppliers WHERE name LIKE ? OR address LIKE ? OR account LIKE ?', ('%'+text+'%', '%'+text+'%', '%'+text+'%'))
    #     else:
    #         c.execute('SELECT * FROM suppliers')

    #     self.supplier_table.setRowCount(0)
    #     for row_data in c.fetchall():
    #         row_count = self.supplier_table.rowCount()
    #         self.supplier_table.setRowCount(row_count + 1)
    #         for column_count, data in enumerate(row_data):
    #             self.supplier_table.setItem(row_count, column_count, QTableWidgetItem(str(data)))

    def closeEvent(self, event):
        conn.close()
    def exit_app(self):
        # إغلاق التطبيق
        self.close()

class SalesReport(QMainWindow):

    def __init__(self):
        super().__init__()

        # set the window title and dimensions
        self.setWindowTitle('تقارير')
        self.setGeometry(100, 100, 600, 400)

        # create the start date label and field
        self.start_date_label = QLabel('Start Date:', self)
        self.start_date_label.move(10, 10)
        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.move(100, 10)
        self.start_date_edit.setLocale(QLocale(QLocale.English))
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        # create the end date label and field
        self.end_date_label = QLabel('End Date:', self)
        self.end_date_label.move(10, 40)
        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.move(100, 40)
        self.end_date_edit.setLocale(QLocale(QLocale.English))
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")

        # create the track sales button
        self.track_sales_button = QPushButton('حساب الفترة', self)
        self.track_sales_button.move(10, 70)
        self.track_sales_button.clicked.connect(self.track_sales)

        # create the sales table
        self.sales_table = QTableWidget(self)
        self.sales_table.setColumnCount(8)
        self.sales_table.setHorizontalHeaderLabels(['ID', 'Invoice_id', 'Product', 'Price', 'Quantity', 'Discount', 'Total Price', 'Date'])
        self.sales_table.setGeometry(10, 100, 780, 250)

        # create the total sales label
        self.total_sales_label = QLabel('', self)
        self.total_sales_label.setAlignment(Qt.AlignRight)
        self.total_sales_label.setGeometry(400, 360, 190, 20)


    def track_sales(self):
        conn = sqlite3.connect('StorDB.db')
        c = conn.cursor()
        search_start_date = self.start_date_edit.text()
        search_end_date = self.end_date_edit.text()
    
        result3 = "SELECT * FROM cart_items WHERE sale_date BETWEEN ? AND ?"
        c.execute(result3, (search_start_date, search_end_date))
        sales_data = c.fetchall()
        total_sales = 0
        # clear the existing table data
        self.sales_table.setRowCount(0)

        for row in sales_data:
            self.sales_table.insertRow(self.sales_table.rowCount())
            for column, item in enumerate(row):
                self.sales_table.setItem(
                    self.sales_table.rowCount() - 1, column, QTableWidgetItem(str(item))
                )
                if column == 6:
                    total_sales += float(item)

        # set the total sales label
        self.total_sales_label.setText('إجمالـــــى  الفترة المحددة:' + str(total_sales))

        conn.commit()
        conn.close()
       

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = Login()
    login.show()
    sys.exit(app.exec_())