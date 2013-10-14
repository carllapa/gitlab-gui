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
import preferences
import gitlab
import ConfigParser
import requests
import markdown
import os


class MainWindow(QtGui.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.label.hide()
        self.label_2.hide()
        self.label_3.hide()
        self.label_4.hide()
        self.label_5.hide()
        self.menuMenu.show()
        self.user = ""
        self.host = ""
        self.token = ""
        self.actionPreferences.triggered.connect(self.preferences)
        self.actionExit.triggered.connect(self.close)
        self.connect(self.label_login, QtCore.SIGNAL("clicked()"),
                     self.clickled_on_login)  # have to do this because we are clicking on a label
        self.model = QtGui.QStandardItemModel(self.listView)


        self.configuration()

        # setup a window that says connecting and catch the error if can't connect
        self.label_login.setText("Logged as " + self.user)
        git = gitlab.Gitlab(host=self.host, user=self.user, token=self.token)
        self.repos = git.getprojects()
        for repo in self.repos:
            print repo
            item = QtGui.QStandardItem()
            item.setText(repo['name'])
            self.model.appendRow(item)
        self.listView.setModel(self.model)
        self.listView.clicked.connect(self.on_item_changed)

    def configuration(self):
        if os.path.isfile("config.ini"):
            logging.info("Config exists")
            config = ConfigParser.ConfigParser()
            config.read("config.ini")
            self.token = config.get("gitlab", "token")
            self.host = config.get("gitlab", "host")
            self.user = config.get("gitlab", "user")
        else:
            while self.token == "" or self.user == "" or self.host == "":
                self.user, ok = QtGui.QInputDialog().getText(self, "User", "Enter your Gitlab user:")
                self.host, ok = QtGui.QInputDialog().getText(self, "Host", "Enter your Gitlab host:")
                self.token, ok = QtGui.QInputDialog().getText(self, "Token", "Enter your user token:")
            # clean up the host name
            if str(self.host).startswith("http://"):
                pass
            else:
                self.host = "http://" + self.host


            with open("config.ini", "wb") as config_file:
                config = ConfigParser.ConfigParser()
                config.add_section("gitlab")
                config.set("gitlab","user", self.user)
                config.set("gitlab","token", self.token)
                config.set("gitlab","host", self.host)
                config.write(config_file)

    def on_item_changed(self, item):
        print self.repos[item.row()]['web_url']+ "/raw/master/README?private_token=" + self.token
        r = requests.get(self.repos[item.row()]['web_url'] + "/raw/master/README?private_token=" + self.token)
        if "<!DOCTYPE html>" in r.content:  # the 404 is html while the raw is plain text
            r = requests.get(self.repos[item.row()]['web_url'] + "/raw/master/README.md?private_token=" + self.token)
            if "<!DOCTYPE html>" in r.content:
                text = "<p>There isn't a README for this repository</p>"
                pass
            else:
                text = markdown.markdown(r.content)
        else:
            text = markdown.markdown(r.content)
        self.label_info.setText("Last modified at: " + self.repos[item.row()]['last_activity_at'] + "<br><br>" + text)

    def clickled_on_login(self):
        # Here we should put some popup to remove the token and logout
        pass
    def preferences(self):
        prefs = PreferencesWindow(self)
        prefs.setModal(True)
        prefs.show()


class PreferencesWindow(QtGui.QDialog, preferences.Ui_Dialog):
    def __init__(self, parent=None):
        super(PreferencesWindow, self).__init__(parent)
        self.setupUi(self)

app = QtGui.QApplication(argv)
form = MainWindow()
form.show()
app.exec_()
