from PyQt5.uic import loadUiType
from matplotlib.widgets import RectangleSelector
from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from PyQt5 import QtCore, QtGui, QtWidgets
import meep as mp
Ui_MainWindow, QMainWindow = loadUiType('sandbox.ui')

import matplotlib.pyplot as plt
plt.style.use('dark_background')

def runsim(x, y, X, Y):
    print(x, y)
    cell = mp.Vector3(40,40,0)
    e = mp.Ellipsoid(size=mp.Vector3(3, 3, mp.inf))
    e.material = mp.Medium(epsilon=6)
    e.center = mp.Vector3(x, y, 0)
    geometry = [mp.Block(mp.Vector3(mp.inf,2,mp.inf),
                         center=mp.Vector3(),
                         material=mp.Medium(epsilon=12)),
                mp.Block(mp.Vector3(2,mp.inf,mp.inf),
                         center=mp.Vector3(),
                         material=mp.Medium(epsilon=12)),
                e
                ]

    sources = [mp.Source(mp.ContinuousSource(frequency=0.15),
                         component=mp.Ez,
                         center=mp.Vector3(X,Y))]

    pml_layers = [mp.PML(1.0)]

    resolution = 10

    sim = mp.Simulation(cell_size=cell,
                        boundary_layers=pml_layers,
                        geometry=geometry,
                        sources=sources,
                        resolution=resolution)

    sim.run(until=200)
    

    eps_data = sim.get_array(center=mp.Vector3(), size=cell, component=mp.Dielectric)
    ez_data = sim.get_array(center=mp.Vector3(), size=cell, component=mp.Ez)
    return np.flipud(eps_data.transpose()), np.flipud(ez_data.transpose())

class RS(object):
    def __init__(self, ax):
        self.ax = ax
        self.RS_list = []
    def toggle_selector(self, event):
        if event.key in ['Q', 'q']:
            self.RS_list.append(RectangleSelector(self.ax, line_select_callback,
                                                   drawtype='box', useblit=False,
                                                   button=[3],  # don't use middle button
                                                   minspanx=5, minspany=5,
                                                   spancoords='pixels',
                                                   interactive=True)
                                      )
        if event.key in ['A', 'a'] and not toggle_selector.RS.active:
            pass
    
def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    print(" The button you used were: %s %s" % (eclick.button, erelease.button))

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.fig = None
        self.pind = None
        self.source_point = None
        self.autoGenerate = True
        self.rs = RS(None)

    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        # self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.mplvl.addWidget(self.canvas)
        self.canvas.update()
        self.canvas.setFocus()
        self.toolbar = NavigationToolbar(self.canvas, 
                self.mplwindows, coordinates=True)
        self.addToolBar(self.toolbar)
        self.rs.ax = self.ax1f1
        self.ax1f1.figure.canvas.mpl_connect('pick_event', self.button_pick_callback)
        self.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.cid = self.canvas.mpl_connect('key_press_event', self.rs.toggle_selector)


    def rmmpl(self):
        if hasattr(self, 'canvas'):
            while self.mplvl.count():
                child = self.mplvl.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        if hasattr(self, 'toolbar'):
            try:
                self.mplvl.removeWidget(self.toolbar)
                self.toolbar.close()
            except:
                pass

    def createFigure(self):
        self.fig = Figure()
        self.ax1f1 = self.fig.add_subplot(111)
        x = self.box_x.value()
        y = self.box_y.value()
        X = self.loc_x.value()
        Y = self.loc_y.value()
        d1, d2 = runsim(x, y, X, Y)
        self.ax1f1.imshow(d2, interpolation='spline36', 
                     cmap='RdBu', 
                     alpha=1.0,
                     # extent=(-x/2, x/2, -y/2, y/2)
                     extent=(-20, 20, -20, 20)
                     )
        self.source_point = self.ax1f1.plot([X], [Y], 
                                            'ob', 
                                            picker=5,
                                            alpha=0.5)
        self.rmmpl()
        self.addmpl(self.fig)
        return 

    def button_pick_callback(self, event):
        if event.mouseevent.button != 1:
            return
        self.pind = 1    

    def button_release_callback(self, event):
        if self.pind is None:
            return
        if event.button != 1:
            return
        self.pind = None
        if self.autoGenerate:
            self.createFigure()

    def motion_notify_callback(self, event):
        if self.pind is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        self.loc_x.setValue(event.xdata)
        self.loc_y.setValue(event.ydata)
        self.source_point[0].set_xdata([event.xdata])
        self.source_point[0].set_ydata([event.ydata])
        self.fig.canvas.draw()


if __name__ == '__main__':
    import sys
    from PyQt5 import QtGui

    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.createFigure()
    main.generateButton.clicked.connect(main.createFigure)
    main.show()
    sys.exit(app.exec_())