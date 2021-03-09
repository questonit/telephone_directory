import sys
import psycopg2
from PyQt5 import QtWidgets
import mainform
import tables


class MainForm(QtWidgets.QMainWindow, mainform.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton.clicked.connect(self.add_row)
        self.pushButton_2.clicked.connect(self.delete_row)
        self.pushButton_3.clicked.connect(self.save_row)
        self.pushButton_4.clicked.connect(self.find_query)
        self.pushButton_5.clicked.connect(self.clean_boxes)
        self.pushButton_6.clicked.connect(self.all_table_show)
        self.action.triggered.connect(self.form_1)
        self.action_2.triggered.connect(self.form_2)
        self.action_3.triggered.connect(self.form_3)
        self.action_4.triggered.connect(self.form_4)
        self.action_5.triggered.connect(self.all_table_show)
        self.action_6.triggered.connect(self.clean_boxes)
        self.tableWidget.currentItemChanged.connect(self.show_row)
        self.radioButton.toggled.connect(self.all_table_show)
        self.radioButton_2.toggled.connect(self.all_table_show)

        self.all_table_show()

    def table_show(self, query):
        rows = execute_query_read(query)
        table = self.tableWidget
        table.setColumnCount(9)
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(["id", "Фамилия", "Имя", "Отчество",
                                         "Улица", "Дом", "Корпус", "Квартира",
                                         "Телефон"])
        table.hideColumn(0)
        for row_number, row in enumerate(rows):
            for column_number, data in enumerate(row):
                cell = QtWidgets.QTableWidgetItem(str(data).strip())
                cell.setToolTip(str(data).strip())
                table.setItem(row_number, column_number, cell)
        self.clean_boxes()

    def all_table_show(self):
        sort_ = ' ASC'
        if self.radioButton_2.isChecked():
            sort_ = ' DESC'
        query = '''
            SELECT u_id, f_val, n_val, o_val, s_val, bldn, bldn_k, appr,
                telephone
            FROM main
                JOIN fam
                ON main.fam = fam.f_id

                JOIN name_
                ON main.name_ = name_.n_id

                JOIN otch
                ON main.otch = otch.o_id

                JOIN street
                ON main.street = street.s_id
            ORDER BY f_val
            ''' + sort_
        self.table_show(query)
        self.update_comboboxes()

    def get_id(self):
        id = self.tableWidget.item(self.tableWidget.currentRow(), 0)
        if id is not None:
            id = id.text()
        return id

    def update_comboboxes(self):
        self.comboBox.clear()
        self.comboBox_2.clear()
        self.comboBox_3.clear()
        self.comboBox_4.clear()
        tables = ['fam', 'name_', 'otch', 'street']
        boxes = []
        for table in tables:
            query = f"SELECT * from {table} ORDER BY { table[0] }_val"
            rows = execute_query_read(query)
            items = [row[1].strip() for row in rows]
            boxes.append(items)
        self.comboBox.addItems(boxes[0])
        self.comboBox_2.addItems(boxes[1])
        self.comboBox_3.addItems(boxes[2])
        self.comboBox_4.addItems(boxes[3])
        self.comboBox.setCurrentIndex(-1)
        self.comboBox_2.setCurrentIndex(-1)
        self.comboBox_3.setCurrentIndex(-1)
        self.comboBox_4.setCurrentIndex(-1)

    def find_element_in_parent(self, table, field, value):
        query = f"SELECT * from { table } WHERE { field } = '{ value }'"
        item = execute_query_read(query)
        if len(item) == 0:
            return None
        return item[0][0]

    def show_row(self):
        if self.get_id() is None:
            self.clean_boxes()
            return
        table = self.tableWidget
        row_id = table.currentRow()
        self.comboBox.setCurrentText(table.item(row_id, 1).text())
        self.comboBox_2.setCurrentText(table.item(row_id, 2).text())
        self.comboBox_3.setCurrentText(table.item(row_id, 3).text())
        self.comboBox_4.setCurrentText(table.item(row_id, 4).text())
        self.lineEdit.setText(table.item(row_id, 5).text())
        self.lineEdit_2.setText(table.item(row_id, 6).text())
        self.lineEdit_3.setText(table.item(row_id, 7).text())
        self.lineEdit_4.setText(table.item(row_id, 8).text())

    def resize_table(self):
        width = (self.tableWidget.width() - 15) / 7
        width1 = width
        for i in range(1, 9):
            self.tableWidget.setColumnWidth(i, int(width1))
            if i in [4, 5, 6]:
                width1 = width * 0.66
            else:
                width1 = width

    def resizeEvent(self, event):
        self.resize_table()
        super(MainForm, self).resizeEvent(event)

    def add_row(self):
        table = self.tableWidget
        table.setRowCount(table.rowCount() + 1)
        table.setCurrentCell(table.rowCount() - 1, 1)
        self.show_row()

    def save_row(self):
        table = self.tableWidget
        row_id = table.currentRow()
        f_id = self.find_element_in_parent(
            'fam', 'f_val', self.comboBox.currentText())
        n_id = self.find_element_in_parent(
            'name_', 'n_val', self.comboBox_2.currentText())
        o_id = self.find_element_in_parent(
            'otch', 'o_val', self.comboBox_3.currentText())
        s_id = self.find_element_in_parent(
            'street', 's_val', self.comboBox_4.currentText())
        if ((f_id is None) or (n_id is None) or (o_id is None) or
                (s_id is None)):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Одно или несколько полей заполнены не правильно")
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            return 0
        bldn = self.lineEdit.text()
        bldn_k = self.lineEdit_2.text()
        appr = self.lineEdit_3.text()
        telephone = self.lineEdit_4.text()
        u_id = table.item(row_id, 0)
        if u_id is not None:
            u_id = u_id.text()
            query = (f"UPDATE main SET fam = { f_id }, name_ = { n_id }, " +
                     f"otch = { o_id }, street = { s_id }," +
                     f"bldn = '{ bldn }', bldn_k = '{ bldn_k }'," +
                     f"appr = '{ appr }', telephone = '{ telephone }' " +
                     f"WHERE u_id = { u_id }")
        else:
            query = ("INSERT INTO main (fam, name_, otch, street, bldn, " +
                     f"bldn_k, appr, telephone) VALUES ({ f_id }, { n_id }, " +
                     f"{ o_id }, { s_id }, '{ bldn }', '{ bldn_k }', " +
                     f"'{ appr }', '{ telephone }')")
        execute_query_write(query)
        self.all_table_show()

    def delete_row(self):
        u_id = self.get_id()
        msg = QtWidgets.QMessageBox()
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok |
                               QtWidgets.QMessageBox.Cancel)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setText("Удалить выделенную строку?")
        msg.setWindowTitle("Удаление")
        if (msg.exec_() == QtWidgets.QMessageBox.Ok):
            query = f"DELETE FROM main WHERE u_id = { u_id }"
            execute_query_write(query)
            self.all_table_show()
            self.clean_boxes()

    def clean_boxes(self):
        self.comboBox.setCurrentIndex(-1)
        self.comboBox_2.setCurrentIndex(-1)
        self.comboBox_3.setCurrentIndex(-1)
        self.comboBox_4.setCurrentIndex(-1)
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()

    def find_query(self):
        sort_ = 'ORDER BY f_val ASC'
        if self.radioButton_2.isChecked():
            sort_ = 'ORDER BY f_val DESC'
        query = '''
            SELECT u_id, f_val, n_val, o_val, s_val, bldn, bldn_k, appr,
                telephone
            FROM main
                JOIN fam
                ON main.fam = fam.f_id

                JOIN name_
                ON main.name_ = name_.n_id

                JOIN otch
                ON main.otch = otch.o_id

                JOIN street
                ON main.street = street.s_id
            '''
        conditions = []
        if (self.comboBox.currentIndex() != -1):
            conditions.append(f"f_val = '{ self.comboBox.currentText() }'")
        if (self.comboBox_2.currentIndex() != -1):
            conditions.append(f"n_val = '{ self.comboBox_2.currentText() }'")
        if (self.comboBox_3.currentIndex() != -1):
            conditions.append(f"o_val = '{ self.comboBox_3.currentText() }'")
        if (self.comboBox_4.currentIndex() != -1):
            conditions.append(f"s_val = '{ self.comboBox_4.currentText() }'")
        if (self.lineEdit.text() != ''):
            conditions.append(f"bldn = '{ self.lineEdit.text() }'")
        if (self.lineEdit_2.text() != ''):
            conditions.append(f"bldn_k = '{ self.lineEdit_2.text() }'")
        if (self.lineEdit_3.text() != ''):
            conditions.append(f"appr = '{ self.lineEdit_3.text() }'")
        if (self.lineEdit_4.text() != ''):
            conditions.append(f"telephone LIKE '{ self.lineEdit_4.text() }'")
        if (len(conditions) > 0):
            query += ' WHERE '
            query += ' AND '.join(conditions)
        query += sort_
        self.table_show(query)

    def form_1(self):
        self.form_create('fam')

    def form_2(self):
        self.form_create('name_')

    def form_3(self):
        self.form_create('otch')

    def form_4(self):
        self.form_create('street')

    def form_create(self, table_name):
        self.table_window = TablesForm(table_name)
        self.table_window.show()


class TablesForm(QtWidgets.QMainWindow, tables.Ui_MainWindow):
    def __init__(self, table_name):
        super().__init__()
        self.setupUi(self)

        self.table_name = table_name
        self.query = ''
        self.header_name = ''

        self.tableWidget.currentItemChanged.connect(self.show_row)
        self.pushButton.clicked.connect(self.add_row)
        self.pushButton_2.clicked.connect(self.save_row)
        self.pushButton_3.clicked.connect(self.delete_row)
        self.pushButton_4.clicked.connect(self.show_table)

        self.load_names()
        self.show_table()

    def get_id(self):
        id = self.tableWidget.item(self.tableWidget.currentRow(), 0)
        if id is not None:
            id = id.text()
        return id

    def load_names(self):
        if self.table_name == 'fam':
            self.setWindowTitle('Фамилии')
            self.header_name = 'Фамилия'
        elif self.table_name == 'name_':
            self.setWindowTitle('Имена')
            self.header_name = 'Имя'
        elif self.table_name == 'otch':
            self.setWindowTitle('Отчества')
            self.header_name = 'Отчество'
        elif self.table_name == 'street':
            self.setWindowTitle('Улицы')
            self.header_name = 'Улица'
        self.label.setText(self.header_name + ':')
        self.query = (f"SELECT * FROM { self.table_name } "
                      + f"ORDER BY { self.table_name[0] }_val")

    def show_table(self):
        rows = execute_query_read(self.query)
        table = self.tableWidget
        table.setColumnCount(2)
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(["id", self.header_name])
        # table.hideColumn(0)
        for row_number, row in enumerate(rows):
            for column_number, data in enumerate(row):
                cell = QtWidgets.QTableWidgetItem(str(data).strip())
                cell.setToolTip(str(data).strip())
                table.setItem(row_number, column_number, cell)

    def show_row(self):
        if self.get_id() is None:
            self.lineEdit.clear()
            return
        table = self.tableWidget
        row_id = table.currentRow()
        self.lineEdit.setText(table.item(row_id, 1).text())

    def add_row(self):
        table = self.tableWidget
        table.setRowCount(table.rowCount() + 1)
        table.setCurrentCell(table.rowCount() - 1, 1)
        self.show_row()

    def delete_row(self):
        id = self.get_id()
        msg = QtWidgets.QMessageBox()
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok |
                               QtWidgets.QMessageBox.Cancel)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setText("Удалить выделенную строку?")
        msg.setWindowTitle("Удаление")
        if (msg.exec_() == QtWidgets.QMessageBox.Ok):
            query = (f"DELETE FROM { self.table_name }"
                     + f" WHERE { self.table_name[0]}_id = { id }")
            try:
                execute_query_write(query)
            except Exception:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("Удаление невозможно, так как поле используется"
                            + " в главной таблице")
                msg.setWindowTitle("Ошибка")
                msg.exec_()
            self.show_table()

    def save_row(self):
        table = self.tableWidget
        row_id = table.currentRow()
        id = table.item(row_id, 0)
        val = self.lineEdit.text()
        char = self.table_name[0]
        if id is not None:
            id = id.text()
            query = (f"UPDATE { self.table_name } " +
                     f"SET  { char }_val = '{ val }' " +
                     f"WHERE { char }_id = { id }")
        else:
            query = (f"INSERT INTO { self.table_name } ({ char }_val)" +
                     f" VALUES ('{ val }')")
        execute_query_write(query)
        self.show_table()


def connect_bd():
    conn = psycopg2.connect(
        database='telspr',
        user='postgres',
        password='1',
        host='localhost',
        port='5432'
    )
    return conn


def execute_query_read(query):
    conn = connect_bd()
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()


def execute_query_write(query):
    conn = connect_bd()
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()


def main():
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainForm()
    mainwindow.show()
    app.exec_()


if __name__ == "__main__":
    main()
