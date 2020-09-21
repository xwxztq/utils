import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
import csv, os, random, shutil, logging
from simulate import simulate_lines
import pathlib
import click

logging.basicConfig(level=logging.WARN, format="%(levelname)s:%(asctime)s:%(funcName)s---->%(message)s")

BATCH_SIZE = 500
EPS = 0.1
CONTROL_RATIO = 0.5


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
        self.fig_name = str(random.random()) + 'fig.png'

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
        logging.debug(event.inaxes)
        self.stop_recording()

    def button_release(self, event):
        logging.debug(event.button)
        if event.button == MouseButton.LEFT:
            self.stop_recording()

    def button_press(self, event):
        logging.debug(event.button)
        # if click the left button, then start recording
        if event.button == MouseButton.LEFT:
            self.start_recording()

        elif event.button == MouseButton.RIGHT:
            # if cilck the right button, then undo last recording
            self.undo()

        elif event.button == MouseButton.MIDDLE:
            # if click the middle button, then generate similar lines
            if not self.line_count:
                return
            current_line = self.lines[self.line_count - 1]
            ret = simulate_lines(current_line.get_data(), BATCH_SIZE, CONTROL_RATIO, 0, 24)
            self.ax.plot(ret[0], np.transpose(ret[1:]))
            fig.canvas.draw()
            fig.savefig(os.path.join('./', self.fig_name))
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
        # todo 支持真正的撤销
        # for i in len(self.tmp_x):G
        #     self.data_x.append(self.tmp_x[i])
        #     self.data_y.append(self.tmp_y[i])
        self.tmp_x = []
        self.tmp_y = []

    def stop_recording(self):
        self.is_recording = False

    def undo(self):
        logging.debug(self.is_recording)
        if self.is_recording:
            return
        if self.line_count >= 0:
            logging.info('delete the last line')
            self.line_count -= 1
            current_line = self.lines[self.line_count]
            current_line.set_xdata([])
            current_line.set_ydata([])
            fig.canvas.draw()

    def mouse_motion(self, event):
        if self.is_recording and event.button == MouseButton.LEFT:
            x, y = event.xdata, event.ydata
            current_line = self.lines[-1]
            [x_array, y_array] = current_line.get_data()
            logging.info(x_array)
            if len(x_array) and x < x_array[-1] + EPS:
                return
            x_array = np.append(x_array, x)
            y_array = np.append(y_array, y)
            current_line.set_xdata(x_array)
            current_line.set_ydata(y_array)

        # elif event.button == MouseButton.MIDDLE:
        fig.canvas.draw()

    def export(self, url=''):
        head, tail = os.path.split(url)

        # deal with the remaining data
        if len(self.tmp_x):
            self.start_recording()
        data_dir = pathlib.Path('./data')
        if not data_dir.exists():
            data_dir.mkdir()
        file_name = os.listdir(data_dir)
        logging.debug("These are filenames in data directory")
        logging.debug(file_name)
        dir_count = 0

        def is_dir(name):
            if os.path.isdir(os.path.join(data_dir, name)):
                return 1
            return 0

        dir_count = sum(map(is_dir, file_name))

        # 如果目录不存在则新建, 否则按顺序新建
        if head != '':
            if os.path.exists(head):
                pass
            else:
                os.mkdir(head)
        else:
            head = os.path.join(data_dir, "case" + str(dir_count))
            os.mkdir(head)

        if tail == '':
            tail = 'data.csv'

        # export data
        with open(os.path.join(head, tail), 'w+', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(['name', 'x', 'y'])
            for i in range(len(self.data_x)):
                xx = self.data_x[i]
                yy = self.data_y[i]
                data_size = len(yy)
                for j in range(data_size):
                    f_csv.writerow([i, xx[j], yy[j]])

        # export ground truth
        with open(os.path.join(head, 'representative line.csv'), 'w+', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(['name', 'x', 'y'])
            for i in range(len(self.lines)):
                xx, yy = self.lines[i].get_data()
                line_size = xx.shape[0]
                for j in range(line_size):
                    f_csv.writerow([i, xx[j], yy[j]])

        logging.debug(os.path.join(head, 'figure.png'))
        shutil.copyfile(os.path.join('./', self.fig_name), os.path.join(head, 'fig.png'))
        os.remove(os.path.join('./', self.fig_name))
        # plt.show()
        # fig.savefig(os.path.join(head,'figure.png'))
        # print("Data and figure are exported to ", os.path.join(head, tail))
        print("Data and figure are exported to ", os.path.join(head, tail))


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 25)

    sl = SimulateLine(fig, ax)

    Last_line = None
    Current_line = ax.plot([], [])[0]

    arr = []


    def start_recording(event):
        logging.debug(event.button)
        arr.append(len(arr))
        logging.info(arr)
        Current_line.set_xdata(arr)
        Current_line.set_ydata(arr)
        fig.canvas.draw()


    def stop_recording():
        last_line = current_line
        current_line = None


    plt.show()

    sl.export()
