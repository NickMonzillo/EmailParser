# EmailParser
Stores email header and body information in JSON format.

This program is a tool to convert a directory of .eml files into a json format. The json file will contain all header and body information for each email.

To use this program, simply run the program from a Python interpreter. The prompts in the console will ask you for directory and json file locations. Once provided, it will generate the json in the specified location.

This program is very lightweight, and can deal with directories with large amounts of files.

Analyzer.py is a script that utilizes the database created with email_parser.py in order to generate a csv file that contains information on sender's alignment wih Obama. Specifically, it contains the number of emails that the sender sent that align with or bash Barack Obama for every sender in the database. It also contains the percentage of emails that the sender sent that align with or bash Obama.

The Scripts folder houses some of the scripts that can be used to create datasets from the email information. You can view some examples of these datasets in the Data folder.

frequencies.py output:

![frequencies.py](/Media/frequencies.PNG)

common_words.py output:

![common_words.py](/Media/common_words.png)
