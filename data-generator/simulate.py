import random
import numpy as np


def simulate_lines(data, number, control_ratio=1.0):
    def rand():
        return (random.random() - 1.0) * control_ratio

    (x, y) = (data[0], data[1])

    if len(x) != len(y):
        raise Exception("The x and y coordinates are not equal in length")

    length = len(x)
    coordinates = [x]

    # generate num series of lines
    for cnt in range(number):
        # tmp_x and tmp_y are used to temporarily store data
        tmp_y = [y[0] + rand()]
        for i in range(length - 1):
            tmp_y.append(y[i] + (y[i + 1] - y[i] + rand()) * (x[i + 1] - x[i]))

        coordinates.append(np.asarray(tmp_y))

    return coordinates
