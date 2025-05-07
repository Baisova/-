import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit,
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QComboBox, QCheckBox
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon

from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, Float, ForeignKey, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# SQLAlchemy настройка
Base = declarative_base()

class Gost(Base):
    __tablename__ = 'gost'
    id_gostya = Column(Integer, primary_key=True)
    familiya = Column(String)
    imya = Column(String)
    otchestvo = Column(String)
    telefon = Column(String)
    data_rozhdeniya = Column(Date)
    mesto_rozhdeniya = Column(String)
    seriya_pasporta = Column(String)
    nomer_pasporta = Column(String)
    kem_vydan = Column(String)
    data_vydachi = Column(Date)
    adres = Column(String)
    nomer_avto = Column(String)
    nomer_skidochnoy_karty = Column(String)
    
    bronirovaniya = relationship("Bronirovanie", back_populates="gost")

class KategoriyaNomera(Base):
    __tablename__ = 'kategoriya_nomera'
    id_kategorii = Column(Integer, primary_key=True)
    nazvanie = Column(String)
    opisanie = Column(String)
    tsena_v_sutki = Column(Float)
    
    nomera = relationship("Nomer", back_populates="kategoriya")

class Nomer(Base):
    __tablename__ = 'nomer'
    id_nomera = Column(Integer, primary_key=True)
    id_kategorii = Column(Integer, ForeignKey('kategoriya_nomera.id_kategorii'))
    nomer_komnaty = Column(String)
    dostupen = Column(Boolean)
    
    kategoriya = relationship("KategoriyaNomera", back_populates="nomera")
    bronirovaniya = relationship("Bronirovanie", back_populates="nomer")

class Usluga(Base):
    __tablename__ = 'usluga'
    id_uslugi = Column(Integer, primary_key=True)
    nazvanie = Column(String)
    opisanie = Column(String)
    tsena = Column(Float)
    edinitsa_izmereniya = Column(String)

class Bronirovanie(Base):
    __tablename__ = 'bronirovanie'
    id_bronirovaniya = Column(Integer, primary_key=True)
    id_gostya = Column(Integer, ForeignKey('gost.id_gostya'))
    data_zaezda = Column(Date)
    data_vyezda = Column(Date)
    id_nomera = Column(Integer, ForeignKey('nomer.id_nomera'))
    kolichestvo_dney = Column(Integer)
    dop_mesto = Column(Boolean)
    zavtrak = Column(Boolean)
    uzhin = Column(Boolean)
    
    gost = relationship("Gost", back_populates="bronirovaniya")
    nomer = relationship("Nomer", back_populates="bronirovaniya")

engine = create_engine('postgresql://postgres:1234@localhost:5432/gostinitsa')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class AddRecordWindow(QWidget):
    def __init__(self, parent, table_name):
        super().__init__()
        self.parent = parent
        self.table_name = table_name
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Добавить в {self.table_name}")
        self.setGeometry(300, 300, 400, 500)
        self.layout = QVBoxLayout()
        self.inputs = {}

        if self.table_name == "gost":
            self.setup_gost_fields()
        elif self.table_name == "nomer":
            self.setup_nomer_fields()
        elif self.table_name == "usluga":
            self.setup_usluga_fields()
        elif self.table_name == "bronirovanie":
            self.setup_bronirovanie_fields()

        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_record)
        self.layout.addWidget(self.add_btn)
        self.setLayout(self.layout)

    def setup_gost_fields(self):
        fields = [
            ("familiya", "Фамилия"), ("imya", "Имя"), ("otchestvo", "Отчество"),
            ("telefon", "Телефон"), ("data_rozhdeniya", "Дата рождения"),
            ("mesto_rozhdeniya", "Место рождения"), ("seriya_pasporta", "Серия паспорта"),
            ("nomer_pasporta", "Номер паспорта"), ("kem_vydan", "Кем выдан"),
            ("data_vydachi", "Дата выдачи"), ("adres", "Адрес"),
            ("nomer_avto", "Номер авто"), ("nomer_skidochnoy_karty", "Скидочная карта")
        ]
        self.add_fields(fields)

    def setup_nomer_fields(self):
        self.layout.addWidget(QLabel("Категория:"))
        categories = session.query(KategoriyaNomera).all()
        self.category_combo = QComboBox()
        for cat in categories:
            self.category_combo.addItem(cat.nazvanie, cat.id_kategorii)
        self.inputs["id_kategorii"] = self.category_combo
        self.layout.addWidget(self.category_combo)

        self.add_fields([("nomer_komnaty", "Номер комнаты")])
        
        self.layout.addWidget(QLabel("Доступен:"))
        self.inputs["dostupen"] = QCheckBox()
        self.inputs["dostupen"].setChecked(True)
        self.layout.addWidget(self.inputs["dostupen"])

    def setup_usluga_fields(self):
        fields = [
            ("nazvanie", "Название"), ("opisanie", "Описание"),
            ("tsena", "Цена"), ("edinitsa_izmereniya", "Единица измерения")
        ]
        self.add_fields(fields)

    def setup_bronirovanie_fields(self):
        self.layout.addWidget(QLabel("Гость:"))
        guests = session.query(Gost).all()
        self.guest_combo = QComboBox()
        for guest in guests:
            self.guest_combo.addItem(f"{guest.familiya} {guest.imya}", guest.id_gostya)
        self.inputs["id_gostya"] = self.guest_combo
        self.layout.addWidget(self.guest_combo)

        self.add_fields([
            ("data_zaezda", "Дата заезда"),
            ("data_vyezda", "Дата выезда")
        ])

        self.layout.addWidget(QLabel("Номер:"))
        rooms = session.query(Nomer).all()
        self.room_combo = QComboBox()
        for room in rooms:
            self.room_combo.addItem(f"{room.nomer_komnaty}", room.id_nomera)
        self.inputs["id_nomera"] = self.room_combo
        self.layout.addWidget(self.room_combo)

        self.add_fields([
            ("dop_mesto", "Доп. место"),
            ("zavtrak", "Завтрак"),
            ("uzhin", "Ужин")
        ])

    def add_fields(self, fields):
        for key, label in fields:
            self.layout.addWidget(QLabel(label))
            if "data" in key:
                field = QDateEdit()
                field.setCalendarPopup(True)
                field.setDate(QDate.currentDate())
            elif "чекбокс" in label:
                field = QCheckBox()
            else:
                field = QLineEdit()
            self.inputs[key] = field
            self.layout.addWidget(field)

    def add_record(self):
        try:
            data = {}
            for key, widget in self.inputs.items():
                if isinstance(widget, QDateEdit):
                    data[key] = widget.date().toPyDate()
                elif isinstance(widget, QComboBox):
                    data[key] = widget.currentData()
                elif isinstance(widget, QCheckBox):
                    data[key] = widget.isChecked()
                else:
                    data[key] = widget.text()

            if self.table_name == "gost":
                record = Gost(**data)
            elif self.table_name == "nomer":
                record = Nomer(**data)
            elif self.table_name == "usluga":
                record = Usluga(**data)
                record.tsena = float(record.tsena)
            elif self.table_name == "bronirovanie":
                record = Bronirovanie(**data)
                record.kolichestvo_dney = (record.data_vyezda - record.data_zaezda).days

            session.add(record)
            session.commit()
            QMessageBox.information(self, "Успех", "Запись добавлена")
            self.parent.load_table()
            self.close()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))

class GraphWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Графики")
        self.setGeometry(200, 200, 800, 600)
        self.layout = QVBoxLayout()
        
        self.btn_layout = QHBoxLayout()
        for title in ["Статус номеров", "Бронирования", "Услуги"]:
            btn = QPushButton(title)
            btn.clicked.connect(self.plot_graph)
            self.btn_layout.addWidget(btn)
        self.layout.addLayout(self.btn_layout)

        self.canvas = FigureCanvas(plt.Figure())
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def plot_graph(self):
        title = self.sender().text()
        ax = self.canvas.figure.subplots()
        ax.clear()

        if title == "Статус номеров":
            free = session.query(Nomer).filter(Nomer.dostupen == True).count()
            busy = session.query(Nomer).filter(Nomer.dostupen == False).count()
            ax.pie([free, busy], labels=["Свободно", "Занято"], autopct='%1.1f%%')
        
        elif title == "Бронирования":
            bookings = session.query(
                KategoriyaNomera.nazvanie,
                func.count(Bronirovanie.id_bronirovaniya)
            ).join(Bronirovanie.nomer).join(Nomer.kategoriya
            ).group_by(KategoriyaNomera.nazvanie).all()
            
            names = [b[0] for b in bookings]
            counts = [b[1] for b in bookings]
            ax.bar(names, counts)
        
        elif title == "Услуги":
            services = session.query(
                Usluga.nazvanie,
                func.sum(Usluga.tsena)
            ).group_by(Usluga.nazvanie).all()
            
            names = [s[0] for s in services]
            prices = [s[1] or 0 for s in services]
            ax.bar(names, prices)

        ax.set_title(title)
        self.canvas.draw()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Гостиница")
        self.setWindowIcon(QIcon("gostinitsa_icon.png"))
        self.resize(1000, 600)

        self.layout = QHBoxLayout()
        self.menu = QVBoxLayout()
        self.table = QTableWidget()

        tables = {
            "Клиенты": "gost",
            "Номера": "nomer",
            "Услуги": "usluga",
            "Бронирования": "bronirovanie"
        }

        for name, table in tables.items():
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, t=table: self.load_table(t))
            self.menu.addWidget(btn)

        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_record)
        self.menu.addWidget(self.add_btn)

        self.graph_btn = QPushButton("Графики")
        self.graph_btn.clicked.connect(self.show_graphs)
        self.menu.addWidget(self.graph_btn)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск...")
        self.search.textChanged.connect(self.filter_table)
        self.menu.addWidget(self.search)

        self.layout.addLayout(self.menu)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.current_table = ""
        self.data = []

    def load_table(self, table_name):
        self.current_table = table_name
        try:
            if table_name == "gost":
                records = session.query(Gost).all()
                self.data = [[getattr(r, c) for c in Gost.__table__.columns.keys()] for r in records]
                headers = Gost.__table__.columns.keys()
            
            elif table_name == "nomer":
                records = session.query(Nomer).join(KategoriyaNomera).all()
                self.data = []
                for r in records:
                    self.data.append([
                        r.id_nomera,
                        r.kategoriya.nazvanie,
                        r.nomer_komnaty,
                        "Да" if r.dostupen else "Нет"
                    ])
                headers = ["ID", "Категория", "Номер", "Доступен"]
            
            elif table_name == "usluga":
                records = session.query(Usluga).all()
                self.data = [[getattr(r, c) for c in Usluga.__table__.columns.keys()] for r in records]
                headers = Usluga.__table__.columns.keys()
            
            elif table_name == "bronirovanie":
                records = session.query(Bronirovanie).join(Gost).join(Nomer).join(KategoriyaNomera).all()
                self.data = []
                for r in records:
                    self.data.append([
                        r.id_bronirovaniya,
                        f"{r.gost.familiya} {r.gost.imya}",
                        r.data_zaezda.strftime("%Y-%m-%d"),
                        r.data_vyezda.strftime("%Y-%m-%d"),
                        f"{r.nomer.nomer_komnaty} ({r.nomer.kategoriya.nazvanie})",
                        r.kolichestvo_dney,
                        "Да" if r.dop_mesto else "Нет",
                        "Да" if r.zavtrak else "Нет",
                        "Да" if r.uzhin else "Нет"
                    ])
                headers = ["ID", "Гость", "Заезд", "Выезд", "Номер", "Дней", "Доп место", "Завтрак", "Ужин"]

            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.setRowCount(len(self.data))

            for i, row in enumerate(self.data):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def filter_table(self):
        text = self.search.text().lower()
        filtered = [row for row in self.data if any(text in str(cell).lower() for cell in row)]
        self.table.setRowCount(len(filtered))
        for i, row in enumerate(filtered):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_record(self):
        if self.current_table:
            self.add_window = AddRecordWindow(self, self.current_table)
            self.add_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите таблицу")

    def show_graphs(self):
        self.graph_window = GraphWindow(self)
        self.graph_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
