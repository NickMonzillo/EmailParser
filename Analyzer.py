import json,csv

class Analyzer(object):
    def __init__(self,json_fp):
        '''Initializes an instance of the Analyzer class.'''
        self.emails = read_json(json_fp)
        self.data = [x for x in self.emails if x['polarity'] != None] 
        self.total_counts = self.get_total_counts()
        self.align_raw,self.bash_raw = self.raw_count_dicts()
        self.align_pct = divide_dictionaries(self.total_counts,self.align_raw)
        self.bash_pct = divide_dictionaries(self.total_counts,self.bash_raw)

    def raw_count_dicts(self):
        '''Returns a list of dictionaries (align_dict,bash_dict)
        bash_dict[sender] = # of bash emails sent
        align_dict[sender] = # of align emails sent'''
        align_dict = {}
        bash_dict = {}
        for email in self.data:
            name = email['firstname'] + ' ' + email['lastname']
            if not align_dict.has_key(name):
                align_dict[name] = 0
            if not bash_dict.has_key(name):
                    bash_dict[name] = 0
            if email['alignment'] == 'Align':
                align_dict[name] += 1
            elif email['alignment'] == 'Bash':
                bash_dict[name] += 1
        return (align_dict,bash_dict)
        
    def get_total_counts(self):
        '''Returns a dictionary in the format total_counts['sender'] = frequency
        where frequency is the total number of emails sent by the sender.
        This is used to find out the alignment percentages.'''
        total_counts = {}
        for email in self.emails:
            name = email['firstname'] + ' ' + email['lastname']
            if not total_counts.has_key(name):
                total_counts[name] = 0
            total_counts[name] += 1
        return total_counts

    def generate_csv(self):
        '''Returns the list of tuples that will be written to a csv.'''
        senders = list(set(self.align_raw.keys()) | set(self.bash_raw.keys()))
        #senders contains the names of all senders in self.data
        return_list = [('Sender','Total','align_raw','align_pct','bash_raw','bash_pct')]
        for sender in senders:
            entry = (sender,self.total_counts[sender],self.align_raw[sender],self.align_pct[sender],self.bash_raw[sender],self.bash_pct[sender])
            return_list.append(entry)
        return return_list
    
def divide_dictionaries(divisor,dividend,digits=4):
    '''Divides the dividend[key] by the divisor[key].
    Returns the resulting quotient dictionary.'''
    quotient = {k: round(float(dividend[k])/divisor[k],digits) for k in divisor.viewkeys() & dividend.viewkeys()}
    return quotient

def read_json(json_fp):
    '''Reads a json and returns the enclosed data.'''
    with open (json_fp,'r') as json_file:
        data = json.load(json_file)
        return data
    
def write_csv(data,csv_fp):
    '''Writes a list to a csv file.'''
    with open(csv_fp,'w') as out:
        csv_out=csv.writer(out,lineterminator='\n')
        for row in data:
            csv_out.writerow(row)

a = Analyzer('analysis_dataset.json')
csv_list = a.generate_csv()
write_csv(csv_list,'alignment.csv')
