from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QGridLayout, QTableWidget,
    QTableWidgetItem, QComboBox, QMessageBox,
    QHBoxLayout, QHeaderView, QStyle
)

from PyQt6.QtGui import QDoubleValidator, QRegularExpressionValidator
from PyQt6.QtCore import Qt, QTimer, QRegularExpression

from modules.shipments import (
    get_customers,
    add_shipment,
    get_shipments,
    mark_invoice_generated,
    delete_shipment
)

from modules.invoices import (
    generate_invoice_no,
    add_invoice
)

from modules.payments import add_payment

from datetime import datetime


class ShipmentPage(QWidget):

    def __init__(self, uid):
        super().__init__()

        self.uid = uid

        self.setStyleSheet("""
        QWidget{font-family:Roboto;font-size:13px;}
        QLabel{font-size:12px;font-weight:500;}
        QLineEdit{padding:6px;}
        QComboBox{padding:4px;}

        QPushButton{
            font-size:14px;
            font-weight:500;
            padding:6px;
        }

        QPushButton#saveBtn{
            background:#60A5FA;
            color:white;
            border-radius:6px;
        }

        QPushButton#saveBtn:hover{
            background:#3B82F6;
        }

        QTableWidget{font-size:12px;}
        QHeaderView::section{font-size:13px;font-weight:bold;}
        """)

        main_layout = QVBoxLayout()

        title = QLabel("Shipments / Consignments")
        title.setStyleSheet("font-size:22px;font-weight:bold")
        main_layout.addWidget(title)

        # =========================
        # SEARCH
        # =========================
        search_layout = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search LR Number")

        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self.search_lr)

        search_layout.addWidget(self.search)
        search_layout.addWidget(btn_search)

        main_layout.addLayout(search_layout)

        # =========================
        # FORM
        # =========================
        grid = QGridLayout()

        self.date = QLineEdit()
        self.date.setText(datetime.today().strftime("%Y-%m-%d"))

        self.lr = QLineEdit()
        self.lr.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9]*")))
        self.lr.textChanged.connect(self.format_lr)

        self.vehicle = QLineEdit()
        self.vehicle.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9]*")))
        self.vehicle.textChanged.connect(self.format_vehicle)

        self.origin = QLineEdit()
        self.destination = QLineEdit()

        self.origin.textChanged.connect(lambda: self.origin.setText(self.origin.text().title()))
        self.destination.textChanged.connect(lambda: self.destination.setText(self.destination.text().title()))

        self.pkgs = QLineEdit()
        self.qty = QLineEdit()
        self.rate = QLineEdit()

        self.amount = QLineEdit()
        self.amount.setReadOnly(True)

        validator = QDoubleValidator()
        self.pkgs.setValidator(validator)
        self.qty.setValidator(validator)
        self.rate.setValidator(validator)

        self.qty.textChanged.connect(self.calculate_amount)
        self.rate.textChanged.connect(self.calculate_amount)

        self.customer = QComboBox()
        self.load_customers()

        grid.addWidget(QLabel("Date"),0,0)
        grid.addWidget(self.date,0,1)

        grid.addWidget(QLabel("LR No"),1,0)
        grid.addWidget(self.lr,1,1)

        grid.addWidget(QLabel("Vehicle No"),2,0)
        grid.addWidget(self.vehicle,2,1)

        grid.addWidget(QLabel("Customer"),3,0)
        grid.addWidget(self.customer,3,1)

        grid.addWidget(QLabel("From"),4,0)
        grid.addWidget(self.origin,4,1)

        grid.addWidget(QLabel("To"),5,0)
        grid.addWidget(self.destination,5,1)

        grid.addWidget(QLabel("PKGs"),0,2)
        grid.addWidget(self.pkgs,0,3)

        grid.addWidget(QLabel("Weight"),1,2)
        grid.addWidget(self.qty,1,3)

        grid.addWidget(QLabel("Rate"),2,2)
        grid.addWidget(self.rate,2,3)

        grid.addWidget(QLabel("Amount"),3,2)
        grid.addWidget(self.amount,3,3)

        self.btn_save = QPushButton("Save Shipment")
        self.btn_save.setObjectName("saveBtn")
        self.btn_save.clicked.connect(self.save_shipment)

        grid.addWidget(self.btn_save,5,3)

        main_layout.addLayout(grid)

        # =========================
        # TABLE
        # =========================
        self.table = QTableWidget()
        self.table.setColumnCount(13)

        self.table.setHorizontalHeaderLabels([
            "Date","LR","Vehicle","Customer",
            "From","To","PKGs",
            "Weight","Rate","Amount","Status",
            "Invoice","Delete"
        ])

        header = self.table.horizontalHeader()

        # Short / fixed-width columns
        fixed_cols = {
            0: 90,   # Date
            1: 80,   # LR
            2: 90,   # Vehicle
            6: 55,   # PKGs
            7: 70,   # Weight
            8: 70,   # Rate
            9: 80,   # Amount
            10: 80,  # Status
        }
        for col, width in fixed_cols.items():
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(col, width)

        # Wide text columns — stretch to fill remaining space
        for i in (3, 4, 5):  # Customer, From, To
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # Icon columns
        header.setSectionResizeMode(11, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(12, QHeaderView.ResizeMode.ResizeToContents)

        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        self.load_shipments()


    # =========================
    # FORMAT
    # =========================
    def format_lr(self):
        text = self.lr.text()
        if text != text.upper():
            pos = self.lr.cursorPosition()
            self.lr.blockSignals(True)
            self.lr.setText(text.upper())
            self.lr.setCursorPosition(pos)
            self.lr.blockSignals(False)

    def format_vehicle(self):
        text = self.vehicle.text()
        if text != text.upper():
            pos = self.vehicle.cursorPosition()
            self.vehicle.blockSignals(True)
            self.vehicle.setText(text.upper())
            self.vehicle.setCursorPosition(pos)
            self.vehicle.blockSignals(False)

    # =========================
    # LOAD CUSTOMERS
    # =========================
    def load_customers(self):
        customers = get_customers(self.uid)
        self.customer.clear()
        self.customer.addItem("Select Customer")
        if customers:
            self.customer.addItems(sorted(customers))

    # =========================
    # CALCULATE
    # =========================
    def calculate_amount(self):
        try:
            total = float(self.qty.text()) * float(self.rate.text())
            self.amount.setText(f"{total:.2f}")
        except (ValueError, TypeError):
            self.amount.clear()

    # =========================
    # SAVE
    # =========================
    def save_shipment(self):

        if self.customer.currentText() == "Select Customer":
            QMessageBox.warning(self,"Error","Select customer")
            return

        shipment = {
            "business_uid": self.uid,
            "date": self.date.text(),
            "lr_no": self.lr.text(),
            "vehicle_no": self.vehicle.text(),
            "sender": self.customer.currentText(),
            "receiver": "",
            "from": self.origin.text(),
            "to": self.destination.text(),
            "box": self.pkgs.text(),
            "qty": self.qty.text(),
            "rate": self.rate.text(),
            "amount": self.amount.text(),
            "status": "Booked"
        }

        add_shipment(shipment)

        QMessageBox.information(self,"Saved","Shipment saved")

        self.clear_fields()
        self.load_shipments()

    def clear_fields(self):
        self.lr.clear()
        self.vehicle.clear()
        self.origin.clear()
        self.destination.clear()
        self.pkgs.clear()
        self.qty.clear()
        self.rate.clear()
        self.amount.clear()
        self.customer.setCurrentIndex(0)

    # =========================
    # GENERATE INVOICE
    # =========================
    def generate_invoice(self, shipment):

        if shipment.get("invoice_generated"):
            QMessageBox.information(self, "Info", "Invoice already generated")
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            "Generate invoice for this shipment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        invoice_no = generate_invoice_no(self.uid)

        add_invoice({
            "business_uid": self.uid,
            "invoice_no": invoice_no,
            "customer": shipment["sender"],
            "amount": shipment["amount"],
            "date": shipment["date"],
            "shipments": [shipment["id"]],
            "status": "Pending"
        })

        add_payment({
            "business_uid": self.uid,
            "invoice_no": invoice_no,
            "customer": shipment["sender"],
            "amount": shipment["amount"],
            "status": "Pending"
        })

        mark_invoice_generated(self.uid, shipment["id"], invoice_no)

        QMessageBox.information(self, "Success", f"Invoice {invoice_no} generated")

        self.load_shipments()

    # =========================
    # DELETE
    # =========================
    def delete_shipment(self, shipment):

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Delete this shipment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        delete_shipment(self.uid, shipment["id"])

        QMessageBox.information(self, "Deleted", "Shipment deleted")

        self.load_shipments()

    # =========================
    # LOAD SHIPMENTS
    # =========================
    def load_shipments(self):

        data = get_shipments(self.uid)
        data = [s for s in data if not s.get("invoice_generated", False)]
        data = sorted(data, key=lambda x: x["date"], reverse=True)

        self.table.setRowCount(len(data))

        for row, s in enumerate(data):

            cols = [
                s["date"], s["lr_no"], s["vehicle_no"], s["sender"],
                s["from"], s["to"], s["box"],
                s["qty"], s["rate"], s["amount"], s["status"]
            ]

            for col,val in enumerate(cols):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row,col,item)

            # Invoice icon
            btn_invoice = QPushButton()
            btn_invoice.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            btn_invoice.clicked.connect(lambda _, x=s: self.generate_invoice(x))
            self.table.setCellWidget(row,11,btn_invoice)

            # Delete icon
            btn_delete = QPushButton()
            btn_delete.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
            btn_delete.clicked.connect(lambda _, x=s: self.delete_shipment(x))
            self.table.setCellWidget(row,12,btn_delete)

    # =========================
    # SEARCH
    # =========================
    def search_lr(self):

        lr = self.search.text().lower()

        data = get_shipments(self.uid)
        data = [s for s in data if not s.get("invoice_generated", False)]

        filtered = [s for s in data if lr in s["lr_no"].lower()]

        self.table.setRowCount(len(filtered))

        for row,s in enumerate(filtered):

            cols = [
                s["date"], s["lr_no"], s["vehicle_no"], s["sender"],
                s["from"], s["to"], s["box"],
                s["qty"], s["rate"], s["amount"], s["status"]
            ]

            for col,val in enumerate(cols):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row,col,item)

            btn_invoice = QPushButton()
            btn_invoice.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            btn_invoice.clicked.connect(lambda _, x=s: self.generate_invoice(x))
            self.table.setCellWidget(row,11,btn_invoice)

            btn_delete = QPushButton()
            btn_delete.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
            btn_delete.clicked.connect(lambda _, x=s: self.delete_shipment(x))
            self.table.setCellWidget(row,12,btn_delete)
