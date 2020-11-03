import matplotlib.pyplot as plt
import pathlib
import pandas
import numpy as np
import datetime


class DrawLines(object):
    """
    A class for drawing line above a image.
    """

    def __init__(self, img_data):
        """
        Initial the class background.
        :param img_data:
        """
        self.drag_cids = []
        self.fig, self.ax = self.setup_axes(img_data)
        self.x = []
        self.y = []
        self.all_lines = None

        self.cnt = 0

        self.lines = self.ax.plot([], [])
        connect = self.fig.canvas.mpl_connect
        connect('button_press_event', self.on_click)
        self.draw_cid = connect('draw_event', self.grab_background)

    def setup_axes(self, img_data):
        """Setup the figure/axes and plot any background artists"""
        fig, ax = plt.subplots()

        # Display the background.
        ax.imshow(img_data)
        ax.set_title('Left click to add lines.\nRight click to delete')

        return fig, ax

    def on_click(self, event):
        """Decide whether to add or drag a line"""

        # if self.fig.canvas.toolbar._active is not None:
        #     return

        for i, line in zip(range(len(self.lines)), self.lines):
            contains, info = line.contains(event)
            if contains:
                # In future version, need to deal with the drag-problem
                return

        """If no lines contains the event, deal with adding new lines"""
        self.create_new_line(event)

    def create_new_line(self, event):
        """Create new line"""

        # Need to create listen event
        connect = self.fig.canvas.mpl_connect
        cid1 = connect('motion_notify_event', self.draw_update)
        cid2 = connect('button_release_event', self.end_drag)
        cid3 = connect('axes_leave_event', self.end_drag)
        self.drag_cids = [cid1, cid2, cid3]

    def draw_update(self, event):
        """When move the mouse, update current point to the canvas"""
        # TODO
        self.x.append(event.xdata)
        self.y.append(event.ydata)
        self.update()

    def end_drag(self, event):
        """When drag event ends, stop recording"""
        # TODO There're two possible event: 1. leave axes 2. button release
        self.lines = self.ax.plot([], [])

        lst_line = np.vstack(([self.cnt] * len(self.x), self.x, self.y))
        if self.all_lines is None:
            self.all_lines = lst_line
        else:
            self.all_lines = np.concatenate((self.all_lines, lst_line), axis=1)

        # Init the variables
        self.x = []
        self.y = []
        self.cnt += 1
        for cid in self.drag_cids:
            self.fig.canvas.mpl_disconnect(cid)

        self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)

    def safe_draw(self):
        """Temporarily disconnect the draw_event callback to avoid recursion."""
        canvas = self.fig.canvas
        canvas.mpl_disconnect(self.draw_cid)
        canvas.draw()
        self.draw_cid = canvas.mpl_connect('draw_event', self.grab_background)

    def update(self):
        """Update the lines for any change to self.lines"""
        self.lines[-1].set_xdata(self.x)
        self.lines[-1].set_ydata(self.y)
        self.blit()

    def grab_background(self, event=None):
        """
        When the figure is resized, hide the lines, draw everything,
        and update the background
        :param event:
        :return:
        """
        for line in self.lines:
            line.set_visible(False)
        self.safe_draw()

        self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)
        for line in self.lines:
            line.set_visible(True)
        self.blit()

    def blit(self):
        """
        Efficiently update the figure, without needing to redraw the
        "background" artists.
        :return:
        """
        self.fig.canvas.restore_region(self.background)
        for line in self.lines:
            self.ax.draw_artist(line)
        self.fig.canvas.blit(self.fig.bbox)

    def show(self):
        plt.show()

    def export(self, file_path=None, translate_value=None):
        """
        Export the drawn data to csv file
        :param file_path: file path for export
        :param translate_value: Scale value for translating [minX, maxX, minY, maxY]
        :return:
        """
        if file_path is None:
            file_path = pathlib.Path('./data/draw_data/data.csv')

        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)

        original_line = self.all_lines.copy()

        if translate_value is not None and self.all_lines is not None:
            for value in translate_value:
                value = float(value)

            def translate(domain_left, domain_right, value_left, value_right, domain_value):
                min_domain = min(domain_left, domain_right)
                max_domain = max(domain_left, domain_right)
                if domain_value < min_domain or domain_value > max_domain:
                    raise ValueError(
                        "The value(%d) is not in interval [%d, %d]" % (domain_value, min_domain, max_domain))
                return abs(domain_value - domain_left) / (max_domain - min_domain) * (
                            value_right - value_left) + value_left

            def translate_x(value):
                xlim = self.ax.get_xlim()
                return translate(xlim[0], xlim[1], translate_value[0], translate_value[1], value)

            def translate_y(value):
                ylim = self.ax.get_ylim()
                return translate(ylim[0], ylim[1], translate_value[2], translate_value[3], value)

            length = self.all_lines.shape[1]
            for i in range(length):
                self.all_lines[1][i] = translate_x(self.all_lines[1][i])
                self.all_lines[2][i] = translate_y(self.all_lines[2][i])

        df = pandas.DataFrame(np.transpose(self.all_lines))
        df2 = pandas.DataFrame(np.transpose(original_line))

        parent = file_path.parent
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        new_dir = parent / timestamp
        new_dir.mkdir(parents=True)

        df.to_csv(new_dir / file_path.name, header=["name", "time", "value"], index=False)
        df2.to_csv(new_dir / "original_lines.csv", header=["name", "time", "value"], index=False)