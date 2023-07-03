import sys 
import csv
import json

def flatten_csv(input_data):
    reader = csv.reader(input_data)
    header = next(reader)
    output_rows = []
    for row in reader:
        label = row[0]
        for i in range(1, len(row)):
            new_key = (label + '-' + header[i]).replace(' ', '_')
            new_value = row[i]
            output_rows.append({new_key: new_value})

    return json.dumps(output_rows)

with open(sys.argv[1], 'r') as input_file:
    json_output = flatten_csv(input_file)

print(json_output)
