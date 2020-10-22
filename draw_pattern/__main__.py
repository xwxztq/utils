"""Draw pattern with background."""
import click
import pathlib
import matplotlib.image as mpimg
from draw_pattern.draw_lines import DrawLines
import pandas


@click.command()
@click.argument('image_path')
@click.option('--save-path', default='./data')
@click.option('--data-path')
@click.option('--time-field', type=str)
@click.option('--value-field', type=str)
def draw_pattern(image_path, save_path, data_path, time_field, value_field):
    save_path = pathlib.Path(save_path)
    image_path = pathlib.Path(image_path)

    if not save_path.exists():
        print("The save path is not valid")
        exit(1)

    if not image_path.exists():
        print("The file doesn't exist")
        exit(1)

    img = mpimg.imread(image_path)  # Read the image data

    draw_lines = DrawLines(img)
    draw_lines.show()

    # if specify the data.csv, translate the value
    if data_path is not None:
        data_path = pathlib.Path(data_path)
        if not data_path.exists():
            raise FileNotFoundError("The file %s doesn't exist" % str(data_path))

        df = pandas.read_csv(data_path)
        translation = [df[time_field].min(), df[time_field].max(), df[value_field].min(), df[value_field].max()]
        draw_lines.export(translate_value=translation)

    else:
        draw_lines.export()


if __name__ == '__main__':
    draw_pattern()
