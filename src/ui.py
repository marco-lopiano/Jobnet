from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import database
from utils.checkableComboBox import HorizontalCheckable
from utils.customMapView import CustomMapView
import utils.pandasCustomModel

import os
import sys
import pandas as pd

from filtering import advancedFilter

#TODO make notations for each function - !
#TODO implement logging
#TODO implement menu bar - is it really needed?
#TODO create args for this module for cli - is it really needed?

class CustomFilterList(QListWidget):
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            sel_items = self.selectedItems()
            if not sel_items: return
            for i in sel_items:
                self.takeItem(self.row(i))
        else:
            super().keyPressEvent(event)

class JobScanner(QMainWindow):
    def __init__(self):
        super(JobScanner, self).__init__()
        # self.columns = ['Studio', 'City', 'Country', 'Job Title', 'Date', 'Source/Contact']
        self.columns = ['Studio','City', 'Country', 'Job Title', 'Contract Type', 'Date', 'Source/Contact' ]

        self.database = database.main()

        self.initUI()
        self.center()

    def initUI(self):
        self.setGeometry( 10, 10, 1500, 800 )
        self.setWindowTitle('Job Net')

        #self._menu_bar()

        # main window
        self.mainWindow = QWidget()
        self.setCentralWidget(self.mainWindow)

        # filter widget
        filter = QWidget()
        self.list = QWidget()

        # main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.list, 90)
        main_layout.addWidget(filter, 10)
        
        # list layout
        self.list_layout = QHBoxLayout()
        
        self.Result = QTableView()
        self.list_layout.addWidget(self.Result)
        self.list.setLayout(self.list_layout)

        # filter layout
        filter_layout = QVBoxLayout()
 
        self.drop_menu  = HorizontalCheckable(choices=self.columns)

        drop_filter_layout = QHBoxLayout()
        drop_filter_layout.addWidget(self.drop_menu, 75)

        # view mode
        self.viewMode = QComboBox()
        self.viewMode.addItems(["Sheet", "Map"])
        drop_filter_layout.addWidget(self.viewMode, 25)
        self.viewMode.currentIndexChanged.connect(self.refresh)

        filter_layout.addLayout(drop_filter_layout)
        
        filter_label = QLabel('Add Filters: ')
        self.filter_text = QLineEdit()
        self.filter_text.returnPressed.connect(self.addFilter)

        label_filter_layout = QHBoxLayout()
        label_filter_layout.addWidget(filter_label)
        label_filter_layout.addWidget(self.filter_text, 75)

        self.mostRecent = QCheckBox("Most Recent")
        self.mostRecent.stateChanged.connect(self.refresh)
        label_filter_layout.addWidget(self.mostRecent)

        self.refresh_btn = QPushButton('update')
        self.refresh_btn.clicked.connect(lambda: self.refresh(bypassLocal=True))
        label_filter_layout.addWidget(self.refresh_btn)

        filter_layout.addLayout(label_filter_layout)

        self.filterAdd_btn = QPushButton('Add')
        self.filterAdd_btn.clicked.connect(self.addFilter)

        self.filterRem_btn = QPushButton('Remove')
        self.filterRem_btn.clicked.connect(self.removeSelected)

        self.filterRemAll_btn = QPushButton('Remove All')
        self.filterRemAll_btn.clicked.connect(self.removeAll)

        self.reset_btn = QPushButton('Reset')
        self.reset_btn.clicked.connect(self.reset)

        self.filter_list = CustomFilterList()
        self.filter_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # adding buttons to layout
        buttons_filter_layout = QVBoxLayout()
        buttons_filter_layout.addWidget(self.filterAdd_btn)
        buttons_filter_layout.addWidget(self.filterRem_btn)
        buttons_filter_layout.addWidget(self.filterRemAll_btn)
        buttons_filter_layout.addWidget(self.reset_btn)

        buttons_list_filter_layout = QHBoxLayout()
        buttons_list_filter_layout.addWidget(self.filter_list)
        buttons_list_filter_layout.addLayout(buttons_filter_layout)

        filter_layout.addLayout(buttons_list_filter_layout)

        search_btn = QPushButton('Search')
        search_btn.clicked.connect(self.refresh)

        filter_layout.addWidget(search_btn)

        filter.setLayout(filter_layout)
        self.mainWindow.setLayout(main_layout)
        self.refresh()
        self.show()

    # the reason of * is https://stackoverflow.com/questions/56422246/function-call-through-signal-changes-default-keyed-arguments-to-false-why
    def refresh(self, *, bypassLocal=False):
        # view mode
        viewState = self.viewMode.currentText()
        
        # filters
        filters = [str(self.filter_list.item(i).text()) for i in range(self.filter_list.count())]
        columnsToFilter = self.drop_menu.currentData()

        updated = database.main(force=bypassLocal)
        df = advancedFilter(updated, filters=filters, columnsToFilter=columnsToFilter, mostRecent=self.mostRecent.isChecked())

        if df is False:
            self.database = database.main()
        else:
            self.database = df
        
        self.list_layout.removeWidget(self.Result)
        if viewState == 'Map':
            self.Result = CustomMapView(data=self.database)

        elif viewState == 'Sheet':
            self.model = utils.pandasCustomModel.PandasCustomModel(self.database)
            self.Result = QTableView() # for spreadsheet view
            self.Result.setModel(self.model)

            try:
                source_idx = self.columns.index('Source/Contact')
                self.Result.horizontalHeader().setSectionResizeMode(source_idx, QHeaderView.ResizeMode.Stretch)
                
                date_idx = self.columns.index('Date')
                self.Result.horizontalHeader().setSectionResizeMode(date_idx, QHeaderView.ResizeMode.ResizeToContents)
                
                contract_idx = self.columns.index('Contract Type')
                self.Result.horizontalHeader().setSectionResizeMode(contract_idx, QHeaderView.ResizeMode.ResizeToContents)
            except ValueError:
                pass

            self.Result.verticalHeader().hide()

        self.list_layout.addWidget(self.Result)
        self.list.setLayout(self.list_layout)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def addFilter(self):
        filters = self.filter_text.text()
        if len(filters)>0:
            texts = filters.split(',')
            for text in texts:
                if text!=' ' or text!='':
                    self.filter_list.addItem(text)
                    self.filter_text.setText('')
                else:
                    pass
        else:
            pass

    def removeSelected(self):
        sel_items = self.filter_list.selectedItems()
        if not sel_items: return
        for i in sel_items:
            self.filter_list.takeItem(self.filter_list.row(i))

    def removeAll(self):
        self.filter_list.clear()

    def reset(self):
        self.removeAll()
        self.drop_menu.uncheckAll()
        self.refresh()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icon/icon.png')))
    window = JobScanner()
    sys.exit(app.exec_())
