import email.message, email.parser, email, json, re, email.utils
from os import listdir
from time import strftime


def remove_junk(string):
    '''Removes whitespace characters, escapes, and links from a string.'''
    string = re.sub(r'\s+', ' ', string)
    string = re.sub(r"[\x80-\xff]", '', string)
    #link_regex = "(([\w]+:)?//)?(([\d\w]|%[a-fA-f\d]{2,2})+(:([\d\w]|%[a-fA-f\d]{2,2})+)?@)?([\d\w][-\d\w]{0,253}[\d\w]\.)+[\w]{2,4}(:[\d]+)?(/([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)*(\?(&?([-+_~.\d\w]|%[a-fA-f\d]{2,2})=?)*)?(#([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)?"
    #string = re.sub(link_regex,'',string)
    return string

def get_body(email_path):
    '''Returns the body of an email, removing any whitespace characters and escapes.'''
    fp = open(email_path)   
    msg = email.message_from_file(fp)
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                return remove_junk(str(part.get_payload(decode=True)))    
    else:
        return remove_junk(str(msg.get_payload(decode=True)))

def construct_dict(email_path):
    '''Constructs a dictionary of email information.
    Takes in a file path for a .eml file'''
    include = ('From','Date','Subject')
    fp = open(email_path)
    msg = email.message_from_file(fp)
    email_dict = {}
    for item in msg.items():
        if item[0] == 'From':
            address = email.utils.parseaddr(item[1])
            email_dict['Name'] = address[0]
            email_dict['Address'] = address[1]
        if item[0] == 'Date':
            email_dict['Date'] = strftime('%d %B %Y',email.utils.parsedate(item[1]))
        if item[0] == 'Subject':
            email_dict['Subject'] = item[1]
    email_dict['Body'] = get_body(email_path)
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
        
def convert_json(directory):
    with open('test.json','w') as json_path:
        json.dump(dir_dict(directory),json_path)
