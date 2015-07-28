import string, json, csv
from itertools import chain

def separate(text,stopwords=''):
    '''Takes text and separates it into a list of words, removes stopwords.'''
    words = text.split()
    standardwords = []
    for word in words:
        newstr = ''
        for char in word:
            if char in string.ascii_letters:
               newstr += char.lower()
        if newstr != '' and newstr not in stopwords:
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
    
def add_to_dict(dictionary,word_list,month):
    if not dictionary.has_key(month):
        dictionary[month] = {}
    for word in word_list:
        if not dictionary[month].has_key(word):
            dictionary[month][word] = 1
        else:
            dictionary[month][word] += 1
            
def monthly_counts(data,search_term):
    '''Returns a dictionary of wordcounts by month
    from emails containing the search_term.
    The format is freq_dict[(Month,Year)] = {word:frequency}.'''
    total = {'id': 'total'}
    republican = {'id': 'republican'}
    democrat = {'id': 'democrat'}
    male = {'id': 'male'}
    female = {'id': 'female'}
    senate = {'id': 'senate'}
    house = {'id': 'house'}
    for email in data:
        if search_term in email['Body']:
            month = (email['Month'],email['Year'])
            words = separate(email['Body'],STOPWORDS)
            add_to_dict(total,words,month)
            if email['party'] == 'Republican':
                add_to_dict(republican,words,month)
            if email['party'] == 'Democrat':
                add_to_dict(democrat,words,month)
            if email['gender'] == 'male':
                add_to_dict(male,words,month)
            if email['gender'] == 'female':
                add_to_dict(female,words,month)
            if email['title_long'] == 'Representative':
                add_to_dict(house,words,month)
            if email['title_long'] == 'Senator':
                add_to_dict(senate,words,month)
    return (total,republican,democrat,male,female,senate,house)

def sort_counts(freq_dict,word_count):
    '''Sorts the frequency dictionary returned by monthly_counts().
    Returns a dictionary of lists in the format:
    sort_dict[('Month','Year')] = [(word1,freq),(word2,freq),...]
    This list will be sorted based on the frequencies.'''
    sort_dict = {}
    for month in freq_dict:
        if month != 'id':
            if not sort_dict.has_key(month):
                sort_dict[month] = []
            for word in freq_dict[month]:
                sort_dict[month].append((word,freq_dict[month][word]))
            sort_dict[month].sort(key=lambda x: x[1],reverse=True)
            sort_dict[month] = sort_dict[month][:word_count]
        else:
            sort_dict['id'] = freq_dict['id']
    return sort_dict

def multiple_sort(list_of_dicts,word_count):
    '''Sorts a list of multiple frequency dictionaries.'''
    return_list = []
    for dictionary in list_of_dicts:
        dictionary = sort_counts(dictionary,word_count)
        return_list.append(dictionary)
    return return_list

def format_csv(sorted_dicts):
    total,republican,democrat,male,female,senate,house = sorted_dicts
    header = ['Year','Month','Total_word','Total_freq','Republican_word','Republican_freq','Democrat_word','Democrat_freq','Male_word','Male_freq','Female_word','Female_freq','Senate_word','Senate_freq','House_word','House_freq']
    return_list = [header]
    for month in total:
        if month != 'id':
            prepend = [month[1],month[0]]
            monthly_words = zip(total[month],republican[month],democrat[month],male[month],female[month],senate[month],house[month])
            for i in range(len(monthly_words)):
                monthly_words[i] = prepend + list(chain.from_iterable(monthly_words[i]))
                return_list.append(monthly_words[i])
    return return_list

def write_csv(data,csv_fp):
    '''Writes a list to a csv file.'''
    with open(csv_fp,'w') as out:
        csv_out=csv.writer(out,lineterminator='\n')
        for row in data:
            csv_out.writerow(row)

STOPWORDS = read_file('stopwords.txt')
data = read_json('analysis_dataset.json')
counts = monthly_counts(data,'Obama')
sorted_counts = multiple_sort(counts,10)
write_csv(format_csv(sorted_counts),'common_words_test.csv')

