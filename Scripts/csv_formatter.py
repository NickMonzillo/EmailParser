import time, string, json, csv, random
from urllib2 import Request, urlopen


def read_json(json_fp):
    '''Reads a json and returns the enclosed data.'''
    with open (json_fp,'r') as json_file:
        data = json.load(json_file)
        return data

def convert_time(time_str):
    ''' Converts a time string from month/day/Year -> daymonthYear'''
    time_obj = time.strptime(time_str,'%m/%d/%Y')
    return time.strftime('%d%m%Y',time_obj)

def remove_space(string):
    '''Removes the spaces froma string.'''
    return string.replace(" ", "")

def read_file(filename):
    '''Reads the contents of a file.'''
    with open(filename,'r') as f:
        content = f.read().split('\n')
    return content

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

def frequencies(words):
    '''Generates a frequency dictionary. Pass separate(text) as an argument.'''
    freq_dict = {}
    for word in words:
        if not freq_dict.has_key(word):
            freq_dict[word] = 1
        else:
            freq_dict[word] += 1
    return freq_dict

def docID(entry,duplicate=False):
    '''Returns the docID associated with an individual email.'''
    if not duplicate:
        return entry['bioguideid'] + convert_time(entry['Date'])
    else:
        return entry['bioguideid'] + convert_time(entry['Date']) + '_' + str(duplicate)

def api_call():
    '''Makes an api call and returns a JSOn object of information on the current US congress.'''
    request = Request('https://www.govtrack.us/api/v2/role?current=true&limit=600')
    return json.load(urlopen(request))['objects']

def get_state_info(fp='state_table.json'):
    '''Gets information about US states from a file.'''
    info = read_json(fp)
    abbreviations,states = [],[]
    for state in info:
        abbreviations.append(state['abbreviation'])
        states.append(state['name'])
    return (abbreviations,states)

def get_names():
    '''Returns the first and last names of all congressmen.
    Format is ([firstnames],[lastnames]).'''
    info = api_call()
    firstnames,lastnames = [],[]
    for congressman in info:
        if congressman['person']['firstname'] not in firstnames:
            firstnames.append(congressman['person']['firstname'])
        if congressman['person']['lastname'] not in lastnames:
            lastnames.append(congressman['person']['lastname'])
    return (lastnames,firstnames)

def form_stopwords(stopwords_fp='stopwords.txt'):
    '''Creates a list of stopwords.'''
    stopwords = []
    #Remove all names of congressmen
    for cong_list in get_names():
        stopwords.extend(cong_list)
    #Remove all states and their abbreviations
    for state_list in get_state_info():
        stopwords.extend(state_list)
    #Remove all designated stopwords
    stopwords.extend(read_file(stopwords_fp))
    return stopwords

def remove_non_ascii(text):
    '''Removes any non-ascii characters from a string.'''
    return ''.join(i for i in text if ord(i)<128)

def metadata(entry,words,doc):
    '''Creates the metadata entry for an individual email.
    doc = docID(entry)'''
    return [doc,entry['party'],entry['Year'],'fic',len(words),remove_non_ascii(entry['Subject'])]

def rid_uncommon_words(word_dict,min_occur=100):
    '''Gets rid of dictionary elements with key < min_occur.'''
    for word in word_dict.keys():
        if word_dict[word] < min_occur:
            del word_dict[word]

def append_words(word_dict,words):
    '''Appends a list of words to a dictionary, dict[word] = frequency.'''
    for word in words:
        if not word_dict.has_key(word):
            word_dict[word] = 1
        else:
            word_dict[word] += 1

def format_lists(parsed_json):
    '''Creates the lists that can be written as csvs.'''
    metadata_list = []
    sparse_list = []
    overflow_list = []
    docs = []
    total_dict = {}
    loop_count = 0
    for email in parsed_json:
        doc = docID(email)
        counter = 1
        while doc in docs:
            doc = docID(email,counter)
            counter += 1
        docs.append(doc)
        words = separate(email['Body'],STOPWORDS)
        if words:
            metadata_list.append(metadata(email,words,doc))
            freq_dict = frequencies(words)
            append_words(total_dict,words)
            for word in freq_dict:
                term_list = [doc,word,freq_dict[word]]
                try:
                    sparse_list.append(term_list)
                except:
                    overflow_list.append(term_list)
        loop_count += 1
        if loop_count%100==0:
            print loop_count
    print 'Done with list creation!'
    #Get rid of all words that occur < min_ooccur(default 100) times in the dataset
    rid_uncommon_words(total_dict,25)
    print 'total_dict '+ str(len(total_dict.keys()))
    print 'Done with ridding words'
    print total_dict.keys()
    print sparse_list[:200]
    sparse_list = [x for x in sparse_list if x[1] in total_dict.keys()]
    print 'sparse list: ' +str(len(sparse_list))
    print 'On overflow removal'
    overflow_list = [x for x in overflow_list if x[1] in total_dict.keys()]
    
    return (metadata_list,sparse_list,overflow_list)

def write_csv(data,csv_fp,overflow=False):
    '''Writes a list to a csv file.'''
    with open(csv_fp,'w') as out:
        csv_out=csv.writer(out,lineterminator='\n')
        for row in data:
            csv_out.writerow(row)
        if overflow:
            for row in overflow:
                csv_out.writerow(row)
                
STOPWORDS = form_stopwords()
emails = random.sample(read_json('analysis_dataset.json'),10000)
print len(emails)
lists = format_lists(emails)
print 'On csv writing!'
write_csv(lists[0],'metadata_10k.csv')
print 'list 1: ' + str(len(lists[1]))
print 'list 2: ' + str(len(lists[2]))
write_csv(lists[1],'sparse_10k.csv',lists[2])

