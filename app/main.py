from PyQt5.QtWidgets import (QLineEdit, QMainWindow, QWidget, QTableWidgetItem, QMessageBox,
							 QDialog, QApplication, QInputDialog, QFileDialog, QAbstractItemView, QTreeWidgetItem, QDockWidget)
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication
from PyQt5 import QtCore
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
import sqlalchemy as sqla
from sqlalchemy.sql import text
import sys
import os
import xlsxwriter
import reports
import matplotlib as mpl
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from ui.main import Ui_MainWindow
from ui import loading
from utils import seeder
from query_docks import *
from admin_widgets import *
from client_widgets import *

DB_HOST = "127.0.0.1"
DB_NAME = "meatplants"
DB_PORT = 5432

engine = None
con = None


class GenThread(QtCore.QThread):
	def __init__(self, con):
		super().__init__()
		self.con = con

	def run(self):
		seeder.standart_generate(self.con)


class ReportThread(QtCore.QThread):
	def __init__(self, w, resp, h, c, r=None):
		super().__init__()
		self.w = w
		self.resp = resp
		self.h = h
		self.c = c
		self.r = r

	def run(self):
		reports.writeReport(self.w, self.resp, self.h, self.c, self.r)


class LoadDialog(QDialog, loading.Ui_Dialog):
	def __init__(self, parent, text, thread):
		super().__init__(parent)
		self.setupUi(self)
		self.label.setText(text)
		self.setWindowFlags(
			QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
		self.thread = thread
		self.thread.finished.connect(self.close)
		self.thread.start()


class Canvas(FigureCanvas):
	def __init__(self, parent=None):
		self.figure = plt.figure()
		FigureCanvas.__init__(self, self.figure)
		self.setParent(parent)


class MainWindow(QMainWindow, Ui_MainWindow):
	def __init__(self, con, engine):
		super().__init__()
		self.con = con
		self.engine = engine
		self.setupUi(self)
		self.T = 'Мясокомбинаты'
		self.messages = {}

	def chTitle(self, t):
		self.setWindowTitle("{} - {}".format(self.T, t))

	def query(self, q, d=None):
		res = None
		try:
			if d:
				res = self.con.execute(text(q), **d)
			else:
				res = self.con.execute(q)
		except sqla.exc.SQLAlchemyError as e:
			m = e._message()
			m = m.replace('psycopg2.errors.', '')
			m = 'Произошла ошибка:\n'+m
			name = e.__cause__.diag.constraint_name
			if name:
				mes = self.messages.get(name, 0)
				if mes:
					m += "\n"+name+":\n"+mes
			QMessageBox.critical(self, "Ошибка", m, buttons=QMessageBox.Ok)
		return res


class AddClientOrderDialog(QDialog):
	def __init__(self, con):
		super().__init__()
		self.con = con
		uic.loadUi('./ui/cl_order_in.ui', self)
		self.products = []
		self.product.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		res = self.con.query(
			"select pop.id,pt.name,pn.name from products_of_plants pop join products p on p.id = pop.product_id join product_names pn on pn.id = p.name_id join product_types pt on pt.id = p.type_id order by pt.name,pn.name;")
		if res:
			for i in res:
				self.product.addItem(f'{i[1]} "{i[2]}"')
				self.products.append(i[0])
		self.date.setDate(QtCore.QDate.currentDate())
		self.btn.clicked.connect(self.accept)

	def getData(self):
		i = self.product.currentIndex()
		return {
			'product_id': self.products[i] if i > -1 else None,
			'volume': self.volume.value(),
			'date': self.date.date().toString("yyyy.MM.dd")
		}

	def insert(self, d):
		self.con.query(
			"insert into orders values(default,:date,:volume,:client,:product_id)", d)


class AddClientOrderDialog2(QDialog):
	def __init__(self, con):
		super().__init__()
		self.con = con
		uic.loadUi('./ui/cl_order_in2.ui', self)
		self.products = []
		self.product.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		res = self.con.query(
			"select pop.id,pt.name,pn.name from products_of_plants pop join products p on p.id = pop.product_id join product_names pn on pn.id = p.name_id join product_types pt on pt.id = p.type_id order by pt.name,pn.name;")
		if res:
			for i in res:
				self.product.addItem(f'{i[1]} "{i[2]}"')
				self.products.append(i[0])
		self.clients = []
		self.client.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		res = self.con.query("select id, name from clients;")
		if res:
			for i in res:
				self.client.addItem(i[1])
				self.clients.append(i[0])
		self.date.setDate(QtCore.QDate.currentDate())
		self.btn.clicked.connect(self.accept)

	def getData(self):
		i = self.product.currentIndex()
		j = self.client.currentIndex()
		return {
			'product_id': self.products[i] if i > -1 else None,
			'client_id': self.clients[j] if j > -1 else None,
			'volume': self.volume.value(),
			'date': self.date.date().toString("yyyy.MM.dd")
		}

	def insert(self, d):
		self.con.query(
			"insert into orders values(default,:date,:volume,:client_id,:product_id)", d)


class UpdateClientOrderDialog(QDialog):
	def __init__(self, con):
		super().__init__()
		self.con = con
		uic.loadUi('./ui/cl_order_up.ui', self)
		self.products = []
		self.product.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		res = self.con.query(
			"select p.id,pt.name,pn.name from products_of_plants pop join products p on p.id = pop.product_id join product_names pn on pn.id = p.name_id join product_types pt on pt.id = p.type_id order by pt.name,pn.name;")
		if res:
			for i in res:
				self.product.addItem(f'{i[1]} "{i[2]}"')
				self.products.append(i[0])
		self.btn.clicked.connect(self.accept)

	def getData(self):
		i = self.product.currentIndex()
		d = {}
		if self.pB.isChecked():
			d['product_id'] = self.products[i] if i > -1 else None
		if self.vB.isChecked():
			d['volume'] = self.volume.value()
		if self.dB.isChecked():
			d['date'] = self.date.date().toString("yyyy.MM.dd")
		return d

	def setData(self, r):
		t = self.con.centralWidget().table.model()
		self.product.setCurrentText(
			f"{t.index(r,1).data()} \"{t.index(r,2).data()}\"")
		self.volume.setValue(t.index(r, 3).data())
		self.date.setDate(t.index(r, 4).data())

	def update(self, ind, d):
		args = []
		del d['client']
		for i in d.keys():
			a = ":"+i
			args.append("{}={}".format(i, a))
		print("update orders set {} where id = {};".format(','.join(args), ind))
		print(d)
		res = self.con.query(
			"update orders set {} where id = {};".format(','.join(args), ind), d)
		m = self.con.centralWidget().table.model()
		if res != None:
			q = QSqlQuery()
			q.prepare(m.query().lastQuery())
			q.exec()
			m.setQuery(q)
			self.con.centralWidget().tablew.select()
		self.con.centralWidget().table.clearSelection()


class UpdateClientOrderDialog2(QDialog):
	def __init__(self, con):
		super().__init__()
		self.con = con
		uic.loadUi('./ui/cl_order_up2.ui', self)
		self.products = []
		self.product.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		res = self.con.query(
			"select p.id,pt.name,pn.name from products_of_plants pop join products p on p.id = pop.product_id join product_names pn on pn.id = p.name_id join product_types pt on pt.id = p.type_id order by pt.name,pn.name;")
		if res:
			for i in res:
				self.product.addItem(f'{i[1]} "{i[2]}"')
				self.products.append(i[0])
		self.clients = []
		self.client.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		res = self.con.query("select id, name from clients;")
		if res:
			for i in res:
				self.client.addItem(i[1])
				self.clients.append(i[0])
		self.btn.clicked.connect(self.accept)

	def getData(self):
		i = self.product.currentIndex()
		j = self.client.currentIndex()
		d = {}
		if self.pB.isChecked():
			d['product_id'] = self.products[i] if i > -1 else None
		if self.cB.isChecked():
			d['client_id'] = self.clients[j] if j > -1 else None
		if self.vB.isChecked():
			d['volume'] = self.volume.value()
		if self.dB.isChecked():
			d['date'] = self.date.date().toString("yyyy.MM.dd")
		return d

	def setData(self, r):
		t = self.con.centralWidget().table.model()
		self.product.setCurrentText(
			f"{t.index(r,1).data()} \"{t.index(r,2).data()}\"")
		self.volume.setValue(t.index(r, 3).data())
		self.client.setCurrentText(t.index(r, 4).data())
		self.date.setDate(t.index(r, 5).data())

	def update(self, ind, d):
		args = []
		for i in d.keys():
			a = ":"+i
			args.append("{}={}".format(i, a))
		res = self.con.query(
			"update orders set {} where id = {};".format(','.join(args), ind), d)
		m = self.con.centralWidget().table.model()
		if res != None:
			q = QSqlQuery()
			q.prepare(m.query().lastQuery())
			q.exec()
			m.setQuery(q)
			self.con.chooseWidget.widget().select()
		self.con.centralWidget().table.clearSelection()


class TableWidget(QWidget):
	def __init__(self, con, headers, query, pars={}, sizes=[], limit=100):
		super().__init__()
		uic.loadUi('./ui/table.ui', self)
		self.limit = limit
		self.con = con
		self.headers = headers
		self.sizes = sizes
		self.query = query
		self.fquery = query + " offset :offset limit :limit;"
		self.pars = pars
		self.table.verticalHeader().setVisible(False)
		self.table.setModel(QSqlQueryModel())
		self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.table.setSelectionMode(QAbstractItemView.MultiSelection)
		self.next.clicked.connect(self.getNext)
		self.back.clicked.connect(self.getBack)
		self.first.clicked.connect(self.getFirst)
		self.last.clicked.connect(self.getLast)
		self.page.valueChanged.connect(self.select)

	def select(self):
		if self.pars:
			q = QSqlQuery()
			q.prepare(self.fquery)
			for i in self.pars.keys():
				q.bindValue(":"+i, self.pars[i])
			q.bindValue(':offset', self.limit*(self.page.value()-1))
			q.bindValue(':limit', self.limit)
			q.exec()
			self.table.model().setQuery(q)
		else:
			self.table.model().setQuery(self.query)
		for i in range(len(self.headers)):
			self.table.model().setHeaderData(
				i, QtCore.Qt.Horizontal, self.headers[i])
		for i in self.sizes:
			self.table.setColumnWidth(i[0], i[1])
		#print(QSqlQuery().lastQuery())
		self.count.setText(str(self.con.query(
			"select count(*) from ("+self.query+") as res;", self.pars).scalar()))

	def getNext(self):
		self.page.setValue(self.page.value()+1)

	def getBack(self):
		self.page.setValue(self.page.value()-1)

	def getLast(self):
		self.page.setValue(math.ceil(int(self.count.text())/self.limit))

	def getFirst(self):
		self.page.setValue(1)


class EditableTableWidget(QWidget):
	def __init__(self, con, headers, name, query, iw, ew, el, pars={}, sizes=[], limit=100):
		super().__init__()
		uic.loadUi('./ui/etable.ui', self)
		self.con = con
		self.name = name
		self.tablew = TableWidget(con, headers, query, pars, sizes, limit)
		self.table = self.tablew.table
		self.layout().addWidget(self.tablew)
		self.rmBtn.clicked.connect(self.delete)
		self.addBtn.clicked.connect(self.insert)
		self.table.doubleClicked.connect(self.update)
		self.iw = iw
		self.ew = ew
		self.el = el

	def insert(self):
		#w = AddClientOrderDialog(self.con)
		w = self.iw
		if w.exec_():
			d = w.getData()
			#d['client'] = self.tablew.pars['client']
			if self.el:
				d[self.el] = self.tablew.pars[self.el]
			w.insert(d)
			self.select()

	def delete(self):
		t = self.table
		selected = t.selectionModel().selectedRows()
		ids = []
		l = len(selected)
		m = t.model()
		if l:
			for i in range(l):
				ids.append(str(m.index(selected[i].row(), 0).data()))
			res = self.con.query("delete from {} where {}.id in ({});".format(
				self.name, self.name, ",".join(ids)))
			if res != None:
				q = QSqlQuery()
				q.prepare(m.query().lastQuery())
				q.exec()
				m.setQuery(q)
				self.select()
				t.clearSelection()

	def select(self):
		self.tablew.select()

	def update(self, item):
		#w = UpdateClientOrderDialog(self.con)
		w = self.ew
		w.setData(item.row())
		if w.exec_():
			d = w.getData()
			if d:
				if self.el:
					d[self.el] = self.tablew.pars[self.el]
				w.update(self.table.model().index(item.row(), 0).data(), d)

class ChooseWidget2(QWidget):
	def __init__(self, main, options, cols, table):
		super().__init__()
		uic.loadUi('./ui/choose2.ui', self)
		self.main = main
		for i in options:
			self.cols.addItem(i)
		self.allR.toggled.connect(self.setAll)
		self.idR.toggled.connect(self.setId)
		self.chooseR.toggled.connect(self.setCh)
		self.colR.toggled.connect(self.setCol)
		self.table = table
		self.coln = cols
		self.v = None
		self.setCh(True)
		self.sB.clicked.connect(self.select)
		self.table.page.valueChanged.connect(self.select)

	def getData(self):
		t = self.colV.text()
		if not t:
			t = None
		return (self.coln[self.cols.currentIndex()], t)

	def setAll(self, enabled):
		if enabled:
			self.v = 1
			self.table.table.clearSelection()
			self.table.table.setSelectionMode(QAbstractItemView.NoSelection)

	def setId(self, enabled):
		if enabled:
			self.v = 3
			self.table.table.clearSelection()
			self.table.table.setSelectionMode(QAbstractItemView.NoSelection)

	def setCol(self, enabled):
		if enabled:
			self.v = 4
			self.table.table.clearSelection()
			self.table.table.setSelectionMode(QAbstractItemView.NoSelection)

	def setCh(self, enabled):
		if enabled:
			self.v = 2
			self.table.table.setSelectionMode(QAbstractItemView.MultiSelection)

	def select(self):
		if self.v == 1:
			self.table.selectAll()
		elif self.v == 2:
			self.table.selectAll()
		elif self.v == 3:
			self.table.selectWhere('id', self.idV.value())
		elif self.v == 4:
			d = self.getData()
			if d:
				self.table.selectWhere(d[0], d[1])


class ChooseWidget(QWidget):
	def __init__(self, main, options, cols, table):
		super().__init__()
		uic.loadUi('./ui/choose.ui', self)
		self.main = main
		for i in options:
			self.cols.addItem(i)
		self.allR.toggled.connect(self.setAll)
		self.idR.toggled.connect(self.setId)
		self.chooseR.toggled.connect(self.setCh)
		self.colR.toggled.connect(self.setCol)
		self.table = table
		self.coln = cols
		self.v = None
		self.setCh(True)
		self.deleteB.clicked.connect(self.delete)
		self.sB.clicked.connect(self.select)
		self.table.page.valueChanged.connect(self.select)

	def getData(self):
		t = self.colV.text()
		if not t:
			t = None
		return (self.coln[self.cols.currentIndex()], t)

	def setAll(self, enabled):
		if enabled:
			self.v = 1
			self.table.table.clearSelection()
			self.table.table.setSelectionMode(QAbstractItemView.NoSelection)

	def setId(self, enabled):
		if enabled:
			self.v = 3
			self.table.table.clearSelection()
			self.table.table.setSelectionMode(QAbstractItemView.NoSelection)

	def setCol(self, enabled):
		if enabled:
			self.v = 4
			self.table.table.clearSelection()
			self.table.table.setSelectionMode(QAbstractItemView.NoSelection)

	def setCh(self, enabled):
		if enabled:
			self.v = 2
			self.table.table.setSelectionMode(QAbstractItemView.MultiSelection)

	def delete(self):
		if self.v == 1:
			self.table.truncate()
		elif self.v == 2:
			self.table.deleteSelected()
		elif self.v == 3:
			self.table.deleteWhere('id', self.idV.value())
		elif self.v == 4:
			d = self.getData()
			if d:
				self.table.deleteWhere(d[0], d[1])

	def select(self):
		if self.v == 1:
			self.table.selectAll()
		elif self.v == 2:
			self.table.selectAll()
		elif self.v == 3:
			self.table.selectWhere('id', self.idV.value())
		elif self.v == 4:
			d = self.getData()
			if d:
				self.table.selectWhere(d[0], d[1])


class TableWidget2(QWidget):
	def __init__(self, main, table, headers, query, pk, keys, orde='asc',role=None):
		super().__init__()
		uic.loadUi('./ui/table.ui', self)
		self.main = main
		self.name = table
		self.pk = pk
		self.keys = keys
		self.query = query
		self.headers = headers
		self.offset = 0
		self.limit = 1000
		self.ord = orde
		self.role = None
		self.table.verticalHeader().setVisible(False)
		self.table.setModel(QSqlQueryModel())
		self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.table.setSelectionMode(QAbstractItemView.MultiSelection)
		self.next.clicked.connect(self.getNext)
		self.back.clicked.connect(self.getBack)
		self.first.clicked.connect(self.getFirst)
		self.last.clicked.connect(self.getLast)
		self.page.valueChanged.connect(self.selectAll)

	def getNext(self):
		self.page.setValue(self.page.value()+1)

	def getBack(self):
		self.page.setValue(self.page.value()-1)

	def getLast(self):
		self.page.setValue(math.ceil(int(self.count.text())/self.limit))

	def getFirst(self):
		self.page.setValue(1)

	def select(self):
		# self.count.setText(str(self.table.model().rowCount()))
		for i in range(len(self.headers)):
			self.table.model().setHeaderData(
				i, QtCore.Qt.Horizontal, self.headers[i])

	def selectAll(self):
		self.count.setText(str(self.main.query(
			"select count(*) from ("+self.query+") as res;").scalar()))
		if self.role:
			QSqlQuery(f'set role {self.role}').exec_()
		self.table.model().setQuery(
			QSqlQuery("{} order by {} {} offset {} limit {}".format(self.query, self.pk, self.ord, self.limit*(self.page.value()-1), self.limit)))
		self.select()

	def selectWhere(self, c, v):
		sv = ":svalue"
		for i in self.keys.keys():
			if i == c:
				sv = self.keys[i][0].format("svalue")
				c = self.keys[i][1]
				break
		if self.role:
			QSqlQuery(f'set role {self.role}').exec_()
		q = QSqlQuery()
		if v == None:
			self.count.setText(str(self.main.query(
				"select count(*) from ("+self.query+"where {}.{} is NULL) as res;".format(self.name, c)).scalar()))
			q.prepare("{} where {}.{} is NULL order by {} {} offset {} limit {};".format(
				self.query, self.name, c, self.pk, self.ord, self.limit*(self.page.value()-1), self.limit))
		else:
			self.count.setText(str(self.main.query(
				"select count(*) from ("+self.query+"where {}.{}={}) as res;".format(self.name, c, sv), {'svalue': v}).scalar()))
			q.prepare("{} where {}.{}={} order by {} {} offset {} limit {}".format(
				self.query, self.name, c, sv, self.pk, self.ord, self.limit*(self.page.value()-1), self.limit))
			q.bindValue(":svalue", v)
		q.exec()
		self.table.model().setQuery(q)
		self.select()

	def deleteSelected(self):
		t = self.table
		selected = t.selectionModel().selectedRows()
		ids = []
		l = len(selected)
		m = t.model()
		if l:
			for i in range(l):
				ids.append(str(m.index(selected[i].row(), 0).data()))
			res = self.main.query("delete from {} where {} in ({});".format(
				self.name, 'id', ",".join(ids)))
			if res != None:
				q = QSqlQuery()
				q.prepare(m.query().lastQuery())
				q.bindValue(":svalue", m.query().boundValue(":svalue"))
				q.exec()
				m.setQuery(q)
				self.select()
				t.clearSelection()

	def deleteWhere(self, c, v):
		res = None
		if v == None:
			res = self.main.query("delete from {} where {} is NULL;".format(
				self.name, c), {"svalue": v})
		else:
			sv = ":svalue"
			for i in self.keys.keys():
				if i == c:
					sv = self.keys[i][0].format("svalue")
					c = self.keys[i][1]
					break
			res = self.main.query("delete from {} where {}={};".format(
				self.name, c, sv), {"svalue": v})
		if res:
			self.selectAll()

	def insert(self, d):
		args = []
		for i in d.keys():
			a = ":"+i
			for j in self.keys.keys():
				if i == j:
					a = self.keys[i][0].format(i)
					break
			args.append(a)
		res = self.main.query("insert into {}({}) values({})".format(
			self.name, ','.join(d.keys()), ','.join(args)), d)
		if res:
			self.selectAll()

	def updateWhere(self, c, v, d):
		if d:
			args = []
			for i in d.keys():
				a = ":"+i
				for j in self.keys.keys():
					if i == j:
						a = self.keys[i][0].format(i)
						i = self.keys[i][1]
						break
				args.append("{}={}".format(i, a))
			q = None
			if v == None:
				q = """update {} set {} where {} is NULL""".format(
					self.name, ','.join(args), c)
			else:
				sv = ":svalue"
				for i in self.keys.keys():
					if i == c:
						sv = self.keys[i].format("svalue")
						break
				q = """update {} set {} where {}={}""".format(
					self.name, ','.join(args), c, sv)
				d['svalue'] = v
			res = self.main.query(q, d)
			if res != None:
				self.selectAll()
		else:
			self.raiseEmpty()

	def truncate(self):
		self.main.query("delete from {} cascade;".format(self.name))
		self.selectAll()

	def raiseEmpty(self):
		QMessageBox.information(
			self.main, "Ошибка", "Ни одно поле не выбрано.", buttons=QMessageBox.Ok)


class AdminWindow(MainWindow):
	def __init__(self, con, engine):
		super().__init__(con, engine)
		self.query('set role admin;')
		QSqlQuery('set role admin;').exec_()
		ca = self.menubar.addAction("Клиенты")
		ca.triggered.connect(self.setClientsWidget)
		ma = self.menubar.addAction("Управляющие")
		ma.triggered.connect(self.setManagersWidget)
		tm = self.menubar.addMenu("Таблицы")
		ts = [
           ('Комбинаты',self.setMeatplantsWidget),
           ('Продукты комбинатов',self.setProductsOfPlantsWidget),
           ('Заказы',self.setOrdersWidget),
           ('Продукты',self.setProductsWidget),
		]
		for i in ts:
			ai = tm.addAction(i[0])
			ai.triggered.connect(i[1])
		di = tm.addAction('Справочники')
		di.triggered.connect(self.setCatalogs)
		gm = self.menubar.addMenu("Генерация")
		sg = gm.addAction('Стандартная генерация')
		sg.triggered.connect(self.standartGenerate)
		self.catalogDock = QDockWidget(self.tr("Управление"), self)
		self.catalogDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
										 QtCore.Qt.RightDockWidgetArea)
		self.catalogDock.setFeatures(QDockWidget.DockWidgetMovable)
		self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.catalogDock)
		self.catalogDock.close()
		self.chooseWidget = QDockWidget(self.tr("Выбор записей"), self)
		self.chooseWidget.setAllowedAreas(QtCore.Qt.TopDockWidgetArea |
										  QtCore.Qt.BottomDockWidgetArea)
		self.chooseWidget.setFeatures(QDockWidget.DockWidgetMovable)
		self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.chooseWidget)
		self.setManagersWidget()
		self.show()

	def addMeatplant(self):
		w = AddMeatplantDialog(self)
		if w.exec_():
			d = w.getData()
			w.insert(d)
			self.chooseWidget.widget().select()

	def updateMeatplant(self, item):
		w = UpdateMeatplantDialog(self)
		w.setData(item.row())
		if w.exec_():
			d = w.getData()
			if d:
				w.update(self.centralWidget().table.model().index(
					item.row(), 0).data(), d)

	def setMeatplantsWidget(self):
		self.clearStuff()
		self.chTitle('Комбинаты')
		t = TableWidget2(self, "meatplants", ('№', 'Название', 'Город', 'Телефон', 'Год открытия', 'Тип собственности'),
						 """select meatplants.id,meatplants.name,c.name,meatplants.phone,meatplants.year,pt.name 
						 from meatplants join cities c on c.id = meatplants.city_id join property_types pt on pt.id = meatplants.property_type_id
				""", "meatplants.name",
						 {
						  'city_id': ['(select id from cities where name = :{})', 'city_id'],
						  'property_type_id': ['(select id from property_types where name = :{})', 'property_type_id']
						  },
						 'asc','admin'
						 )
		self.setCentralWidget(t)
		ops = ['Название', 'Город', 'Телефон', 'Год открытия', 'Тип собственности']
		cols = ['name', 'city_id', 'phone', 'year', 'property_type_id']
		c = ChooseWidget(self, ops, cols, t)
		self.chooseWidget.setWidget(c)
		self.chooseWidget.show()
		c.addBtn.clicked.connect(self.addMeatplant)
		t.table.doubleClicked.connect(self.updateMeatplant)
		t.selectAll()

	def addProductOfPlant(self):
		w = AddProductOfPlantDialog(self)
		if w.exec_():
			d = w.getData()
			w.insert(d)
			self.chooseWidget.widget().select()

	def updateProductOfPlant(self, item):
		w = UpdateProductOfPlantDialog(self)
		w.setData(item.row())
		if w.exec_():
			d = w.getData()
			if d:
				w.update(self.centralWidget().table.model().index(
					item.row(), 0).data(), d)

	def setProductsOfPlantsWidget(self):
		self.clearStuff()
		self.chTitle('Продукты комбинатов')
		t = TableWidget2(self, "products_of_plants", ('№', 'Название', 'Тип', 'Комбинат', 'Цена за кг', 'Годовой объем выпуска'),
						 """select products_of_plants.id,pn.name,pt.name,m.name,products_of_plants.price_per_kg,products_of_plants.volume 
						 from products_of_plants join products p on p.id = products_of_plants.product_id join product_names pn on pn.id = p.name_id 
						 join product_types pt on pt.id = p.type_id join meatplants m on m.id = products_of_plants.meatplant_id
				""", "pn.name",
						 {
						  'meatplant_id': ['(select id from meatplants where name = :{})', 'meatplant_id'],
						  'type_id': ['any(select p.id from products p join product_types pt on pt.id = p.type_id where pt.name=:{})', 'product_id'],
						  'name_id': ['any(select p.id from products p join product_names pn on pn.id = p.name_id where pn.name=:{})', 'product_id'],
						  },
						 'asc','admin'
						 )
		self.setCentralWidget(t)
		ops = ['Название', 'Тип', 'Комбинат', 'Цена за кг', 'Годовой объем выпуска']
		cols = ['name_id', 'type_id', 'meatplant_id', 'price_per_kg', 'volume']
		c = ChooseWidget(self, ops, cols, t)
		self.chooseWidget.setWidget(c)
		self.chooseWidget.show()
		c.addBtn.clicked.connect(self.addProductOfPlant)
		t.table.doubleClicked.connect(self.updateProductOfPlant)
		t.selectAll()

	def addOrder(self):
		w = AddOrderDialog(self)
		if w.exec_():
			d = w.getData()
			w.insert(d)
			self.chooseWidget.widget().select()

	def updateOrder(self, item):
		w = UpdateOrderDialog(self)
		w.setData(item.row())
		if w.exec_():
			d = w.getData()
			if d:
				w.update(self.centralWidget().table.model().index(
					item.row(), 0).data(), d)

	def setOrdersWidget(self):
		self.clearStuff()
		self.chTitle('Заказы')
		t = TableWidget2(self, "orders", ('№', 'Название', 'Тип', 'Комбинат','Клиент','Вес', 'Дата'),
						 """select orders.id,pn.name,pt.name,m.name,c.name,orders.volume,orders.date 
			from orders join clients c on c.id = orders.client_id join products_of_plants pop on orders.product_id = pop.id join products p on pop.product_id = p.id join product_types pt on pt.id = p.type_id join product_names pn on pn.id = p.name_id
			join meatplants m on pop.meatplant_id = m.id
				""", "date",
						 {
						  'meatplant_id': ['any(select pop.id from meatplants m join products_of_plants pop on pop.meatplant_id = m.id where m.name = :{})', 'product_id'],
						  'client_id': ['(select id from clients where name = :{})', 'client_id'],
						  'type_id': ['any(select pop.id from products_of_plants pop join products p on p.id = pop.product_id join product_types pt on pt.id = p.type_id where pt.name=:{})', 'product_id'],
						  'name_id': ['any(select pop.id from products_of_plants pop join products p on p.id = pop.product_id join product_names pn on pn.id = p.name_id where pn.name=:{})', 'product_id'],
						  },
						 'desc'
						 )
		self.setCentralWidget(t)
		ops = ['Название', 'Тип', 'Комбинат','Клиент','Вес', 'Дата']
		cols = ['name_id', 'type_id', 'meatplant_id', 'сlient_id', 'volume','date']
		c = ChooseWidget(self, ops, cols, t)
		self.chooseWidget.setWidget(c)
		self.chooseWidget.show()
		c.addBtn.clicked.connect(self.addOrder)
		t.table.doubleClicked.connect(self.updateOrder)
		t.selectAll()

	def addProduct(self):
		w = AddProductDialog(self)
		if w.exec_():
			d = w.getData()
			w.insert(d)
			self.chooseWidget.widget().select()

	def updateProduct(self, item):
		w = UpdateProductDialog(self)
		w.setData(item.row())
		if w.exec_():
			d = w.getData()
			if d:
				w.update(self.centralWidget().table.model().index(
					item.row(), 0).data(), d)

	def setProductsWidget(self):
		self.clearStuff()
		self.chTitle('Продукты')
		t = TableWidget2(self, "products", ('№', 'Тип', 'Название'),
						 """select products.id,pt.name,pn.name from products join product_names pn on pn.id = products.name_id 
						 join product_types pt on pt.id = products.type_id
				""", "id",
						 {
						  'type_id': ['(select id from product_types where name = :{})','type_id'],
						  'name_id': ['(select id from product_names where name = :{})','name_id'],
						  },
						 'asc'
						 )
		self.setCentralWidget(t)
		ops = ['Тип', 'Название']
		cols = ['type_id','name_id']
		c = ChooseWidget(self, ops, cols, t)
		self.chooseWidget.setWidget(c)
		self.chooseWidget.show()
		c.addBtn.clicked.connect(self.addProduct)
		t.table.doubleClicked.connect(self.updateProduct)
		t.selectAll()

	def clearStuff(self):
		self.catalogDock.close()
		if self.catalogDock.widget():
			self.catalogDock.widget().destroy()
		self.chooseWidget.close()
		if self.chooseWidget.widget():
			self.chooseWidget.widget().destroy()

	def addClient(self):
		w = AddClientDialog(self)
		if w.exec_():
			d = w.getData()
			w.insert(d)
			self.chooseWidget.widget().select()

	def updateClient(self, item):
		w = UpdateClientDialog(self)
		w.setData(item.row())
		if w.exec_():
			d = w.getData()
			if d:
				w.update(self.centralWidget().table.model().index(
					item.row(), 0).data(), d)

	def setClientsWidget(self):
		self.clearStuff()
		self.chTitle('Клиенты')
		t = TableWidget2(self, "clients", ('№', 'Логин', 'Название', 'Город', 'Телефон', 'Адрес'),
						 """select clients.id, clients.login, clients.name, c.name, clients.phone, clients.address 
						 from clients join cities c on c.id = clients.city_id
				""", "login",
						 {
						  'city_id': ['(select id from cities where name = :{})', 'city_id']
						  },
						 'asc'
						 )
		self.setCentralWidget(t)
		ops = ['Логин', 'Название', 'Город', 'Телефон', 'Адрес']
		cols = ['login', 'name', 'city_id', 'phone', 'address']
		c = ChooseWidget(self, ops, cols, t)
		self.chooseWidget.setWidget(c)
		self.chooseWidget.show()
		c.addBtn.clicked.connect(self.addClient)
		t.table.doubleClicked.connect(self.updateClient)
		t.selectAll()

	def setManagersWidget(self):
		self.clearStuff()
		self.chTitle("Менеджеры")
		w = EditableTableWidget(self, ["№", "Мясокомбинат", "Город", "Логин"], 'meatplants_managers',
								"""select * from managers_view""",
								AddManagerDialog(
									self), UpdateManagerDialog(self),
								'', {})
		self.setCentralWidget(w)
		w.select()

	def setCatalogs(self):
		self.clearStuff()
		self.chTitle("Справочники")
		self.catalogDock.setWidget(CatDock())
		self.setCentralWidget(Catalogs(self))
		self.catalogDock.show()

	def standartGenerate(self):
		dial = LoadDialog(
			self, "Генерируются записи. Пожалуйста, подождите...", GenThread(self.con))
		dial.exec_()
		QMessageBox.information(
			self, "Сообщение", "БД заполнена новыми записями.", buttons=QMessageBox.Ok)


class ClientsWidget(QWidget):
	def __init__(self, parent):
		super().__init__()
		uic.loadUi('./ui/clients_for_manager.ui', self)
		self.parent = parent
		self.tablew = EditableTableWidget(parent, ["№", "Тип", "Название", "Вес", "Дата"], 'orders',
										  """select * from clients_orders(:client)""", AddClientOrderDialog(self.parent), UpdateClientOrderDialog(self.parent), 'client', {'client': 0})
		self.table = self.tablew.table
		self.widget.layout().addWidget(self.tablew)
		self.tree.itemClicked.connect(self.getClients)
		self.getCities()
		self.tablew.setDisabled(True)
		self.show()

	def getCities(self):
		cs = self.parent.query(
			"select distinct ci.name from cities ci join clients c on ci.id = c.city_id order by ci.name;")
		if cs:
			for c in cs:
				ti = QTreeWidgetItem([c[0]])
				self.tree.addTopLevelItem(ti)

	def getClients(self, it, col):
		if it.parent() == None:
			if it.isExpanded():
				it.takeChildren()
				it.setExpanded(False)
			else:
				cs = self.parent.query("select c.name from clients c join cities ci on ci.id = c.city_id where ci.name = :name order by c.name;",
									   {"name": it.text(0)})
				if cs:
					for c in cs:
						it.addChild(QTreeWidgetItem([c[0]]))
					it.setExpanded(True)
		else:
			cl = self.parent.query("select c.id,c.phone,c.address from clients c where c.name = :name;",
								   {"name": it.text(0)}).fetchone()
			self.client = cl[0]
			self.name.setText(it.text(0))
			self.phone.setText(cl[1])
			self.addr.setText(cl[2])
			self.tablew.setDisabled(False)
			self.tablew.tablew.pars['client'] = self.client
			self.table.model().clear()
			self.tablew.select()


class AddProductWidget(QDialog):
	def __init__(self, con):
		super().__init__()
		self.con = con
		uic.loadUi('./ui/prod_in.ui', self)
		self.btn.clicked.connect(self.accept)

	def getData(self):
		return {
			'name': self.name.text(),
			'volume': self.vol.value(),
			'price': self.price.value()
		}

	def insert(self, d):
		mi = self.con.query(
			'select meatplant_id from meatplants_managers where user_name = current_user;').scalar()
		try:
			self.con.con.execute(
				text('insert into product_names values(default,:name);'), {'name': d['name']})
		except sqla.exc.SQLAlchemyError as e:
			pass
		ni = self.con.query('select id from product_names where name=:name', {
			'name': d['name']}).scalar()
		try:
			self.con.con.execute(text('insert into products values(default,:type,:name);'), {
				'name': ni, 'type': d['type_id']})
		except sqla.exc.SQLAlchemyError as e:
			pass
		pi = self.con.query('select id from products where type_id=:type_id and name_id=:name_id', {
			'name_id': ni, 'type_id': d['type_id']}).scalar()
		self.con.query(
			"insert into products_of_plants values(default,:plant_id,:product_id,:volume,:price)", {'plant_id': mi, 'product_id': pi, 'volume': d['volume'], 'price': d['price']})


class EditProductWidget(QDialog):
	def __init__(self, con):
		super().__init__()
		self.con = con
		uic.loadUi('./ui/prod_up.ui', self)
		self.btn.clicked.connect(self.accept)

	def getData(self):
		d = {}
		if self.pB.isChecked():
			d['price_per_kg'] = self.price.value()
		if self.nB.isChecked():
			d['name'] = self.name.text()
		if self.vB.isChecked():
			d['vol'] = self.vol.value()
		return d

	def setData(self, r):
		t = self.con.centralWidget().table.model()
		self.name.setText(t.index(r, 1).data())
		self.price.setValue(t.index(r, 2).data())
		self.vol.setValue(t.index(r, 3).data())

	def update(self, ind, d):
		args = []
		pi = None
		typid = d['type_id']
		del d['type_id']
		for i in d.keys():
			if i == 'name':
				try:
					self.con.con.execute(
						text('insert into product_names values(default,:name);'), {'name': d['name']})
				except sqla.exc.SQLAlchemyError as e:
					pass
				ni = self.con.query('select id from product_names where name=:name', {
					'name': d['name']}).scalar()
				try:
					self.con.con.execute(text('insert into products values(default,:type,:name);'), {
						'name': ni, 'type': typid})
				except sqla.exc.SQLAlchemyError as e:
					pass
				pi = self.con.query('select id from products where type_id=:type_id and name_id=:name_id', {
					'name_id': ni, 'type_id': typid}).scalar()
				args.append("product_id=:product_id")
			else:
				a = ":"+i
				args.append("{}={}".format(i, a))
		d['product_id'] = pi
		res = self.con.query(
			"update products_of_plants set {} where id = {};".format(','.join(args), ind), d)
		m = self.con.centralWidget().table.model()
		if res != None:
			q = QSqlQuery()
			q.prepare(m.query().lastQuery())
			q.exec()
			m.setQuery(q)
			self.con.centralWidget().tablew.select()
		self.con.centralWidget().table.clearSelection()


class PlantProducts(QWidget):
	def __init__(self, parent):
		super().__init__()
		uic.loadUi('./ui/mproducts.ui', self)
		self.parent = parent
		self.tablew = EditableTableWidget(parent, ["№", "Название", "Цена за кг", "Годовой объем"], 'products_of_plants',
										  """select pop.id,pn.name,pop.price_per_kg,pop.volume from products_of_plants pop join products p on p.id = pop.product_id join product_names pn on pn.id = p.name_id 
			where p.type_id = :type_id
			order by pn.name asc""", AddProductWidget(self.parent), EditProductWidget(self.parent),
										  'type_id', {'type_id': 0})
		self.table = self.tablew.table
		self.layout().addWidget(self.tablew)
		self.types.itemClicked.connect(self.getProducts)
		self.getTypes()
		self.tablew.setDisabled(True)
		self.show()

	def getTypes(self):
		cs = self.parent.query("select name from product_types order by name;")
		if cs:
			for c in cs:
				self.types.addItem(c[0])

	def getProducts(self, item):
		ti = self.parent.query('select id from product_types where name = :name;', {
			'name': item.text()}).scalar()
		self.tablew.setDisabled(False)
		self.tablew.tablew.pars['type_id'] = ti
		self.table.model().clear()
		self.tablew.select()

class TableWidget6(TableWidget):
	def __init__(self,parent):
		super().__init__(parent, ['Клиент', 'Город', 'Стоимость'], 
			"""select * from clients_max_order_price_greater_than({})""")

	def select(self):
		q = QSqlQuery()
		q.prepare(self.fquery.format(self.pars['value']))
		q.bindValue(':offset', self.limit*(self.page.value()-1))
		q.bindValue(':limit', self.limit)
		q.exec()
		self.table.model().setQuery(q)
		for i in range(len(self.headers)):
			self.table.model().setHeaderData(
				i, QtCore.Qt.Horizontal, self.headers[i])
		self.count.setText(str(self.con.query(
			"select count(*) from ("+self.query.format(self.pars['value'])+") as res;").scalar()))

class ManagerWindow(MainWindow):
	def __init__(self, con, engine):
		super().__init__(con, engine)
		pa = self.menubar.addAction("Продукты")
		oa = self.menubar.addAction("Заказы")
		ca = self.menubar.addAction("Клиенты")
		pa.triggered.connect(self.setProductsWidget)
		oa.triggered.connect(self.setOrdersWidget)
		ca.triggered.connect(self.setClientsWidget)
		qm = self.menubar.addMenu("Запросы")
		queries = [
			('Клиенты', self.setClientsQuery),
			('Средние цены продуктов', self.setAvgProdTypePriceQuery),
			('Кол-во заказов', self.setOrdersCountQuery),
			('Кол-во заказов клиентов',
			 self.setClientsOrdersCountQuery),
			('Кол-во продуктов типов', self.setProdCountTypeQuery),
			('Клиенты в этом месяце', self.setClientsCurMonthQuery),
			('Постоянные клиенты в этом году',
			 self.setRegularYearClientsQuery),
			("Клиенты в городах", self.setClientsInCitiesQuery),
			('Средние размеры заказов клиента по типам', self.setAvgVolumeByTypeQuery),
			('Средняя стоимость заказа клиента', self.setAvgOrderPriceClientQuery),
			('Клиенты, сделавшие заказ более чем на',
			 self.setClientsMaxOrderPriceGreaterQuery)
		]
		for i in queries:
			q = qm.addAction(i[0])
			q.triggered.connect(i[1])
		xm = self.menubar.addMenu("Отчеты")
		queries = [
			("Кол-во продуктов каждого типа и всего", self.genTypeCountAndAllReport)
		]
		for i in queries:
			q = xm.addAction(i[0])
			q.triggered.connect(i[1])
		dm = self.menubar.addMenu("Диаграммы")
		queries = [
			("Средние цены типов продуктов", self.setAverageTypePriceDiagram)
		]
		for i in queries:
			q = dm.addAction(i[0])
			q.triggered.connect(i[1])
		self.chooseWidget = QDockWidget(self.tr("Выбор записей"), self)
		self.chooseWidget.setAllowedAreas(QtCore.Qt.TopDockWidgetArea |
										  QtCore.Qt.BottomDockWidgetArea)
		self.chooseWidget.setFeatures(QDockWidget.DockWidgetMovable)
		self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.chooseWidget)
		self.qparWidget = QDockWidget(self.tr("Выбор параметров"), self)
		self.qparWidget.setAllowedAreas(QtCore.Qt.TopDockWidgetArea |
										QtCore.Qt.BottomDockWidgetArea)
		self.qparWidget.setFeatures(QDockWidget.DockWidgetMovable)
		self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.qparWidget)
		self.setOrdersWidget()
		self.show()

	def setAvgVolumeByTypeQuery(self):
		self.clearStuff()
		self.chTitle('Средние размеры заказов клиента по типам')
		w = TableWidget(self, ['Тип', 'Объем'],
						"""select * from avg_volume_by_type(:value)""")
		w.table.model().clear()
		self.setCentralWidget(w)
		d = lineDock(w, 'Клиент')
		self.qparWidget.setWidget(d)
		self.qparWidget.show()

	def setAvgOrderPriceClientQuery(self):
		self.clearStuff()
		self.chTitle('Средняя стоимость заказа клиента')
		w = TableWidget(self, ['Клиент', 'Стоимость'],
						"""select * from avg_order_price_for_clients(:value)""")
		w.table.model().clear()
		self.setCentralWidget(w)
		d = lineDock(w, 'Клиент')
		self.qparWidget.setWidget(d)
		self.qparWidget.show()

	def setClientsMaxOrderPriceGreaterQuery2(self):
		self.clearStuff()
		self.chTitle('Клиенты, сделавшие заказ более чем на')
		w = TableWidget(self, ['Клиент', 'Город', 'Стоимость'],
						"""select * from clients_max_order_price_greater_than(:value)""")
		w.table.model().clear()
		self.setCentralWidget(w)
		d = doubleValueDock2(w)
		self.qparWidget.setWidget(d)
		self.qparWidget.show()

	def setClientsMaxOrderPriceGreaterQuery(self):
		self.clearStuff()
		self.chTitle('Клиенты, сделавшие заказ более чем на')
		w = TableWidget6(self)
		w.table.model().clear()
		self.setCentralWidget(w)
		d = doubleValueDock2(w)
		self.qparWidget.setWidget(d)
		self.qparWidget.show()

	def setClientsMaxOrderPriceGreaterQuery3(self):
		self.clearStuff()
		self.chTitle('Клиенты, сделавшие заказ более чем на')
		w = TableWidget(self, ['Клиент', 'Город', 'Стоимость'],
						"""select * from clients_max_order_price_greater_than(6.2)""")
		w.table.model().clear()
		self.setCentralWidget(w)
		w.select()

	def prepareDiagram(self):
		cn = Canvas(self)
		self.setCentralWidget(cn)
		QSqlQueryModel().clear()
		plt.clf()
		return cn

	def setAverageTypePriceDiagram(self):
		self.clearStuff()
		self.chTitle("Средние цены типов продуктов")
		cn = self.prepareDiagram()
		resp = self.query("""
			   select * from avg_prod_type_price;
		""")
		types = []
		values = []
		for i in resp:
			types.append(i[0])
			values.append(i[1])
		if types:
			fig = cn.figure
			y_pos = [i for i in range(len(types))]
			plt.bar(y_pos, values, align='center', alpha=0.5)
			plt.xticks(y_pos, types, rotation='82')
			plt.ylabel('Цена')
			plt.title('Средние цены типов продуктов')
			fig.tight_layout()
			cn.draw()

	def genTypeCountAndAllReport(self):
		fn = QFileDialog.getSaveFileName(self, "Сохранить отчет", os.path.join(
			os.getcwd(), "types_count.xlsx"), "Таблицы Excel (*.xlsx)")
		if fn and fn[1]:
			try:
				wb = xlsxwriter.Workbook(fn[0])
				resp = self.query(
					"select * from prod_count_per_type_and_all;",)
				thr = ReportThread(wb, resp, ("Тип", 'Кол-во'), (20, 20))
				dial = LoadDialog(
					self, "Отчет сохраняется. Пожалуйста, подождите...", thr)
				dial.exec_()
				wb.close()
				QMessageBox.information(
					self, "Сообщение", "Отчет сохранен.", buttons=QMessageBox.Ok)
			except:
				QMessageBox.critical(
					self, "Ошибка", "Невозможно открыть файл.", buttons=QMessageBox.Ok)

	def setProductsWidget(self):
		self.clearStuff()
		self.chTitle('Продукты')
		self.setCentralWidget(PlantProducts(self))

	def addOrder(self):
		w = AddClientOrderDialog2(self)
		if w.exec_():
			d = w.getData()
			w.insert(d)
			self.chooseWidget.widget().select()

	def updateOrder(self, item):
		w = UpdateClientOrderDialog2(self)
		w.setData(item.row())
		if w.exec_():
			d = w.getData()
			if d:
				w.update(self.centralWidget().table.model().index(
					item.row(), 0).data(), d)

	def clearStuff(self):
		if self.chooseWidget:
			self.chooseWidget.close()
			if self.chooseWidget.widget():
				self.chooseWidget.widget().destroy()
		if self.qparWidget:
			self.qparWidget.close()
			if self.qparWidget.widget():
				self.qparWidget.widget().destroy()
		plt.clf()

	def setOrdersWidget(self):
		self.clearStuff()
		self.chTitle('Заказы')
		t = TableWidget2(self, "orders", ('№', 'Тип', 'Название', 'Вес', 'Клиент', 'Дата'),
						 """select orders.id,pt.name,pn.name,orders.volume,c.name,orders.date 
			from orders join clients c on c.id = orders.client_id join products_of_plants pop on orders.product_id = pop.id join products p on pop.product_id = p.id join product_types pt on pt.id = p.type_id join product_names pn on pn.id = p.name_id 
				""", "date",
						 {'type_id': ['any(select pop.id from products_of_plants pop join products p on p.id = pop.product_id join product_types pt on pt.id = p.type_id where pt.name=:{})', 'product_id'],
						  'name_id': ['any(select pop.id from products_of_plants pop join products p on p.id = pop.product_id join product_names pn on pn.id = p.name_id where pn.name=:{})', 'product_id'],
						  'client_id': ['(select id from clients where name = :{})', 'client_id']
						  },
						 'desc'
						 )
		self.setCentralWidget(t)
		ops = ['Тип', 'Название', 'Вес', 'Клиент', 'Дата']
		cols = ['type_id', 'name_id', 'volume', 'client_id', 'date']
		c = ChooseWidget(self, ops, cols, t)
		self.chooseWidget.setWidget(c)
		self.chooseWidget.show()
		c.addBtn.clicked.connect(self.addOrder)
		t.table.doubleClicked.connect(self.updateOrder)
		t.selectAll()

	def setClientsWidget(self):
		self.clearStuff()
		self.chTitle('Клиенты')
		w = ClientsWidget(self)
		self.setCentralWidget(w)

	def setClientsInCitiesQuery(self):
		self.clearStuff()
		self.chTitle('Клиенты в городах')
		w = TableWidget(self, ['Город', 'Клиент', 'Номер телефона'],
						"""select * from clients_in_cities""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def setClientsQuery(self):
		self.clearStuff()
		self.chTitle('Клиенты')
		w = TableWidget(self, ['№', 'Имя', 'Город', 'Телефон',
							   'Адрес'], """select * from clients_view""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def setAvgProdTypePriceQuery(self):
		self.clearStuff()
		self.chTitle('Средние цены продуктов')
		w = TableWidget(self, ['Тип', 'Цена'],
						"""select * from avg_prod_type_price""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def setOrdersCountQuery(self):
		self.clearStuff()
		self.chTitle('Кол-во заказов')
		w = TableWidget(self, ['Всего', 'За текущий месяц'],
						"""select * from orders_count_all_and_cur_month""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def setClientsOrdersCountQuery(self):
		self.clearStuff()
		self.chTitle('Кол-во заказов клиентов')
		w = TableWidget(self, ['Клиент', 'Кол-во'],
						"""select * from clients_orders_count""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def setProdCountTypeQuery(self):
		self.clearStuff()
		self.chTitle('Кол-во продуктов типов')
		w = TableWidget(self, ['Тип', 'Кол-во'],
						"""select * from prod_count_per_type_and_all""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def setClientsCurMonthQuery(self):
		self.clearStuff()
		self.chTitle('Клиенты в этом месяце')
		w = TableWidget(self, ['№', 'Имя', 'Город', 'Телефон',
							   'Адрес'], """select * from client_cur_month""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def setRegularYearClientsQuery(self):
		self.clearStuff()
		self.chTitle('Постоянные клиенты в этом году')
		w = TableWidget(self, ['Клиент', 'Постоянный?'],
						"""select * from regular_cur_year_clients""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

class ClientProducts(QWidget):
	def __init__(self, parent):
		super().__init__()
		uic.loadUi('./ui/client_products.ui', self)
		self.parent = parent
		self.tablew = TableWidget(parent, ["№", 'Тип', "Название", "Цена за кг", "Годовой объем"],
			"""select * from products_of_choosed_plant(:meatplant)""", {'meatplant': 0})
		self.table = self.tablew.table
		self.widget.layout().addWidget(self.tablew)
		self.tree.itemClicked.connect(self.getProducts)
		self.getCities()
		self.tablew.setDisabled(True)
		self.show()

	def getCities(self):
		cs = self.parent.query(
			"select distinct ci.name from cities ci join meatplants m on ci.id = m.city_id order by ci.name;")
		if cs:
			for c in cs:
				ti = QTreeWidgetItem([c[0]])
				self.tree.addTopLevelItem(ti)

	def getProducts(self, it, col):
		if it.parent() == None:
			if it.isExpanded():
				it.takeChildren()
				it.setExpanded(False)
			else:
				cs = self.parent.query("select m.name from meatplants m join cities ci on ci.id = m.city_id where ci.name = :name order by m.name;",
									   {"name": it.text(0)})
				if cs:
					for c in cs:
						it.addChild(QTreeWidgetItem([c[0]]))
					it.setExpanded(True)
		else:
			cl = self.parent.query("select m.id,m.phone,m.year,pt.name from meatplants m join property_types pt on pt.id = m.property_type_id where m.name = :name;",
								   {"name": it.text(0)}).fetchone()
			self.plant = cl[0]
			self.phone.setText(cl[1])
			self.year.setText(str(cl[2]))
			self.proptype.setText(cl[3])
			self.tablew.setDisabled(False)
			self.tablew.pars['meatplant'] = self.plant
			self.table.model().clear()
			self.tablew.select()

class ClientWindow(MainWindow):
	def __init__(self, con, engine):
		super().__init__(con, engine)
		pa = self.menubar.addAction("Продукты")
		oa = self.menubar.addAction("Заказы")
		pa.triggered.connect(self.setProductsWidget)
		oa.triggered.connect(self.setOrdersWidget)
		qm = self.menubar.addMenu("Запросы")
		queries = [
			('Заказы между датами',self.setOrdersBetweenDatesQuery),
			('Комбинаты открытые после указанного года',self.setPlantsAfterYearQuery),
			('Комбинаты',self.setMeatplantsQuery),
			('Комбинаты по типам собственности',self.setPlantsByPropTypeQuery),
			('Комбинаты по городам',self.setPlantsInCitiesQuery),
			('Комбинаты, чьи объемы производства превышают указанный',self.setPlantsVolumeGreaterQuery),
			('Продукты, указанного типа, с ценой выше средней',self.setProductsPriceGreaterAvgQuery),
			('Города без комбинатов',self.setCitiesWithoutPlantsQuery)
		]
		for i in queries:
			q = qm.addAction(i[0])
			q.triggered.connect(i[1])
		self.chooseWidget = QDockWidget(self.tr("Выбор записей"), self)
		self.chooseWidget.setAllowedAreas(QtCore.Qt.TopDockWidgetArea |
										  QtCore.Qt.BottomDockWidgetArea)
		self.chooseWidget.setFeatures(QDockWidget.DockWidgetMovable)
		self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.chooseWidget)
		self.qparWidget = QDockWidget(self.tr("Выбор параметров"), self)
		self.qparWidget.setAllowedAreas(QtCore.Qt.TopDockWidgetArea |
										QtCore.Qt.BottomDockWidgetArea)
		self.qparWidget.setFeatures(QDockWidget.DockWidgetMovable)
		self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.qparWidget)
		self.setProductsWidget()
		self.show()

	def setOrdersBetweenDatesQuery(self):
		self.clearStuff()
		self.chTitle('Заказы между датами')
		w = TableWidget(self, ['№','Название','Тип', 'Комбинат','Город','Объем','Дата'],
						"""select * from orders_between_dates(:date1,:date2)""")
		w.table.model().clear()
		self.setCentralWidget(w)
		d = twoDatesDock(w)
		self.qparWidget.setWidget(d)
		self.qparWidget.show()

	def setPlantsAfterYearQuery(self):
		self.clearStuff()
		self.chTitle('Комбинаты открытые после указанного года')
		w = TableWidget(self, ['№','Название','Город', 'Год','Тип собственности','Телефон'],
						"""select * from plants_opened_after_year(:value)""")
		w.table.model().clear()
		self.setCentralWidget(w)
		d = oneValueDock(w,'Год')
		self.qparWidget.setWidget(d)
		self.qparWidget.show()

	def setMeatplantsQuery(self):
		self.clearStuff()
		self.chTitle('Комбинаты')
		w = TableWidget(self, ['№','Название','Город', 'Год','Телефон','Тип собственности'],
						"""select * from meatplants_view""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def setPlantsByPropTypeQuery(self):
		self.clearStuff()
		self.chTitle('Комбинаты по типам собственности')
		w = TableWidget(self, ['№','Тип собственности','Название','Город'],
						"""select * from meatplants_by_prop_type""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def setPlantsInCitiesQuery(self):
		self.clearStuff()
		self.chTitle('Комбинаты по городам')
		w = TableWidget(self, ['Название','Город'],
						"""select * from meatplants_in_cities""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def setPlantsVolumeGreaterQuery(self):
		self.clearStuff()
		self.chTitle('Комбинаты, чьи объемы производства превышают указанный')
		w = TableWidget(self, ['Название','Объем'],
						"""select * from meatplants_volume_greater_than(:comb1,:comb2,:vol)""")
		w.table.model().clear()
		self.setCentralWidget(w)
		d = specDock1(w)
		self.qparWidget.setWidget(d)
		self.qparWidget.show()

	def setProductsPriceGreaterAvgQuery(self):
		self.clearStuff()
		self.chTitle('Продукты, указанного типа, с ценой выше средней')
		w = TableWidget(self, ['Название','Стоимость','Комбинат','Город'],
						"""select * from products_price_greater_avg(:value)""")
		w.table.model().clear()
		self.setCentralWidget(w)
		d = specDock2(w)
		self.qparWidget.setWidget(d)
		self.qparWidget.show()

	def setCitiesWithoutPlantsQuery(self):
		self.clearStuff()
		self.chTitle('Города без комбинатов')
		w = TableWidget(self, ['Город'],
						"""select * from cities_without_meatplants""")
		w.table.model().clear()
		w.select()
		self.setCentralWidget(w)

	def clearStuff(self):
		if self.chooseWidget:
			self.chooseWidget.close()
			if self.chooseWidget.widget():
				self.chooseWidget.widget().destroy()
		if self.qparWidget:
			self.qparWidget.close()
			if self.qparWidget.widget():
				self.qparWidget.widget().destroy()

	def setProductsWidget(self):
		self.clearStuff()
		self.chTitle('Продукты')
		self.setCentralWidget(ClientProducts(self))

	def setOrdersWidget(self):
		self.clearStuff()
		self.chTitle('Заказы')
		t = TableWidget2(self, "orders", ('№', 'Тип', 'Название', 'Комбинат', 'Объем', 'Дата'),
						 """select orders.id,pt.name,pn.name,m.name,orders.volume,orders.date 
			from orders join products_of_plants pop on orders.product_id = pop.id join meatplants m on m.id = pop.meatplant_id join products p on pop.product_id = p.id join product_types pt on pt.id = p.type_id join product_names pn on pn.id = p.name_id 
				""", "date",
						 {'type_id': ['any(select pop.id from products_of_plants pop join products p on p.id = pop.product_id join product_types pt on pt.id = p.type_id where pt.name=:{})', 'product_id'],
						  'name_id': ['any(select pop.id from products_of_plants pop join products p on p.id = pop.product_id join product_names pn on pn.id = p.name_id where pn.name=:{})', 'product_id'],
						  'meatplant_id': ['any(select pop.id from meatplants m join products_of_plants pop on pop.meatplant_id = m.id where m.name = :{})', 'product_id']
						  },
						 'desc'
						 )
		self.setCentralWidget(t)
		ops = ['Тип', 'Название', 'Комбинат', 'Объем', 'Дата']
		cols = ['type_id', 'name_id', 'meatplant_id', 'volume', 'date']
		c = ChooseWidget2(self, ops, cols, t)
		self.chooseWidget.setWidget(c)
		self.chooseWidget.show()
		t.selectAll()


class AuthorizationDialog(QDialog):
	def __init__(self):
		super().__init__()
		uic.loadUi('./ui/auth.ui', self)
		self.loginB.clicked.connect(self.auth)
		self.password.setEchoMode(QLineEdit.Password)
		self.logged = False
		self.show()

	def auth(self):
		try:
			global engine, con
			engine = sqla.create_engine('postgresql://{}:{}@{}:{}/{}'.format(
				self.login.text(), self.password.text(),
				DB_HOST, str(DB_PORT), DB_NAME))
			con = engine.connect()
			db = QSqlDatabase.addDatabase("QPSQL")
			db.setHostName(DB_HOST)
			db.setPort(DB_PORT)
			db.setDatabaseName(DB_NAME)
			db.setUserName(self.login.text())
			db.setPassword(self.password.text())
			self.logged = True
			if not db.open():
				self.logged = False
		except Exception as e:
			self.logged = False
		self.accept()

	def getRole(self):
		global con
		if con.execute("select pg_has_role('admin', 'MEMBER');").scalar():
			return 0
		elif con.execute("select pg_has_role('manager', 'MEMBER');").scalar():
			return 1
		elif con.execute("select pg_has_role('client', 'MEMBER');").scalar():
			return 2
		else:
			return None


if __name__ == '__main__':
	app = QApplication(sys.argv)
	authd = AuthorizationDialog()
	if authd.exec_():
		if authd.logged:
			try:
				r = authd.getRole()
				if r == 0:
					w = AdminWindow(con, engine)
					sys.exit(app.exec_())
				elif r == 1:
					w = ManagerWindow(con, engine)
					sys.exit(app.exec_())
				elif r == 2:
					w = ClientWindow(con, engine)
					sys.exit(app.exec_())
				else:
					QMessageBox.critical(
						None, 'Ошибка', 'Неизвестный тип пользователя.', buttons=QMessageBox.Ok)
			except Exception as e:
				QMessageBox.critical(
					None, 'Ошибка', 'Произошла ошибка авторизации.', buttons=QMessageBox.Ok)
				QMessageBox.critical(
					None, 'Ошибка', e._message(), buttons=QMessageBox.Ok)
		else:
			QMessageBox.critical(
				None, 'Ошибка', 'Произошла ошибка авторизации.', buttons=QMessageBox.Ok)
