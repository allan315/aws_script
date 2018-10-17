import boto3
import json
import datetime
import sys
import os

__author__ = 'Allan Pilvet'

'''
This script uses boto3 sdk to pull info from aws couldformation, extracts
selected info about the stacks and saves the output as a json file.

To use this script, run it from command line, specifying the output.

Usage: cfn_pull.py Output-location

Example:

D:\scripts>cfn_pull.py my_pull.json
Pulling resources... This will take a while..
Writing to file D:\scripts\my_pull.json
File written to D:\scripts\my_pull.json
'''


# Define my exception
class MyError(Exception):
    pass

# Define dictionary mappings
list_stacks_map = (('Stack Name', 'StackName'),
                   ('Stack ID', 'StackId'),
                   ('Stack Status', 'StackStatus'),
                   ('Stack Creation Timestamp', 'CreationTime'),
                   ('Stack Template', 'TemplateDescription'),
                   ('Nested', 'ParentId'),
                   ('Stack Parameters', 'Parameters'),
                   ('Resource Types', 'ResourceType'))


# Define list for storing output
my_list = []

# Create cloudformation client
cfn = boto3.client('cloudformation')


# Use datetime utils to convert 'CreationTime' datetime
class tzutc(datetime.tzinfo):

    def tzname(self, dt):
        return "UTC"


# Abstract resources loading function.
# It takes a resource function and optional keyword args
# Also if NextToken exists in response, use it to get rest of the data
def load_resource(resource, **kwargs):

    response_list = []
    response = resource(**kwargs)
    status_check(response.get('ResponseMetadata').get('HTTPStatusCode'))
    while response.get('NextToken'):
        response_list.append(response)
        response = resource(NextToken=response.get('NextToken'))
        status_check(response.get('ResponseMetadata').get('HTTPStatusCode'))
    response_list.append(response)
    return response_list


# Make a dict from resources.
def map_summary(item):

    my_dict = {}
    for a, b in list_stacks_map:

        if a == 'Stack Creation Timestamp':
            my_dict[a] = parse_time(item.get(b))

        elif a == 'Nested':
            # If 'ParentId' exists, then 'Nested' key is 'True'
            my_dict[a] = True if item.get(b) else False
        
        elif a == 'Stack Parameters':
            # Don't call 'get_stack_parameters'
            # if status 'DELETE_COMPLETE' because it throws an excpetion
            my_dict[a] = get_stack_parameters(item) if item.get(
                'StackStatus') != "DELETE_COMPLETE" else "DELETED"

        elif a == 'Resource Types':
            # Don't call 'get_resource_type'
            # if status 'DELETE_COMPLETE' because it throws an excpetion
            my_dict[a] = get_resource_type(item) if item.get(
                'StackStatus') != "DELETE_COMPLETE" else "DELETED"

        else:
            my_dict[a] = item.get(b)

    return my_dict


# Add map_summary dicts to a list
def stack_summary(summary):

    for item in summary.get('StackSummaries'):
        my_item = map_summary(item)
        keys_check(my_item)
        my_list.append(my_item)


# Use 'cfn.describe_stacks' to get Stack parameters.
def get_stack_parameters(item):

    response = load_resource(
        cfn.describe_stacks, StackName=item.get('StackName'))[0]
    params = ([i.get('Parameters') for i in response.get('Stacks')])
    return params


# Use 'cfn.describe_stack_resources' to get Stack resource types.
def get_resource_type(item):

    response = load_resource(
        cfn.describe_stack_resources, StackName=item.get('StackName'))[0]
    params = ([i.get('ResourceType') for i in response.get('StackResources')])
    return params


# Convert datetime to string
def parse_time(time):
    return time.strftime('%m/%d/%Y -- %H:%M %Z')


# Check if https status is 200 OK
def status_check(status):
    if status != 200:
        raise MyError("Ivalid https status: {}".format(status))
        sys.exit()

# There shouldn't be 'None' values in the output
def keys_check(keys):
    for item,_ in list_stacks_map:
        if keys.get(item) == None:
            raise MyError("Missing '{}' key value in response".format(item))
            sys.exit()

if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.exit("Usage: {} Output-location".format(
            os.path.basename(sys.argv[0])))

    path = sys.argv[1]
    if not os.path.exists(path):
        path = os.path.join(os.getcwd(), os.path.basename(path))

    print("Loading resources.. This will take some time.. Standby..")
    response = load_resource(cfn.list_stacks)
    for r in response:
        stack_summary(r)

    print("Writing file '{}'".format(path))
    with open(path, 'w') as f:
        json.dump(my_list, f, indent=4)
    print("'{}' written!".format(path))

