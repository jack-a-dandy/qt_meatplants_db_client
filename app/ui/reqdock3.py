# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reqdock3.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(418, 46)
        Form.setMinimumSize(QtCore.QSize(418, 46))
        Form.setMaximumSize(QtCore.QSize(418, 46))
        self.btn = QtWidgets.QPushButton(Form)
        self.btn.setGeometry(QtCore.QRect(300, 10, 100, 27))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn.sizePolicy().hasHeightForWidth())
        self.btn.setSizePolicy(sizePolicy)
        self.btn.setMinimumSize(QtCore.QSize(100, 0))
        self.btn.setObjectName("btn")
        self.date1 = QtWidgets.QDateEdit(Form)
        self.date1.setGeometry(QtCore.QRect(40, 10, 101, 28))
        self.date1.setObjectName("date1")
        self.date2 = QtWidgets.QDateEdit(Form)
        self.date2.setGeometry(QtCore.QRect(180, 10, 101, 28))
        self.date2.setObjectName("date2")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 21, 28))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(150, 10, 21, 28))
        self.label_3.setObjectName("label_3")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Выбор параметров"))
        self.btn.setText(_translate("Form", "Выбрать"))
        self.date1.setDisplayFormat(_translate("Form", "dd.MM.yyyy"))
        self.date2.setDisplayFormat(_translate("Form", "dd.MM.yyyy"))
        self.label_2.setText(_translate("Form", "От"))
        self.label_3.setText(_translate("Form", "По"))

