"""Plot data for csv format"""
import pathlib
import click
import csv
import json
import pandas
import matplotlib.pyplot as plt


@click.command()
@click.option('--data-path', '-d', help='Original Data for Plotting', default='data/data.csv')
@click.option('--cluster-data-path', '-c', help='Clustering Result with json format', default='data/density.json')
def plot_data(data_path, cluster_data_path):
    """Load csv data for plotting"""
    data_path = pathlib.Path(data_path)
    cluster_data_path = pathlib.Path(cluster_data_path)
    if not data_path.exists():
        print("ERROR: the file%s doesn't exist" % str(data_path))
        exit(1)
    if not cluster_data_path.exists():
        print("ERROR: the file %s doesn't exist" % str(cluster_data_path))
        exit(1)

    mp = dict()
    with open(data_path, newline='\n') as csv_file:
        plt.xlim(0, 20)
        plt.ylim(0, 25)
        reader = csv.reader(csv_file)
        is_first_row = True
        first_row = ''

        x = []
        y = []
        lst_name = None
        for row in reader:
            if len(row) == 0:
                continue
            if is_first_row:
                first_row = row
                is_first_row = False
                continue

            if row[0] != lst_name:
                if lst_name is not None:
                    mp[lst_name] = [x, y]
                lst_name = row[0]
                x = []
                y = []
            x.append(float(row[1]))
            y.append(float(row[2]))

    with open('data/density.json') as f:
        res = json.loads(f.read())
        cluster_res = res['clusterIndices']

        for i in range(len(cluster_res)):
            cluster_num = cluster_res[i]
            plt.subplot(2, 2, cluster_num + 1)
            plt.xlim(0, 20)
            plt.ylim(0, 25)
            if mp.get(str(i)):
                plt.plot(mp[str(i)][0], mp[str(i)][1])
        plt.show()


if __name__ == "__main__":
    plot_data()
