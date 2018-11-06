# This version works with Pyinstaller. Make sure it is up to date

import SmRoot
reload(SmRoot)
from SmRoot import RootManager
from PyQt4 import QtCore, QtGui, Qt

import IvStandalone
import _version
import subprocess
# import json
import sys, os
import pprint
import logging




__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2018, Scene Manager for Maya Project"
__credits__ = []
__version__ = "2.0.0"
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

SM_Version = "Scene Manager Standalone v%s" %_version.__version__

logging.basicConfig()
logger = logging.getLogger('smStandalone')
logger.setLevel(logging.DEBUG)

# def excepthook(excType, excValue, tracebackobj):
#     """Overrides sys.excepthook for gui feedback"""
#
#     errorCodeDict = {200: "Corrupted File",
#                      201: "Missing File",
#                      202: "Read/Write Error",
#                      203: "Delete Error",
#                      210: "OS Not Supported",
#                      101: "Out of range",
#                      102: "Missing Override",
#                      340: "Naming Error",
#                      341: "Mandatory fields are not filled",
#                      360: "Action not permitted"}
#
#
#     errorCode = excValue[0][0]
#     errorMsg = excValue[0][1]
#
#     if errorCode == 200: # question box for this
#         q = QtGui.QMessageBox()
#         q.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
#         q.setText(errorMsg)
#         q.setWindowTitle(errorCodeDict[errorCode])
#         ret = q.exec_()
#         if ret == QtGui.QMessageBox.Yes:
#             os.startfile(excValue[0][2])
#         elif ret == QtGui.QMessageBox.No:
#             pass
#             # print "no"
#
#     else:
#         errorbox = QtGui.QMessageBox()
#         errorbox.setText(errorMsg)
#         errorbox.setWindowTitle(errorCodeDict[errorCode])
#         errorbox.exec_()
#
# sys.excepthook = excepthook

class SwViewer(RootManager):
    def __init__(self, swDict, projectDir):
        super(SwViewer, self).__init__()
        self.swDict = swDict
        self.niceName = swDict["niceName"]
        self.projectDir = projectDir

        self.init_paths()
        self.init_database()

    def getSoftwarePaths(self):
        """Overriden function"""
        return self.swDict

    def getProjectDir(self):
        """Overriden function"""
        return self.projectDir

    def getSceneFile(self):
        """Overriden function"""
        return ""

    def getExecutables(self, rootPath, relativePath, executableList, searchword=None):
        if searchword:
            try:
                versionRoots = [x for x in os.listdir(rootPath) if x.startswith(searchword) and os.path.isdir(os.path.join(rootPath, x))]
            except WindowsError:
                msg = "Cannot resolve executable paths"
                self._exception(360, msg)
                return
        else:
            try:
                versionRoots = [x for x in os.listdir(rootPath) if os.path.isdir(os.path.join(rootPath, x))]
            except WindowsError:
                msg = "Cannot resolve executable paths"
                self._exception(360, msg)
                return
        for v in versionRoots:
            exeDir = os.path.join(rootPath, v, relativePath)
            for exe in executableList:
                exePath = os.path.join(exeDir, exe)
                if os.path.isfile(exePath):
                    yield [v, exePath]

    def executeScene(self):
        if self.currentPlatform is not "Windows":
            logger.warning("Currently only windows executables are supported")
            return None

        ID = self._currentSceneInfo["ID"]

        if ID.startswith("SmMaya"):
            swID = "SmMaya"
        elif ID.startswith("Sm3dsmax"):
            swID = "Sm3dsmax"
        elif ID.startswith("SmHoudini"):
            swID = "SmHoudini"
        else:
            msg = "Cannot resolve software version from database"
            self._exception(360, msg)
            return



        # resolve executables
        programFiles32 = os.environ["PROGRAMFILES(X86)"]
        programFiles64 = os.environ["PROGRAMFILES"]

        pDict={"SmMaya":
                    {
                        "root": "Autodesk",
                        "relPath": "bin",
                        "exeList": ["maya.exe"],
                        "searchWord": "Maya"
                     },
                "Sm3dsmax":
                    {
                        "root": "Autodesk",
                        "relPath": "",
                        "exeList": ["3dsmax.exe"],
                        "searchWord": "3ds"
                    },
                "SmHoudini":
                    {
                        "root": "Side Effects Software",
                        "relPath": "bin",
                        "exeList": ["houdini.exe", "houdinifx.exe"],
                        "searchWord": "Hou"
                    }

                }
        exeGen32Bit = self.getExecutables(os.path.join(programFiles32, pDict[swID]["root"]), pDict[swID]["relPath"],
                                           pDict[swID]["exeList"], searchword=pDict[swID]["searchWord"])

        exeGen64Bit = self.getExecutables(os.path.join(programFiles64, pDict[swID]["root"]), pDict[swID]["relPath"],
                                           pDict[swID]["exeList"], searchword=pDict[swID]["searchWord"])

        # for x in exeGen64Bit:
        #     print x
        if not exeGen32Bit and exeGen64Bit:
            msg = "Cannot resolve executable paths"
            self._exception(360, msg)
            return

        # resolve versions

        #----
        #MAYA
        #----
        if swID == "SmMaya":
            versionDict = {201400: "Maya2014",
                           201450: "Maya2014",
                           201451: "Maya2014",
                           201459: "Maya2014",
                           201402: "Maya2014",
                           201404: "Maya2014",
                           201406: "Maya2014",
                           201500: "Maya2015",
                           201506: "Maya2015",
                           201507: "Maya2015",
                           201501: "Maya2015",
                           201502: "Maya2015",
                           201505: "Maya2015",
                           201506: "Maya2015",
                           201507: "Maya2015",
                           201600: "Maya2016",
                           201650: "Maya2016.5",
                           201651: "Maya2016.5",
                           201653: "Maya2016.5",
                           201605: "Maya2016",
                           201607: "Maya2016",
                           201650: "Maya2016.5",
                           201651: "Maya2016.5",
                           201653: "Maya2016.5",
                           201605: "Maya2016",
                           201607: "Maya2016",
                           201700: "Maya2017",
                           201701: "Maya2017",
                           201720: "Maya2017",
                           201740: "Maya2017",
                           20180000: "Maya2018"}
            try:
                versionName = versionDict[self._currentSceneInfo["MayaVersion"]]
            except KeyError:
                msg = "Maya version cannot resolved"
                self._exception(360, msg)
                return

            exePath = None
            for v in exeGen64Bit:
                if v[0] == versionName:
                    exePath = v[1]
                    break
            for v in exeGen32Bit:
                if v[0] == versionName:
                    exePath = v[1]
                    break

            if not exePath:
                msg = "%s is not installed on this workstation" %versionName
                self._exception(360, msg)
                return
            # subprocess.check_call([exePath, "-file", self.currentScenePath], shell=True)
            subprocess.Popen([exePath, "-file", self.currentScenePath], shell=True)
            return

        elif swID == "Sm3dsMax":
            versionDict = {16000: "3ds Max 2014",
                           17000: "3ds Max 2015",
                           18000: "3ds Max 2016",
                           19000: "3ds Max 2017",
                           20000: "3ds Max 2018"
                           }
            try:
                versionName = versionDict[self._currentSceneInfo["3dsMaxVersion"][0]]
            except KeyError:
                msg = "3ds Max version cannot resolved"
                self._exception(360, msg)
                return

            exePath = None
            for v in exeGen64Bit:
                if v[0] == versionName:
                    exePath = v[1]
                    break
            for v in exeGen32Bit:
                if v[0] == versionName:
                    exePath = v[1]
                    break

            if not exePath:
                msg = "%s is not installed on this workstation" % versionName
                self._exception(360, msg)
                return
            # subprocess.check_call([exePath, "-file", self.currentScenePath], shell=True)
            subprocess.Popen([exePath, "-file", self.currentScenePath], shell=True)
            return

        elif swID == "SmHoudini":
            for v in exeGen64Bit:
                versionNumber = v[0].split()[1]
                versionAsList = [int(s) for s in versionNumber.split(".") if s.isdigit()]
                print v
                print versionAsList
                print "database", self._currentSceneInfo["HoudiniVersion"]

            # return

    def _exception(self, code, msg):
        """OVERRIDEN"""
        # logger.error("Exception %s" %self.errorCodeDict[code])
        # logger.error(msg)

        errorbox = QtGui.QMessageBox()
        errorbox.setModal(True)
        errorbox.setText(msg)
        errorbox.setWindowTitle(self.errorCodeDict[code])
        errorbox.exec_()

        if (200 >= code < 210):
            raise Exception(code, msg)


class StandaloneManager(RootManager):
    def __init__(self):
        super(StandaloneManager, self).__init__()

        self.swDictList = [{"niceName": "3dsMax",
                            "databaseDir": "maxDB",
                            "scenesDir": "scenes_3dsMax",
                            "pbSettingsFile": "pbSettings_3dsMax.json",
                            "categoriesFile": "categories3dsMax.json",
                            "userSettingsDir": "Documents\\SceneManager\\3dsMax"},

                           {"niceName": "Maya",
                            "databaseDir": "mayaDB",
                            "scenesDir": "scenes",
                            "pbSettingsFile": "pbSettings.json",
                            "categoriesFile": "categoriesMaya.json",
                            "userSettingsDir": "Documents\\SceneManager\\Maya"},

                           {"niceName": "Houdini",
                            "databaseDir": "houdiniDB",
                            "scenesDir": "scenes_houdini",
                            "pbSettingsFile": "pbSettings_houdini.json",
                            "categoriesFile": "categoriesHoudini.json",
                            "userSettingsDir": "Documents\\SceneManager\\Houdini"}

                           ]

        # self.validSoftwares = []
        self.swList = []
        self.init_paths()
        self.init_database()

        self.initSoftwares()


    def init_paths(self):
        """Overriden function"""
        # homeDir = os.path.expanduser("~")
        # self.userSettingsDir = os.path.normpath(os.path.join(homeDir, "Documents", "SceneManager", "Standalone"))
        # self._folderCheck(self.userSettingsDir)
        # self.projectsFile = os.path.join(self.userSettingsDir, "smProjects.json")

        self._pathsDict["userSettingsDir"] = os.path.normpath(os.path.join(os.path.expanduser("~"), "Documents", "SceneManager", "Standalone"))
        self._folderCheck(self._pathsDict["userSettingsDir"])

        self._pathsDict["bookmarksFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smBookmarks.json"))
        self._pathsDict["currentsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smCurrents.json"))
        self._pathsDict["projectsFile"] = os.path.normpath(os.path.join(self._pathsDict["userSettingsDir"], "smProjects.json"))


        self._pathsDict["projectDir"] = self.getProjectDir()
        self._pathsDict["sceneFile"] = ""

        self._pathsDict["masterDir"] = os.path.normpath(os.path.join(self._pathsDict["projectDir"], "smDatabase"))

        self._pathsDict["projectSettingsFile"] = os.path.normpath(os.path.join(self._pathsDict["masterDir"], "projectSettings.json"))


        self._pathsDict["generalSettingsDir"] = os.path.dirname(os.path.abspath(__file__))
        self._pathsDict["usersFile"] = os.path.normpath(os.path.join(self._pathsDict["generalSettingsDir"], "sceneManagerUsers.json"))

    def init_database(self):
        """Overriden function"""

        self._usersDict = self._loadUsers()
        self._currentsDict = self._loadUserPrefs()

    def getProjectDir(self):
        """Overriden function"""
        # get the projects file for standalone manager
        projectsDict = self._loadProjects()

        if not projectsDict:
            norm_p_path = os.path.normpath(os.path.expanduser("~"))
            projectsDict = {"StandaloneProject": norm_p_path}
            self._saveProjects(projectsDict)
            return norm_p_path

        # get the project defined in the database file
        try:
            norm_p_path = projectsDict["StandaloneProject"]
            return norm_p_path
        except KeyError:
            norm_p_path = os.path.normpath(os.path.expanduser("~"))
            projectsDict = {"StandaloneProject": norm_p_path}
            self._saveProjects(projectsDict)
            return norm_p_path

    def setProject(self, path):
        """Sets the project"""
        # logger.debug("Func: setProject")
        # self.currentProject = path
        # # totally software specific or N/A
        #
        # # self.projectDir = cmds.workspace(q=1, rd=1)
        projectsDict = self._loadProjects()
        if not projectsDict:
            projectsDict = {"StandaloneProject": path}
        else:
            projectsDict["StandaloneProject"] = path
        self._saveProjects(projectsDict)
        self.projectDir = path
        self.init_paths()
        self.init_database()
        self.initSoftwares()


    def initSoftwares(self):
        # We need to get which softwares are used in the current project
        self.swList = []
        dbFolder = self._pathsDict["masterDir"]
        if not os.path.isdir(dbFolder):
            self.swList = [] # empty software list
            return self.swList#this is not a sceneManager project
        for swDict in self.swDictList:
            searchPath = (os.path.join(self.projectDir, "smDatabase", swDict["databaseDir"]))
            if os.path.isdir(searchPath):
                self.swList.append(SwViewer(swDict, self.projectDir))
        return self.swList

    # def initTlocation(self, path):
    #     """
    #     Sets the Remote Server transfer location and saves it into the json database
    #     Args:
    #         path: (String) Path of the remote directory
    #
    #     Returns: None
    #
    #     """
    #     projectPath = self.getProjectDir()
    #     jsonPath = os.path.normpath(os.path.join(projectPath, "smDatabase"))
    #     if not os.path.isdir(jsonPath):
    #         logger.warning("NOT SCENE MANAGER PROJECT")
    #         return None
    #     tLocationFile = os.path.normpath(os.path.join(jsonPath, "tLocation.json"))
    #     self._dumpJson(path, tLocationFile)
    #     return tLocationFile


    @property
    def currentSwIndex(self):
        """returns current sofware"""
        return self._currentsDict["currentSwIndex"]

    @currentSwIndex.setter
    def currentSwIndex(self, indexData):
        """Moves the cursor to the given software index"""
        if not 0 <= indexData < len(self.swList):
            msg="Software index is out of range!"
            raise Exception([101, msg])
        if indexData == self.currentSwIndex:
            self.swList[indexData].cursorInfo()
            return
        self._setCurrents("currentSwIndex", indexData)
        # self.swList[indexData].scanBaseScenes()
        # self.swList[indexData].currentBaseSceneName = ""
        # self.swList[indexData]._currentPreviewCamera = ""
        # self.swList[indexData].cursorInfo()
        pass

    # def getSoftwareList(self):
    #     return self.swList

    def _exception(self, code, msg):
        """OVERRIDEN"""
        logger.error("Exception %s" %self.errorCodeDict[code])
        logger.error(msg)

        errorCodeDict = {200: "Corrupted File",
                         201: "Missing File",
                         202: "Read/Write Error",
                         203: "Delete Error",
                         210: "OS Not Supported",
                         101: "Out of range",
                         102: "Missing Override",
                         340: "Naming Error",
                         341: "Mandatory fields are not filled",
                         360: "Action not permitted"}


        errorbox = QtGui.QMessageBox()
        errorbox.setModal(True)
        errorbox.setText(msg)
        errorbox.setWindowTitle(errorCodeDict[code])
        errorbox.exec_()

        if (200 >= code < 210):
            raise Exception(code, msg)


    def _loadUserPrefs(self):
        """OVERRIDEN FUNCTION Load Last CategoryIndex, SubProject Index,
        User name and Access mode from file as dictionary"""
        if os.path.isfile(self._pathsDict["currentsFile"]):
            settingsData = self._loadJson(self._pathsDict["currentsFile"])
            if settingsData == -2:
                return -2
        else:
            settingsData = {"currentTabIndex": 0,
                            "currentSubIndex": 0,
                            "currentUser": self._usersDict.keys()[0],
                            "currentSwIndex": -1} # added multi software switch
            self._dumpJson(settingsData, self._pathsDict["currentsFile"])
        return settingsData




    # def getAllBaseScenes(self):
    #     """Collects all base scenes for each category at cursor category and subproject"""
    #     pass

    # def _folderCheck(self, folder):
    #     if not os.path.isdir(os.path.normpath(folder)):
    #         os.makedirs(os.path.normpath(folder))
    #
    # def _loadJson(self, file):
    #     """Loads the given json file"""
    #     if os.path.isfile(file):
    #         try:
    #             with open(file, 'r') as f:
    #                 data = json.load(f)
    #                 return data
    #         except ValueError:
    #             msg = "Corrupted JSON file => %s" % file
    #             return -2 # code for corrupted json file
    #     else:
    #         return None
    #
    # def _dumpJson(self, data, file):
    #     """Saves the data to the json file"""
    #     with open(file, "w") as f:
    #         json.dump(data, f, indent=4)



class MainUI(QtGui.QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()

        self.swColorDict = {"Maya": "rgb(81, 230, 247, 255)",
                            "3dsMax": "rgb(150, 247, 81, 255)",
                            "Houdini": "rgb(247, 172, 81, 255)",
                            "":  "rgb(0, 0, 0, 0)",
                            }

        self.masterManager = StandaloneManager()

        self.setObjectName(SM_Version)
        self.resize(680, 600)
        self.setWindowTitle(SM_Version)
        self.centralwidget = QtGui.QWidget(self)

        self.buildUI()

        self.setCentralWidget(self.centralwidget)

        self.initMainUI(newborn=True)

    def buildUI(self):

        self.main_gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.main_gridLayout.setObjectName(("main_gridLayout"))

        self.main_horizontalLayout = QtGui.QHBoxLayout()
        self.main_horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.main_horizontalLayout.setSpacing(6)
        self.main_horizontalLayout.setObjectName(("horizontalLayout"))
        self.main_horizontalLayout.setStretch(0, 1)

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.main_horizontalLayout.addItem(spacerItem)

        self.loadScene_pushButton = QtGui.QPushButton(self.centralwidget)
        self.loadScene_pushButton.setMinimumSize(QtCore.QSize(150, 45))
        self.loadScene_pushButton.setMaximumSize(QtCore.QSize(150, 45))
        self.loadScene_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.loadScene_pushButton.setText(("Load Scene"))
        self.loadScene_pushButton.setObjectName(("loadScene_pushButton"))
        self.main_horizontalLayout.addWidget(self.loadScene_pushButton)
        #
        self.main_gridLayout.addLayout(self.main_horizontalLayout, 4, 0, 1, 1)
        #
        self.r2_gridLayout = QtGui.QGridLayout()
        self.r2_gridLayout.setObjectName(("r2_gridLayout"))
        self.r2_gridLayout.setColumnStretch(1, 1)

        self.software_label = QtGui.QLabel(self.centralwidget)
        self.software_label.setText("Software:")
        self.software_label.setObjectName(("software_label"))
        self.r2_gridLayout.addWidget(self.software_label, 0, 0, 1, 1)

        self.software_comboBox = QtGui.QComboBox(self.centralwidget)
        self.software_comboBox.setMinimumSize(QtCore.QSize(150, 30))
        self.software_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.software_comboBox.setObjectName(("software_comboBox"))
        self.r2_gridLayout.addWidget(self.software_comboBox, 0, 1, 1, 1)

        self.subProject_label = QtGui.QLabel(self.centralwidget)
        self.subProject_label.setText(("Sub-Project:"))
        self.subProject_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.subProject_label.setObjectName(("subProject_label"))
        self.r2_gridLayout.addWidget(self.subProject_label, 0, 2, 1, 1)

        self.subProject_comboBox = QtGui.QComboBox(self.centralwidget)
        self.subProject_comboBox.setMinimumSize(QtCore.QSize(150, 30))
        self.subProject_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.subProject_comboBox.setObjectName(("subProject_comboBox"))
        self.r2_gridLayout.addWidget(self.subProject_comboBox, 0, 3, 1, 1)

        self.addSubProject_pushButton = QtGui.QPushButton(self.centralwidget)
        self.addSubProject_pushButton.setMinimumSize(QtCore.QSize(30, 30))
        self.addSubProject_pushButton.setMaximumSize(QtCore.QSize(30, 30))
        self.addSubProject_pushButton.setText(("+"))
        self.addSubProject_pushButton.setObjectName(("addSubProject_pushButton"))
        self.r2_gridLayout.addWidget(self.addSubProject_pushButton, 0, 4, 1, 1)

        self.user_label = QtGui.QLabel(self.centralwidget)
        self.user_label.setText(("User:"))
        self.user_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.user_label.setObjectName(("user_label"))
        self.r2_gridLayout.addWidget(self.user_label, 0, 5, 1, 1)

        self.user_comboBox = QtGui.QComboBox(self.centralwidget)
        self.user_comboBox.setMinimumSize(QtCore.QSize(130, 30))
        self.user_comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.user_comboBox.setObjectName(("user_comboBox"))
        self.r2_gridLayout.addWidget(self.user_comboBox, 0, 6, 1, 1)

        self.main_gridLayout.addLayout(self.r2_gridLayout, 1, 0, 1, 1)
        self.r1_gridLayout = QtGui.QGridLayout()
        self.r1_gridLayout.setObjectName(("r1_gridLayout"))

        self.project_label = QtGui.QLabel(self.centralwidget)
        self.project_label.setText(("Project:"))
        self.project_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.project_label.setObjectName(("project_label"))
        self.r1_gridLayout.addWidget(self.project_label, 1, 0, 1, 1)

        self.project_lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.project_lineEdit.setText((""))
        self.project_lineEdit.setPlaceholderText((""))
        self.project_lineEdit.setObjectName(("project_lineEdit"))
        self.project_lineEdit.setReadOnly(True)
        self.r1_gridLayout.addWidget(self.project_lineEdit, 1, 1, 1, 1)

        self.setProject_pushButton = QtGui.QPushButton(self.centralwidget)
        self.setProject_pushButton.setText(("SET"))
        self.setProject_pushButton.setObjectName(("setProject_pushButton"))
        self.r1_gridLayout.addWidget(self.setProject_pushButton, 1, 2, 1, 1)

        self.main_gridLayout.addLayout(self.r1_gridLayout, 0, 0, 1, 1)

        self.category_tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.category_tabWidget.setMaximumSize(QtCore.QSize(16777215, 20))
        self.category_tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.category_tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.category_tabWidget.setUsesScrollButtons(False)
        self.category_tabWidget.setObjectName(("tabWidget"))

        self.category_tabWidget.setCurrentIndex(self.masterManager.currentTabIndex)

        self.main_gridLayout.addWidget(self.category_tabWidget, 2, 0, 1, 1)

        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(("splitter"))


        self.scenes_listWidget = QtGui.QListWidget(self.splitter)
        self.scenes_listWidget.setObjectName(("listWidget"))
        # self.scenes_listWidget.setStyleSheet("background-color: rgb(80,80,80); color: white")

        self.frame = QtGui.QFrame(self.splitter)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(("frame"))

        self.gridLayout_6 = QtGui.QGridLayout(self.frame)
        self.gridLayout_6.setContentsMargins(-1, -1, 0, 0)
        self.gridLayout_6.setObjectName(("gridLayout_6"))

        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(("verticalLayout"))

        self.notes_label = QtGui.QLabel(self.frame)
        self.notes_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.notes_label.setText(("Version Notes:"))
        self.notes_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.notes_label.setObjectName(("version_label_2"))
        self.verticalLayout.addWidget(self.notes_label)

        self.notes_textEdit = QtGui.QTextEdit(self.frame)
        self.notes_textEdit.setObjectName(("textEdit"))
        self.notes_textEdit.setReadOnly(True)
        self.verticalLayout.addWidget(self.notes_textEdit)

        self.tPixmap = QtGui.QPixmap("")
        self.thumbnail_label = ImageWidget(self.frame)
        self.thumbnail_label.setPixmap(self.tPixmap)

        self.thumbnail_label.setMinimumSize(QtCore.QSize(221, 124))
        self.thumbnail_label.setFrameShape(QtGui.QFrame.Box)
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail_label.setObjectName(("label"))
        self.verticalLayout.addWidget(self.thumbnail_label)

        self.gridLayout_6.addLayout(self.verticalLayout, 3, 0, 1, 1)

        self.gridLayout_7 = QtGui.QGridLayout()
        self.gridLayout_7.setContentsMargins(-1, -1, 10, 10)
        self.gridLayout_7.setObjectName(("gridLayout_7"))

        self.showPreview_pushButton = QtGui.QPushButton(self.frame)
        self.showPreview_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.showPreview_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.showPreview_pushButton.setText(("Show Preview"))
        self.showPreview_pushButton.setObjectName(("setProject_pushButton_5"))
        self.gridLayout_7.addWidget(self.showPreview_pushButton, 0, 3, 1, 1)

        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(1)
        self.horizontalLayout_4.setObjectName(("horizontalLayout_4"))

        self.version_label = QtGui.QLabel(self.frame)
        self.version_label.setMinimumSize(QtCore.QSize(60, 30))
        self.version_label.setMaximumSize(QtCore.QSize(60, 30))
        self.version_label.setFrameShape(QtGui.QFrame.Box)
        self.version_label.setText(("Version:"))
        self.version_label.setAlignment(QtCore.Qt.AlignCenter)
        self.version_label.setObjectName(("version_label"))
        self.horizontalLayout_4.addWidget(self.version_label)

        self.version_comboBox = QtGui.QComboBox(self.frame)
        self.version_comboBox.setMinimumSize(QtCore.QSize(60, 30))
        self.version_comboBox.setMaximumSize(QtCore.QSize(100, 30))
        self.version_comboBox.setObjectName(("version_comboBox"))
        self.horizontalLayout_4.addWidget(self.version_comboBox)

        self.gridLayout_7.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)

        self.makeReference_pushButton = QtGui.QPushButton(self.frame)
        self.makeReference_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.makeReference_pushButton.setMaximumSize(QtCore.QSize(300, 30))
        self.makeReference_pushButton.setText(("Make Reference"))
        self.makeReference_pushButton.setObjectName(("makeReference_pushButton"))
        self.gridLayout_7.addWidget(self.makeReference_pushButton, 1, 0, 1, 1)

        self.addNote_pushButton = QtGui.QPushButton(self.frame)
        self.addNote_pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.addNote_pushButton.setMaximumSize(QtCore.QSize(150, 30))
        self.addNote_pushButton.setToolTip((""))
        self.addNote_pushButton.setStatusTip((""))
        self.addNote_pushButton.setWhatsThis((""))
        self.addNote_pushButton.setAccessibleName((""))
        self.addNote_pushButton.setAccessibleDescription((""))
        self.addNote_pushButton.setText(("Add Note"))
        self.addNote_pushButton.setObjectName(("addNote_pushButton"))
        self.gridLayout_7.addWidget(self.addNote_pushButton, 1, 3, 1, 1)

        self.gridLayout_6.addLayout(self.gridLayout_7, 0, 0, 1, 1)

        self.main_gridLayout.addWidget(self.splitter, 3, 0, 1, 1)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self.splitter.setSizePolicy(sizePolicy)

        self.splitter.setStretchFactor(0, 1)

        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 18))
        self.menubar.setObjectName(("menubar"))

        self.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName(("statusbar"))
        self.setStatusBar(self.statusbar)

        # MENU BAR / STATUS BAR
        # ---------------------
        file = self.menubar.addMenu("File")
        loadReferenceScene_fm = QtGui.QAction("&Load/Reference Scene", self)
        createProject_fm = QtGui.QAction("&Create Project", self)
        add_remove_users_fm = QtGui.QAction("&Add/Remove Users", self)
        add_remove_categories_fm = QtGui.QAction("&Add/Remove Categories", self)
        projectSettings_fm = QtGui.QAction("&Project Settings", self)

        # TODO : ref
        changeAdminPass_fm = QtGui.QAction("&Change Admin Password", self)


        deleteFile_fm = QtGui.QAction("&Delete Selected Base Scene", self)
        deleteReference_fm = QtGui.QAction("&Delete Reference of Selected Scene", self)
        reBuildDatabase_fm = QtGui.QAction("&Re-build Project Database", self)
        projectReport_fm = QtGui.QAction("&Project Report", self)
        checkReferences_fm = QtGui.QAction("&Check References", self)

        #save
        file.addAction(createProject_fm)

        #load
        file.addSeparator()
        file.addAction(loadReferenceScene_fm)

        #settings
        file.addSeparator()
        file.addAction(add_remove_users_fm)
        file.addAction(add_remove_categories_fm)
        file.addAction(projectSettings_fm)
        # TODO : ref
        file.addAction(changeAdminPass_fm)

        #delete
        file.addSeparator()
        file.addAction(deleteFile_fm)
        file.addAction(deleteReference_fm)

        #misc
        file.addSeparator()
        file.addAction(projectReport_fm)
        file.addAction(checkReferences_fm)

        tools = self.menubar.addMenu("Tools")
        iviewer = QtGui.QAction("&Image Viewer", self)

        tools.addAction(iviewer)


        # RIGHT CLICK MENUS
        # -----------------

        # List Widget Right Click Menu
        self.scenes_listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.scenes_listWidget.customContextMenuRequested.connect(self.onContextMenu_scenes)
        self.popMenu_scenes = QtGui.QMenu()

        self.scenes_rcItem_0 = QtGui.QAction('Import Scene', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_0)
        self.scenes_rcItem_0.triggered.connect(lambda: self.rcAction_scenes("importScene"))

        self.scenes_rcItem_1 = QtGui.QAction('Show Project File in Explorer', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_1)
        self.scenes_rcItem_1.triggered.connect(lambda: self.rcAction_scenes("showInExplorerMaya"))

        self.scenes_rcItem_2 = QtGui.QAction('Show Playblast Folder in Explorer', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_2)
        self.scenes_rcItem_2.triggered.connect(lambda: self.rcAction_scenes("showInExplorerPB"))

        self.scenes_rcItem_3 = QtGui.QAction('Show Data Folder in Explorer', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_3)
        self.scenes_rcItem_3.triggered.connect(lambda: self.rcAction_scenes("showInExplorerData"))

        self.popMenu_scenes.addSeparator()
        self.scenes_rcItem_4 = QtGui.QAction('Scene Info', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_4)
        self.scenes_rcItem_4.triggered.connect(lambda: self.rcAction_scenes("showSceneInfo"))

        self.popMenu_scenes.addSeparator()
        self.scenes_rcItem_5 = QtGui.QAction('View Rendered Images', self)
        self.popMenu_scenes.addAction(self.scenes_rcItem_5)
        self.scenes_rcItem_5.triggered.connect(lambda: self.rcAction_scenes("viewRender"))

        # Thumbnail Right Click Menu
        self.thumbnail_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.thumbnail_label.customContextMenuRequested.connect(self.onContextMenu_thumbnail)
        self.popMenu_thumbnail = QtGui.QMenu()

        rcAction_thumb_0 = QtGui.QAction('Replace with current view', self)
        self.popMenu_thumbnail.addAction(rcAction_thumb_0)
        rcAction_thumb_0.triggered.connect(lambda: self.rcAction_thumb("currentView"))


        rcAction_thumb_1 = QtGui.QAction('Replace with external file', self)
        self.popMenu_thumbnail.addAction(rcAction_thumb_1)
        rcAction_thumb_1.triggered.connect(lambda: self.rcAction_thumb("file"))


        # SHORTCUTS
        # ---------
        shortcutRefresh = Qt.QShortcut(Qt.QKeySequence("F5"), self, self.refresh)

        # SIGNAL CONNECTIONS
        # ------------------

        createProject_fm.triggered.connect(self.createProjectUI)
        #
        add_remove_users_fm.triggered.connect(self.addRemoveUserUI)
        add_remove_categories_fm.triggered.connect(self.addRemoveCategoryUI)

        projectSettings_fm.triggered.connect(self.projectSettingsUI)

        # TODO : ref
        changeAdminPass_fm.triggered.connect(self.changePasswordUI)


        deleteFile_fm.triggered.connect(self.onDeleteBaseScene)

        deleteReference_fm.triggered.connect(self.onDeleteReference)

        checkReferences_fm.triggered.connect(lambda: self.populateBaseScenes(deepCheck=True))

        iviewer.triggered.connect(self.onIviewer)

        self.statusBar().showMessage("Status | Idle")



        self.category_tabWidget.currentChanged.connect(self.onCategoryChange)

        self.scenes_listWidget.currentItemChanged.connect(self.onBaseSceneChange)

        self.version_comboBox.activated.connect(self.onVersionChange)

        self.makeReference_pushButton.clicked.connect(self.onMakeReference)

        self.subProject_comboBox.activated.connect(self.onSubProjectChange)

        self.user_comboBox.activated.connect(self.onUserChange)

        self.showPreview_pushButton.clicked.connect(self.onShowPreview)

        self.addSubProject_pushButton.clicked.connect(self.createSubProjectUI)

        self.setProject_pushButton.clicked.connect(self.setProjectUI)

        self.scenes_listWidget.doubleClicked.connect(self.onLoadScene)
        self.loadScene_pushButton.clicked.connect(self.onLoadScene)

        self.addNote_pushButton.clicked.connect(self.addNoteDialog)

        self.software_comboBox.activated.connect(self.onSoftwareChange)



    def createSubProjectUI(self):

        newSub, ok = QtGui.QInputDialog.getText(self, "Create New Sub-Project", "Enter an unique Sub-Project name:")
        if ok:
            if self.masterManager._nameCheck(newSub):
                self.subProject_comboBox.clear()
                self.subProject_comboBox.addItems(self.masterManager.createSubproject(newSub))
                self.subProject_comboBox.setCurrentIndex(self.masterManager.currentSubIndex)
                self.populateBaseScenes()
            else:
                self.infoPop(textTitle="Naming Error", textHeader="Naming Error",
                             textInfo="Choose an unique name with latin characters without spaces", type="C")

    def createProjectUI(self):

        self.createproject_Dialog = QtGui.QDialog(parent=self)
        self.createproject_Dialog.setObjectName(("createproject_Dialog"))
        self.createproject_Dialog.resize(419, 300)
        self.createproject_Dialog.setWindowTitle(("Create New Project"))

        self.projectroot_label = QtGui.QLabel(self.createproject_Dialog)
        self.projectroot_label.setGeometry(QtCore.QRect(20, 30, 71, 20))
        self.projectroot_label.setText(("Project Path:"))
        self.projectroot_label.setObjectName(("projectpath_label"))

        currentProjects = os.path.abspath(os.path.join(self.masterManager.projectDir, os.pardir))
        self.projectroot_lineEdit = QtGui.QLineEdit(self.createproject_Dialog)
        self.projectroot_lineEdit.setGeometry(QtCore.QRect(90, 30, 241, 21))
        self.projectroot_lineEdit.setText((currentProjects))
        self.projectroot_lineEdit.setObjectName(("projectpath_lineEdit"))

        self.browse_pushButton = QtGui.QPushButton(self.createproject_Dialog)
        self.browse_pushButton.setText(("Browse"))
        self.browse_pushButton.setGeometry(QtCore.QRect(340, 30, 61, 21))
        self.browse_pushButton.setObjectName(("browse_pushButton"))

        self.resolvedpath_label = QtGui.QLabel(self.createproject_Dialog)
        self.resolvedpath_label.setGeometry(QtCore.QRect(20, 70, 381, 21))
        self.resolvedpath_label.setObjectName(("resolvedpath_label"))

        self.brandname_label = QtGui.QLabel(self.createproject_Dialog)
        self.brandname_label.setGeometry(QtCore.QRect(20, 110, 111, 20))
        self.brandname_label.setFrameShape(QtGui.QFrame.Box)
        self.brandname_label.setText(("Brand Name"))
        self.brandname_label.setAlignment(QtCore.Qt.AlignCenter)
        self.brandname_label.setObjectName(("brandname_label"))

        self.projectname_label = QtGui.QLabel(self.createproject_Dialog)
        self.projectname_label.setGeometry(QtCore.QRect(140, 110, 131, 20))
        self.projectname_label.setFrameShape(QtGui.QFrame.Box)
        self.projectname_label.setText(("Project Name"))
        self.projectname_label.setAlignment(QtCore.Qt.AlignCenter)
        self.projectname_label.setObjectName(("projectname_label"))

        self.client_label = QtGui.QLabel(self.createproject_Dialog)
        self.client_label.setGeometry(QtCore.QRect(280, 110, 121, 20))
        self.client_label.setFrameShape(QtGui.QFrame.Box)
        self.client_label.setText(("Client"))
        self.client_label.setAlignment(QtCore.Qt.AlignCenter)
        self.client_label.setObjectName(("client_label"))

        resolution_label = QtGui.QLabel(self.createproject_Dialog)
        resolution_label.setGeometry(QtCore.QRect(24, 180 , 111, 21))
        resolution_label.setText("Resolution")

        resolutionX_spinBox = QtGui.QSpinBox(self.createproject_Dialog)
        resolutionX_spinBox.setGeometry(QtCore.QRect(80, 180, 60, 21))
        resolutionX_spinBox.setObjectName(("resolutionX_spinBox"))
        resolutionX_spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        resolutionX_spinBox.setRange(1,99999)
        resolutionX_spinBox.setValue(1920)

        resolutionY_spinBox = QtGui.QSpinBox(self.createproject_Dialog)
        resolutionY_spinBox.setGeometry(QtCore.QRect(145, 180, 60, 21))
        resolutionY_spinBox.setObjectName(("resolutionY_spinBox"))
        resolutionY_spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        resolutionY_spinBox.setRange(1,99999)
        resolutionY_spinBox.setValue(1080)

        fps_label = QtGui.QLabel(self.createproject_Dialog)
        fps_label.setGeometry(QtCore.QRect(54, 210 , 111, 21))
        fps_label.setText("FPS")

        fps_comboBox = QtGui.QComboBox(self.createproject_Dialog)
        fps_comboBox.setGeometry(QtCore.QRect(80, 210 , 60, 21))
        fps_comboBox.addItems(self.masterManager.fpsList)
        fps_comboBox.setCurrentIndex(2)

        self.brandname_lineEdit = QtGui.QLineEdit(self.createproject_Dialog)
        self.brandname_lineEdit.setGeometry(QtCore.QRect(20, 140, 111, 21))
        self.brandname_lineEdit.setPlaceholderText(("(optional)"))
        self.brandname_lineEdit.setObjectName(("brandname_lineEdit"))

        self.projectname_lineEdit = QtGui.QLineEdit(self.createproject_Dialog)
        self.projectname_lineEdit.setGeometry(QtCore.QRect(140, 140, 131, 21))
        self.projectname_lineEdit.setPlaceholderText(("Mandatory Field"))
        self.projectname_lineEdit.setObjectName(("projectname_lineEdit"))

        self.client_lineEdit = QtGui.QLineEdit(self.createproject_Dialog)
        self.client_lineEdit.setGeometry(QtCore.QRect(280, 140, 121, 21))
        self.client_lineEdit.setPlaceholderText(("Mandatory Field"))
        self.client_lineEdit.setObjectName(("client_lineEdit"))

        self.createproject_buttonBox = QtGui.QDialogButtonBox(self.createproject_Dialog)
        self.createproject_buttonBox.setGeometry(QtCore.QRect(30, 250, 371, 32))
        self.createproject_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.createproject_buttonBox.setStandardButtons(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.createproject_buttonBox.setObjectName(("buttonBox"))

        self.cp_button = self.createproject_buttonBox.button(QtGui.QDialogButtonBox.Ok)
        self.cp_button.setText('Create Project')

        def browseProjectRoot():
            dlg = QtGui.QFileDialog()
            dlg.setFileMode(QtGui.QFileDialog.Directory)

            if dlg.exec_():
                selectedroot = os.path.normpath(str(dlg.selectedFiles()[0]))
                self.projectroot_lineEdit.setText(selectedroot)
                resolve()

        def onCreateNewProject():
            root = self.projectroot_lineEdit.text()
            pName = self.projectname_lineEdit.text()
            bName = self.brandname_lineEdit.text()
            cName = self.client_lineEdit.text()
            projectSettingsDB = {"Resolution": [resolutionX_spinBox.value(), resolutionY_spinBox.value()],
                                   "FPS": int(fps_comboBox.currentText())}
            pPath = self.masterManager.createNewProject(root, pName, bName, cName, settingsData=projectSettingsDB)
            self.masterManager.setProject(pPath)
            self.onProjectChange()
            self.scenes_listWidget.clear()
            self.createproject_Dialog.close()

        def resolve():
            if self.projectname_lineEdit.text() == "" or self.client_lineEdit.text() == "" or self.projectroot_lineEdit.text() == "":
                self.resolvedpath_label.setText("Fill the mandatory fields")
                self.newProjectPath = None
                return
            resolvedPath = self.masterManager._resolveProjectPath(self.projectroot_lineEdit.text(),
                                                                  self.projectname_lineEdit.text(),
                                                                  self.brandname_lineEdit.text(),
                                                                  self.client_lineEdit.text())
            self.resolvedpath_label.setText(resolvedPath)

        resolve()
        self.browse_pushButton.clicked.connect(browseProjectRoot)

        self.brandname_lineEdit.textEdited.connect(lambda: resolve())
        self.projectname_lineEdit.textEdited.connect(lambda: resolve())
        self.client_lineEdit.textEdited.connect(lambda: resolve())

        self.createproject_buttonBox.accepted.connect(onCreateNewProject)
        self.createproject_buttonBox.rejected.connect(self.createproject_Dialog.reject)

        self.brandname_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.brandname_lineEdit.text(), self.cp_button,
                                  self.brandname_lineEdit))
        self.projectname_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.projectname_lineEdit.text(), self.cp_button,
                                  self.projectname_lineEdit))
        self.client_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.client_lineEdit.text(), self.cp_button, self.client_lineEdit))

        self.createproject_Dialog.show()

    def setProjectUI(self):

        iconFont = QtGui.QFont()
        iconFont.setPointSize(12)
        iconFont.setBold(True)
        iconFont.setWeight(75)

        self.setProject_Dialog = QtGui.QDialog(parent=self)
        self.setProject_Dialog.setObjectName(("setProject_Dialog"))
        self.setProject_Dialog.resize(982, 450)
        self.setProject_Dialog.setWindowTitle(("Set Project"))

        gridLayout = QtGui.QGridLayout(self.setProject_Dialog)
        gridLayout.setObjectName(("gridLayout"))

        M1_horizontalLayout = QtGui.QHBoxLayout()
        M1_horizontalLayout.setObjectName(("M1_horizontalLayout"))

        lookIn_label = QtGui.QLabel(self.setProject_Dialog)
        lookIn_label.setText(("Look in:"))
        lookIn_label.setObjectName(("lookIn_label"))

        M1_horizontalLayout.addWidget(lookIn_label)

        self.lookIn_lineEdit = QtGui.QLineEdit(self.setProject_Dialog)
        self.lookIn_lineEdit.setText((""))
        self.lookIn_lineEdit.setPlaceholderText((""))
        self.lookIn_lineEdit.setObjectName(("lookIn_lineEdit"))

        M1_horizontalLayout.addWidget(self.lookIn_lineEdit)

        browse_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(browse_pushButton.sizePolicy().hasHeightForWidth())
        browse_pushButton.setSizePolicy(sizePolicy)
        browse_pushButton.setMaximumSize(QtCore.QSize(50, 16777215))
        browse_pushButton.setText("Browse")
        browse_pushButton.setObjectName(("browse_pushButton"))

        M1_horizontalLayout.addWidget(browse_pushButton)

        self.back_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.back_pushButton.sizePolicy().hasHeightForWidth())
        self.back_pushButton.setSizePolicy(sizePolicy)
        self.back_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        self.back_pushButton.setFont(iconFont)
        self.back_pushButton.setText(("<"))
        self.back_pushButton.setShortcut((""))
        self.back_pushButton.setObjectName(("back_pushButton"))

        M1_horizontalLayout.addWidget(self.back_pushButton)

        self.forward_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        self.forward_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        self.forward_pushButton.setFont(iconFont)
        self.forward_pushButton.setText((">"))
        self.forward_pushButton.setShortcut((""))
        self.forward_pushButton.setObjectName(("forward_pushButton"))

        M1_horizontalLayout.addWidget(self.forward_pushButton)

        up_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        up_pushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        up_pushButton.setText(("Up"))
        up_pushButton.setShortcut((""))
        up_pushButton.setObjectName(("up_pushButton"))

        M1_horizontalLayout.addWidget(up_pushButton)

        gridLayout.addLayout(M1_horizontalLayout, 0, 0, 1, 1)

        M2_horizontalLayout = QtGui.QHBoxLayout()
        M2_horizontalLayout.setObjectName(("M2_horizontalLayout"))

        M2_splitter = QtGui.QSplitter(self.setProject_Dialog)
        M2_splitter.setHandleWidth(10)
        M2_splitter.setObjectName(("M2_splitter"))


        # self.folders_tableView = QtWidgets.QTableView(self.M2_splitter)
        self.folders_tableView = QtGui.QTreeView(M2_splitter)
        self.folders_tableView.setMinimumSize(QtCore.QSize(0, 0))
        self.folders_tableView.setDragEnabled(True)
        self.folders_tableView.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.folders_tableView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.folders_tableView.setObjectName(("folders_tableView"))

        self.folders_tableView.setFrameShape(QtGui.QFrame.NoFrame)
        self.folders_tableView.setItemsExpandable(False)
        self.folders_tableView.setRootIsDecorated(False)
        self.folders_tableView.setSortingEnabled(True)
        # self.folders_tableView.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)


        verticalLayoutWidget = QtGui.QWidget(M2_splitter)
        verticalLayoutWidget.setObjectName(("verticalLayoutWidget"))

        M2_S2_verticalLayout = QtGui.QVBoxLayout(verticalLayoutWidget)
        M2_S2_verticalLayout.setContentsMargins(0, 10, 0, 10)
        M2_S2_verticalLayout.setSpacing(6)
        M2_S2_verticalLayout.setObjectName(("M2_S2_verticalLayout"))

        favorites_label = QtGui.QLabel(verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        favorites_label.setFont(font)
        favorites_label.setText(("Bookmarks:"))
        favorites_label.setObjectName(("favorites_label"))

        M2_S2_verticalLayout.addWidget(favorites_label)

        self.favorites_listWidget = DropListWidget(verticalLayoutWidget)
        # self.favorites_listWidget.setAlternatingRowColors(True)
        self.favorites_listWidget.setObjectName(("favorites_listWidget"))

        M2_S2_verticalLayout.addWidget(self.favorites_listWidget)
        M2_S2_horizontalLayout = QtGui.QHBoxLayout()
        M2_S2_horizontalLayout.setObjectName(("M2_S2_horizontalLayout"))

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        M2_S2_horizontalLayout.addItem(spacerItem)

        remove_pushButton = QtGui.QPushButton(verticalLayoutWidget)
        remove_pushButton.setMaximumSize(QtCore.QSize(35, 35))
        remove_pushButton.setFont(iconFont)
        remove_pushButton.setText(("-"))
        remove_pushButton.setObjectName(("remove_pushButton"))

        M2_S2_horizontalLayout.addWidget(remove_pushButton)

        add_pushButton = QtGui.QPushButton(verticalLayoutWidget)
        add_pushButton.setMaximumSize(QtCore.QSize(35, 35))
        add_pushButton.setFont(iconFont)
        add_pushButton.setText(("+"))
        add_pushButton.setObjectName(("add_pushButton"))

        M2_S2_horizontalLayout.addWidget(add_pushButton)

        M2_S2_verticalLayout.addLayout(M2_S2_horizontalLayout)

        M2_horizontalLayout.addWidget(M2_splitter)

        gridLayout.addLayout(M2_horizontalLayout, 1, 0, 1, 1)

        M3_horizontalLayout = QtGui.QHBoxLayout()

        M3_horizontalLayout.setContentsMargins(0, 20, -1, -1)

        M3_horizontalLayout.setObjectName(("M3_horizontalLayout"))

        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        M3_horizontalLayout.addItem(spacerItem1)

        cancel_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        cancel_pushButton.setMaximumSize(QtCore.QSize(70, 16777215))
        cancel_pushButton.setText("Cancel")
        cancel_pushButton.setObjectName(("cancel_pushButton"))

        M3_horizontalLayout.addWidget(cancel_pushButton, QtCore.Qt.AlignRight)

        set_pushButton = QtGui.QPushButton(self.setProject_Dialog)
        set_pushButton.setMaximumSize(QtCore.QSize(70, 16777215))
        set_pushButton.setText("Set")
        set_pushButton.setObjectName(("set_pushButton"))

        M3_horizontalLayout.addWidget(set_pushButton, QtCore.Qt.AlignRight)

        gridLayout.addLayout(M3_horizontalLayout, 2, 0, 1, 1)

        verticalLayoutWidget.raise_()

        M2_splitter.setStretchFactor(0,1)

        ## Initial Stuff
        self.projectsRoot = os.path.abspath(os.path.join(self.masterManager.projectDir, os.pardir))
        self.browser = Browse()
        self.spActiveProjectPath = None
        self.__flagView = True

        self.setPmodel = QtGui.QFileSystemModel()
        self.setPmodel.setRootPath(self.projectsRoot)
        self.setPmodel.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Time)

        self.folders_tableView.setModel(self.setPmodel)
        self.folders_tableView.setRootIndex(self.setPmodel.index(self.projectsRoot))
        self.folders_tableView.hideColumn(1)
        self.folders_tableView.hideColumn(2)
        self.folders_tableView.setColumnWidth(0,400)

        self.favList = self.masterManager._loadFavorites()
        self.favorites_listWidget.addItems([x[0] for x in self.favList])

        self.lookIn_lineEdit.setText(self.projectsRoot)

        def navigate(command, index=None):
            if command == "init":
                # feed the initial data
                self.browser.addData(self.projectsRoot)

            if command == "up":
                self.projectsRoot = os.path.abspath(os.path.join(self.projectsRoot, os.pardir))
                self.browser.addData(self.projectsRoot)

            if command == "back":
                self.browser.backward()

            if command == "forward":
                self.browser.forward()

            if command == "browse":
                dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
                if dir:
                    self.projectsRoot = dir
                    self.browser.addData(self.projectsRoot)


                else:
                    return

            if command == "folder":
                index = self.folders_tableView.currentIndex()
                self.projectsRoot = os.path.normpath(str(self.setPmodel.filePath(index)))
                self.browser.addData(self.projectsRoot)

            if command == "lineEnter":
                dir = str(self.lookIn_lineEdit.text())
                if os.path.isdir(dir):
                    self.projectsRoot = dir
                    self.browser.addData(self.projectsRoot)

                else:
                    self.lookIn_lineEdit.setText(self.projectsRoot)

            self.setPmodel.setRootPath(self.projectsRoot)

            self.forward_pushButton.setDisabled(self.browser.isForwardLocked())
            self.back_pushButton.setDisabled(self.browser.isBackwardLocked())
            self.folders_tableView.setRootIndex(self.setPmodel.index(self.browser.getData()))
            self.lookIn_lineEdit.setText(self.browser.getData())

        def onRemoveFavs():

            row = self.favorites_listWidget.currentRow()
            if row == -1:
                return
            # item = self.favList[row]
            self.favList = self.masterManager._removeFromFavorites(row)
            # block the signal to prevent unwanted cycle

            self.favorites_listWidget.blockSignals(True)
            self.favorites_listWidget.takeItem(row)
            self.favorites_listWidget.blockSignals(False)

        def onAddFavs():
            index = self.folders_tableView.currentIndex()
            if index.row() == -1:  # no row selected, abort
                return
            fullPath = self.setPmodel.filePath(index)
            onDragAndDrop(fullPath)

        def onDragAndDrop(path):
            normPath = os.path.normpath(str(path))

            path, fName = os.path.split(normPath)
            if [fName, normPath] in self.favList:
                return
            self.favorites_listWidget.addItem(fName)
            self.favList = self.masterManager._addToFavorites(fName, normPath)

        def favoritesActivated():
            # block the signal to prevent unwanted cycle
            self.folders_tableView.selectionModel().blockSignals(True)
            row = self.favorites_listWidget.currentRow()
            self.spActiveProjectPath = self.favList[row][1]

            # clear the selection in folders view
            self.folders_tableView.setCurrentIndex(self.setPmodel.index(self.projectsRoot))
            self.folders_tableView.selectionModel().blockSignals(False)

        def foldersViewActivated():
            # block the signal to prevent unwanted cycle
            self.favorites_listWidget.blockSignals(True)
            index = self.folders_tableView.currentIndex()
            self.spActiveProjectPath = os.path.normpath(str(self.setPmodel.filePath(index)))


            # clear the selection in favorites view
            self.favorites_listWidget.setCurrentRow(-1)
            self.favorites_listWidget.blockSignals(False)

        def setProject():
            self.masterManager.setProject(self.spActiveProjectPath)
            self.onProjectChange()
            self.setProject_Dialog.close()

        navigate("init")

        ## SIGNALS & SLOTS
        self.favorites_listWidget.dropped.connect(lambda path: onDragAndDrop(path))
        remove_pushButton.clicked.connect(onRemoveFavs)
        add_pushButton.clicked.connect(onAddFavs)

        self.favorites_listWidget.doubleClicked.connect(setProject)

        up_pushButton.clicked.connect(lambda: navigate("up"))
        self.back_pushButton.clicked.connect(lambda: navigate("back"))
        self.forward_pushButton.clicked.connect(lambda: navigate("forward"))
        browse_pushButton.clicked.connect(lambda: navigate("browse"))
        self.lookIn_lineEdit.returnPressed.connect(lambda: navigate("lineEnter"))
        self.folders_tableView.doubleClicked.connect(lambda index: navigate("folder", index=index))


        self.favorites_listWidget.currentItemChanged.connect(favoritesActivated)
        # self.folders_tableView.selectionModel().currentRowChanged.connect(foldersViewActivated)
        # There is a bug in here. If following two lines are run in a single line, a segmentation fault occurs and crashes 3ds max immediately
        selectionModel = self.folders_tableView.selectionModel()
        selectionModel.selectionChanged.connect(foldersViewActivated)


        self.favorites_listWidget.doubleClicked.connect(setProject)
        #
        cancel_pushButton.clicked.connect(self.setProject_Dialog.close)
        set_pushButton.clicked.connect(setProject)
        # set_pushButton.clicked.connect(self.setProject_Dialog.close)
        #
        self.setProject_Dialog.show()

    def addRemoveUserUI(self):
        passw, ok = QtGui.QInputDialog.getText(self, "Password Query",
                                               "Enter Admin Password:", QtGui.QLineEdit.Password)

        if ok:
            if self.masterManager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return

        users_Dialog = QtGui.QDialog(parent=self)
        users_Dialog.setModal(True)
        users_Dialog.setObjectName(("users_Dialog"))
        users_Dialog.resize(380, 483)
        users_Dialog.setMinimumSize(QtCore.QSize(342, 177))
        users_Dialog.setMaximumSize(QtCore.QSize(342, 177))
        users_Dialog.setWindowTitle(("Add/Remove Users"))
        users_Dialog.setFocus()

        addnewuser_groupBox = QtGui.QGroupBox(users_Dialog)
        addnewuser_groupBox.setGeometry(QtCore.QRect(10, 10, 321, 91))
        addnewuser_groupBox.setTitle(("Add New User"))
        addnewuser_groupBox.setObjectName(("addnewuser_groupBox"))

        fullname_label = QtGui.QLabel(addnewuser_groupBox)
        fullname_label.setGeometry(QtCore.QRect(0, 30, 81, 21))
        fullname_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        fullname_label.setText(("Full Name:"))
        fullname_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        fullname_label.setObjectName(("fullname_label"))

        self.fullname_lineEdit = QtGui.QLineEdit(addnewuser_groupBox)
        self.fullname_lineEdit.setGeometry(QtCore.QRect(90, 30, 151, 20))
        self.fullname_lineEdit.setPlaceholderText(("e.g \"John Doe\""))
        self.fullname_lineEdit.setObjectName(("fullname_lineEdit"))

        initials_label = QtGui.QLabel(addnewuser_groupBox)
        initials_label.setGeometry(QtCore.QRect(0, 60, 81, 21))
        initials_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        initials_label.setText(("Initials:"))
        initials_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        initials_label.setObjectName(("initials_label"))

        self.initials_lineEdit = QtGui.QLineEdit(addnewuser_groupBox)
        self.initials_lineEdit.setGeometry(QtCore.QRect(90, 60, 151, 20))
        self.initials_lineEdit.setText((""))
        self.initials_lineEdit.setPlaceholderText(("e.g \"jd\" (must be unique)"))
        self.initials_lineEdit.setObjectName(("initials_lineEdit"))

        addnewuser_pushButton = QtGui.QPushButton(addnewuser_groupBox)
        addnewuser_pushButton.setGeometry(QtCore.QRect(250, 30, 61, 51))
        addnewuser_pushButton.setText(("Add"))
        addnewuser_pushButton.setObjectName(("addnewuser_pushButton"))

        deleteuser_groupBox = QtGui.QGroupBox(users_Dialog)
        deleteuser_groupBox.setGeometry(QtCore.QRect(10, 110, 321, 51))
        deleteuser_groupBox.setTitle(("Delete User"))
        deleteuser_groupBox.setObjectName(("deleteuser_groupBox"))

        self.selectuser_comboBox = QtGui.QComboBox(deleteuser_groupBox)
        self.selectuser_comboBox.setGeometry(QtCore.QRect(10, 20, 231, 22))
        self.selectuser_comboBox.setObjectName(("selectuser_comboBox"))

        userListSorted = sorted(self.masterManager._usersDict.keys())
        for num in range(len(userListSorted)):
            self.selectuser_comboBox.addItem((userListSorted[num]))
            self.selectuser_comboBox.setItemText(num, (userListSorted[num]))

        deleteuser_pushButton = QtGui.QPushButton(deleteuser_groupBox)
        deleteuser_pushButton.setGeometry(QtCore.QRect(250, 20, 61, 21))
        deleteuser_pushButton.setText(("Delete"))
        deleteuser_pushButton.setObjectName(("deleteuser_pushButton"))


        def onAddUser():
            ret, msg = self.masterManager.addUser(self.fullname_lineEdit.text(), self.initials_lineEdit.text())
            if ret == -1:
                self.infoPop(textTitle="Cannot Add User", textHeader=msg)
                return
            self.masterManager.currentUser = self.fullname_lineEdit.text()
            self._initUsers()
            userListSorted = sorted(self.masterManager._usersDict.keys())
            self.selectuser_comboBox.clear()
            for num in range(len(userListSorted)):
                self.selectuser_comboBox.addItem((userListSorted[num]))
                self.selectuser_comboBox.setItemText(num, (userListSorted[num]))
            self.statusBar().showMessage("Status | User Added => %s" % self.fullname_lineEdit.text())
            self.fullname_lineEdit.setText("")
            self.initials_lineEdit.setText("")

            pass

        def onRemoveUser():
            self.masterManager.removeUser(self.selectuser_comboBox.currentText())
            self.masterManager.currentUser = self.masterManager._usersDict.keys()[0]
            self._initUsers()
            userListSorted = sorted(self.masterManager._usersDict.keys())
            self.selectuser_comboBox.clear()
            for num in range(len(userListSorted)):
                self.selectuser_comboBox.addItem((userListSorted[num]))
                self.selectuser_comboBox.setItemText(num, (userListSorted[num]))
            pass

        addnewuser_pushButton.clicked.connect(onAddUser)
        deleteuser_pushButton.clicked.connect(onRemoveUser)

        self.fullname_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.fullname_lineEdit.text(), addnewuser_pushButton,
                                  self.fullname_lineEdit, allowSpaces=True))
        self.initials_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.initials_lineEdit.text(), addnewuser_pushButton,
                                  self.initials_lineEdit))

        users_Dialog.show()

    def addRemoveCategoryUI(self):

        passw, ok = QtGui.QInputDialog.getText(self, "Password Query",
                                               "Enter Admin Password:", QtGui.QLineEdit.Password)

        manager = self._getManager()
        if not manager:
            return

        if ok:
            if self.masterManager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return


        categories_dialog = QtGui.QDialog(parent=self)
        categories_dialog.setModal(True)
        categories_dialog.setObjectName(("category_Dialog"))
        categories_dialog.setMinimumSize(QtCore.QSize(342, 177))
        categories_dialog.setMaximumSize(QtCore.QSize(342, 177))
        categories_dialog.setWindowTitle(("Add/Remove Categories"))
        categories_dialog.setFocus()

        addnewcategory_groupbox = QtGui.QGroupBox(categories_dialog)
        addnewcategory_groupbox.setGeometry(QtCore.QRect(10, 10, 321, 81))
        addnewcategory_groupbox.setTitle(("Add New Category"))
        addnewcategory_groupbox.setObjectName(("addnewcategory_groupBox"))

        categoryName_label = QtGui.QLabel(addnewcategory_groupbox)
        categoryName_label.setGeometry(QtCore.QRect(10, 30, 81, 21))
        categoryName_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        categoryName_label.setText(("Category Name:"))
        categoryName_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        categoryName_label.setObjectName(("categoryName_label"))

        self.categoryName_lineEdit= QtGui.QLineEdit(addnewcategory_groupbox)
        self.categoryName_lineEdit.setGeometry(QtCore.QRect(105, 30, 135, 20))
        self.categoryName_lineEdit.setPlaceholderText(("e.g \"Look Dev\""))
        self.categoryName_lineEdit.setObjectName(("categoryName_lineEdit"))

        addnewcategory_pushButton = QtGui.QPushButton(addnewcategory_groupbox)
        addnewcategory_pushButton.setGeometry(QtCore.QRect(250, 28, 61, 26))
        addnewcategory_pushButton.setText(("Add"))
        addnewcategory_pushButton.setObjectName(("addnewcategory_pushButton"))

        deletecategory_groupBox = QtGui.QGroupBox(categories_dialog)
        deletecategory_groupBox.setGeometry(QtCore.QRect(10, 110, 321, 51))
        deletecategory_groupBox.setTitle(("Delete and Change Order"))
        deletecategory_groupBox.setObjectName(("deletecategory_groupBox"))

        self.selectcategory_comboBox = QtGui.QComboBox(deletecategory_groupBox)
        self.selectcategory_comboBox.setGeometry(QtCore.QRect(10, 20, 231, 22))
        self.selectcategory_comboBox.setObjectName(("selectcategory_comboBox"))

        self.selectcategory_comboBox.addItems(manager._categories)

        deletecategory_pushButton = QtGui.QPushButton(deletecategory_groupBox)
        deletecategory_pushButton.setGeometry(QtCore.QRect(250, 20, 61, 21))
        deletecategory_pushButton.setText(("Delete"))
        deletecategory_pushButton.setObjectName(("deletecategory_pushButton"))


        def onAddCategory():
            manager.addCategory(str(self.categoryName_lineEdit.text()))


            preTab = QtGui.QWidget()
            preTab.setObjectName(self.categoryName_lineEdit.text())
            self.category_tabWidget.addTab(preTab, self.categoryName_lineEdit.text())
            self.selectcategory_comboBox.addItem(self.categoryName_lineEdit.text())

            self.categoryName_lineEdit.setText("")

        def onRemoveCategory():
            manager.removeCategory(str(self.selectcategory_comboBox.currentText()))
            self.selectcategory_comboBox.clear()
            self.selectcategory_comboBox.addItems(manager.getCategories())

            self._initCategories()


        addnewcategory_pushButton.clicked.connect(onAddCategory)
        deletecategory_pushButton.clicked.connect(onRemoveCategory)

        self.categoryName_lineEdit.textChanged.connect(
            lambda: self._checkValidity(self.categoryName_lineEdit.text(), addnewcategory_pushButton,
                                        self.categoryName_lineEdit))


        categories_dialog.show()

    def projectSettingsUI(self):
        passw, ok = QtGui.QInputDialog.getText(self, "Password Query", "Enter Admin Password:",
                                                   QtGui.QLineEdit.Password)

        if ok:
            if self.masterManager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return

        projectSettingsDB = self.masterManager._loadProjectSettings()

        projectSettings_Dialog = QtGui.QDialog(parent=self)
        projectSettings_Dialog.setObjectName("projectSettings_Dialog")
        projectSettings_Dialog.resize(270, 120)
        projectSettings_Dialog.setMinimumSize(QtCore.QSize(270, 120))
        projectSettings_Dialog.setMaximumSize(QtCore.QSize(270, 120))
        projectSettings_Dialog.setWindowTitle("Project Settings")

        gridLayout = QtGui.QGridLayout(projectSettings_Dialog)
        gridLayout.setObjectName(("gridLayout"))

        buttonBox = QtGui.QDialogButtonBox(projectSettings_Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        buttonBox.setMaximumSize(QtCore.QSize(16777215, 30))
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Save)
        buttonBox.setObjectName("buttonBox")

        gridLayout.addWidget(buttonBox, 1, 0, 1, 1)

        formLayout = QtGui.QFormLayout()
        formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        formLayout.setFormAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        formLayout.setObjectName("formLayout")

        resolution_label = QtGui.QLabel(projectSettings_Dialog)
        resolution_label.setText("Resolution:")
        resolution_label.setObjectName("resolution_label")
        formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, resolution_label)

        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setObjectName("horizontalLayout")

        resolutionX_spinBox = QtGui.QSpinBox(projectSettings_Dialog)
        resolutionX_spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        resolutionX_spinBox.setObjectName("resolutionX_spinBox")
        horizontalLayout.addWidget(resolutionX_spinBox)
        resolutionX_spinBox.setRange(1, 99999)
        resolutionX_spinBox.setValue(projectSettingsDB["Resolution"][0])

        resolutionY_spinBox = QtGui.QSpinBox(projectSettings_Dialog)
        resolutionY_spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        resolutionY_spinBox.setObjectName("resolutionY_spinBox")
        horizontalLayout.addWidget(resolutionY_spinBox)
        resolutionY_spinBox.setRange(1, 99999)
        resolutionY_spinBox.setValue(projectSettingsDB["Resolution"][1])

        formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, horizontalLayout)
        fps_label = QtGui.QLabel(projectSettings_Dialog)
        fps_label.setText("FPS")
        fps_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        fps_label.setObjectName("fps_label")
        formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, fps_label)

        fps_comboBox = QtGui.QComboBox(projectSettings_Dialog)
        fps_comboBox.setMaximumSize(QtCore.QSize(60, 16777215))
        fps_comboBox.setObjectName("fps_comboBox")
        formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, fps_comboBox)
        fps_comboBox.addItems(self.masterManager.fpsList)
        try:
            index = self.masterManager.fpsList.index(str(projectSettingsDB["FPS"]))
        except:
            index = 2
        fps_comboBox.setCurrentIndex(index)
        gridLayout.addLayout(formLayout, 0, 0, 1, 1)

        # SIGNALS
        # -------
        def onAccepted():
            projectSettingsDB = {"Resolution": [resolutionX_spinBox.value(), resolutionY_spinBox.value()],
                                 "FPS": int(fps_comboBox.currentText())}
            self.masterManager._saveProjectSettings(projectSettingsDB)
            projectSettings_Dialog.close()


        buttonBox.accepted.connect(onAccepted)
        buttonBox.rejected.connect(projectSettings_Dialog.reject)

        projectSettings_Dialog.show()

    def changePasswordUI(self):
        # TODO : ref

        changePassword_Dialog = QtGui.QDialog(parent=self)
        changePassword_Dialog.setObjectName("projectSettings_Dialog")
        changePassword_Dialog.resize(270, 120)
        changePassword_Dialog.setMinimumSize(QtCore.QSize(270, 120))
        changePassword_Dialog.setMaximumSize(QtCore.QSize(270, 120))
        changePassword_Dialog.setWindowTitle("Project Settings")

        gridLayout = QtGui.QGridLayout(changePassword_Dialog)
        gridLayout.setObjectName(("gridLayout"))

        buttonBox = QtGui.QDialogButtonBox(changePassword_Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        buttonBox.setMaximumSize(QtCore.QSize(16777215, 30))
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Save)
        buttonBox.setObjectName("buttonBox")

        gridLayout.addWidget(buttonBox, 1, 0, 1, 1)

        formLayout = QtGui.QFormLayout()
        formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        formLayout.setFormAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        formLayout.setObjectName("formLayout")

        oldPass_label = QtGui.QLabel(changePassword_Dialog)
        oldPass_label.setText("Old Password:")
        formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, oldPass_label)

        oldPass_lineEdit = QtGui.QLineEdit(changePassword_Dialog)
        oldPass_lineEdit.setEchoMode(2)
        formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, oldPass_lineEdit)


        newPass_label = QtGui.QLabel(changePassword_Dialog)
        newPass_label.setText("New Password:")
        newPass_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, newPass_label)

        newPass_lineEdit = QtGui.QLineEdit(changePassword_Dialog)
        newPass_lineEdit.setEchoMode(2)
        formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, newPass_lineEdit)

        newPassAgain_label = QtGui.QLabel(changePassword_Dialog)
        newPassAgain_label.setText("New Password Again:")
        newPassAgain_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, newPassAgain_label)

        newPassAgain_lineEdit = QtGui.QLineEdit(changePassword_Dialog)
        newPassAgain_lineEdit.setEchoMode(2)
        formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, newPassAgain_lineEdit)

        gridLayout.addLayout(formLayout, 0, 0, 1, 1)
        # SIGNALS
        # -------
        def onAccepted():

            if not self.masterManager.checkPassword(oldPass_lineEdit.text()):
                self.infoPop(textTitle="Incorrect Password", textHeader="Invalid Old Password", type="C")
                return
            if newPass_lineEdit.text() == "" or newPassAgain_lineEdit.text() == "":
                self.infoPop(textTitle="Error", textHeader="Admin Password cannot be blank", type="C")
                return
            if newPass_lineEdit.text() != newPassAgain_lineEdit.text():
                self.infoPop(textTitle="Error", textHeader="New passwords are not matching", type="C")
                return

            if self.masterManager.changePassword(oldPass_lineEdit.text(), newPass_lineEdit.text()):
                self.infoPop(textTitle="Success", textHeader="Password Changed", type="I")
                changePassword_Dialog.close()

        buttonBox.accepted.connect(onAccepted)
        buttonBox.rejected.connect(changePassword_Dialog.reject)

        changePassword_Dialog.show()


    def addNoteDialog(self):
        manager = self._getManager()
        if not manager:
            return
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            return

        addNotes_Dialog = QtGui.QDialog(parent=self)
        addNotes_Dialog.setModal(True)
        addNotes_Dialog.setObjectName(("addNotes_Dialog"))
        addNotes_Dialog.resize(255, 290)
        addNotes_Dialog.setMinimumSize(QtCore.QSize(255, 290))
        addNotes_Dialog.setMaximumSize(QtCore.QSize(255, 290))
        addNotes_Dialog.setWindowTitle(("Add Notes"))

        addNotes_label = QtGui.QLabel(addNotes_Dialog)
        addNotes_label.setGeometry(QtCore.QRect(15, 15, 100, 20))
        addNotes_label.setText(("Additional Notes"))
        addNotes_label.setObjectName(("addNotes_label"))

        addNotes_textEdit = QtGui.QTextEdit(addNotes_Dialog)
        addNotes_textEdit.setGeometry(QtCore.QRect(15, 40, 215, 170))
        addNotes_textEdit.setObjectName(("addNotes_textEdit"))

        addNotes_buttonBox = QtGui.QDialogButtonBox(addNotes_Dialog)
        addNotes_buttonBox.setGeometry(QtCore.QRect(20, 250, 220, 32))
        addNotes_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        addNotes_buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Cancel)

        buttonS = addNotes_buttonBox.button(QtGui.QDialogButtonBox.Save)
        buttonS.setText('Add Notes')
        buttonC = addNotes_buttonBox.button(QtGui.QDialogButtonBox.Cancel)
        buttonC.setText('Cancel')

        addNotes_buttonBox.setObjectName(("addNotes_buttonBox"))
        addNotes_buttonBox.accepted.connect(lambda: manager.addNote(addNotes_textEdit.toPlainText()))
        addNotes_buttonBox.accepted.connect(self.onVersionChange)
        addNotes_buttonBox.accepted.connect(addNotes_Dialog.accept)

        addNotes_buttonBox.rejected.connect(addNotes_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(addNotes_Dialog)

        addNotes_Dialog.show()

    def onContextMenu_scenes(self, point):
        # show context menu
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            return
        # check paths
        manager = self._getManager()
        self.scenes_rcItem_1.setEnabled(os.path.isdir(manager.currentBaseScenePath))
        self.scenes_rcItem_2.setEnabled(os.path.isdir(manager.currentPreviewPath))
        self.scenes_rcItem_5.setEnabled(os.path.isdir(os.path.join(self.masterManager.projectDir, "images", manager.currentBaseSceneName)))
        self.popMenu_scenes.exec_(self.scenes_listWidget.mapToGlobal(point))
    def onContextMenu_thumbnail(self, point):
        # show context menu
        self.popMenu_thumbnail.exec_(self.thumbnail_label.mapToGlobal(point))

    def rcAction_scenes(self, command):
        manager = self._getManager()
        if not manager:
            return

        if command == "showInExplorerMaya":
            manager.showInExplorer(manager.currentBaseScenePath)

        if command == "showInExplorerPB":
            manager.showInExplorer(manager.currentPreviewPath)

        if command == "showInExplorerData":
            filePath = manager._baseScenesInCategory[manager.currentBaseSceneName]
            dirPath = os.path.dirname(filePath)
            manager.showInExplorer(dirPath)

        if command == "showSceneInfo":
            textInfo = pprint.pformat(manager._currentSceneInfo)
            self.messageDialog = QtGui.QDialog()
            self.messageDialog.setWindowTitle("Scene Info")
            self.messageDialog.resize(800, 700)
            self.messageDialog.show()
            messageLayout = QtGui.QVBoxLayout(self.messageDialog)
            messageLayout.setContentsMargins(0, 0, 0, 0)
            helpText = QtGui.QTextEdit()
            helpText.setReadOnly(True)
            helpText.setStyleSheet("background-color: rgb(255, 255, 255);")
            helpText.setStyleSheet(""
                                   "border: 20px solid black;"
                                   "background-color: black;"
                                   "font-size: 16px"
                                   "")
            helpText.setText(textInfo)
            messageLayout.addWidget(helpText)

        if command == "viewRender":
            imagePath = os.path.join(self.masterManager.projectDir, "images", manager.currentBaseSceneName)
            IvStandalone.MainUI(self.masterManager.projectDir, relativePath=imagePath, recursive=True).show()

    def onProjectChange(self):
        self.initMainUI(newborn=True)


    def onSoftwareChange(self):

        self.masterManager.currentSwIndex = self.software_comboBox.currentIndex()

        self._initCategories()
        self._initSubProjects()
        self.populateBaseScenes()
        self.software_comboBox.setStyleSheet("background-color: %s; color: black" %self.swColorDict[str(self.software_comboBox.currentText())])
        self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        self._vEnableDisable()

    def onSubProjectChange(self):
        manager = self._getManager()


        manager.currentSubIndex = self.subProject_comboBox.currentIndex()
        self.onCategoryChange()

    def onCategoryChange(self):
        manager = self._getManager()


        manager.currentTabIndex = self.category_tabWidget.currentIndex()
        self.populateBaseScenes()
        self.onBaseSceneChange()

    def onUserChange(self):
        manager = self._getManager()
        manager.currentUser = str(self.user_comboBox.currentText())

    def onBaseSceneChange(self):
        self.version_comboBox.blockSignals(True)

        manager = self._getManager()
        #clear version_combobox
        self.version_comboBox.clear()

        row = self.scenes_listWidget.currentRow()
        if row == -1:
            manager.currentBaseSceneName = ""

        else:
            manager.currentBaseSceneName = str(self.scenes_listWidget.currentItem().text())

        self._vEnableDisable()
        #get versions and add it to the combobox
        versionData = manager.getVersions()
        for num in range(len(versionData)):
            self.version_comboBox.addItem("v{0}".format(str(num + 1).zfill(3)))
        self.version_comboBox.setCurrentIndex(manager.currentVersionIndex-1)
        self.onVersionChange()

        self.version_comboBox.blockSignals(False)

    def onVersionChange(self):

        manager = self._getManager()
        self.version_comboBox.blockSignals(True)

        if self.version_comboBox.currentIndex() is not -1:
            manager.currentVersionIndex = self.version_comboBox.currentIndex() + 1

        # clear Notes and verison combobox
        self.notes_textEdit.clear()

        # update notes
        self.notes_textEdit.setPlainText(manager.getNotes())

        # update thumb
        self.tPixmap = QtGui.QPixmap(manager.getThumbnail())
        self.thumbnail_label.setPixmap(self.tPixmap)

        if manager.currentVersionIndex != len(manager.getVersions()) and manager.currentVersionIndex != -1:
            self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: yellow")
        else:
            self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")

        self.version_comboBox.blockSignals(False)



    def initMainUI(self, newborn=False):

        if not newborn:
            self.masterManager.init_paths()
            self.masterManager.init_database()
        # init softwares
        self.masterManager.initSoftwares()
        self._initSoftwares()

        self._initCategories()
        # init project
        self.project_lineEdit.setText(self.masterManager.projectDir)
        # init subproject
        self._initSubProjects()
        # init base scenes
        self.populateBaseScenes()
        # init users
        self._initUsers()
        # # disable the version related stuff
        self.version_comboBox.setStyleSheet("background-color: rgb(80,80,80); color: white")
        self._vEnableDisable()

    def refresh(self):
        currentSWindex = self.software_comboBox.currentIndex()
        # currentUserIndex = self.user_comboBox.currentIndex()
        # currentTabIndex = self
        self.initMainUI()

        self.software_comboBox.setCurrentIndex(currentSWindex)
        self.populateBaseScenes()

    def onLoadScene(self):
        if self.scenes_listWidget.currentRow() == -1:
            return
        manager = self._getManager()
        if not manager:
            return
        manager.executeScene()

    def onMakeReference(self):
        manager = self._getManager()

        manager.makeReference()
        self.onVersionChange()
        self.statusBar().showMessage(
            "Status | Version {1} is the new reference of {0}".format(manager.currentBaseSceneName, manager.currentVersionIndex))
        currentRow = self.scenes_listWidget.currentRow()
        self.populateBaseScenes()
        self.scenes_listWidget.setCurrentRow(currentRow)

    def onShowPreview(self):
        row = self.scenes_listWidget.currentRow()
        if row == -1:
            return

        manager = self._getManager()

        cameraList = manager.getPreviews()
        if len(manager.getPreviews()) == 1:
            manager.playPreview(cameraList[0])
        else:
            zortMenu = QtGui.QMenu()
            for z in cameraList:
                tempAction = QtGui.QAction(z, self)
                zortMenu.addAction(tempAction)
                tempAction.triggered.connect(lambda item=z: manager.playPreview(item)) ## Take note about the usage of lambda "item=pbDict[z]" makes it possible using the loop

            zortMenu.exec_((QtGui.QCursor.pos()))

    def onDeleteBaseScene(self):
        passw, ok = QtGui.QInputDialog.getText(self, "!!!DELETING BASE SCENE!!! %s\n\nAre you absolutely sure?", "Enter Admin Password:", QtGui.QLineEdit.Password)

        if ok:
            if self.masterManager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return



        manager = self._getManager()

        name = manager.currentBaseSceneName

        row = self.scenes_listWidget.currentRow()
        if not row == -1:
            manager.deleteBasescene(manager.currentDatabasePath)
            self.populateBaseScenes()
            self.statusBar().showMessage("Status | Scene Deleted => %s" % name)


    def onDeleteReference(self):
        passw, ok = QtGui.QInputDialog.getText(self, "DELETING Reference File of %s\n\nAre you sure?", "Enter Admin Password:", QtGui.QLineEdit.Password)

        if ok:
            if self.masterManager.checkPassword(passw):
                pass
            else:
                self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                return
        else:
            return


        manager = self._getManager()

        name = manager.currentBaseSceneName

        row = self.scenes_listWidget.currentRow()
        if not row == -1:
            manager.deleteReference(manager.currentDatabasePath)
            self.populateBaseScenes()
            self.statusBar().showMessage("Status | Reference of %s is deleted" % name)



    def populateBaseScenes(self, deepCheck=False):
        self.scenes_listWidget.blockSignals(True)

        manager = self._getManager()
        if not manager:
            return

        self.scenes_listWidget.clear()
        baseScenesDict = manager.getBaseScenesInCategory()

        codeDict = {-1: QtGui.QColor(255, 0, 0, 255), 1: QtGui.QColor(0, 255, 0, 255),
                    0: QtGui.QColor(255, 255, 0, 255), -2: QtGui.QColor(20, 20, 20, 255)}  # dictionary for color codes red, green, yellow
                    # gray for the corrupted database file

        for key in sorted(baseScenesDict):
            retCode = manager.checkReference(baseScenesDict[key], deepCheck=deepCheck) # returns -1, 0, 1 or -2 for color ref
            color = codeDict[retCode]
            listItem = QtGui.QListWidgetItem()
            listItem.setText(key)
            listItem.setForeground(color)
            self.scenes_listWidget.addItem(listItem)
        self.scenes_listWidget.blockSignals(False)

    def onIviewer(self):
        IvStandalone.MainUI(self.masterManager.projectDir).show()

    def _initSoftwares(self):
        self.software_comboBox.blockSignals(True)

        self.software_comboBox.clear()
        for x in self.masterManager.swList:
            self.software_comboBox.addItem(x.niceName)


        self.software_comboBox.setStyleSheet("background-color: %s; color: black" %self.swColorDict[str(self.software_comboBox.currentText())])

        self.software_comboBox.blockSignals(False)

    def _getManager(self):
        swList = self.masterManager.swList
        swIndex = self.software_comboBox.currentIndex()
        try:
            manager = swList[swIndex]
        except IndexError:
            return
        return manager

    def _initCategories(self):
        self.category_tabWidget.blockSignals(True)

        # swList = self.masterManager.swList
        # swIndex = self.software_comboBox.currentIndex()
        manager = self._getManager()
        if not manager:
            return

        self.category_tabWidget.clear()

        for i in manager._categories:
            self.preTab = QtGui.QWidget()
            self.preTab.setObjectName((i))
            self.category_tabWidget.addTab(self.preTab, (i))

        self.category_tabWidget.setCurrentIndex(manager.currentTabIndex)
        self.category_tabWidget.blockSignals(False)

    def _initUsers(self):
        self.user_comboBox.blockSignals(True)

        manager = self._getManager()
        if not manager:
            return
        # init users
        self.user_comboBox.clear()
        self.user_comboBox.addItems(manager.getUsers())
        index = self.user_comboBox.findText(manager.currentUser, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.user_comboBox.setCurrentIndex(index)

        self.user_comboBox.blockSignals(False)

    def _initSubProjects(self):

        self.subProject_comboBox.blockSignals(True)

        manager = self._getManager()
        if not manager:
            return

        self.subProject_comboBox.clear()
        self.subProject_comboBox.addItems(manager.getSubProjects())
        self.subProject_comboBox.setCurrentIndex(manager.currentSubIndex)

        self.subProject_comboBox.blockSignals(False)

    def _checkValidity(self, text, button, lineEdit, allowSpaces=False):
        if self.masterManager._nameCheck(text, allowSpaces=allowSpaces):
            lineEdit.setStyleSheet("background-color: rgb(40,40,40); color: white")
            button.setEnabled(True)
        else:
            lineEdit.setStyleSheet("background-color: red; color: black")
            button.setEnabled(False)


    def _vEnableDisable(self):
        manager = self._getManager()
        if not manager:
            return

        if  manager.currentBaseSceneName:
            self.version_comboBox.setEnabled(True)
            if manager.getPreviews():
                self.showPreview_pushButton.setEnabled(True)
            else:
                self.showPreview_pushButton.setEnabled(False)
            self.makeReference_pushButton.setEnabled(True)
            self.addNote_pushButton.setEnabled(True)
            self.version_label.setEnabled(True)

        else:
            self.version_comboBox.setEnabled(False)
            self.showPreview_pushButton.setEnabled(False)
            self.makeReference_pushButton.setEnabled(False)
            self.addNote_pushButton.setEnabled(False)
            self.version_label.setEnabled(False)

    def infoPop(self, textTitle="info", textHeader="", textInfo="", type="I"):
        self.msg = QtGui.QMessageBox(parent=self)
        if type == "I":
            self.msg.setIcon(QtGui.QMessageBox.Information)
        if type == "C":
            self.msg.setIcon(QtGui.QMessageBox.Critical)

        self.msg.setText(textHeader)
        self.msg.setInformativeText(textInfo)
        self.msg.setWindowTitle(textTitle)
        self.msg.setStandardButtons(QtGui.QMessageBox.Ok)
        self.msg.show()

    def queryPop(self, type, textTitle="Question", textHeader="", textInfo="", password=""):
        # if type == "password":
        #     if password != "":
        #         passw, ok= QtGui.QInputDialog.getText(self, textTitle,
        #                                                textInfo, QtGui.QLineEdit.Password, parent=self)
        #         if ok:
        #             if passw == password:
        #                 return True
        #             else:
        #                 self.infoPop(textTitle="Incorrect Passsword", textHeader="Incorrect Password", type="C")
        #                 return False
        #         else:
        #             return False
        #     else:
        #         return -1

        if type == "yesNoCancel":

            q = QtGui.QMessageBox(parent=self)
            q.setIcon(QtGui.QMessageBox.Question)
            q.setText(textHeader)
            q.setInformativeText(textInfo)
            q.setWindowTitle(textTitle)
            q.setStandardButtons(
                QtGui.QMessageBox.Save | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            ret = q.exec_()
            if ret == QtGui.QMessageBox.Save:
                return "yes"
            elif ret == QtGui.QMessageBox.No:
                return "no"
            elif ret == QtGui.QMessageBox.Cancel:
                return "cancel"

        if type == "okCancel":
            q = QtGui.QMessageBox(parent=self)
            q.setIcon(QtGui.QMessageBox.Question)
            q.setText(textHeader)
            q.setInformativeText(textInfo)
            q.setWindowTitle(textTitle)
            q.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            ret = q.exec_()
            if ret == QtGui.QMessageBox.Ok:
                return "ok"
            elif ret == QtGui.QMessageBox.Cancel:
                return "cancel"

        if type == "yesNo":
            q = QtGui.QMessageBox(parent=self)
            q.setIcon(QtGui.QMessageBox.Question)
            q.setText(textHeader)
            q.setInformativeText(textInfo)
            q.setWindowTitle(textTitle)
            q.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            ret = q.exec_()
            if ret == QtGui.QMessageBox.Yes:
                return "yes"
            elif ret == QtGui.QMessageBox.No:
                return "no"


class ImageWidget(QtGui.QLabel):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__()
        self.aspectRatio = 1.78
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, r):
        h = self.width()
        self.setMinimumHeight(h/self.aspectRatio)
        self.setMaximumHeight(h/self.aspectRatio)

class ImageWidget(QtGui.QLabel):
    """Custom class for thumbnail section. Keeps the aspect ratio when resized."""
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__()
        self.aspectRatio = 1.78
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, r):
        h = self.width()
        self.setMinimumHeight(h/self.aspectRatio)
        self.setMaximumHeight(h/self.aspectRatio)

class DropListWidget(QtGui.QListWidget):
    """Custom List Widget which accepts drops"""
    # dropped = Qt.QtCore.Signal(str)
    dropped = QtCore.pyqtSignal(str)

    def __init__(self, type, parent=None):
        super(DropListWidget, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        rawPath = event.mimeData().data('text/uri-list').__str__()
        path = rawPath.replace("file:///", "").splitlines()[0]
        self.dropped.emit(path)

class Browse(object):
    """Browsing class with history"""
    def __init__(self):
        super(Browse, self).__init__()
        self.history = []
        self.index = 0
        self.undoCount = 10
    def forward(self):
        if not self.isForwardLocked():
            self.index += 1
        else:
            pass
    def backward(self):
        if not self.isBackwardLocked():
            self.index -= 1
        else:
            pass
    def addData(self, data):
        # if the incoming data is identical with the current, do nothing
        try:
            currentData = self.history[self.index]
            if data == currentData:
                return
        except IndexError:
            pass
        # delete history after index
        del self.history[self.index+1:]
        self.history.append(data)
        if len(self.history) > self.undoCount:
            self.history.pop(0)
        self.index = len(self.history)-1
        # the new data writes the history, so there is no future
        self.forwardLimit = True
        # but there is past
        self.backwardLimit = False
    def getData(self, index=None):
        if index:
            return self.history[index]
        else:
            return self.history[self.index]
    def isBackwardLocked(self):
        return self.index == 0
    def isForwardLocked(self):
        return self.index == (len(self.history)-1)


if __name__ == '__main__':
    selfLoc = os.path.dirname(os.path.abspath(__file__))
    stylesheetFile = os.path.join(selfLoc, "CSS", "darkorange.stylesheet")

    app = QtGui.QApplication(sys.argv)
    with open(stylesheetFile, "r") as fh:
        app.setStyleSheet(fh.read())
    window = MainUI()
    window.show()
    # window.changePasswordUI()
    sys.exit(app.exec_())