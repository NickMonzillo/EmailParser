import email.message, email.parser, email, json
from HTMLParser import HTMLParser
from os import listdir


class MLStripper(HTMLParser):
    def __init__(self):
        # initialize the base class
        HTMLParser.__init__(self)

    def read(self, data):
        # clear the current output before re-use
        self._lines = []
        # re-set the parser's state before re-use
        self.reset()
        self.feed(data)
        return ''.join(self._lines)

    def handle_data(self, d):
        self._lines.append(d)

def strip_tags(html):
    s = MLStripper()
    return s.read(html)

#TODO: create a function that removes the \n and \x** from strings
'''
def remove_junk(string):
    for char in string:'''
        
def get_body(email_path):
    '''Returns the body of an email'''
    fp = open(email_path)   
    msg = email.message_from_file(fp)
    if msg.is_multipart():
        for payload in msg.get_payload():
        # if payload.is_multipart()
            if type(payload.get_payload(decode=True)) == str:
                return unicode(payload.get_payload(decode=True),errors = 'ignore').lstrip()
    else:
        return strip_tags(msg.get_payload(decode=True)).replace('\n','')

def construct_dict(email_path):
    '''Constructs a dictionary of email information.
    Takes in a file path for a .eml file'''
    include = ('From','Date','Subject')
    fp = open(email_path)
    msg = email.message_from_file(fp)
    email_dict = {}
    for item in msg.items():
        if item[0] in include:
            email_dict[item[0]] = item[1]
    #email_dict['Body'] = get_body(email_path)
    return email_dict

def dir_list(directory):
    '''Returns the list of all files in the directory.'''
    try:
        content = listdir(directory)
        return content
    except WindowsError as winErr:
        print("Directory error: " + str((winErr)))
        
def dir_dict(directory):
    '''Constructs a dictionary of email dictionaries
    from a directory of .eml files.'''
    eml_list = []
    for email in dir_list(directory):
        eml_list.append(construct_dict(directory + '/' + email))
    return eml_list
        
def convert_json(email_list):
    with open('test.json','w') as json_path:
        json.dump(email_list,json_path)
