import json, csv

def read_json(json_fp):
    '''Reads a json and returns the enclosed data.'''
    with open (json_fp,'r') as json_file:
        data = json.load(json_file)
        return data

def term_search(term,search_dict):
    '''Returns a dictionary of frequencies for the search term on any given date.'''
    frequencies = {}
    for entry in search_dict:
        if entry['party'] == 'Republican':
            if term in entry['Body']:
                if frequencies.has_key(entry['Date']):
                    frequencies[entry['Date']] += 1
                else:
                    frequencies[entry['Date']] = 1
            else:
                if not frequencies.has_key(entry['Date']):
                    frequencies[entry['Date']] = 0
    return frequencies

def write_csv(dictionary,csv_fp):
    '''Writes a dictionary to a csv file with key/values in different columns.'''
    writer = csv.writer(open(csv_fp, 'wb'))
    for key, value in dictionary.items():
        writer.writerow([key, value])

json_data = read_json('dataset.json')
frequencies = term_search('Obama',json_data)
write_csv(frequencies,'rep_frequencies.csv')
