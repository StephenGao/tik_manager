#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# Copyright (c) 2017-2018, Arda Kutlu (ardakutlu@gmail.com)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  - Neither the name of the software nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

# Module to access Library of global assets

import os
import sys
import shutil
import re
import _version

import time

FORCE_QT4 = bool(os.getenv("FORCE_QT4"))

# Enabele FORCE_QT4 for compiling with pyinstaller
# FORCE_QT4 = True

if FORCE_QT4:
    from PyQt4 import QtCore, Qt
    from PyQt4 import QtGui as QtWidgets
else:
    import Qt
    from Qt import QtWidgets, QtCore, QtGui

import json
import os, fnmatch
import logging

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Asset Library"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

logging.basicConfig()
logger = logging.getLogger('AssetLibrary')
logger.setLevel(logging.WARNING)

BoilerDict = {"Environment": "Standalone",
              "MainWindow": None,
              "WindowTitle": "Asset Library Standalone v%s" % _version.__version__,
              "Stylesheet": "mayaDark.stylesheet"}

class AssetEditor(object):
    def __init__(self):
        super(AssetEditor, self).__init__()
        pass


# ---------------
# GET ENVIRONMENT
# ---------------
try:
    from maya import OpenMayaUI as omui
    import maya.cmds as cmds

    ##
    ## EDITOR CLASS
    import assetEditorMaya # for dev
    reload(assetEditorMaya)# for dev

    from assetEditorMaya import AssetEditorMaya as AssetEditor


    BoilerDict["Environment"] = "Maya"
    BoilerDict["WindowTitle"] = "Asset Library Maya v%s" % _version.__version__
    if Qt.__binding__ == "PySide":
        from shiboken import wrapInstance
    elif Qt.__binding__.startswith('PyQt'):
        from sip import wrapinstance as wrapInstance
    else:
        from shiboken2 import wrapInstance
except ImportError:
    pass

try:
    import MaxPlus

    BoilerDict["Environment"] = "3dsMax"
    BoilerDict["WindowTitle"] = "Asset Library 3ds Max v%s" % _version.__version__
except ImportError:
    pass

try:
    import hou

    BoilerDict["Environment"] = "Houdini"
    BoilerDict["WindowTitle"] = "Asset Library Houdini v%s" % _version.__version__
except ImportError:
    pass

try:
    import nuke

    BoilerDict["Environment"] = "Nuke"
    BoilerDict["WindowTitle"] = "Asset Library Nuke v%s" % _version.__version__
except ImportError:
    pass

def getMainWindow():
    """This function should be overriden"""
    if BoilerDict["Environment"] == "Maya":
        win = omui.MQtUtil_mainWindow()
        ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
        return ptr

    elif BoilerDict["Environment"] == "3dsMax":
        return MaxPlus.GetQMaxWindow()

    elif BoilerDict["Environment"] == "Houdini":
        return hou.qt.mainWindow()

    elif BoilerDict["Environment"] == "Nuke":
        # TODO // Needs a main window getter for nuke
        return None

    else:
        return None

def _loadJson(file):
    """Loads the given json file"""
    try:
        with open(file, 'r') as f:
            data = json.load(f)
            return data
    except ValueError:
        # msg = "Corrupted JSON file => %s" % file
        # logger.error(msg)
        # self._exception(200, msg)
        return(-1) # code for corrupted json file

def _dumpJson(data, file):
    """Saves the data to the json file"""
    name, ext = os.path.splitext(file)
    tempFile = "{0}.tmp".format(name)
    with open(tempFile, "w") as f:
        json.dump(data, f, indent=4)
    shutil.copyfile(tempFile, file)
    os.remove(tempFile)

class AssetLibrary(AssetEditor):
    """
    Asset Library Logical operations Class. This Class holds the main functions (save,import,scan)
    """

    def __init__(self, directory):
        self.directory = directory
        if not os.path.exists(directory):
            logger.error("Cannot reach the library directory: \n" + directory)

        self.errorCodeDict = {200: "Corrupted File",
                         201: "Missing File",
                         202: "Read/Write Error",
                         203: "Delete Error",
                         210: "OS Not Supported",
                         101: "Out of range",
                         102: "Missing Override",
                         340: "Naming Error",
                         341: "Mandatory fields are not filled",
                         360: "Action not permitted"}

        self.assetsList=[]

    # def getLibraries(self):
    #     pass
    #
    # def addLibrary(self):
    #     pass
    #
    # def removeLibrary(self):
    #     pass

    def mergeAsset(self, assetName):
        print "merging %s" %assetName
        pass

    def importAsset(self, assetName):
        print "importing %s" % assetName
        pass

    def importObj(self, assetName):
        print "importing Obj %s" % assetName
        pass

    def loadAsset(self, assetName):
        print "loading %s" % assetName
        pass

    # def saveAsset(self, assetName, screenshot=True, moveCenter=False, selectionOnly=True, exportUV=True, exportOBJ=True, **info):
    #     """
    #     Saves the selected object(s) as an asset into the predefined library
    #     Args:
    #         assetName: (Unicode) Asset will be saved as with this name
    #         screenshot: (Bool) If true, screenshots (Screenshot, Thumbnail, Wireframe, UV Snapshots) will be taken with playblast. Default True
    #         directory: (Unicode) Default Library location. Default is predefined outside of this class
    #         moveCenter: (Bool) If True, selected object(s) will be moved to World 0 point. Pivot will be the center of selection. Default False
    #         **info: (Any) Extra information which will be hold in the .json file
    #
    #     Returns:
    #         None
    #
    #     """
    #
    #     pass


    def scanAssets(self):
        """
        Scans the directory for .json files, and gather info.
        Args:
            directory: (Unicode) Default Library location. Default is predefined outside of this class

        Returns:
            None

        """
        if not os.path.exists(self.directory):
            return
        # first collect all the json files from second level subfolders
        subDirs = next(os.walk(self.directory))[1]
        # for dir in subDirs:
        #     filePath = os.path.join(self.directory, dir, "%s.json" %dir)
        #     if os.path.isfile(filePath):
        #         self[dir]={"dataPath": filePath}
        self.assetsList = [d for d in subDirs if os.path.isfile(os.path.join(self.directory, d, "%s.json" %d))]

    def getThumbnail(self, assetName):
        thumbPath = os.path.join(self.directory, assetName, "%s_thumb.jpg" %assetName)
        return thumbPath

    def getScreenShot(self, assetName):
        data = self._getData(assetName)
        ssPath = os.path.join(self.directory, assetName, data["ssPath"])
        return ssPath

    def getWireFrame(self, assetName):
        data = self._getData(assetName)
        swPath = os.path.join(self.directory, assetName, data["swPath"])
        return swPath

    def getNotes(self, assetName):
        data = self._getData(assetName)
        try:
            notes = data["notes"]
        except KeyError:
            notes = ""
        return notes

    def setNotes(self, assetName, note):
        data = self._getData(assetName)
        data["notes"] = note
        self._setData(assetName, data)

    def showInExplorer(self, assetName):
        path = os.path.join(self.directory, assetName)
        os.startfile(path)

    def _getData(self, assetName):
        jsonFile = os.path.join(self.directory, assetName, "%s.json" %assetName)
        data = _loadJson(jsonFile)
        return data

    def _setData(self, assetName, data):
        jsonFile = os.path.join(self.directory, assetName, "%s.json" % assetName)
        _dumpJson(data, jsonFile)


    def _savePreviews(self, name, assetDirectory, uvSnap=True, selectionOnly=True):
        """
        Saves the preview files under the Asset Directory
        Args:
            name: (Unicode) Name of the Asset
            assetDirectory: (Unicode) Directory of Asset

        Returns:
            (Tuple) Thumbnail path, Screenshot path, Wireframe path

        """

        pass

    def _updatePreviews(self, name, assetDirectory):

        pass


    def _exception(self, code, msg):
        """Exception report function. Throws a log error and raises an exception"""
        logger.error("Exception %s" %self.errorCodeDict[code])
        logger.error(msg)
        raise Exception (code, msg)



class MainUI(QtWidgets.QMainWindow):
    """Main UI function"""
    def __init__(self):
        for entry in QtWidgets.QApplication.allWidgets():
            try:
                if entry.objectName() == BoilerDict["WindowTitle"]:
                    entry.close()
            except AttributeError:
                pass
        parent = getMainWindow()
        super(MainUI, self).__init__(parent=parent)

        if BoilerDict["Environment"]=="Standalone":
            self.viewOnly = True
        else:
            self.viewOnly = False
        # Set Stylesheet
        dirname = os.path.dirname(os.path.abspath(__file__))
        stylesheetFile = os.path.join(dirname, "CSS", "darkorange.stylesheet")

        self.homedir = os.path.expanduser("~")
        self.DocumentsDir = "Documents" if BoilerDict["Environment"] == "Standalone" else ""
        self.settingsFile = os.path.join(self.homedir, self.DocumentsDir, "assetLibraryConfig.json")

        self.setObjectName(BoilerDict["WindowTitle"])
        self.resize(670, 624)
        self.setWindowTitle(BoilerDict["WindowTitle"])
        self.centralwidget = QtWidgets.QWidget(self)

        # MENU BAR / STATUS BAR
        # ---------------------
        menubar = QtWidgets.QMenuBar(self)
        menubar.setGeometry(QtCore.QRect(0, 0, 735, 21))
        self.setMenuBar(menubar)
        statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(statusbar)

        fileMenu = menubar.addMenu("File")
        addNewLibrary_mi= QtWidgets.QAction("&Add New Library", self)
        renameLibrary_mi = QtWidgets.QAction("&Rename Active Library", self)
        createNewAsset_mi = QtWidgets.QAction("&Create New Asset", self)
        loadAsset_mi = QtWidgets.QAction("&Load Selected Asset", self)
        importAssetWithTextures_mi = QtWidgets.QAction("&Import Asset and Copy Textures", self)
        importAsset_mi = QtWidgets.QAction("&Import only", self)
        deleteAsset_mi = QtWidgets.QAction("&Delete Selected Asset", self)
        removeLibrary_mi = QtWidgets.QAction("&Remove Library", self)

        fileMenu.addAction(addNewLibrary_mi)
        fileMenu.addAction(renameLibrary_mi)
        fileMenu.addAction(createNewAsset_mi)

        fileMenu.addSeparator()
        fileMenu.addAction(loadAsset_mi)
        fileMenu.addAction(importAssetWithTextures_mi)
        fileMenu.addAction(importAsset_mi)

        fileMenu.addSeparator()
        fileMenu.addAction(deleteAsset_mi)
        fileMenu.addAction(removeLibrary_mi)

        self.tabDialog()
        self.setCentralWidget(self.centralwidget)

        addNewLibrary_mi.triggered.connect(self.newLibraryUI)
        renameLibrary_mi.triggered.connect(self.renameLibrary)
        removeLibrary_mi.triggered.connect(lambda: self.removeLibrary(self.tabWidget.currentWidget().objectName()))


    def tabDialog(self):

        self.masterLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.masterLayout.setSpacing(6)
        self.masterLayout.setMargin(0)

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 167777))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setUsesScrollButtons(False)

        self.masterLayout.addWidget(self.tabWidget)

        for lib in self.getLibraryPaths():
            name = lib[0]
            path = lib[1]
            if not os.path.exists(path):
                logger.warning("Cannot reach library path: \n%s \n Removing from the database..." % (path))
                self.removeLibrary(name)
                continue
            preTab = LibraryTab(path)
            self.tabWidget.addTab(preTab, name)
            preTab.setObjectName(name)
            preTab.setLayout(preTab.layout)

        self.tabWidget.currentChanged.connect(self.refreshTab)
        self.refreshTab()

    def refreshTab(self):
        if self.tabWidget.currentWidget():
            self.tabWidget.currentWidget().populate()

    def newLibraryUI(self):
            ## Custom Name for the new library (optional)
            ## Path for the library
        ## check the path if its valid
        newLibrary_Dialog = QtWidgets.QDialog(parent=self)
        newLibrary_Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        newLibrary_Dialog.resize(460, 140)
        newLibrary_Dialog.setWindowTitle("Add New Library")

        self.verticalLayout = QtWidgets.QVBoxLayout(newLibrary_Dialog)

        self.gridLayout = QtWidgets.QGridLayout()

        self.directory_lineEdit = QtWidgets.QLineEdit(newLibrary_Dialog)
        self.directory_lineEdit.setToolTip("Directory path to the assets")

        self.gridLayout.addWidget(self.directory_lineEdit, 1, 1, 1, 1)

        self.directory_label = QtWidgets.QLabel(newLibrary_Dialog)
        self.directory_label.setToolTip("Directory path to the assets")
        self.directory_label.setText("Directory")
        self.gridLayout.addWidget(self.directory_label, 1, 0, 1, 1)

        self.aliasName_label = QtWidgets.QLabel(newLibrary_Dialog)
        self.aliasName_label.setToolTip("This name will be visible on Library tab. Directory name will be used if left empty")
        self.aliasName_label.setText("Alias Name")
        self.gridLayout.addWidget(self.aliasName_label, 0, 0, 1, 1)

        self.browse_pushButton = QtWidgets.QPushButton(newLibrary_Dialog)
        self.browse_pushButton.setText(("Browse"))
        self.browse_pushButton.setShortcut((""))
        self.gridLayout.addWidget(self.browse_pushButton, 1, 2, 1, 1)

        self.aliasName_lineEdit = QtWidgets.QLineEdit(newLibrary_Dialog)
        self.aliasName_lineEdit.setToolTip("This name will be visible on Library tab. Directory name will be used if left empty")
        self.aliasName_lineEdit.setText("")
        self.aliasName_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.aliasName_lineEdit.setPlaceholderText("(optional)")
        self.gridLayout.addWidget(self.aliasName_lineEdit, 0, 1, 1, 2)

        self.verticalLayout.addLayout(self.gridLayout)

        self.buttonBox = QtWidgets.QDialogButtonBox(newLibrary_Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))

        self.addLibrary_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.addLibrary_button.setText('Add Library')

        self.verticalLayout.addWidget(self.buttonBox)

        # SIGNAL CONNECTIONS
        # ------------------

        self.addLibrary_button.clicked.connect(lambda: self.addLibrary(self.directory_lineEdit.text(), self.aliasName_lineEdit.text()))

        self.buttonBox.accepted.connect(newLibrary_Dialog.accept)
        self.buttonBox.rejected.connect(newLibrary_Dialog.reject)

        self.browse_pushButton.clicked.connect(self.onBrowse)


        newLibrary_Dialog.show()
        pass

    def onBrowse(self):
        dir = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            self.directory_lineEdit.setText(str(dir))
        else:
            return

    def renameLibrary(self):
        """ Renames the current Library"""
        customName, ok = QtWidgets.QInputDialog.getText(self, "Rename Library",
                                               "Enter an Alias Name:")
        if ok:
            pass
        else:
            return

        currentTabIndex = self.tabWidget.currentIndex()

        oldName = self.tabWidget.currentWidget().objectName()

        libraryPaths = self.getLibraryPaths()
        #
        for p in libraryPaths:
            if p[0] == oldName:
                p[0] = customName
                _dumpJson(libraryPaths, self.settingsFile)
                self.tabWidget.setTabText(currentTabIndex, customName)
                return

    def getLibraryPaths(self):
        try:
            libraryPaths = _loadJson(self.settingsFile)
        except IOError: # it file does not exist
            libraryPaths = []
            _dumpJson(libraryPaths, self.settingsFile)
        return libraryPaths

    def addLibrary(self, path, name):
        path = os.path.normpath(path)
        if not os.path.isdir(path):
            self.infoPop(textTitle="Path is not valid", textHeader="Path is not valid or accessible", type="C")
            return

        if name == "":
            name = os.path.basename(path)

        libraryPaths = self.getLibraryPaths()

        for p in libraryPaths:
            if p[0] == name:
                self.infoPop(textTitle="Duplicate Name", textHeader="Another library with the same name already exist", type="C")
                return

        newItem = [name, path]
        libraryPaths.append(newItem)
        _dumpJson(libraryPaths, self.settingsFile)

        # add the tab
        preTab = LibraryTab(path, viewOnly=self.viewOnly)
        self.tabWidget.addTab(preTab, name)
        preTab.setObjectName(name)
        preTab.setLayout(preTab.layout)

    def removeLibrary(self, name):

        libraryPaths = self.getLibraryPaths()
        for p in libraryPaths:
            if p[0] == name:
                libraryPaths.pop(libraryPaths.index(p))
                _dumpJson(libraryPaths, self.settingsFile)
                tabIndexToRemove = self.tabWidget.currentIndex()
                self.tabWidget.removeTab(tabIndexToRemove)
                return

    def on_context_menu(self, point):
        # show context menu
        self.tabsRightMenu.exec_(self.mapToGlobal(point))

    def infoPop(self, textTitle="info", textHeader="", textInfo="", type="I"):
        self.msg = QtWidgets.QMessageBox(parent=self)
        if type == "I":
            self.msg.setIcon(QtWidgets.QMessageBox.Information)
        if type == "C":
            self.msg.setIcon(QtWidgets.QMessageBox.Critical)

        self.msg.setText(textHeader)
        self.msg.setInformativeText(textInfo)
        self.msg.setWindowTitle(textTitle)
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.msg.button(QtWidgets.QMessageBox.Ok).setFixedHeight(30)
        self.msg.button(QtWidgets.QMessageBox.Ok).setFixedWidth(100)
        self.msg.show()



class LibraryTab(QtWidgets.QWidget):
    viewModeState = -1

    def __init__(self, directory):
        self.directory = directory
        super(LibraryTab, self).__init__()

        self.wireframeMode = -1 # 1 is for screenshot -1 for wireframe

        self.library = AssetLibrary(directory)
        self.buildTabUI()

        if BoilerDict["Environment"]=="Standalone":
            self.viewOnlyMode()

    def buildTabUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setGeometry(QtCore.QRect(20, 10, 693, 437))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        self.createNewAsset_pushButton = QtWidgets.QPushButton(self)
        self.createNewAsset_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.createNewAsset_pushButton.setMaximumSize(QtCore.QSize(15000, 45))
        self.createNewAsset_pushButton.setText("Create New Asset")
        self.layout.addWidget(self.createNewAsset_pushButton)


        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setLineWidth(0)

        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)

        self.left_verticalLayout = QtWidgets.QVBoxLayout()
        self.left_verticalLayout.setSpacing(0)

        self.assets_listWidget = QtWidgets.QListWidget(self.frame)

        self.left_verticalLayout.addWidget(self.assets_listWidget)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 6, -1, -1)
        self.horizontalLayout.setSpacing(6)

        self.filter_label = QtWidgets.QLabel(self.frame)

        self.horizontalLayout.addWidget(self.filter_label)

        self.filter_lineEdit = QtWidgets.QLineEdit(self.frame)
        self.horizontalLayout.addWidget(self.filter_lineEdit)

        self.left_verticalLayout.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.left_verticalLayout, 2, 0, 1, 1)

        self.frame_right = QtWidgets.QFrame(self.splitter)
        self.frame_right.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Raised)

        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_right)
        self.gridLayout_2.setContentsMargins(-1, -1, 0, 0)

        self.rightBelow_verticalLayout = QtWidgets.QVBoxLayout()

        self.sourceProject_label = QtWidgets.QLabel(self.frame_right)
        self.sourceProject_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.sourceProject_label.setText(("Source: "))
        self.sourceProject_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rightBelow_verticalLayout.addWidget(self.sourceProject_label)

        # self.version_label = QtWidgets.QLabel(self.frame_right)
        # self.version_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        # self.version_label.setText(("Version: "))
        # self.version_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        # self.rightBelow_verticalLayout.addWidget(self.version_label)

        self.objCopy_label = QtWidgets.QLabel(self.frame_right)
        self.objCopy_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.objCopy_label.setText(("Obj File: "))
        self.objCopy_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rightBelow_verticalLayout.addWidget(self.objCopy_label)

        self.facesTriangles_label = QtWidgets.QLabel(self.frame_right)
        self.facesTriangles_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.facesTriangles_label.setText(("Faces/Triangles: "))
        self.facesTriangles_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rightBelow_verticalLayout.addWidget(self.facesTriangles_label)

        # self.uv_label = QtWidgets.QLabel(self.frame_right)
        # self.uv_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        # self.uv_label.setText(("UVs:"))
        # self.uv_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        # self.rightBelow_verticalLayout.addWidget(self.uv_label)

        self.textures_label = QtWidgets.QLabel(self.frame_right)
        self.textures_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.textures_label.setText(("Textures: "))
        self.textures_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rightBelow_verticalLayout.addWidget(self.textures_label)

        self.assetNotes_label = QtWidgets.QLabel(self.frame_right)
        self.assetNotes_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.assetNotes_label.setText(("Asset Notes: "))
        self.assetNotes_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rightBelow_verticalLayout.addWidget(self.assetNotes_label)

        self.notes_textEdit = QtWidgets.QTextEdit(self.frame_right)
        self.rightBelow_verticalLayout.addWidget(self.notes_textEdit)



        ## out of the box
        ## --------------
        # self.thumb_label = QtWidgets.QLabel(self.frame_right)
        #
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.thumb_label.sizePolicy().hasHeightForWidth())
        #
        # self.thumb_label.setSizePolicy(sizePolicy)
        # self.thumb_label.setMinimumSize(QtCore.QSize(221, 124))
        # self.thumb_label.setMaximumSize(QtCore.QSize(884, 496))
        # self.thumb_label.setSizeIncrement(QtCore.QSize(1, 1))
        # self.thumb_label.setBaseSize(QtCore.QSize(0, 0))
        # self.thumb_label.setFrameShape(QtWidgets.QFrame.Box)
        # self.thumb_label.setScaledContents(False)
        # self.thumb_label.setAlignment(QtCore.Qt.AlignCenter)
        ## --------------

        ## ImageWidget
        ## -----------
        # if FORCE_QT4:
        #     self.tPixmap = QtWidgets.QPixmap("")
        # else:
        #     self.tPixmap = QtGui.QPixmap("")
        # self.screenshot_label = ImageWidget(self.frame_right)
        # self.screenshot_label.setPixmap(self.tPixmap)
        #
        # self.screenshot_label.setMinimumSize(QtCore.QSize(200, 200))
        # self.screenshot_label.setFrameShape(QtWidgets.QFrame.Box)
        # self.screenshot_label.setScaledContents(True)
        # self.screenshot_label.setAlignment(QtCore.Qt.AlignCenter)
        ## -----------


        ## QtImageViewer
        ## -------------
        self.screenshot_label = QtImageViewer()
        self.screenshot_label.setMinimumSize(QtCore.QSize(10, 10))
        self.screenshot_label.setFrameShape(QtWidgets.QFrame.Box)
        self.screenshot_label.setAlignment(QtCore.Qt.AlignCenter)
        self.screenshot_label.canZoom = False
        self.screenshot_label.canPan = False
        # self.screenshot_label.setFixedHeight(500)
        ## -------------

        self.rightBelow_verticalLayout.addWidget(self.screenshot_label)

        self.gridLayout_2.addLayout(self.rightBelow_verticalLayout, 3, 0, 1, 1)

        self.rightUp_gridLayout = QtWidgets.QGridLayout()
        self.rightUp_gridLayout.setContentsMargins(-1, -1, 10, 10)

        self.import_pushButton = QtWidgets.QPushButton(self.frame_right)
        self.import_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.import_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.import_pushButton.setText(("Import Only"))

        self.rightUp_gridLayout.addWidget(self.import_pushButton, 1, 0, 1, 1)

        self.load_pushButton = QtWidgets.QPushButton(self.frame_right)
        self.load_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.load_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.load_pushButton.setText(("Load"))

        self.rightUp_gridLayout.addWidget(self.load_pushButton, 0, 3, 1, 1)

        self.importObj_pushButton = QtWidgets.QPushButton(self.frame_right)
        self.importObj_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.importObj_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.importObj_pushButton.setText(("Import .obj"))

        self.rightUp_gridLayout.addWidget(self.importObj_pushButton, 1, 3, 1, 1)

        self.merge_pushButton = QtWidgets.QPushButton(self.frame_right)
        self.merge_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.merge_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.merge_pushButton.setText(("Merge"))
        self.rightUp_gridLayout.addWidget(self.merge_pushButton, 0, 0, 1, 1)

        self.gridLayout_2.addLayout(self.rightUp_gridLayout, 0, 0, 1, 1)

        self.filter_lineEdit.textChanged.connect(self.populate)

        # RIGHT CLICK MENU
        # ----------------

        self.assets_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.assets_listWidget.customContextMenuRequested.connect(self.onContextMenu_assets)
        self.popMenu_assets = QtWidgets.QMenu()

        self.assets_rcItem_0 = QtWidgets.QAction('View as Icons', self)
        self.popMenu_assets.addAction(self.assets_rcItem_0)

        self.assets_rcItem_1 = QtWidgets.QAction('Show in Explorer', self)
        self.popMenu_assets.addAction(self.assets_rcItem_1)

        # SIGNAL CONNECTIONS
        # ------------------

        self.assets_rcItem_0.triggered.connect(lambda: self.rcAction_assets("viewModeChange"))
        self.assets_rcItem_1.triggered.connect(lambda: self.rcAction_assets("showInExplorer"))

        self.assets_listWidget.currentItemChanged.connect(self.onAssetChange)

        # self.screenshot_label.clicked.connect(self.toggleWireframe)
        # self.screenshot_label.leftClicked.connect(self.toggleWireframe)
        self.screenshot_label.leftMouseButtonPressed.connect(self.toggleWireframe)

        self.splitter.setSizes([375, 25])

        self.import_pushButton.clicked.connect(self.onImportAsset)
        self.merge_pushButton.clicked.connect(self.onMergeAsset)
        self.importObj_pushButton.clicked.connect(self.onImportObj)
        self.load_pushButton.clicked.connect(self.onLoadAsset)
        self.createNewAsset_pushButton.clicked.connect(self.createNewAssetUI)


        # self.populate()

    def createNewAssetUI(self):
        saveAsset_Dialog = QtWidgets.QDialog(parent=self)
        saveAsset_Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        saveAsset_Dialog.resize(257, 219)
        saveAsset_Dialog.setWindowTitle("Create New Asset")

        self.verticalLayout = QtWidgets.QVBoxLayout(saveAsset_Dialog)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setVerticalSpacing(10)

        self.assetName_label = QtWidgets.QLabel(saveAsset_Dialog)
        self.assetName_label.setText(("Asset Name"))
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.assetName_label)

        self.assetName_lineEdit = QtWidgets.QLineEdit(saveAsset_Dialog)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.assetName_lineEdit)

        self.exportUv_checkBox = QtWidgets.QCheckBox(saveAsset_Dialog)
        self.exportUv_checkBox.setText(("Export UV Snapshots"))
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.exportUv_checkBox)

        self.exportObj_checkBox = QtWidgets.QCheckBox(saveAsset_Dialog)
        self.exportObj_checkBox.setText(("Export .obj"))
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.exportObj_checkBox)

        self.exportFbx_checkBox = QtWidgets.QCheckBox(saveAsset_Dialog)
        self.exportFbx_checkBox.setText(("Export .fbx"))
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.exportFbx_checkBox)

        self.range_label = QtWidgets.QLabel(saveAsset_Dialog)
        self.range_label.setText(("Range"))
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.range_label)

        self.range_horizontalLayout = QtWidgets.QHBoxLayout()

        range_radioButton_grp = QtWidgets.QButtonGroup(self.range_horizontalLayout)
        self.selection_radioButton= QtWidgets.QRadioButton("Selection", parent=self)
        self.scene_radioButton= QtWidgets.QRadioButton("Scene", parent=self)

        range_radioButton_grp.addButton(self.selection_radioButton)
        range_radioButton_grp.addButton(self.scene_radioButton)
        self.scene_radioButton.setChecked(True)

        self.range_horizontalLayout.addWidget(self.selection_radioButton)
        self.range_horizontalLayout.addWidget(self.scene_radioButton)

        self.formLayout.setLayout(4, QtWidgets.QFormLayout.FieldRole, self.range_horizontalLayout)

        self.format_label = QtWidgets.QLabel(saveAsset_Dialog)
        self.format_label.setText(("Format"))

        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.format_label)
        self.format_horizontalLayout = QtWidgets.QHBoxLayout()
        #####################
        format_radioButton_grp = QtWidgets.QButtonGroup(self.format_horizontalLayout)
        self.ma_radioButton= QtWidgets.QRadioButton("ma", parent=self)
        self.mb_radioButton= QtWidgets.QRadioButton("mb", parent=self)

        format_radioButton_grp.addButton(self.ma_radioButton)
        format_radioButton_grp.addButton(self.mb_radioButton)
        self.ma_radioButton.setChecked(True)

        self.format_horizontalLayout.addWidget(self.ma_radioButton)
        self.format_horizontalLayout.addWidget(self.mb_radioButton)
        #################

        self.formLayout.setLayout(5, QtWidgets.QFormLayout.FieldRole, self.format_horizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)

        self.saveAsset_buttonBox = QtWidgets.QDialogButtonBox(saveAsset_Dialog)
        self.saveAsset_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.saveAsset_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.saveAsset_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        self.saveAsset_buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))
        self.create_pushButton = self.saveAsset_buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.create_pushButton.setText('Create Asset')

        self.verticalLayout.addWidget(self.saveAsset_buttonBox)

        # SIGNAL CONNECTIONS
        # ------------------

        self.saveAsset_buttonBox.accepted.connect(saveAsset_Dialog.accept)
        self.saveAsset_buttonBox.rejected.connect(saveAsset_Dialog.reject)

        if not BoilerDict["Environment"]=="Maya":
            self.ma_radioButton.setHidden(True)
            self.mb_radioButton.setHidden(True)

        self.create_pushButton.clicked.connect(lambda: self.library.saveAsset(assetName=self.assetName_lineEdit.text(),
                                                                      exportUV=self.exportUv_checkBox.isChecked(),
                                                                      exportOBJ=self.exportObj_checkBox.isChecked(),
                                                                      exportFBX=self.exportFbx_checkBox.isChecked(),
                                                                      selectionOnly=self.selection_radioButton.isChecked(),
                                                                      mbFormat=self.mb_radioButton.isChecked()
                                                                      ))
        self.assetName_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.assetName_lineEdit.text(), self.create_pushButton,
                                        self.assetName_lineEdit))

        saveAsset_Dialog.show()

    def viewOnlyMode(self):
        self.importObj_pushButton.setHidden(True)
        self.merge_pushButton.setHidden(True)
        self.import_pushButton.setHidden(True)
        self.load_pushButton.setHidden(True)
        self.createNewAsset_pushButton.setHidden(True)

    def onAssetChange(self):
        assetName = self._getCurrentAssetName()
        if not assetName:
            return

        assetData = self.library._getData(assetName)

        if self.wireframeMode == -1:
            # get preview image
            screenshotPath = self.library.getScreenShot(assetName)
        else:
            screenshotPath = self.library.getWireFrame(assetName)

        # update preview image
        if FORCE_QT4:
            self.tPixmap = QtWidgets.QPixmap(screenshotPath)
        else:
            self.tPixmap = QtGui.QPixmap(screenshotPath)
        # self.screenshot_label.setPixmap(self.tPixmap)
        self.screenshot_label.setImage(self.tPixmap)

        # get Notes
        # assetNotes = self.library.getNotes(assetName)
        # self.notes_textEdit.setText(assetNotes)

        # get display data


        textures = len(assetData["textureFiles"])
        self.textures_label.setText("Textures: %s" %textures)
        facesTriangles = assetData["Faces/Triangles"]
        self.facesTriangles_label.setText("Faces/Triangles: %s" %facesTriangles)
        sourceProject = assetData["sourceProject"]
        version = assetData["version"]
        self.sourceProject_label.setText("Source: %s Version: %s" %(sourceProject, version))
        isObjExist = False if assetData["objPath"] == "NA" else True
        self.objCopy_label.setText("Obj File: %s" %isObjExist)


    def toggleWireframe(self):
        self.wireframeMode *= -1
        self.onAssetChange()

    def populate(self):
        """
        UI populate function - linkes to the assetLibrary.scan()
        Returns:

        """
        filterWord = self.filter_lineEdit.text()

        self.assets_listWidget.clear()
        self.library.scanAssets()


        if self.viewModeState == 1:
            self.assets_listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
            self.assets_listWidget.setIconSize(QtCore.QSize(100, 100))
            self.assets_listWidget.setMovement(QtWidgets.QListView.Static)
            self.assets_listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
            self.assets_listWidget.setGridSize(QtCore.QSize(100*1.2, 100*1.4))

            # self.assets_listWidget.addItems(self.filterList(self.library.assetsList, filterWord))
            filteredItems = self.filterList(self.library.assetsList, filterWord)
            for itemName in filteredItems:
                item = QtWidgets.QListWidgetItem(itemName)
                thumbPath = self.library.getThumbnail(itemName)

                icon = QtGui.QIcon(thumbPath)
                item.setIcon(icon)

                self.assets_listWidget.addItem(item)

        else:
            self.assets_listWidget.setViewMode(QtWidgets.QListWidget.ListMode)
            self.assets_listWidget.setGridSize(QtCore.QSize(15,15))
            self.assets_listWidget.addItems(self.filterList(self.library.assetsList, filterWord))

    def onMergeAsset(self):
        assetName = self._getCurrentAssetName()
        if assetName:
            self.library.mergeAsset(assetName)

    def onImportAsset(self):
        assetName = self._getCurrentAssetName()
        if assetName:
            self.library.importAsset(assetName)

    def onImportObj(self):
        assetName = self._getCurrentAssetName()
        if assetName:
            self.library.importObj(assetName)

    def onLoadAsset(self):
        assetName = self._getCurrentAssetName()
        if assetName:
            self.library.loadAsset(assetName)

    def _clearDisplayInfo(self):

        self.notes_textEdit.clear()
        # self.screenshot_label.clear()
        self.screenshot_label.clearImage()
        self.sourceProject_label.setText(("Source: "))
        self.objCopy_label.setText(("Obj File: "))
        self.facesTriangles_label.setText(("Faces/Triangles: "))
        self.textures_label.setText(("Textures: "))
        self.assetNotes_label.setText(("Asset Notes: "))


    def _getCurrentAssetName(self):
        row = self.assets_listWidget.currentRow()
        if row == -1:
            self._clearDisplayInfo()
            return
        return self.assets_listWidget.currentItem().text()

    def filterList(self, sourceList, filterWord):
        if filterWord == "":
            return sourceList
        else:
            filteredList = [item for item in sourceList if (filterWord.lower() in item.lower())]
            return filteredList

    def onContextMenu_assets(self, point):
        # This method IS Software Specific
        row = self.assets_listWidget.currentRow()
        if row == -1:
            return
        #
        #     self.scenes_rcItem_1.setEnabled(False)
        #     self.scenes_rcItem_2.setEnabled(False)
        #     self.scenes_rcItem_3.setEnabled(False)
        #     self.scenes_rcItem_4.setEnabled(False)
        #     self.scenes_rcItem_5.setEnabled(False)
        #     self.scenes_rcItem_6.setEnabled(True)
        # else:
        #     self.scenes_rcItem_1.setEnabled(os.path.isdir(manager.currentBaseScenePath))
        #     self.scenes_rcItem_2.setEnabled(os.path.isdir(manager.currentPreviewPath))
        #     self.scenes_rcItem_3.setEnabled(True)
        #     self.scenes_rcItem_4.setEnabled(True)
        #     # show context menu
        #     self.scenes_rcItem_5.setEnabled(os.path.isdir(os.path.join(manager.projectDir, "images", manager.currentBaseSceneName)))
        #     self.scenes_rcItem_6.setEnabled(True)

        self.popMenu_assets.exec_(self.assets_listWidget.mapToGlobal(point))


    def rcAction_assets(self, item):
        currentItem = self.assets_listWidget.currentItem()
        name = currentItem.text()

        if item == 'showInExplorer':
            self.library.showInExplorer(name)

        elif item == 'viewModeChange':
            self.viewModeState = self.viewModeState * -1
            if self.viewModeState == 1:
                self.assets_rcItem_0.setText("View As List")
                self.populate()
                # self.assets_listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
            elif self.viewModeState == -1:
                self.assets_rcItem_0.setText("View As Icons")
                self.populate()
                # self.assets_listWidget.setViewMode(QtWidgets.QListWidget.ListMode)

    def _checkValidity(self, text, button, lineEdit, allowSpaces=False):

        if allowSpaces:
            pattern = "^[ A-Za-z0-9_-]*$"
        else:
            pattern = "^[A-Za-z0-9_-]*$"

        if re.match(pattern, text):
            lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: white")
            button.setEnabled(True)
            # return True
        else:
            lineEdit.setStyleSheet("background-color: red; color: black")
            button.setEnabled(False)
            # return False


class ImageWidget(QtWidgets.QLabel):
    """Custom class for thumbnail section. Keeps the aspect ratio when resized."""
    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    if FORCE_QT4:
        leftClicked = QtCore.pyqtSignal(float)
    else:
        leftClicked = QtCore.Signal(float)


    def __init__(self, parent=None):
        super(ImageWidget, self).__init__()
        self.aspectRatio = 1.0
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, r):
        h = self.width()
        self.setMinimumHeight(h/self.aspectRatio)
        self.setMaximumHeight(h/self.aspectRatio)

    def mousePressEvent(self, event):
        self.leftClicked.emit(1)

class QtImageViewer(QtWidgets.QGraphicsView):
    """ PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.
    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).
    To display any other image format, you must first convert it to a QImage or QPixmap.
    Some useful image format conversion utilities:
        qimage2ndarray: NumPy ndarray <==> QImage    (https://github.com/hmeine/qimage2ndarray)
        ImageQt: PIL Image <==> QImage  (https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)
    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.
    """

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    if FORCE_QT4:
        leftMouseButtonPressed = QtCore.pyqtSignal(float, float)
        rightMouseButtonPressed = QtCore.pyqtSignal(float, float)
        leftMouseButtonReleased = QtCore.pyqtSignal(float, float)
        rightMouseButtonReleased = QtCore.pyqtSignal(float, float)
        leftMouseButtonDoubleClicked = QtCore.pyqtSignal(float, float)
        rightMouseButtonDoubleClicked = QtCore.pyqtSignal(float, float)
    else:
        leftMouseButtonPressed = QtCore.Signal(float, float)
        rightMouseButtonPressed = QtCore.Signal(float, float)
        leftMouseButtonReleased = QtCore.Signal(float, float)
        rightMouseButtonReleased = QtCore.Signal(float, float)
        leftMouseButtonDoubleClicked = QtCore.Signal(float, float)
        rightMouseButtonDoubleClicked = QtCore.Signal(float, float)

    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        # self.aspectRatioMode = QtCore.Qt.KeepAspectRatio
        self.aspectRatioMode = QtCore.Qt.IgnoreAspectRatio
        self.aspectRatio = 1.0

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = True

    def hasImage(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None

    def clearImage(self):
        """ Removes the current image pixmap from the scene if it exists.
        """
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if FORCE_QT4:
            if type(image) is QtWidgets.QPixmap:
                pixmap = image
            elif type(image) is QtWidgets.QImage:
                pixmap = QtWidgets.QPixmap.fromImage(image)
            else:
                raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")
        else:
            if type(image) is QtGui.QPixmap:
                pixmap = image
            elif type(image) is QtGui.QImage:
                pixmap = QtGui.QPixmap.fromImage(image)
            else:
                raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")

        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)
        self.setSceneRect(QtCore.QRectF(pixmap.rect()))  # Set scene size to image size.
        self.updateViewer()

    def loadImageFromFile(self, fileName=""):
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if len(fileName) == 0:
            if QtCore.QT_VERSION_STR[0] == '5':
                fileName, dummy = QtWidgets.QFileDialog.getOpenFileName(self, "Open image file.")
            else:
                fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open image file.")

        if len(fileName) and os.path.isfile(fileName):
            image = QtWidgets.QImage(fileName)
            self.setImage(image)

    def updateViewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], QtCore.Qt.IgnoreAspectRatio)  # Show zoomed rect (ignore aspect ratio).
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        ## Edited to keep the image ratio fixed
        h = self.width()
        self.setMinimumHeight(h / self.aspectRatio)
        self.setMaximumHeight(h /self.aspectRatio)
        self.updateViewer()

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if self.canPan:
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QtWidgets.QPainterPath())  # Clear current selection area.
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

    def mouseDoubleClickEvent(self, event):
        """ Show entire image.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                self.zoomStack = []  # Clear zoom stack.
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        QtWidgets.QGraphicsView.mouseDoubleClickEvent(self, event)



if __name__ == '__main__':
    os.environ["FORCE_QT4"] = "True"
    app = QtWidgets.QApplication(sys.argv)
    selfLoc = os.path.dirname(os.path.abspath(__file__))
    stylesheetFile = os.path.join(selfLoc, "CSS", "darkorange.stylesheet")

    with open(stylesheetFile, "r") as fh:
        app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    #
    # window = MainUI(projectPath= os.path.normpath("E:\\SceneManager_Projects\\SceneManager_DemoProject_None_181101"))
    # window.show()
    sys.exit(app.exec_())