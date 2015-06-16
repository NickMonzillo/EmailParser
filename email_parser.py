import email.message, email.parser, email, json, re, email.utils
from os import listdir
from time import strftime

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
                    return
        else:
            self.body = remove_junk(str(msg.get_payload(decode=True)))
        
    def get_header(self):
        '''Gets header information from the email and stores it as attributes.'''
        fp = open(self.path)
        msg = email.message_from_file(fp)
        for item in msg.items():
            if item[0] == 'From':
                parsed_address = email.utils.parseaddr(item[1])
                self.name, encoding = email.Header.decode_header(parsed_address[0])[0]
                self.address = parsed_address[1]
            if item[0] == 'Date':
                self.date = strftime('%d %B %Y',email.utils.parsedate(item[1]))
            if item[0] == 'Subject':
                if item[1].startswith("=?utf-8?"):
                    self.subject, encoding2 = email.Header.decode_header(item[1])[0]
                    # ^^^ breaks program when encounters subject encoded with "iso-8859"
                elif item[1].startswith("=?UTF-8?"):
                    self.subject, encoding2 = email.Header.decode_header(item[1])[0]
                    # ^^^ breaks program when encounters subject encoded with "iso-8859"
                else:
                    parts = email.Header.decode_header(item[1])
                    parts2 = email.Header.make_header(parts)
                    self.subject = unicode(parts2)
                
    def construct_dict(self):
        '''Constructs a dictionary of email information.
        Takes in a file path for a .eml file'''
        self.get_header()
        self.get_body()
        email_dict = {'Subject' : self.subject,
                      'Name' : self.name,
                      'Address' : self.address,
                      'Date' : self.date,
                      'Body' : self.body}
        return email_dict

class Directory(Email):
    def __init__(self,directory):
        '''Initializes an instance of the Directory class.'''
        self.directory = directory
        
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
            eml_list.append(self.construct_dict())
        return eml_list
        
    def convert_json(self, json_path):
        '''Creates a json file of email information at the specified path.'''
        with open(json_path,'w') as json_file:
            json.dump(self.dir_dict(),json_file)
        
def remove_junk(string):
    '''Removes whitespace characters, escapes, and links from a string.'''
    string = re.sub(r'\s+', ' ', string)
    string = re.sub(r"[\x80-\xff]", '', string)
    #link_regex = "(([\w]+:)?//)?(([\d\w]|%[a-fA-f\d]{2,2})+(:([\d\w]|%[a-fA-f\d]{2,2})+)?@)?([\d\w][-\d\w]{0,253}[\d\w]\.)+[\w]{2,4}(:[\d]+)?(/([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)*(\?(&?([-+_~.\d\w]|%[a-fA-f\d]{2,2})=?)*)?(#([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)?"
    #string = re.sub(link_regex,'',string)
    return string

def main():
    '''Guides the user through the program.'''
    directory = raw_input('Please enter the path to the directory of .eml files: ')
    d = Directory(directory)
    json_fp = raw_input('Please enter the location of the json file you would like to create.')
    d.convert_json(json_fp)

if __name__ == '__main__':
    main()
