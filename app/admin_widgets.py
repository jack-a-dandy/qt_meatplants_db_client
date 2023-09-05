from PyQt5.QtWidgets import QLineEdit,QDialog, QWidget, QMessageBox, QAbstractItemView, QTableWidget, QTableWidgetItem
from PyQt5 import QtGui, QtCore, uic
import sqlalchemy as sqla
from PyQt5.QtSql import QSqlRelationalTableModel, QSqlRelation, QSqlTableModel, QSqlRecord, QSqlQueryModel, QSqlQuery
from ui import (cat_dock)

class AddProductDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/addprod.ui', self)
        self.name.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.typ.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select name from product_names;")
        if res:
            for i in res:
                self.name.addItem(i[0])
        res = self.con.query(
            "select name from product_types;")
        if res:
            for i in res:
                self.typ.addItem(i[0])
        self.btn.clicked.connect(self.accept)

    def getData(self):
        return {
            'type_id': self.con.query('select id from products_types where name=:name',
                {'name':self.typ.currentText()}).scalar(),
            'name_id': self.con.query('select id from products_names where name=:name',
                {'name':self.name.currentText()}).scalar()
            
        }

    def insert(self, d):
        self.con.query('insert into products values(default,:type_id,:name_id);',d)

class UpdateProductDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/udpprod.ui', self)
        self.name.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.typ.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select name from product_names;")
        if res:
            for i in res:
                self.name.addItem(i[0])
        res = self.con.query(
            "select name from product_types;")
        if res:
            for i in res:
                self.typ.addItem(i[0])
        self.btn.clicked.connect(self.accept)

    def getData(self):
        d = {}
        if self.tB.isChecked():
            d['type_id']=self.con.query('select id from product_types where name=:name',
                {'name':self.typ.currentText()}).scalar()
        if self.nB.isChecked():
            d['name_id']=self.con.query('select id from product_names where name=:name',
                {'name':self.name.currentText()}).scalar()
        return d

    def setData(self, r):
        t = self.con.centralWidget().table.model()
        self.typ.setCurrentText(t.index(r, 1).data())
        self.name.setCurrentText(t.index(r, 2).data())

    def update(self, ind, d):
        args=[]
        for i in d.keys():
            a = ":"+i
            args.append("{}={}".format(i, a))
        res = self.con.query(
            "update products set {} where id = {};".format(','.join(args), ind), d)
        m = self.con.centralWidget().table.model()
        if res != None:
            q = QSqlQuery()
            q.prepare(m.query().lastQuery())
            q.exec()
            m.setQuery(q)
            self.con.chooseWidget.widget().select()
        self.con.centralWidget().table.clearSelection()

class AddOrderDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/addord.ui', self)
        self.product.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.plant.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.client.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select name from meatplants;")
        if res:
            for i in res:
                self.plant.addItem(i[0])
        res = self.con.query(
            "select name from clients;")
        if res:
            for i in res:
                self.client.addItem(i[0])
        self.products=[]
        self.plant.currentIndexChanged.connect(self.plantChanged)
        self.getProducts()
        self.btn.clicked.connect(self.accept)

    def getProducts(self):
        res = self.con.query(
            """select pop.id,pn.name,pt.name from products p join product_types pt on pt.id = p.type_id 
            join product_names pn on pn.id = p.name_id 
            join products_of_plants pop on pop.product_id = p.id join meatplants m 
            on m.id = pop.meatplant_id where m.name = :name;""",{'name':self.plant.currentText()})
        if res:
            self.products=[]
            for i in res:
                self.product.addItem(f'{i[2]} {i[1]}')
                self.products.append(i[0])

    def plantChanged(self):
        self.getProducts()

    def getData(self):
        i = self.product.currentIndex()
        return {
            'product_id': self.products[i] if i > -1 else None,
            'client_id': self.con.query('select id from clients where name=:name',
                {'name':self.client.currentText()}).scalar(),
            'volume':self.volume.value(),
            'date':self.date.date().toString("yyyy.MM.dd")
            
        }

    def insert(self, d):
        self.con.query('insert into orders values(default,:date,:volume,:client_id,:product_id);',d)

class UpdateOrderDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/udpord.ui', self)
        self.product.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.plant.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.client.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select name from meatplants;")
        if res:
            for i in res:
                self.plant.addItem(i[0])
        res = self.con.query(
            "select name from clients;")
        if res:
            for i in res:
                self.client.addItem(i[0])
        self.products=[]
        self.plant.currentIndexChanged.connect(self.plantChanged)
        self.getProducts()
        self.btn.clicked.connect(self.accept)
        self.plant.setDisabled(True)
        self.pB.stateChanged.connect(self.procName)

    def procName(self, st):
        if st == QtCore.Qt.Checked:
            self.plant.setDisabled(False)
        else:
            self.plant.setDisabled(True)

    def getProducts(self):
        res = self.con.query(
            """select pop.id,pn.name,pt.name from products p join product_types pt on pt.id = p.type_id 
            join product_names pn on pn.id = p.name_id 
            join products_of_plants pop on pop.product_id = p.id join meatplants m 
            on m.id = pop.meatplant_id where m.name = :name;""",{'name':self.plant.currentText()})
        if res:
            self.products=[]
            for i in res:
                self.product.addItem(f'{i[2]} {i[1]}')
                self.products.append(i[0])

    def plantChanged(self):
        self.getProducts()

    def getData(self):
        d = {}
        if self.pB.isChecked():
            i = self.product.currentIndex()
            d['product_id'] = self.products[i] if i > -1 else None 
        if self.dB.isChecked():
            d['date']=self.date.date().toString("yyyy.MM.dd")
        if self.vB.isChecked():
            d['volume']=self.volume.value()
        if self.cB.isChecked():
            d['client_id']=self.con.query('select id from clients where name=:name',
                {'name':self.client.currentText()}).scalar()
        return d

    def setData(self, r):
        t = self.con.centralWidget().table.model()
        self.plant.setCurrentText(t.index(r, 3).data())
        self.product.setCurrentText(f'{t.index(r, 2).data()} {t.index(r, 1).data()}')
        self.client.setCurrentText(t.index(r, 4).data())
        self.volume.setValue(t.index(r, 5).data())
        self.date.setDate(t.index(r, 6).data())

    def update(self, ind, d):
        args=[]
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

class AddProductOfPlantDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/addprodp.ui', self)
        self.product.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.plant.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select name from meatplants;")
        if res:
            for i in res:
                self.plant.addItem(i[0])
        self.products=[]
        res = self.con.query(
            "select p.id,pn.name,pt.name from products p join product_types pt on pt.id = p.type_id join product_names pn on pn.id = p.name_id;")
        if res:
            for i in res:
                self.product.addItem(f'{i[2]} {i[1]}')
                self.products.append(i[0])
        self.btn.clicked.connect(self.accept)

    def getData(self):
        i = self.product.currentIndex()
        return {
            'product_id': self.products[i] if i > -1 else None,
            'meatplant_id': self.con.query('select id from meatplants where name=:name',
                {'name':self.plant.currentText()}).scalar(),
            'volume':self.vol.value(),
            'price_per_kg':self.price.value()
            
        }

    def insert(self, d):
        self.con.query('insert into products_of_plants values(default,:meatplant_id,:product_id,:volume,:price_per_kg);',d)


class UpdateProductOfPlantDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/udpprodp.ui', self)
        self.product.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.plant.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select name from meatplants;")
        if res:
            for i in res:
                self.plant.addItem(i[0])
        self.products=[]
        res = self.con.query(
            "select p.id,pn.name,pt.name from products p join product_types pt on pt.id = p.type_id join product_names pn on pn.id = p.name_id;")
        if res:
            for i in res:
                self.product.addItem(f'{i[2]} {i[1]}')
                self.products.append(i[0])
        self.btn.clicked.connect(self.accept)

    def getData(self):
        d = {}
        if self.pB.isChecked():
            d['price_per_kg'] = self.price.value()
        if self.prB.isChecked():
            i = self.product.currentIndex()
            d['product_id'] = self.products[i] if i > -1 else None
        if self.cB.isChecked():
            d['meatplant_id']=self.con.query('select id from meatplants where name=:name',
                {'name':self.plant.currentText()}).scalar()
        if self.vB.isChecked():
            d['volume']=self.vol.value()
        return d

    def setData(self, r):
        t = self.con.centralWidget().table.model()
        self.product.setCurrentText(f'{t.index(r, 2).data()} {t.index(r, 1).data()}')
        self.plant.setCurrentText(t.index(r, 3).data())
        self.price.setValue(t.index(r, 4).data())
        self.vol.setValue(t.index(r, 5).data())

    def update(self, ind, d):
        args=[]
        for i in d.keys():
            a = ":"+i
            args.append("{}={}".format(i, a))
        res = self.con.query(
            "update products_of_plants set {} where id = {};".format(','.join(args), ind), d)
        m = self.con.centralWidget().table.model()
        if res != None:
            q = QSqlQuery()
            q.prepare(m.query().lastQuery())
            q.exec()
            m.setQuery(q)
            self.con.chooseWidget.widget().select()
        self.con.centralWidget().table.clearSelection()

class AddMeatplantDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/addmeatplant.ui', self)
        self.propt.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.city.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select name from cities;")
        if res:
            for i in res:
                self.city.addItem(i[0])
        res = self.con.query(
            "select name from property_types;")
        if res:
            for i in res:
                self.propt.addItem(i[0])
        self.btn.clicked.connect(self.accept)

    def getData(self):
        return {
            'name': self.name.text(),
            'phone': self.phone.text(),
            'year': self.year.value(),
            'property_type_id': self.con.query('select id from property_types where name=:name',
                {'name':self.propt.currentText()}).scalar(),
            'city_id': self.con.query('select id from cities where name=:name',
                {'name':self.city.currentText()}).scalar()
            
        }

    def insert(self, d):
        self.con.query('insert into meatplants values(default,:name,:city_id,:phone,:year,:property_type_id);',d)

class UpdateMeatplantDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/updmeatplant.ui', self)
        self.propt.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.city.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select name from cities;")
        if res:
            for i in res:
                self.city.addItem(i[0])
        res = self.con.query(
            "select name from property_types;")
        if res:
            for i in res:
                self.propt.addItem(i[0])
        self.btn.clicked.connect(self.accept)

    def getData(self):
        d = {}
        if self.phB.isChecked():
            d['phone'] = self.phone.text()
        if self.nB.isChecked():
            d['name'] = self.name.text()
        if self.pB.isChecked():
            d['property_type_id'] = self.con.query('select id from property_types where name=:name',
                {'name':self.propt.currentText()}).scalar()
        if self.cB.isChecked():
            d['city_id']=self.con.query('select id from cities where name=:name',
                {'name':self.city.currentText()}).scalar()
        if self.yB.isChecked():
            d['year']=self.year.value()
        return d

    def setData(self, r):
        t = self.con.centralWidget().table.model()
        self.name.setText(t.index(r, 1).data())
        self.city.setCurrentText(t.index(r, 2).data())
        self.phone.setText(t.index(r, 3).data())
        self.year.setValue(t.index(r, 4).data())
        self.propt.setCurrentText(t.index(r, 5).data())

    def update(self, ind, d):
        args=[]
        for i in d.keys():
            a = ":"+i
            args.append("{}={}".format(i, a))
        res = self.con.query(
            "update meatplants set {} where id = {};".format(','.join(args), ind), d)
        m = self.con.centralWidget().table.model()
        if res != None:
            q = QSqlQuery()
            q.prepare(m.query().lastQuery())
            q.exec()
            m.setQuery(q)
            self.con.chooseWidget.widget().select()
        self.con.centralWidget().table.clearSelection()

class AddManagerDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/addmanager.ui', self)
        self.plants = []
        self.plant.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select id,name from meatplants;")
        if res:
            for i in res:
                self.plant.addItem(i[1])
                self.plants.append(i[0])
        self.btn.clicked.connect(self.accept)
        self.passw.setEchoMode(QLineEdit.Password)

    def getData(self):
        i = self.plant.currentIndex()
        return {
            'user_name': self.name.text(),
            'meatplant_id': self.plants[i] if i > -1 else None,
            'passw': self.passw.text()
        }

    def insert(self, d):
        with self.con.con.begin():
            self.con.query(f"set role admin; create user {d['user_name']} with password '{d['passw']}' in role manager;")
            self.con.query('insert into meatplants_managers values(default,:meatplant_id,:user_name);',d)

class UpdateManagerDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/updmanager.ui', self)
        self.plants = []
        self.plant.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select id,name from meatplants;")
        if res:
            for i in res:
                self.plant.addItem(i[1])
                self.plants.append(i[0])
        self.btn.clicked.connect(self.accept)
        self.passw.setEchoMode(QLineEdit.Password)
        self.pB.stateChanged.connect(self.procName)

    def procName(self, st):
        if st == QtCore.Qt.Checked:
            self.nB.setDisabled(False)
            self.name.setDisabled(False)
        else:
            self.nB.setDisabled(True)
            self.nB.setChecked(False)
            self.name.setDisabled(True)

    def getData(self):
        d = {}
        if self.pB.isChecked():
            d['passw'] = self.passw.text()
        if self.nB.isChecked():
            d['user_name'] = self.name.text()
        d['name']=self.name.text()
        if self.mB.isChecked():
            i = self.plant.currentIndex()
            d['meatplant_id'] = self.plants[i] if i > -1 else None
        return d

    def setData(self, r):
        t = self.con.centralWidget().table.model()
        self.plant.setCurrentText(t.index(r, 1).data())
        self.name.setText(t.index(r, 3).data())
        self.passw.setText('')

    def update(self, ind, d):
        args=[]
        for i in d.keys():
            if i != 'passw' and i != 'name':
                a = ":"+i
                args.append("{}={}".format(i, a))
        res = None
        with self.con.con.begin():
            if args:
                res = self.con.query(
                "update meatplants_managers set {} where id = {};".format(','.join(args), ind), d)
            if 'passw' in d.keys():
                name = d['user_name'] if 'user_name' in d.keys() else d['name']
                self.con.query(f'alter user {name} with password :passw;',{'passw':d['passw']})
        m = self.con.centralWidget().table.model()
        if res != None:
            q = QSqlQuery()
            q.prepare(m.query().lastQuery())
            q.exec()
            m.setQuery(q)
            self.con.centralWidget().tablew.select()
        self.con.centralWidget().table.clearSelection()

class AddClientDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/addclient.ui', self)
        self.city.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select name from cities;")
        if res:
            for i in res:
                self.city.addItem(i[1])
        self.btn.clicked.connect(self.accept)
        self.passw.setEchoMode(QLineEdit.Password)

    def getData(self):
        return {
            'phone': self.phone.text(),
            'name': self.name.text(),
            'address': self.addr.text(),
            'city_id': self.con.query('select id from cities where name=:name',
                {'name':self.city.currentText()}).scalar(),
            'passw': self.passw.text(),
            'login': self.login.text()
        }

    def insert(self, d):
        with self.con.con.begin():
            self.con.query(f"set role admin; create user {d['login']} with password '{d['passw']}' in role client;")
            self.con.query('insert into clients values(default,:name,:phone,:address,:city_id,:login);',d)

class UpdateClientDialog(QDialog):
    def __init__(self, con):
        super().__init__()
        self.con = con
        uic.loadUi('./ui/updclient.ui', self)
        self.city.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        res = self.con.query(
            "select name from cities;")
        if res:
            for i in res:
                self.city.addItem(i[0])
        self.btn.clicked.connect(self.accept)
        self.passw.setEchoMode(QLineEdit.Password)
        self.pB.stateChanged.connect(self.procName)

    def procName(self, st):
        if st == QtCore.Qt.Checked:
            self.lB.setDisabled(False)
            self.login.setDisabled(False)
        else:
            self.lB.setDisabled(True)
            self.lB.setChecked(False)
            self.login.setDisabled(True)

    def getData(self):
        d = {}
        if self.pB.isChecked():
            d['passw'] = self.passw.text()
        if self.nB.isChecked():
            d['name'] = self.name.text()
        if self.lB.isChecked():
            d['login'] = self.login.text()
        d['ologin']=self.login.text()
        if self.cB.isChecked():
            d['city_id'] = self.con.query('select id from cities where name=:name',
                {'name':self.city.currentText()}).scalar()
        if self.phB.isChecked():
            d['phone'] = self.phone.text()
        if self.aB.isChecked():
            d['address'] = self.addr.text()
        return d

    def setData(self, r):
        t = self.con.centralWidget().table.model()
        self.city.setCurrentText(t.index(r, 3).data())
        self.name.setText(t.index(r, 2).data())
        self.login.setText(t.index(r, 1).data())
        self.phone.setText(t.index(r, 4).data())
        self.addr.setText(t.index(r, 5).data())
        self.passw.setText('')

    def update(self, ind, d):
        args=[]
        for i in d.keys():
            if i != 'passw' and i != 'ologin':
                a = ":"+i
                args.append("{}={}".format(i, a))
        res = None
        with self.con.con.begin():
            if args:
                res = self.con.query(
                "update clients set {} where id = {};".format(','.join(args), ind), d)
            if 'passw' in d.keys():
                name = d['login'] if 'login' in d.keys() else d['ologin']
                self.con.query(f'alter user {name} with password :passw;',{'passw':d['passw']})
        m = self.con.centralWidget().table.model()
        if res != None:
            q = QSqlQuery()
            q.prepare(m.query().lastQuery())
            q.exec()
            m.setQuery(q)
            self.con.chooseWidget.widget().select()
        self.con.centralWidget().table.clearSelection()


class CatDock(QWidget, cat_dock.Ui_Form):
    def __init__(self):
        super(CatDock, self).__init__()
        self.setupUi(self)

class Catalogs(QWidget):
    def __init__(self, parent):
        super(Catalogs, self).__init__()
        uic.loadUi('./ui/catalogs.ui', self)
        self.main=parent
        self.proptypes.setColumnCount(2)
        self.prodtypes.setColumnCount(2)
        self.cities.setColumnCount(2)
        self.prodnames.setColumnCount(2)
        self.proptypes.setHorizontalHeaderLabels(("№","Тип"))
        self.prodtypes.setHorizontalHeaderLabels(("№","Тип"))
        self.prodnames.setHorizontalHeaderLabels(("№","Название"))
        self.cities.setHorizontalHeaderLabels(("№","Город"))
        tables = [self.cities,self.proptypes,self.prodtypes,self.prodnames]
        for i in range(len(tables)):
            t=tables[i]
            t.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
            t.setSelectionBehavior(QAbstractItemView.SelectRows)
            t.setSelectionMode(QAbstractItemView.MultiSelection)
            t.itemChanged.connect(self.updateItem)
            t.verticalHeader().setVisible(False)
        self.data = (
              ('cities', ('name',), self.cities, self.citiesC),
              ('property_types', ('name',), self.proptypes, self.proptypesC),
              ('product_types', ('name',), self.prodtypes, self.prodtypesC),
              ('product_names', ('name',), self.prodnames, self.prodnamesC),
            )
        self.curT=0
        self.tabWidget.currentChanged.connect(self.changeTable)
        self.curName = "cities"
        self.curTable = self.cities
        self.clabel = self.citiesC
        self.pk="id"
        w = self.main.catalogDock.widget()
        w.addB.clicked.connect(self.addItem)
        w.delB.clicked.connect(self.deleteSelected)
        self.loadTable()

    def count(self):
        self.curTable.setRowCount(0)
        c = self.main.query("select count(*) from {};".format(self.curName)).scalar()
        self.clabel.setText(str(c))
        self.curTable.setRowCount(c)
        return c

    def selectAll(self):
        return self.main.query("select * from {} order by {};".format(self.curName, self.pk))

    def deleteSelected(self):
        t = self.curTable
        selected = t.selectionModel().selectedRows()
        ids=[]
        l = len(selected)
        if l:
            for i in range(l):
                ids.append(t.item(selected[i].row(), 0).text())
            res=self.main.query("delete from {} where {} in ({});".format(self.curName, self.pk, ",".join(ids)))
            if res!=None:
                self.loadTable()

    def loadTable(self):
        c = self.count()
        res = self.selectAll()
        if c>0:
            t = self.curTable
            i = 0
            t.blockSignals(True)
            for r in res:
                id = QTableWidgetItem(str(r[0]))
                id.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
                t.setItem(i, 0, id)
                for j in range(1,len(r)):
                    t.setItem(i, j, QTableWidgetItem(r[j]))
                i+=1
            t.blockSignals(False)

    def updateItem(self,i):
        r=i.row()
        c=i.column()
        id=self.curTable.item(r,0)
        id=id.text()
        t=i.text()
        if t=="":
            t=None
        q="""update {} set {}=:{} where id={}""".format(self.curName, self.data[self.curT][1][c-1], self.data[self.curT][1][c-1], str(id))
        res=self.main.query(q, {self.data[self.curT][1][c-1]: t})
        if res == None:
            self.loadTable()

    def addItem(self):
        res=self.main.query("insert into {} values(DEFAULT, :v);".format(self.curName), {'v':self.main.catalogDock.widget().input.text()})
        if res!=None:
            self.loadTable()

    def changeTable(self,i):
        w = CatDock()
        w.addB.clicked.connect(self.addItem)
        w.delB.clicked.connect(self.deleteSelected)
        self.main.catalogDock.setWidget(w)
        self.main.catalogDock.widget().input.clear()
        self.curT=i
        self.curTable = self.data[self.curT][2]
        self.curName = self.data[self.curT][0]
        self.clabel = self.data[self.curT][3]
        self.loadTable()