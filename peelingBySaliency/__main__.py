import pathlib
import click
import cv2
import numpy as np
import logging
import matplotlib.pyplot as plt
# from peelingBySaliency import pySaliencyMap
from peelingBySaliency import pySaliencyMap
from calculate_simiilar_lines import get_lines
from calculate_simiilar_lines import write_data_to_csv as write_lines
from calculate_simiilar_lines import get_timestamp_str


def peeling(image_path, original_line_path, in_region):
    # Read the image
    img = cv2.imread(image_path)
    image_path = pathlib.Path(image_path)

    # Initialize
    image_size = img.shape
    img_width = image_size[1]
    img_height = image_size[0]
    sm = pySaliencyMap.pySaliencyMap(img_width, img_height)
    # print(img_width, img_height)
    salient_region = sm.SMGetSalientRegion(img)

    logging.debug(salient_region.sum(axis=2).sum(axis=0))
    saliency_sum = salient_region.sum(axis=2).sum(axis=0)
    # saliency_sum = np.where(saliency_sum > 0, 1 , 0)
    all_length = np.where(saliency_sum > 0, 1, 0).sum()
    logging.info("The overall length of the salient region is %d" % all_length)

    # For Debugging
    # """
    # print(np.where(saliency_sum > 0, range(len(saliency_sum)), 0))
    plt.figure(figsize=(6, 6))
    grid = plt.GridSpec(3, 1, wspace=0.5, hspace=0.5)
    plt.subplot(grid[:2, :])
    plt.imshow(cv2.cvtColor(salient_region, cv2.COLOR_BGR2RGB))
    plt.subplot(grid[2, :])
    plt.xlim([0, 1000])
    # plt.bar(np.where(saliency_sum > 0, range(len(saliency_sum)), 0), color='grey')
    plt.plot(range(len(saliency_sum)), saliency_sum)
    plt.show()
    # """

    # GET LINES

    logging.info('Start calculate min/max value of the original data')
    lines = get_lines(original_line_path)
    x_max = x_min = lines[0][0][0]
    y_max = y_min = lines[0][0][1]
    for line in lines:
        l = np.array(line)
        [x_max, y_max] = np.maximum([x_max, y_max], l.max(axis=0))
        [x_min, y_min] = np.minimum([x_min, y_min], l.min(axis=0))
    logging.info('x_max: %d, x_min %d, y_max: %d, y_min: %d', x_max, x_min, y_max, y_min)

    # Calculate if each line in region

    ratio = []

    def translate(domain_left, domain_right, value_left, value_right, domain_value):
        min_domain = min(domain_left, domain_right)
        max_domain = max(domain_left, domain_right)
        if domain_value < min_domain or domain_value > max_domain:
            raise ValueError(
                "The value(%d) is not in interval [%d, %d]" % (domain_value, min_domain, max_domain))
        return abs(domain_value - domain_left) / (max_domain - min_domain) * (
                value_right - value_left) + value_left

    def scale(domain, value):

        def _scale(x):
            return translate(domain[0], domain[1], value[0], value[1], x)

        return _scale

    def line_in_salient_region(line):
        # TODO finish the judgement
        lst = None
        length_cnt = 0
        x = scale([x_min, x_max], [0, img_width - 1])
        y = scale([y_min, y_max], [img_height - 1, 0])
        for cor in line:
            # TODO transform data to the image space coordinate
            nx = int(x(cor[0]))
            ny = int(y(cor[1]))

            if (salient_region[ny, nx] > 0).any():
                if lst:
                    length_cnt += nx - lst
                lst = nx
            else:
                lst = None
        # print(length_cnt, all_length)
        ratio.append(length_cnt / all_length)
        return length_cnt / all_length > 0.4

    logging.info("Start judging if the line in the salient region")
    lines_count = len(lines)
    status = [True for i in range(lines_count)]
    for i in range(lines_count):
        line = lines[i]
        if in_region:
            status[i] = line_in_salient_region(line)
        else:
            status[i] = not line_in_salient_region(line)

    ratio.sort()
    plt.plot(ratio)
    plt.show()

    output_dir = './data/peeling_by_saliency'
    output_dir = pathlib.Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    timestamp = get_timestamp_str()
    image_tail = image_path.parts[-1]
    if in_region:
        data_name = "in_region_" + str(image_tail) + '-' + timestamp
    else:
        data_name = "not_in_region_" + str(image_tail) + '-' + timestamp

    output_path = output_dir / (data_name + '.csv')

    # Export data
    write_lines(output_path, lines, ['Name', 'Time', 'Value'], status)


@click.command()
@click.argument('image')
@click.argument('line')
@click.option('--in-region', '-i', default=False)
def main(image, line, in_region):
    peeling(image, line, in_region)


if __name__ == '__main__':
    main()
