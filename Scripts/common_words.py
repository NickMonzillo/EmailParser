import string, json, csv

def separate(text):
    '''Takes text and separates it into a list of words'''
    words = text.split()
    standardwords = []
    for word in words:
        newstr = ''
        for char in word:
            if char in string.ascii_letters:
               newstr += char.lower()
        if newstr != '' and newstr not in STOPWORDS:
            standardwords.append(newstr)
    return standardwords

def read_file(filename):
    '''Reads the contents of a file.'''
    with open(filename,'r') as f:
        content = f.read()
    return content

def read_json(json_fp):
    '''Reads a json and returns the enclosed data.'''
    with open (json_fp,'r') as json_file:
        data = json.load(json_file)
        return data

def monthly_counts(json_fp,search_term):
    '''Returns a dictionary of wordcounts by month
    from emails containg the search_term.
    The format is freq_dict[(Month,Year)] = {word:frequency}.'''
    freq_dict = {}
    for email in read_json(json_fp):
        if search_term in email['Body']:
            month = (email['Month'],email['Year'])
            if not freq_dict.has_key(month):
                    freq_dict[month] = {}
            for word in separate(email['Body']):
                if not freq_dict[month].has_key(word):
                    freq_dict[month][word] = 1
                else:
                    freq_dict[month][word] += 1
    return freq_dict

def sort_counts(freq_dict,word_count):
    '''Sorts the frequency dictionary returned by monthly_counts().
    Returns a dictionary of lists in the format:
    sort_dict[('Month','Year')] = [(word1,freq),(word2,freq),...]
    This list will be sorted based on the frequencies.'''
    sort_dict = {}
    for month in freq_dict:
        if not sort_dict.has_key(month):
            sort_dict[month] = []
        for word in freq_dict[month]:
            sort_dict[month].append((word,freq_dict[month][word]))
        sort_dict[month].sort(key=lambda x: x[1],reverse=True)
        sort_dict[month] = sort_dict[month][:word_count]
    return sort_dict

def tupleize(sorted_dict):
    '''Forms a list of 4-tuples from the sort_counts() dictionary.
    Use this function to make it easier to write the dict to a csv.'''
    csv_list = [('Year','Month','Word','Frequency')]
    for month in sorted_dict:
        for word in sorted_dict[month]:
            csv_list.append((month[1],month[0],word[0],word[1]))
    return csv_list
                
def write_csv(data,csv_fp):
    '''Writes a list to a csv file.'''
    with open(csv_fp,'w') as out:
        csv_out=csv.writer(out,lineterminator='\n')
        for row in data:
            csv_out.writerow(row)
            
STOPWORDS = read_file('stopwords.txt')
counts = monthly_counts('analysis_dataset.json','Obama')
sorted_counts = sort_counts(counts,10)
write_csv(tupleize(sorted_counts),'common_words.csv')
