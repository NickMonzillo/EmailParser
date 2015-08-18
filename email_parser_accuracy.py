import email.message, email.parser, email, json, re, email.utils, csv
from os import listdir
from time import strftime
from urllib2 import Request, urlopen
import sPickle
from word_extractor import word_extractor
from textblob import TextBlob
from statistics import stdev, mean

class Email(object):
    def __init__(self, email_path):
        '''Initializes an instance of the Email class.'''
        self.path = email_path
          
    def get_body(self):
        '''Stores the body of the email as an attribute, removing any whitespace characters and escapes.'''
        fp = open(self.path)   
        msg = email.message_from_file(fp)
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    self.body = remove_junk(str(part.get_payload(decode=True)))
                    if len(self.body) <= 16:
                        self.valid = False
                    return
        else:
            self.body = remove_junk(str(msg.get_payload(decode=True)))
            if len(self.body) <= 16:
                self.valid = False
            return
        
    def get_header(self):
        '''Gets header information from the email and stores it as attributes.'''
        fp = open(self.path)
        msg = email.message_from_file(fp)
        for item in msg.items():
            if item[0] == 'From':
                parsed_address = email.utils.parseaddr(item[1])
                self.name, encoding = email.Header.decode_header(parsed_address[0])[0]
                self.name = remove_non_ascii(self.name)
                self.address = parsed_address[1]
                if "google.com" in self.address or "Google.com" in self.address or "pols.exp@gmail.com" in self.address:
                    self.valid = False
                    return
                else:
                    self.valid = True
            if item[0] == 'Date':
                self.date = strftime('%m/%d/%Y',email.utils.parsedate(item[1]))
                self.month = strftime('%m',email.utils.parsedate(item[1]))
                self.year = strftime('%Y',email.utils.parsedate(item[1]))
            if item[0] == 'Subject':
                if item[1].startswith("=?utf-8?") or item[1].startswith("=?UTF-8?"):
                    self.subject, encoding2 = email.Header.decode_header(item[1])[0]
                    self.subject = remove_non_ascii(self.subject)
                    # ^^^ breaks program when encounters subject encoded with "iso-8859"
                else:
                    self.subject = item[1]
                    #self.subject = remove_non_ascii(self.subject)
   
    def get_info(self):
        '''Returns a dictionary containing the api information of the sender of an email.'''
        for member in self.congress:
            if member['person']['lastname'] in self.name:
                if member['person']['firstname'] in self.name:
                #if the last name and first name/nick name are in self.name: get self.party
                    return pull_api_info(member)
                elif member['person']['nickname']:
                    if member['person']['nickname'] in self.name:
                        return pull_api_info(member)
        #If the first loop didn't classify the email, search instead for just the first two letters
        #of the first name, along with the full last name.
        for member in self.congress:
            if member['person']['lastname'] in self.name:
                if member['person']['firstname'][:2] in self.name:
                    return pull_api_info(member)
        #If neither loop got the information, look just for the last name.
        for member in self.congress:
            if member['person']['lastname'] in self.name:
                return pull_api_info(member)
        
    def construct_dict(self,assignment):
        '''Constructs a dictionary of email information.'''
        self.get_header()
        self.get_body()
        if self.valid == False:
            return False
        try:
            email_dict = self.get_info()
            email_dict['Subject'] = self.subject
            email_dict['Name'] = self.name
            email_dict['Address'] = self.address
            email_dict['Date'] = self.date
            email_dict['Body'] = self.body
            email_dict['Month'] = self.month
            email_dict['Year'] = self.year
            email_dict['polarity'] = self.polarity()
            email_dict['assignment'] = assignment
            return email_dict
        except:
            return None

    def polarity(self,csv_fp='word_values_MWR.csv'):
        '''Assigns a polarity to the email.
        Higher number means that the email praises Obama.
        Lower number means the email bashes Obama.'''
        #text = word_extractor(self.body, 'obama', 75)
        score = 0
        if 'Obama' in self.body:
            text = self.body
            with open(csv_fp,'rb') as csvfile:
                value_list = list(tuple(line) for line in csv.reader(csvfile,delimiter=','))
            if text:
                for word in text.split():
                    word = word.lower()
                    for scored_word,value in value_list:
                        if word == scored_word:
                            score += float(value)
        if not score:
            #print self.body
            #print self.subject
            #print self.name
            #raw_input()
            return 'None'
        #if self.subject == 'Leading the Effort to Secure Half a Billion Dollars for Tennessee Hospitals':
         #   print self.body
        return score
    
class Directory(Email):
    def __init__(self,directory):
        '''Initializes an instance of the Directory class.'''
        self.directory = directory
        self.congress = api_call()
        self.email_json = self.dir_dict()
        
    def dir_list(self):
        '''Returns the list of all files in self.directory'''
        try:
            return listdir(self.directory)
        except WindowsError as winErr:
            print("Directory error: " + str((winErr)))
        
    def dir_dict(self):
        '''Constructs a list of email dictionaries
        from a directory of .eml files.'''
        eml_list = []
        folders = ('manual_data/align_test','manual_data/bash_test')
        assignments = ('Align','Bash')
        assignment_count = 0
        for folder in folders:
            self.directory = folder
            for email in self.dir_list():
                self.path = self.directory + '/' + email
                eml_dict = self.construct_dict(assignments[assignment_count])
                if eml_dict:
                    eml_list.append(eml_dict)
            assignment_count += 1
        return eml_list
        
    def convert_json(self, json_path):
        '''Creates a json file of email information at the specified path.'''
        self.email_json = self.dir_dict()
        with open(json_path,'w') as json_file:
            json.dump(self.email_json,json_file)

class Alignment(object):
    def __init__(self,email_json):
        self.emails = email_json
        self.raw_polarities = [x['polarity'] for x in self.emails if x['polarity'] != 'None']
        self.raw_polarities.sort()
        self.raw_polarities = self.raw_polarities[0:-1]
        multiplier = 0
        #write_file = open('accuracies.txt','w')
        #write_str = ''
        #for i in range(100):
        self.align_threshold,self.bash_threshold = self.establish_thresholds(multiplier)
        self.assign_alignment()
        print accuracy(self.emails)
            #write_str += '(' + str(multiplier) + ' , ' + str(accuracy(self.emails)) + ')\n'
            #multiplier += 0.01
        #write_file.write(write_str)
        #write_file.close()

    def establish_thresholds(self,multiplier):
        '''Establishes the thresholds for align and bash.'''
        avg_pol = mean(self.raw_polarities)
        std_dev = stdev(self.raw_polarities)
        print 'std_dev: ' + str(std_dev)
        align = avg_pol + (multiplier*std_dev)
        bash = avg_pol - (multiplier*std_dev)
        print avg_pol
        return align,bash

    def assign_alignment(self):
        '''Creates an alignment field for all emails.
        This uses the thresholds created in establish_thresholds().'''
        for email in self.emails:
            if email['polarity'] >= self.align_threshold:
                email['alignment'] = 'Align'
            elif email['polarity'] < self.bash_threshold:
                email['alignment'] = 'Bash'
            else:
                email['alignment'] = 'Neutral'
            if email['polarity'] == 'None':
                email['alignment'] = 'None'
                
    def convert_json(self,json_path):
        '''Creates a json file of email information at the specified path.'''
        with open(json_path,'w') as json_file:
            json.dump(self.emails,json_file)

def read_json(json_fp):
    '''Reads a json and returns the enclosed data.'''
    with open(json_fp,'r') as json_file:
        data = json.load(json_file)
        return data

def remove_junk(string):
    '''Removes whitespace characters, escapes, and links from a string.'''
    string = re.sub(r'\s+', ' ', string)
    string = re.sub(r"[\x80-\xff]", '', string)
    #link_regex=["<http.*?>","http.*? ","http.*?[^\s]\.gov","http.*?[^\s]\.com","http.*?[^\s]\.COM",
     #           "www.*?[^\s]\.com","www.*?[^\s]\.org","www.*?[^\s]\.net","www.*?[^\s]\.gov","/.*?[^\s]\.com",
      #          "/.*?[^\s]\.COM","/.*?[^\s]\.gov",",.*?[^\s]\.gov",",.*?[^\s]\.com",
       #         "<.*?>"]
    #for curr in link_regex:
     #   string = re.sub(curr,'',string)
    return string

def remove_non_ascii(text):
    '''Removes any non-ascii characters from a string.'''
    return ''.join(i for i in text if ord(i)<128)

def api_call():
    '''Makes an api call and returns a JSOn object of information on the current US congress.'''
    request = Request('https://www.govtrack.us/api/v2/role?sort=-enddate&limit=2019')
    return json.load(urlopen(request))['objects']

def pull_api_info(entry):
        '''Returns a dictionary of all the info from the API call.'''
        info_dict = {}
        for key in entry:
            if key == 'person':
                for person_key in entry[key]:
                    info_dict[person_key] = entry[key][person_key]
            else:        
                info_dict[key] = entry[key]
        return info_dict

def accuracy(data):
    '''Returns the accuracy of classfication of emails.'''
    total = 0.0
    correct = 0.0
    for email in data:
        if email['polarity'] != 'None': 
            if email['alignment'] == email['assignment']:
                correct += 1
            total += 1
    return correct/total

def main():
    '''Guides the user through the program.'''
    #directory = raw_input('Please enter the path to the directory of .eml files: ')
    d = Directory('directory')
    #json_fp = raw_input('Please enter the location of the json file you would like to create: ')
    json_fp = 'accuracy_test.json'
    #d.convert_json(json_fp)
    a = Alignment(d.email_json)
    a.assign_alignment()
    a.convert_json(json_fp)
if __name__ == '__main__':
    main()

