import email.message, email.parser, email, json, re, email.utils
from os import listdir
from time import strftime
from urllib2 import Request, urlopen

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
                self.date = strftime('%d %B %Y',email.utils.parsedate(item[1]))
            if item[0] == 'Subject':
                if item[1].startswith("=?utf-8?") or item[1].startswith("=?UTF-8?"):
                    self.subject, encoding2 = email.Header.decode_header(item[1])[0]
                    self.subject = remove_non_ascii(self.subject)
                    # ^^^ breaks program when encounters subject encoded with "iso-8859"
                else:
                    self.subject = item[1]
                    #self.subject = remove_non_ascii(self.subject)
   
    def get_info(self):
        '''Gets the party and state of the person who sent the email.'''
        for member in self.congress:
            if member['person']['lastname'] in self.name:
                if member['person']['firstname'] in self.name:
                #if the last name and first name/nick name are in self.name: get self.party
                    self.party = member['party']
                    self.state = member['state']
                    return
                elif member['person']['nickname']:
                    if member['person']['nickname'] in self.name:
                        self.party = member['party']
                        self.state = member['state']
                        return
        #If the first loop didn't classify the email, search instead for just the first two letters
        #of the first name, along with the full last name.
        for member in self.congress:
            if member['person']['lastname'] in self.name:
                if member['person']['firstname'][:2] in self.name:
                    self.party = member['party']
                    self.state = member['state']
                    return
        #If neither loop got the information, look just for the last name.
        for member in self.congress:
            if member['person']['lastname'] in self.name:
                self.party = member['party']
                self.state = member['state']
                return
        self.party = 'N/A'
        self.state = 'N/A'
                    
    def construct_dict(self):
        '''Constructs a dictionary of email information.'''
        self.get_header()
        self.get_body()
        if self.valid == False:
            return False
        self.get_info()
        email_dict = {'Subject' : self.subject,
                      'Name' : self.name,
                      'Address' : self.address,
                      'Date' : self.date,
                      'Body' : self.body,
                      'Party' : self.party,
                      'State' : self.state}
        return email_dict

class Directory(Email):
    def __init__(self,directory):
        '''Initializes an instance of the Directory class.'''
        self.directory = directory
        self.congress = api_call()
        
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
        for email in self.dir_list():
            self.path = self.directory + '/' + email
            eml_dict = self.construct_dict()
            if eml_dict:
                eml_list.append(eml_dict)
        return eml_list
        
    def convert_json(self, json_path):
        '''Creates a json file of email information at the specified path.'''
        with open(json_path,'w') as json_file:
            json.dump(self.dir_dict(),json_file)
        
def remove_junk(string):
    '''Removes whitespace characters, escapes, and links from a string.'''
    string = re.sub(r'\s+', ' ', string)
    string = re.sub(r"[\x80-\xff]", '', string)
    link_regex=["<http.*?>","http.*? ","http.*?[^\s]\.gov","http.*?[^\s]\.com","http.*?[^\s]\.COM",
                "www.*?[^\s]\.com","www.*?[^\s]\.org","www.*?[^\s]\.net","www.*?[^\s]\.gov","/.*?[^\s]\.com",
                "/.*?[^\s]\.COM","/.*?[^\s]\.gov",",.*?[^\s]\.gov",",.*?[^\s]\.com",
                "<.*?>"]
    for curr in link_regex:
        string = re.sub(curr,'',string)
    return string

def remove_non_ascii(text):
    '''Removes any non-ascii characters from a string.'''
    return ''.join(i for i in text if ord(i)<128)

def api_call():
    '''Makes an api call and returns a JSOn object of information on the current US congress.'''
    request = Request('https://www.govtrack.us/api/v2/role?current=true&limit=600')
    return json.load(urlopen(request))['objects']

def main():
    '''Guides the user through the program.'''
    directory = raw_input('Please enter the path to the directory of .eml files: ')
    d = Directory(directory)
    json_fp = raw_input('Please enter the location of the json file you would like to create: ')
    d.convert_json(json_fp)

 
if __name__ == '__main__':
    main()


