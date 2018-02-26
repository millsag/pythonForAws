#! /usr/bin/python
################################################################################
## ebs-tagger - gives a name tag to  EBS volumes, based on connected ec2 instance's name
## Written by Adam Mills
## Date: February 26, 2018
## 
##
################################################################################
import csv
import os, sys
import datetime
import argparse
from boto import ec2
from boto.exception import EC2ResponseError

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
        
def tag_volumes (regions, access_key, secret_key):

     # opens file
    f = open(args.file, 'wt', newline='')
    """
    tags ebs volumes with name of linked ec2 instance
    """
    
    region_list = regions.split('|')
    
    vd = {}
    instanceDict = {}
    # go over all regions in list
    for region in region_list:
    
        # connects to ec2
        conn = ec2_connect (access_key, secret_key, region)
        if not conn:
            sys.stderr.write ('Could not connect to region: %s. Skipping\n' % region)
            continue

        #get map of instance names
        instanceDict[region] = {}
        reservations = conn.get_all_instances()
        instances = [j for r in reservations for j in r.instances]
        for i in instances:
            architecture = i.architecture
            instanceDict[region][i.id] = { 'region' : region,
                                           'instance_id' : i.id,
                                           'name' : i.tags['Name']
                                           }
                                              
        # get all volumes 
        try:
            volumes = conn.get_all_volumes ()
        except EC2ResponseError:
            sys.stderr.write ('Could not get volumes for region: %s. Skipping (problem: %s)\n' % (region))
            continue
        
        
        vd [region] = {}
        # goes over volumes and insert relevant data into a python dictionary
        for vol in volumes:
            tags = {}
            try:
                name = vol.tags['Name']
            except:
                name = u''
        
            if vol.attachment_state() == u'attached':
                instance_id = vol.attach_data.instance_id
                device = vol.attach_data.device
            else:
                instance_id = u'N/A'
                device = 'N/A'
            
            if  instance_id != 'N/A':
                related_instance = instanceDict[region][instance_id]
                instance_name= related_instance['name']
                tags['Name'] = instance_name
            else:
                instance_name = 'N/A'

            vd [region][vol.id] = { 'name' : name, 
                                             'instance' : instance_id,
                                             'instance name' : instance_name
                                            }
                    
            if name == '':
                conn.create_tags(vol.id,tags)


                                            

        
                                                    

    # starts the csv file
    writer = csv.writer (f)
    # header
    writer.writerow ([ 'Region','volume ID','Volume Name','instance id','instance name'])
         
    # writes actual data
    for region in vd.keys ():
        for volume_id in vd[region].keys ():
            volume = vd[region][volume_id]
            writer.writerow ([region, volume_id, volume['name'],volume['instance'],volume['instance name']])
                              


    return True
    
if __name__ == '__main__':

    # Define command line argument parser
    parser = argparse.ArgumentParser(description='Creates a CSV report about EBS volumes and tracks snapshots on them.')
    parser.add_argument('--regions', default = AWS_REGIONS, help='AWS regions to create the report on, can add multiple with | as separator. Default will assume all regions')
    parser.add_argument('--access_key', default = AWS_ACCESS_KEY, help='AWS API access key.  If missing default is used')
    parser.add_argument('--secret_key', default = AWS_SECRET_KEY, help='AWS API secret key.  If missing default is used')
    parser.add_argument('--file',  default = 'names.csv', help='Path for output CSV file')
    args = parser.parse_args ()

    # does the work
    retval = tag_volumes (args.regions, args.access_key, args.secret_key)
    if retval:
        sys.exit (0)
    else:
        sys.exit (1)
        
        
