extractor = dict(
    use_extractor = False, #Set to False if you want to use entire email body
    keyword = 'obama', #set to the keyword that you want to extract text around
    str_length = 50 #sets the amount of words before and after the keyword that you want to extract
)

classifier = dict(
    use_classifier = True, #True if you want to classify emails in email_parser.py
    classifier_fp = 'Classifiers/NB_classifier.pickle' #Define the path to the Naive Bayes classifier, must have .pickle extension
)
stopwords_fp = 'stopwords.txt' #Define the path to the file containing stopwords
