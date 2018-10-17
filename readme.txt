## This is a script that pulls information about all the CFN stacks in an AWS account via AWS API and outputs the result to JSON file.
## Written in Python 3.7

1. Requierments:

	Python 3 - https://www.python.org/downloads/
	Boto3 - https://boto3.readthedocs.io/en/latest/

2. How to use:

	1. Setup Boto3 with your AWS credentials - https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration
	2. Run cfn_pull.py from command-line with output name e.g.
		D:\scripts>cfn_pull2.py my_pull.json
	3. Script should display the following:
		Loading resources.. This will take some time.. Standby..
		Writing to file my_pull.json
		File written to my_pull.json
	4. Open the JSON file to display the result

3. How it works:
	
	This script uses 3 different Boto3 SDK calls to gather the data:
	1. list_stacks()
	2. describe_stacks()
	3. describe_stack_resources()
	
	For each stack a dictionary is created from the response of the above calls.
	Each dictionary is stored in a list which in the end is converted to a JSON file.


	In the JSON file, following info is displayed:
	'Stack Name' - string
        'Stack ID' - string
        'Stack Status' - string
        'Stack Creation Timestamp' - string
        'Stack Template' - string
        'Nested' - boolean
        'Stack Parameters' - list
        'Resource Types' - list

4. Tests:

	I have only made 2 tests for this script. These are defined in 'cfn_pull_test.py' file.
	First test checks if we have a 200 response from boto3 call. Second checks that we don't have 
	'None' values in the output.