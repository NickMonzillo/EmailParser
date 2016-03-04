import nltk, csv, json, pickle, settings
from random import shuffle

def stopwords(stopwords_fp=settings.stopwords_fp):
    '''Returns a list of stopwords from the given stopwords file.'''
    with open(stopwords_fp) as f:
        content = f.readlines()
    lines = [line.rstrip() for line in content]
    return lines

def get_training_data(csv_fp,train_ratio=0.7):
    '''Gets the training set of data from the csv file.
    train_ratio defines the % of the dataset used to train the classifier.'''
    with open(csv_fp,'rb') as f:
        reader = csv.reader(f)
        dataset = list(reader)
    shuffle(dataset)
    dataset = [data for data in dataset if data[1] != '0']
    num_train = int(round(train_ratio*len(dataset),0))
    train_set,test_set = dataset[:num_train],dataset[num_train:]
    if settings.extractor['use_extractor']:
        train_set = [(wordlist(word_extractor(data[0])),data[1]) for data in train_set]
        test_set = [(wordlist(word_extractor(data[0])),data[1]) for data in test_set]
    else:
        train_set = [(wordlist(data[0]),data[1]) for data in train_set]
        test_set = [(wordlist(data[0]),data[1]) for data in test_set]
    return train_set,test_set

def word_extractor(text, keyword=settings.extractor['keyword'], n=settings.extractor['str_length']):
    '''Extracts n words before and after the keyword in a given text.'''
    text = text.lower()
    separated = text.partition(keyword)
    if separated[2]:
        neg = -1*n
        before,after = separated[0].split()[neg:],separated[2].split()[:n]
        before.extend(after)
        return ' '.join(before)
    else:
        return text

def write_csv(data,csv_fp):
    '''Writes a list of lists to a csv file with each list as a row.'''
    with open(csv_fp,'w') as out:
        csv_out=csv.writer(out,lineterminator='\n')
        for row in data:
            csv_out.writerow(row)

def convert_assignments(assignment_fp,csv_fp='NB_trainer.csv'):
    '''Converts a json of email assignments to a csv
    that can be processed by the classifier.'''
    with open(assignment_fp,'r') as fp:
        content = json.load(fp)
    useful_content = [(item['Body'],item['assignment']) for item in content]
    write_csv(useful_content,csv_fp)
    
def separate(text):
    '''Takes text and separates it into a list of words'''
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    stop_list = stopwords()
    words = text.split()
    standardwords = []
    for word in words:
        if word not in stop_list:
            newstr = ''
            for char in word:
                if char.lower() in alphabet:
                   newstr += char
            if newstr != '':
                standardwords.append(newstr)
    return map(lambda x: x.lower(),standardwords)

def wordcount(text):
    '''Returns the count of the words in a file.'''    
    wordcount = {}
    separated = separate(text)
    for word in separated:
        if not wordcount.has_key(word):
            wordcount[word] = 1
        else:
            wordcount[word] += 1
    return wordcount

def wordlist(text):
    '''Returns a list of words in the text.'''
    words = {}
    separated = separate(text)
    for word in separated:
        if word not in words.keys():
            words[word] = 1
    return words

def get_test_csv(csv_fp='classified_comments.csv'):
    with open(csv_fp,'rb') as f:
        reader = csv.reader(f)
        dataset = list(reader)
    print len(dataset)
    print type(dataset[1][0])
    #filtered = [(wordcount(data[0]),data[1]) for data in dataset if data[2] != 'n']
    return dataset

def save_classifier(classifier, file_path='NB_classifier.pickle'):
    '''Saves the classifier as a pickle file.'''
    f = open(file_path,'wb')
    pickle.dump(classifier,f)
    f.close()

def create_classifier(train_data='NB_trainer.csv',save_to_fp='NB_classifier.pickle'):
    '''Creates a Naive-Bayes classifier from the given training data
    and saves it as a pickle file to save_to_fp.'''
    train_set,test_set = get_training_data(train_data,1.0)
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    #print nltk.classify.accuracy(classifier,test_set)
    #classifier.show_most_informative_features()
    save_classifier(classifier,save_to_fp)

def main():
    train_fp = raw_input('Enter the path to the training data: ')
    #save_fp = raw_input('Enter the path where you want to save the classifier (must have .pickle extension): ')
    save_fp = settings.classifier['classifier_fp']
    create_classifier(train_fp,save_fp)

if __name__ == '__main__':
    main()
