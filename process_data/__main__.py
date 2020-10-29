"""Convert the value into numerical value."""

import datetime
import pathlib
import pandas


def valid_number(number_text):
    try:
        float(number_text)
    except ValueError:
        return False
    return True


DATE_FORMAT = [
    "%Y/%m/%d",
    "%Y-%m-%d",
]


def valid_date(date_text):
    """Judge the date is valid for parsing."""
    for fmt in DATE_FORMAT:
        try:
            datetime.datetime.strptime(date_text, fmt)
        except ValueError:
            continue
        return True
    return False


def parse_date(date_text):
    for fmt in DATE_FORMAT:
        try:
            return datetime.datetime.strptime(date_text, fmt)
        except ValueError:
            continue
    raise ValueError("Current parsing format [%s] cannot format the string -> %s" % (', '.join(DATE_FORMAT), date_text))


def convert_data(file_path, fields=[]):
    file_path = pathlib.Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError("The file not found --> %s" % str(file_path))

    df = pandas.read_csv(file_path)
    length = len(df)

    min_time = {}
    # Convert the numerical field and update the minimal date field
    result = []
    for i in range(1, length):
        tmp = []
        for field in fields:
            if valid_number(df[field][i]):
                tmp.append(float(df[field][i]))
            elif valid_date(df[field][i]):
                dt = parse_date(df[field][i])
                tmp.append(dt)
                min_time[field] = min(min_time.get(field) or dt, dt)
            else:
                tmp.append(df[field][i])
        result.append(tmp)

    # Update the date field
    for i in range(length-1):
        for j in range(len(fields)):
            if type(result[i][j]) is datetime.datetime:
                result[i][j] = (result[i][j] - min_time[fields[j]]).days

    print(result)

    pandas.DataFrame(result).to_csv("transformed-data-%s.csv" % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
                                    index=False,
                                    header=fields)


if __name__ == '__main__':
    convert_data("../data/stocks_after_2006.filtered.csv", ["Symbol", "Date", "Open"])
