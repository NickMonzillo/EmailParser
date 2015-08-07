import json,csv

class Analyzer(object):
    def __init__(self,json_fp):
        '''Initializes an instance of the Analyzer class.'''
        self.emails = read_json(json_fp)
        #self.data = [x for x in self.emails if x['polarity'] != None] 
        self.align_raw,self.bash_raw,self.total_counts = self.raw_count_dicts()
        self.align_pct = divide_dictionaries(self.total_counts,self.align_raw)
        self.bash_pct = divide_dictionaries(self.total_counts,self.bash_raw)

    def raw_count_dicts(self):
        '''Returns a list of dictionaries (align_dict,bash_dict)
        bash_dict[sender] = # of bash emails sent
        align_dict[sender] = # of align emails sent
        total_dict[sender] = total # of emails sent'''
        align_dict = {}
        bash_dict = {}
        total_dict = {}
        for email in self.emails:
            name = email['firstname'] + ' ' + email['lastname']
            if not total_dict.has_key(name):
                total_dict[name] = 0
            total_dict[name] += 1
            if not align_dict.has_key(name):
                align_dict[name] = 0
            if not bash_dict.has_key(name):
                    bash_dict[name] = 0
            if email['alignment'] == 'Align':
                align_dict[name] += 1
            elif email['alignment'] == 'Bash':
                bash_dict[name] += 1
        return (align_dict,bash_dict,total_dict)
        

    def generate_csv(self):
        '''Returns the list of tuples that will be written to a csv.'''
        return_list = [('Sender','Total','align_raw','align_pct','bash_raw','bash_pct')]
        for sender in self.total_counts.keys():
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
            try:
                csv_out.writerow(row)
            except:
                continue

a = Analyzer('pol_test.json')
csv_list = a.generate_csv()
print len(a.total_counts.keys())
#write_csv(csv_list,'alignment.csv')
