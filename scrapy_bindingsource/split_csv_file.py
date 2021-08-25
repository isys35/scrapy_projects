import csv


def write_csv(file_name, data):
    print(file_name)
    with open(file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)


with open('data.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    count_file = 0
    count_row = 0
    data_to_write = []
    for row in reader:
        data_to_write.append(row)
        count_row += 1
        if count_row == 20000:
            count_file += 1
            write_csv('{}.csv'.format(count_file), data_to_write)
            data_to_write = []
            count_row = 0
