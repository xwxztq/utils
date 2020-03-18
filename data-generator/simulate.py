import random
import numpy as np

INF = 1e9


def simulate_lines(data, number, control_ratio=1.0, min_v=0, max_v=INF):
    if min_v > max_v:
        raise Exception("The min_v is large than max_v")

    def rand():
        return (random.random() - 0.5) * control_ratio

    def make_in_range(value):
        return min(max_v, max(min_v, value))

    (x, y) = (data[0], data[1])

    if len(x) != len(y):
        raise Exception("The x and y coordinates are not equal in length")

    length = len(x)
    coordinates = [x]

    # generate num series of lines
    for cnt in range(number):
        # tmp_x and tmp_y are used to temporarily store data
        rd = rand()
        tmp_y = [y[0] + rand() * (max_v - min_v) * 0.2]
        for i in range(length - 1):
            tmp_y.append(make_in_range(tmp_y[-1] + y[i + 1] - y[i] + rand() * (x[i + 1] - x[i])))
        coordinates.append(np.asarray(tmp_y))

    return coordinates
