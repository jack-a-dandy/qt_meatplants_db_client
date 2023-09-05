# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cat_dock.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(205, 191)
        Form.setMinimumSize(QtCore.QSize(205, 191))
        self.input = QtWidgets.QLineEdit(Form)
        self.input.setGeometry(QtCore.QRect(0, 0, 201, 27))
        self.input.setObjectName("input")
        self.addB = QtWidgets.QPushButton(Form)
        self.addB.setGeometry(QtCore.QRect(0, 30, 201, 27))
        self.addB.setStyleSheet("background-color:green;")
        self.addB.setObjectName("addB")
        self.delB = QtWidgets.QPushButton(Form)
        self.delB.setGeometry(QtCore.QRect(0, 90, 201, 27))
        self.delB.setStyleSheet("background-color:red;")
        self.delB.setObjectName("delB")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        self.addB.setText(_translate("Form", "Добавить"))
        self.delB.setText(_translate("Form", "Удалить"))
