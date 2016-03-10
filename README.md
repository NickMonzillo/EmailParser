# EmailParser
Stores email header and body information in JSON format.

This program is a tool to convert a directory of .eml files into a json format. The json file will contain all header and body information for each email.

It can also be used to evaluate sentiment within these emails and assign a negative/positive rating.

**Currently this program is being used for a research project that renders it too specific for general use. Once this project is over, I will tune the program for a more general purpose.**

To use this program, simply run the program from a Python interpreter. The prompts in the console will ask you for directory and json file locations. Once provided, it will generate the json in the specified location.

This program is very lightweight, and can deal with directories with large amounts of files.

To activate the sentiment analyzer, edit the settings.py by setting use_classifier to True. Classifiers are created by running NB_classifier.py and inputting training data. Training data should be structured like the NB_trainer.csv file in the CLassifiers folder. This file was used to create the NB_classifier.pickle file in the same folder. This classifier identifies whether an email is positive or negative in regards to Barack Obama.

The extractor settings in settings.py is used to extract keywords from the email bodies and perform the sentiment analysis on only the given number of words. The number of words that are extracted around the keyword is defined by str_length. If use_extractor is set to False, the entire email body is used for the training set and sentiment analysis.

Analyzer.py is a script that utilizes the database created with email_parser.py in order to generate a csv file that contains information on sender's alignment wih Obama. Specifically, it contains the number of emails that the sender sent that align with or bash Barack Obama for every sender in the database. It also contains the percentage of emails that the sender sent that align with or bash Obama.

The Scripts folder houses some of the scripts that can be used to create datasets from the email information. You can view some examples of these datasets in the Data folder.

frequencies.py output:

![frequencies.py](/Media/frequencies.PNG)

common_words.py output:

![common_words.py](/Media/common_words.png)
