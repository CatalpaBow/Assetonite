import numpy as np
from numpy import ndarray
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph import PlotItem
from collections import deque
from PyQt6.QtCore import QTimer

class TelemetryPlotter(QtCore.QObject):
    def __init__(self, initial_data : ndarray = np.empty((0, 2))):
        #SetupMainWidget
        self.data_queue = deque()
        self.app = pg.mkQApp('Telemetry Plotting')
        self.win = pg.GraphicsLayoutWidget(show=False,title="Telemetry Plotting")
        self.win.resize(800,600)
        pg.setConfigOptions(antialias=True)

        #CreatePlot
        self.data = initial_data
        self.p1 : PlotItem = self.win.addPlot(title='Telemetry')
        self.p1.getViewBox().setAspectLocked(True)
        self.curve = self.p1.plot(name='Coordinate')
        self.curve.setData(self.data)
        self.win.show()
    
    def update(self, x : float,y :float):
        self.data_queue.append((x,y))

    def _on_timer_tick(self):
        def tick():
            if self.data_queue:
                new_data = np.array(self.data_queue)
                self.data = np.vstack((self.data, new_data))
                self.curve.setData(self.data)
                self.data_queue.clear()
        return tick

    def run(self):
        self.win.show()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_tick())
        self.timer.start(16)
        self.app.exec()
    
    def close(self):
        self.win.hide()
        self.win.close()
        self.app.closeAllWindows()

    def __del__(self):
        self.close()
        

def timer_update(pltr : TelemetryPlotter):
    x0 = 0
    y0 = 0
    def _update():
        nonlocal x0, y0
        x0 += 1
        y0 += 1
        pltr.update(x0,y0)
    return _update

if __name__ == '__main__':
    pltr = TelemetryPlotter()
    x = np.arange(-10, 10, 0.1)
    y = y = x**2
    timer = QtCore.QTimer()
    timer.timeout.connect(timer_update(pltr))
    timer.start(100)
    pltr.run()
    print('hoge')