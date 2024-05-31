import sys
import time
import os
from pathlib import Path

import numpy as np
import pandas as pd

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
from qtpy.QtWidgets import (
    QHBoxLayout, QPushButton, QWidget, QFileDialog, 
    QVBoxLayout, QGroupBox, QGridLayout, QTabWidget, QListWidget,
    QDoubleSpinBox, QLabel, QComboBox, QLineEdit, QMainWindow
    #QSpinBox, QPlainTextEdit,
    #QTreeWidget, QTreeWidgetItem, QCheckBox, QSlider, QTableView, QMessageBox, QToolButton
    )
from qtpy.QtCore import QEvent

class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QWidget()
        self.setCentralWidget(self._main)
        self.main_layout = QGridLayout(self._main)
        self.setLayout(self.main_layout)

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        self.main_layout.addWidget(NavigationToolbar(static_canvas, self))
        self.main_layout.addWidget(static_canvas)

        # dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # layout.addWidget(dynamic_canvas)
        # layout.addWidget(NavigationToolbar(dynamic_canvas, self))

        self._static_ax = static_canvas.figure.subplots()
        
        #t = np.linspace(0, 10, 501)
        #self._static_ax.plot(t, np.tan(t), ".")

        # self._dynamic_ax = dynamic_canvas.figure.subplots()
        # t = np.linspace(0, 10, 101)
        # Set up a Line2D.
        # self._line, = self._dynamic_ax.plot(t, np.sin(t + time.time()))
        # self._timer = dynamic_canvas.new_timer(50)
        # self._timer.add_callback(self._update_canvas)
        # self._timer.start()


        self.display_plot_btn = QPushButton("Push") 
        self.main_layout.addWidget(self.display_plot_btn)




        ######## Mot-Correction tab ########
        self.task_widget = QWidget()
        self._task_widget_layout = QVBoxLayout()
        self.task_widget.setLayout(self._task_widget_layout)
        #self.tabs.addTab(self.motion_correction, 'Mot-Correction') # this tab is just ok!
        self.main_layout.addWidget(self.task_widget)

        self.task_group1 = VHGroup('Do here stuff', orientation='G')
        self._task_widget_layout.addWidget(self.task_group1.gbox)

        # label
        self.dir_label = QLabel("File path")
        self.task_group1.glayout.addWidget(self.dir_label, 0, 0, 1, 1)

        # edit line for input directory

        self.dir_edit_box = QLineEdit()
        self.dir_edit_box.installEventFilter(self)
        self.dir_edit_box.setAcceptDrops(True)
        self.dir_edit_box.setPlaceholderText(os.getcwd())
        self.dir_edit_box.setToolTip(("Drag and drop or copy/paste a directory path to export your results"))
        self.task_group1.glayout.addWidget(self.dir_edit_box, 0, 1, 1, 1)

        # explore directory btn

        self.explore_dir_btn = QPushButton("Explore")
        self.explore_dir_btn.setToolTip(("Navigate to add or change the current file."))
        self.task_group1.glayout.addWidget(self.explore_dir_btn, 0, 2, 1, 1)
        
        # explore directory btn

        self.load_dir_btn = QPushButton("load")
        self.explore_dir_btn.setToolTip(("Navigate to add or change the current file."))
        self.task_group1.glayout.addWidget(self.load_dir_btn, 0, 3, 1, 1)

        # selector for plotting
        self.x_selector_label = QLabel("Select x")
        self.task_group1.glayout.addWidget(self.x_selector_label, 1, 0, 1, 1)

        self.x_selector = QComboBox()
        self.task_group1.glayout.addWidget(self.x_selector, 1, 1, 1, 1)

        self.y_selector_label = QLabel("Select y")
        self.task_group1.glayout.addWidget(self.y_selector_label, 1, 2, 1, 1)

        self.y_selector = QComboBox()
        self.task_group1.glayout.addWidget(self.y_selector, 1, 3, 1, 1)

        
        # plotting traces btn
        self.plot_csv_file_bnt = QPushButton("Plot traces")
        self.task_group1.glayout.addWidget(self.plot_csv_file_bnt, 2, 1, 1, 1)




        ##################################################################
        ############################ callbacks ###########################
        ##################################################################

        self.display_plot_btn.clicked.connect(self._display_plot_func)
        self.explore_dir_btn.clicked.connect(self._explore_new_file)
        self.load_dir_btn.clicked.connect(self._load_new_file)
        self.plot_csv_file_bnt.clicked.connect(self._plot_traces_func)


    #def _update_canvas(self):
    #    t = np.linspace(0, 10, 101)
    #    # Shift the sinusoid as a function of time.
    #    self._line.set_data(t, np.sin(t + time.time()))
    #    self._line.figure.canvas.draw()

    def _display_plot_func(self):
        print("you push me")
    
    def _explore_new_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "SLoad csv filey", self.dir_edit_box.placeholderText(), "*.csv")
        self.dir_edit_box.setText(filename)

    def _load_new_file(self):
        self.df = pd.read_csv(self.dir_edit_box.text())

        self.x_selector.clear()
        self.x_selector.addItems(self.df.columns)

        self.y_selector.clear()
        self.y_selector.addItems(self.df.columns)


    def _plot_traces_func(self):
        x = self.df[self.x_selector.currentText()]
        y = self.df[self.y_selector.currentText()]
        #clear canvas
        self._static_ax.cla()
        #plot
        self._line = self._static_ax.plot(x, y, "-")
        self._line[0].figure.canvas.draw()







    def eventFilter(self, source, event):
        """
        #### NOTE: in order to allow drop events, you must allow to drag!!
        found this solution here: https://stackoverflow.com/questions/25505922/dragdrop-from-qlistwidget-to-qplaintextedit 
        and here:https://www.programcreek.com/python/?CodeExample=drop+event
        """
        if (event.type() == QEvent.DragEnter): # and source is self.textedit):
            event.accept()
            # print ('DragEnter')
            return True
        elif (event.type() == QEvent.Drop): # and source is self.textedit):
            dir_name = event.mimeData().text().replace("file://", "")
            
            # handel windows path
            if os.name == "nt":
                # print(dir_name)
                # print(Path(dir_name))
                dir_name = Path(dir_name)
                last_part = dir_name.parts[0]
                # this load files hosted locally
                if last_part.startswith("\\"):
                    # print("ozozozozozoz")
                    dir_name = str(dir_name)[1:]
                else:
                    # this load files hosted in servers
                    # print("lllalalalalalalala")
                    dir_name = "//" + str(dir_name)
                    
            # handel Unix path
            elif os.name == "posix":
                dir_name = dir_name[:-1]
            
            else:
                warn(f"your os with value os.name ='{os.name}' has not be normalized for directory paths yet. Please reach out with the package manteiner to discuss this feature.")
            
            dir_name = os.path.normpath(dir_name)  # find a way here to normalize path
            self.dir_edit_box.setText(dir_name)
            # print ('Drop')
            return True
        else:
            return super(ApplicationWindow, self).eventFilter(source, event)


    # this class helper allow to make gorup layouts easily"
class VHGroup():
    """Group box with specific layout.

    Parameters
    ----------
    name: str
        Name of the group box
    orientation: str
        'V' for vertical, 'H' for horizontal, 'G' for grid
    """

    def __init__(self, name, orientation='V'):
        self.gbox = QGroupBox(name)
        if orientation=='V':
            self.glayout = QVBoxLayout()
        elif orientation=='H':
            self.glayout = QHBoxLayout()
        elif orientation=='G':
            self.glayout = QGridLayout()
        else:
            raise Exception(f"Unknown orientation {orientation}") 

        self.gbox.setLayout(self.glayout)



if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()