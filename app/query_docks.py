from PyQt5.QtWidgets import QMessageBox, QWidget, QAbstractItemView
from PyQt5 import QtGui, QtCore
from PyQt5 import uic
from ui import (reqdock3,reqdock6,reqdock1,reqdock12
	)

class queryDockWidget(QWidget):
    def __init__(self, t):
        super().__init__()
        self.table=t
        self.table.setDisabled(True)

    def prepare(self):
        self.btn.clicked.connect(self.query)

    def query(self):
        self.table.pars.update(self.getPars())
        self.table.setDisabled(False)
        self.table.select()

class specDock1(queryDockWidget):
    def __init__(self, t):
        super().__init__(t)
        uic.loadUi('./ui/reqdock13.ui',self)
        self.prepare()
        res = t.con.query(
            "select name from cities;")
        if res:
            for i in res:
                self.comb1.addItem(i[0])
        res = t.con.query(
            "select name from product_types;")
        if res:
            for i in res:
                self.comb2.addItem(i[0])

    def getPars(self):
    	return {'comb1':str(self.comb1.currentText()),'comb2':str(self.comb1.currentText()),'vol':self.vol.value()}

class specDock2(queryDockWidget):
    def __init__(self, t):
        super().__init__(t)
        uic.loadUi('./ui/reqdock14.ui',self)
        self.prepare()
        res = t.con.query(
            "select name from product_types;")
        if res:
            for i in res:
                self.value.addItem(i[0])

    def getPars(self):
    	return {'value':self.table.con.query('select id from product_types where name = :name;',{'name':self.value.currentText()}).scalar()}

class twoDatesDock(queryDockWidget, reqdock3.Ui_Form):
    def __init__(self, t):
        super().__init__(t)
        self.setupUi(self)
        self.prepare()
        self.date2.setDate(QtCore.QDate.currentDate())

    def getPars(self):
        return {'date1': self.date1.date().toString("yyyy.MM.dd"), 'date2': self.date2.date().toString("yyyy.MM.dd")}

class lineDock(queryDockWidget, reqdock6.Ui_Form):
    def __init__(self, t, l):
        super().__init__(t)
        self.setupUi(self)
        self.label.setText(l)
        self.prepare()

    def getPars(self):
        return {"value":self.line.text().strip()}

class oneValueDock(queryDockWidget, reqdock1.Ui_Form):
    def __init__(self, t, l):
        super().__init__(t)
        self.setupUi(self)
        self.label.setText(l)
        self.prepare()

    def getPars(self):
        return {'value': self.par.value()}

class doubleValueDock(queryDockWidget, reqdock12.Ui_Form):
    def __init__(self, t, l):
        super().__init__(t)
        self.setupUi(self)
        self.label.setText(l)
        self.prepare()

    def getPars(self):
        return {'value': self.par.value()}

class doubleValueDock2(queryDockWidget):
    def __init__(self, t):
        super().__init__(t)
        uic.loadUi('./ui/reqdock17.ui',self)
        self.prepare()

    def getPars(self):
        return {'value': self.par.value()}
