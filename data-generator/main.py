import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
import csv
from simulate import simulate_lines

BATCH_SIZE = 200
EPS = 0.1


class SimulateLine:

    def __init__(self, figure, axes):

        self.lines = []
        self.line_count = 0
        self.is_recording = False
        self.data_x = []
        self.data_y = []
        self.tmp_x = []
        self.tmp_y = []
        self.fig = figure
        self.ax = axes

        self.fig.canvas.mpl_connect(
            'button_press_event', self.button_press
        )
        self.fig.canvas.mpl_connect(
            'button_release_event', self.button_release
        )
        self.fig.canvas.mpl_connect(
            'axes_leave_event', self.leave_axes
        )
        self.fig.canvas.mpl_connect(
            'motion_notify_event', self.mouse_motion
        )

    def leave_axes(self, event):
        print('Leave axes', event.inaxes)
        self.stop_recording()

    def button_release(self, event):
        print('Button release: ', event.button)
        if event.button == MouseButton.LEFT:
            self.stop_recording()

    def button_press(self, event):
        print('Button press:', event.button)
        if event.button == MouseButton.LEFT:
            self.start_recording()

        elif event.button == MouseButton.RIGHT:
            self.undo()

        elif event.button == MouseButton.MIDDLE:
            if not self.line_count:
                return
            current_line = self.lines[self.line_count -1]
            ret = simulate_lines(current_line.get_data(), BATCH_SIZE, 2, 0, 24)
            self.ax.plot(ret[0], np.transpose(ret[1:]))
            fig.canvas.draw()
            data_length = len(ret)
            for i in range(1, data_length):
                self.data_x.append(ret[0])
                self.data_y.append(ret[i])



    def start_recording(self):
        while len(self.lines) > self.line_count:
            # delete the lines will be covered
            self.lines.pop()
        self.lines.append(self.ax.plot([], [])[0])
        self.line_count += 1
        self.is_recording = True
        # for i in len(self.tmp_x):
        #     self.data_x.append(self.tmp_x[i])
        #     self.data_y.append(self.tmp_y[i])
        self.tmp_x = []
        self.tmp_y = []

    def stop_recording(self):
        self.is_recording = False

    def undo(self):
        print('undo line', self.is_recording)
        if self.is_recording:
            return
        if self.line_count >= 0:
            print('delete the last line')
            self.line_count -= 1
            current_line = self.lines[self.line_count]
            current_line.set_xdata([])
            current_line.set_ydata([])
            fig.canvas.draw()

    def mouse_motion(self, event):
        if self.is_recording and event.button == MouseButton.LEFT:
            x, y = event.xdata, event.ydata
            current_line = self.lines[-1]
            print(type(current_line))
            [x_array, y_array] = current_line.get_data()
            print(x_array)
            if len(x_array) and x < x_array[-1] + EPS:
                return
            x_array = np.append(x_array, x)
            y_array = np.append(y_array, y)
            current_line.set_xdata(x_array)
            current_line.set_ydata(y_array)

        # elif event.button == MouseButton.MIDDLE:
        fig.canvas.draw()

    def export(self, url):
        if len(self.tmp_x):
            self.start_recording()
        # print(self.tmp_x)
        # print(self.data_x)
        with open(url, 'w+') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(['name', 'x', 'y'])
            for i in range(len(self.data_x)):
                xx = self.data_x[i]
                yy = self.data_y[i]
                data_size = len(yy)
                for j in range(data_size):
                    f_csv.writerow([i, xx[j], yy[j]])



fig, ax = plt.subplots(figsize=(14, 7))
ax.set_xlim(0, 20)
ax.set_ylim(0, 25)

sl = SimulateLine(fig, ax)



Last_line = None
Current_line = ax.plot([], [])[0]

arr = []


def start_recording(event):
    print('start recording', event.button)
    print(event.button == MouseButton.LEFT)
    print(type(Current_line))
    arr.append(len(arr))
    print(arr)
    Current_line.set_xdata(arr)
    Current_line.set_ydata(arr)
    fig.canvas.draw()


def stop_recording():
    last_line = current_line
    current_line = None

# fig.canvas.mpl_connect('button_press_event', start_recording)


# rects = ax.bar(range(10), 20 * np.random.rand(10))
# drs = []
# for rect in rects:
#     dr = DraggableRectangle(rect)
#     dr.connect()
#     drs.append(dr)
#
plt.show()


sl.export("./data.csv")
