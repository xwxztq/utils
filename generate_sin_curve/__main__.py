import csv
import pathlib
import math
from calculate_simiilar_lines import get_timestamp_str


if __name__ == '__main__':

    save_dir = pathlib.Path('../data/sin_curve')
    if not save_dir.exists():
        save_dir.mkdir(parents=True)

    timestamp = get_timestamp_str()

    save_path = save_dir / (timestamp +  '.csv')

    with open(save_path, 'w', newline='\n') as f_out:
        f_writer = csv.writer(f_out)

        f_writer.writerow(['name', 'time', 'value'])

        num_of_lines = 1
        time_range = 1000
        PI = math.pi
        for i in range(num_of_lines):
            delta = i / num_of_lines * 2 * PI
            for t in range(time_range):
                x = t / 100
                f_writer.writerow([i, x, math.sin(x+delta) + 1])
