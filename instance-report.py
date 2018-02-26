#! /usr/bin/python
################################################################################
## instance-report - Creates a CSV report for aws instances
##
################################################################################
import csv
import os, sys
import datetime
import argparse
from boto import ec2
from boto.exception import EC2ResponseError
from pprint import pprint

# Defaults, can be modified
secretsFile = open("c:/python/keys.txt", "r")
for line in secretsFile:
    fields = line.split(";")
    AWS_ACCESS_KEY = fields[0]
    AWS_SECRET_KEY = fields[1]
    AWS_REGIONS = 'us-east-1'
    


#array to hold errors
    volumeErrs=[]
    
        
def ec2_connect (access_key, secret_key, region):
    """
    Connects to EC2, returns a connection object
    """
    
    try:
        conn = ec2.connect_to_region (region, 
                                      aws_access_key_id=access_key, 
                                      aws_secret_access_key=secret_key)
    except Exception:
        sys.stderr.write ('Could not connect to region: %s. Exception: %s\n' % (region))
        conn = None
        
    return conn
        
def create_ebs_report (regions, access_key, secret_key, filepath):
    """
    Creates the actual report, first into a python data structure
    Then write into a csv file
    """
    # opens file
    f = open(args.file, 'wt', newline='')

    region_list = regions.split('|')
    
    instanceDict = {}
    # go over all regions in list
    for region in region_list:
    
        # connects to ec2
        conn = ec2_connect (access_key, secret_key, region)
        if not conn:
            sys.stderr.write ('Could not connect to region: %s. Skipping\n' % region)
            continue

        instanceDict[region] = {}
        reservations = conn.get_all_instances()
        instances = [j for r in reservations for j in r.instances]
        for i in instances:
            #break
##            status = conn.get_all_instance_status(instance_ids=i.id)
##            print(status[0].system_status.details)
##            print(status[0].system_status.status + '/' + status[0].instance_status.status)
            architecture = i.architecture
            instanceDict[region][i.id] = { 'region' : region,
                                           'instance_id' : i.id,
                                           'key_name' : i.key_name,
                                           'architecture' : architecture,
                                           'state' : i.state,
                                           'instance_type' : i.instance_type,
                                           'ip_address' : i.ip_address,
                                           'launch_time' : i.launch_time,
                                           'persistent': i.persistent,
                                           'placement' : i.placement,
                                           'public_dns_name' : i.public_dns_name,
                                           'vpc_id': i.vpc_id,
                                           'tags' : i.tags['Name']
                                           }
                                              
    # starts the csv file
    writer = csv.writer (f)
    # header
    writer.writerow (['Region','Instance ID','Key Name','Architecture','State', 'Instance Type', 'IP Address', \
                      'Launch Time', 'Persistent', 'Placement', 'Public DNS', 'VPC ID', 'Name'])
         
    # writes actual data
    for region in instanceDict.keys ():
        for instance_id in instanceDict[region].keys ():
            instance = instanceDict[region][instance_id]
            writer.writerow ([region, instance_id, instance['key_name'], instance['architecture'], \
                              instance['state'],instance['instance_type'],instance['ip_address'], \
                              instance['launch_time'],instance['persistent'],instance['placement'], \
                              instance['public_dns_name'],instance['vpc_id'], instance['tags']])
                              

    
    f.close ()
    return True
    
if __name__ == '__main__':

    # Define command line argument parser
    parser = argparse.ArgumentParser(description='Creates a CSV report about EBS volumes and tracks snapshots on them.')
    parser.add_argument('--regions', default = AWS_REGIONS, help='AWS regions to create the report on, can add multiple with | as separator. Default will assume all regions')
    parser.add_argument('--access_key', default = AWS_ACCESS_KEY, help='AWS API access key.  If missing default is used')
    parser.add_argument('--secret_key', default = AWS_SECRET_KEY, help='AWS API secret key.  If missing default is used')
    parser.add_argument('--file',  default = 'instances.csv', help='Path for output CSV file')
    
    args = parser.parse_args ()

    today = datetime.datetime.today().strftime("%Y-%m-%d")
    today = datetime.datetime.strptime(today, '%Y-%m-%d')
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(today)
    print(now)

    startTime = "0830"
    stopTime = "2330"
    startTime = today + datetime.timedelta(
    hours=int(startTime[:2]), minutes=int(startTime[-2:]))
    stopTime = today + datetime.timedelta(
    hours=int(stopTime[:2]), minutes=int(stopTime[-2:]))
    print(startTime)
    print(stopTime)
    print(datetime.datetime.today().strftime("%a").lower())

    nowTime = datetime.datetime(2018, 2, 7, 00, 30)
    nowMax = nowTime - datetime.timedelta(minutes=59)
    nowMax = nowMax.strftime("%H%M")
    print(nowMax)
    
    # creates the report
    retval = create_ebs_report (args.regions, args.access_key, args.secret_key, args.file)
    if retval:
        sys.exit (0)
    else:
        sys.exit (1)
        
        
