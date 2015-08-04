import json
from statistics import stdev,mean

class Alignment(object):
    def __init__(self,json_fp):
        self.emails = read_json(json_fp)
        self.raw_polarities = [x['polarity'] for x in self.emails if x['polarity'] != None]
        self.align_threshold,self.bash_threshold = self.establish_thresholds()
        
    def establish_thresholds(self):
        '''Establishes the thresholds for align and bash.'''
        avg_pol = mean(self.raw_polarities)
        std_dev = stdev(self.raw_polarities)
        align = avg_pol + (0.5*std_dev)
        bash = avg_pol - (0.5*std_dev)
        return (align,bash)

    def assign_alignment(self):
        '''Creates an alignment field for all emails.
        This uses the thresholds created in establish_thresholds().'''
        for email in self.emails:
            if email['polarity'] == None:
                email['alignment'] = None
            if email['polarity'] >= self.align_threshold:
                email['alignment'] = 'Align'
            if email['polarity'] <= self.bash_threshold:
                email['alignment'] = 'Bash'
            else:
                email['alignment'] = 'Neutral'
                
     def convert_json(self, json_path):
        '''Creates a json file of email information at the specified path.'''
        with open(json_path,'w') as json_file:
            json.dump(self.emails,json_file)
            
def read_json(json_fp):
    '''Reads a json and returns the enclosed data.'''
    with open (json_fp,'r') as json_file:
        data = json.load(json_file)
        return data

a = Alignment('analysis_dataset.json')
a.assign_alignment()
a.convert_json('analysis_dataset.json')
