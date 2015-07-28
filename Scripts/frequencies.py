import json, csv

def read_json(json_fp):
    '''Reads a json and returns the enclosed data.'''
    with open (json_fp,'r') as json_file:
        data = json.load(json_file)
        return data
    
def increment_key(dictionary,key):
    '''If the dictionary has the key, increment the value,
    otherwise initialize the key with value 1.'''
    if dictionary.has_key(key):
        dictionary[key] += 1
    else:
        dictionary[key] = 1
    
def term_search(term,search_dict):
    '''Returns a dictionary of frequencies for the search term on any given date.'''
    frequencies = {'id':'total'}
    dem_frequencies = {'id':'Democrat'}
    rep_frequencies = {'id':'Republican'}
    dictionaries = (frequencies,dem_frequencies,rep_frequencies)
    for entry in search_dict:
        if term in entry['Body']:
            for dictionary in dictionaries:
                if dictionary['id'] == entry['party'] or dictionary['id'] == 'total':
                    increment_key(dictionary,entry['Date'])
        else:
            for dictionary in dictionaries:
                if not dictionary.has_key(entry['Date']):
                    dictionary[entry['Date']] = 0
    return dictionaries

def form_lists(dictionaries):
    '''Forms the lists that will be written as csvs.'''
    return_list = [['Date','Total','Democrat','Republican']]
    total,democrat,republican = dictionaries
    for date in total:
        if date == 'id':
            continue
        dem_valid = True if democrat.has_key(date) else False
        rep_valid = True if republican.has_key(date) else False
        if not dem_valid:
            democrat[date] = 0
        if not rep_valid:
            republican[date] = 0
        append_list = [date,total[date],democrat[date],republican[date]]
        return_list.append(append_list)
    return return_list

def write_csv(data,csv_fp):
    '''Writes a list of lists to a csv file with each list as a row.'''
    with open(csv_fp,'w') as out:
        csv_out=csv.writer(out,lineterminator='\n')
        for row in data:
            csv_out.writerow(row)

json_data = read_json('analysis_dataset.json')
freq_dicts = term_search('Obama',json_data)
lists = form_lists(freq_dicts)
write_csv(lists,'frequencies.csv')

