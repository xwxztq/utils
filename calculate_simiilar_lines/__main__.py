"""Calculating the similar lines for some lines."""
import csv
import matplotlib.pyplot as plt
import datetime
import logging
import matplotlib.image as mip

logging.basicConfig(level=logging.INFO)

INF = 1e9


def similarity_with_l0(line_a, line_b) -> float:
    len_a = len(line_a)
    len_b = len(line_b)
    ind_a = 0
    ind_b = 0
    result = 0
    cnt = 0
    negative_sign = False
    positive_sign = False
    min_value = INF

    while ind_a < len_a and ind_b < len_b:
        lst = None
        cur = None
        compare = None
        if line_a[ind_a][0] < line_b[ind_b][0]:
            if ind_b > 0:
                lst = line_b[ind_b - 1]
                cur = line_b[ind_b]
                compare = line_a[ind_a]
            ind_a += 1
        else:
            if ind_a > 0:
                lst = line_a[ind_a - 1]
                cur = line_a[ind_a]
                compare = line_b[ind_b]
            ind_b += 1
        if lst:
            value = (cur[1] - lst[1]) / (cur[0] - lst[0]) * (compare[0] - lst[0]) + lst[1]
            # print(value, lst, cur, compare)
            if value - compare[1] > 0:
                positive_sign = True
            else:
                negative_sign = True
            value = abs(value - compare[1])
            min_value = min(value, min_value)
            result += value
            cnt += 1

    # print(cnt, min_value, negative_sign, positive_sign, (min_value < 1e-5 or (negative_sign and positive_sign)))
    if cnt and (min_value < 1e-5 or (negative_sign and positive_sign)):
        # if cnt:
        result /= cnt
    else:
        result = INF
    return result


def is_similar(line_a, line_b, threehold=10):
    len_a = len(line_a)
    len_b = len(line_b)
    ind_a = 0
    ind_b = 0
    flag = True
    common_point = False

    while ind_a < len_a and ind_b < len_b:
        lst = None
        cur = None
        compare = None
        if line_a[ind_a][0] < line_b[ind_b][0]:
            if ind_b > 0:
                lst = line_b[ind_b - 1]
                cur = line_b[ind_b]
                compare = line_a[ind_a]
            ind_a += 1
        else:
            if ind_a > 0:
                lst = line_a[ind_a - 1]
                cur = line_a[ind_a]
                compare = line_b[ind_b]
            ind_b += 1
        if lst:
            value = (cur[1] - lst[1]) / (cur[0] - lst[0]) * (compare[0] - lst[0]) + lst[1]
            value = abs(value - compare[1])
            flag = (value < threehold) and flag
            common_point = True

    return flag and common_point


def in_box(x, y, line):
    lst = None
    flag = True
    for point in line:
        if x[0] < point[0] < x[1]:
            flag = flag and (y[0] < point[1] < y[1])

        if lst is not None:
            k = (point[1] - lst[1]) / (point[0] - lst[0])

            if lst[0] < x[0] < point[0]:
                yy = (x[0] - lst[0]) * k + lst[1]
                flag = flag and (y[0] < yy < y[1])

            elif lst[0] < x[1] < point[0]:
                yy = (x[1] - lst[0]) * k + lst[1]
                flag = flag and (y[0] < yy < y[1])
        lst = point
        if not flag:
            return False

    return True


def get_lines(filepath):
    """Get lines from csv file."""
    lines = []
    with open(filepath) as fin:
        f_csv = csv.reader(fin)
        lst_name = None
        first_row = True
        tmp = []
        for row in f_csv:
            try:
                if first_row:
                    first_row = False
                    continue
                if lst_name and lst_name != row[0]:
                    lines.append(tmp)
                    tmp = []
                tmp.append([float(row[1]), float(row[2])])
                lst_name = row[0]
            except IndexError:
                continue
        lines.append(tmp)

    return lines


def draw_similarity_relation():
    # version 1 stock data
    drawn_lines = get_lines('../data/draw_data/2020-10-23-160830/data.csv')
    original_lines = get_lines('../data/transformed-data-2020-10-20-16-19-11.csv')

    # version 2 sin curve
    # drawn_lines = get_lines('../data/draw_data/2020-10-23-171357/data.csv')
    # original_lines = get_lines(r'D:\san\onedrive\IRC\gt\line density\figure\fig6\sin curve.csv')

    print(len(drawn_lines))
    print(len(original_lines))

    fig, ax = plt.subplots()
    cnt = 0
    for d_line in drawn_lines:
        tmp = []
        for o_line in original_lines:
            tmp.append(similarity_with_l0(d_line, o_line))

        tmp.sort()
        print(tmp)
        ind = 0
        # print(tmp)
        while ind < len(tmp) and tmp[ind] < INF:
            ind += 1
        ax.plot(tmp[:ind], range(ind), label=str(cnt))

        cnt += 1

    ax.set_xlabel("Difference")
    ax.set_ylabel("Line Count")
    ax.set_title("Line count with increasing difference")
    ax.legend()

    plt.show()


def write_data_to_csv(file_path, data_list: list, header, draw_flag=None):
    if draw_flag is None:
        draw_flag = [True] * len(data_list)

    cnt = 0
    with open(file_path, 'w', newline='\n') as f_out:
        f_writer = csv.writer(f_out)
        f_writer.writerow(header)
        for i in range(len(data_list)):
            if draw_flag[i]:
                cnt += 1
                for row in data_list[i]:
                    f_writer.writerow([i, row[0], row[1]])

    logging.info("%d lines in total, stored in %s" % (cnt, file_path))


def delete_lines_similar():
    drawn_lines = get_lines('../data/draw_data/2020-10-23-160830/data.csv')
    original_lines = get_lines('../data/transformed-data-2020-10-20-16-19-11.csv')

    arr = [True for i in range(len(original_lines))]
    for d_line in drawn_lines:
        for i, o_line in zip(range(len(original_lines)), original_lines):
            if is_similar(d_line, o_line):
                arr[i] = False

    write_data_to_csv('../data/data-not-similar.csv', original_lines, ['name', 'time', 'value'], arr)


def draw_in_box():

    original_lines = get_lines('../data/transformed-data-2020-10-20-16-19-11.csv')

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    with open('../data/line-in-box%s.csv' % timestamp, 'w', newline='\n') as f_out:
        f_writer = csv.writer(f_out)
        f_writer.writerow(['name', 'time', 'value'])

        cnt = 0
        for i in range(len(original_lines)):
            if in_box([3900, 4179], [24, 26], original_lines[i]):
                cnt += 1
                for d in original_lines[i]:
                    if len(d) != 2:
                        continue
                    f_writer.writerow([i, d[0], d[1]])

        print(cnt)


def find_lines_similar(target, lines):
    # drawn_lines = get_lines('../data/draw_data/2020-11-03-144957/data.csv')
    # original_lines = get_lines('../data/transformed-data-2020-10-20-16-19-11.csv')

    arr = [True for i in range(len(lines))]
    for d_line in target:
        for i, o_line in zip(range(len(lines)), lines):
            if not is_similar(d_line, o_line, 3):
                arr[i] = False

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    write_data_to_csv('../data/data-is-similar-%s.csv' % timestamp, lines, ['name', 'time', 'value'], arr)


def plot_lines(lines, img_path):
    # draw_lines = get_lines('../data/draw_data/2020-11-03-150010/original_lines.csv')
    # image_path = '../data/images/stock_data.png'
    fig, ax = plt.subplots()

    img = mip.imread(img_path)
    ax.imshow(img)
    for line in lines:
        x = []
        y = []
        for point in line:
            x.append(point[0])
            y.append(point[1])
        ax.plot(x, y)
    plt.show()


if __name__ == '__main__':

    drawn_path = '../data/draw_data/2020-11-03-160712/'
    drawn_lines = get_lines(drawn_path + 'original_lines.csv')
    transformed_drawn_lines = get_lines(drawn_path + 'data.csv')
    original_lines = get_lines('../data/transformed-data-2020-10-20-16-19-11.csv')
    image_path = '../data/images/stock_data.png'
    # drawn_lines = get_lines('../data/draw_data/2020-11-03-144957/data.csv')
    # original_lines = get_lines('../data/transformed-data-2020-10-20-16-19-11.csv')

    plot_lines(drawn_lines, image_path)
    find_lines_similar(transformed_drawn_lines, original_lines)
    # find_lines_similar()
