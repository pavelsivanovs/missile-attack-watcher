import ast
import csv


def process_csv(input_file, output_file=''):
    if output_file == '':
        output_file = 'processed_' + input_file

    locations = {}

    print('Reading data from file', input_file)
    with open(input_file, mode='r', encoding='utf8') as file:
        reader = csv.reader(file)

        for index, row in enumerate(reader):
            if index == 0:
                continue

            row_locs = ast.literal_eval(row[4])

            for loc in row_locs:
                if loc in locations:
                    locations[loc] = locations[loc] + 1
                else:
                    locations[loc] = 1

    print('Writing processed data into', output_file)
    with open(output_file, mode='w', encoding='utf8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Location', 'Count'])

        for loc, count in sorted(locations.items(), key=lambda item: item[1], reverse=True):
            writer.writerow([loc, count])


if __name__ == '__main__':
    process_csv('twitter_25_26.csv')
