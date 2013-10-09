#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Itxaka Serrano 2/08/13

import logging


# logging parameters below
logging.basicConfig(filename='gitlab-gui.log', level=logging.DEBUG, format='%(asctime)s - %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logging.info("Program gitlab-gui Start")

from sys import argv
from PyQt4 import QtCore, QtGui
import mainwindow
import gitlab
import ConfigParser
from os import getenv
import requests
import json
import markdown


class mainwindow(QtGui.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(mainwindow, self).__init__(parent)
        self.setupUi(self)
        self.label.hide()
        self.label_2.hide()
        self.label_3.hide()
        self.label_4.hide()
        self.label_5.hide()
        self.actionExit.triggered.connect(self.close)
        #self.user = getenv("LOGNAME")  # get the logged username so we can configure git

        self.connect(self.label_login, QtCore.SIGNAL("clicked()"),
                     self.clickled_on_login)  # have to do this because we are clicking on a label
        self.token = ""
        self.host = ""
        self.user = ""
        self.model = QtGui.QStandardItemModel(self.listView)
        config = ConfigParser.ConfigParser()
        config.read("config.ini")
        try:
            self.token = config.get("gitlab", "token")
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            QtGui.QMessageBox.information(self.parent(), "Authentication",
                                          "We need to use your token in order to login to your gitlab instance\n"
                                          "Please find it in your Gitlab profile", QtGui.QMessageBox.Ok)
            while self.token == "":
                self.token, ok = QtGui.QInputDialog().getText(self, "Token", "Enter your token:")
            config.add_section("gitlab")
            config.set("gitlab", "token", self.token)
            with open("config.ini", "wb") as f:
                config.write(f)
        try:
            self.host = config.get("gitlab", "url")
        except ConfigParser.NoOptionError:
            while self.host == "" and self.user == "":
                self.host, ok = QtGui.QInputDialog().getText(self, "Gitlab",
                                                             "Enter the gitlab full URL (http://xxx.xxxx.xxx)")
                self.user, ok = QtGui.QInputDialog().getText(self, "Gitlab",
                                             "Enter the gitlab user")
            config.set("gitlab", "url", self.host)
            config.set("gitlab", "user", self.user)
            with open("config.ini", "wb") as f:
                config.write(f)
        self.label_login.setText("Logged as " + config.get("gitlab","user"))
        git = gitlab.Gitlab(host=self.host, user=self.user, token=self.token)
        print git.getprojects()
        for repo in git.getprojects():
            item = QtGui.QStandardItem()
            item.setText(repo['name'])
            self.model.appendRow(item)
        self.listView.setModel(self.model)
        self.listView.clicked.connect(self.on_item_changed)

        # future use
        #user_url = "http://localhost/api/v3/user?private_token=" + self.token
        #r = requests.get(user_url)
        #print json.loads(r.content)
        #new_ssh_key_url = "http://localhost/api/v3/user/keys?private_token=" + self.token + "&title=" +
        #  ssh_title + "&key=" + ssh_key

    def on_item_changed(self, item):
        r = requests.get(self.repos[item.row()][2] + "/raw/master/README?private_token=" + self.token)
        if "<!DOCTYPE html>" in r.content:  # the 404 is html while the raw is plain text
            text = "<p>There isn't a README for this repository</p>"
            pass
        else:
            text = markdown.markdown(r.content)
        self.label_info.setText("Last modified at: " + self.repos[item.row()][1] + "<br><br>" + text)

    def clickled_on_login(self):
        # Here we should put some popup to remove the token and logout
        pass


app = QtGui.QApplication(argv)
form = mainwindow()
form.show()
app.exec_()
