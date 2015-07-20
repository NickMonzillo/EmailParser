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

def add_to_dict(dictionary,word_list,month):
    if not dictionary.has_key(month):
        dictionary[month] = {}
    for word in word_list:
        if not dictionary[month].has_key(word):
            dictionary[month][word] = 1
        else:
            dictionary[month][word] += 1
    
def monthly_counts(json_fp,search_term):
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
    for email in read_json(json_fp):
        if search_term in email['Body']:
            month = (email['Month'],email['Year'])
            words = separate(email['Body'])
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
        #sort_dict[month] = sort_dict[month][:word_count]
        else:
            sort_dict['id'] = freq_dict['id']
    return sort_dict

def multiple_sort(list_of_dicts,word_count):
    '''Sorts a list of multiple frequency dictionaries.'''
    return_list = []
    for dictionary in list_of_dicts:
        dictionary = sort_counts(dictionary,word_count)
        return_list.append(dictionary)
    return (return_list,word_count)

def get_top_x(list_of_dicts):
    '''Returns the top x words and their frequencies by month.
    Pass the results of multiple_sort() as the argument.'''
    top_dict = {}
    word_count = list_of_dicts[1]
    for dictionary in list_of_dicts[0]:
        for month in dictionary:
            if not top_dict.has_key(month):
                top_dict[month] = []
            for word_tuple in dictionary[month[:word_count]]: #Only take the top word_count words from each dict.
                if word_tuple[0] not in top_dict[month]:
                    top_dict[month].append(word_tuple[0])
    return top_dict
                

def tupleize(sorted_dicts):
    '''Forms a list of 10-tuples from the multiple_sort() dictionary.
    Use this function to make it easier to write the dict to a csv.'''
    csv_list = [('Year','Month','Word','Total','Republican','Democrat','Male','Female','House','Senate')]
    word_list = get_top_x(sorted_dicts)
    for month in word_list:
        for word in word_list[month]:
            for dictionary in sorted_dicts[0]:
                if dictionary.has_key(month):
                    if word not in [x[1] for x in dictionary[month]]:
                        dictionary[month].append((word,0))
                    for dict_word in dictionary[month]:
                        if dict_word[0] == word:
                            if dictionary['id'] == 'total':
                                total_freq = dict_word[1]
                            if dictionary['id'] == 'republican':
                                republican_freq = dict_word[1]
                            if dictionary['id'] == 'democrat':
                                democrat_freq = dict_word[1]
                            if dictionary['id'] == 'male':
                                male_freq = dict_word[1]
                            if dictionary['id'] == 'female':
                                female_freq = dict_word[1]
                            if dictionary['id'] == 'senate':
                                senate_freq = dict_word[1]
                            if dictionary['id'] == 'house':
                                house_freq = dict_word[1]
                        break
        csv_list.append((month[1],month[0],word[0],total_freq,republican_freq,democrat_freq,male_freq,female_freq,house_freq,senate_freq))
    return csv_list
                
def write_csv(data,csv_fp):
    '''Writes a list to a csv file.'''
    with open(csv_fp,'w') as out:
        csv_out=csv.writer(out,lineterminator='\n')
        for row in data:
            csv_out.writerow(row)
            
STOPWORDS = read_file('stopwords.txt')
counts = monthly_counts('small_dataset.json','Obama')
sorted_counts = multiple_sort(counts,10)
write_csv(tupleize(sorted_counts),'common_words.csv')
