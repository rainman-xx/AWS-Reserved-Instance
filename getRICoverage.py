#!/usr/bin/env python3
# coding: utf-8
'''
  Get the Reserved Instance Usage for each region
'''
from collections import Counter
import boto3
from termcolor import colored
from collections import namedtuple

# tuple name:         Description or Example:
# describe_fn         Corresponding describe function. In ec2 it's describe_instances
# instances_listname  Attribute (name) for the list of instance. In rds it's DBInstances
# instances_filters   Dictionary of attribute as keys and corresponding values to match. Could be empty
# cluster_count       Attribute for the number of nodes in the cluster. Applicable only to cluster type service like elasticache
# instance_type       Attribute  for the Instance type. In ec2 it's 'InstanceType'
# reserved_fn         In ec2 it's describe_reserved_instances
# reserved_listname   Attribute for the list of reserved instance. In ec2 it's 'ReservedInstances'
# reserved_filters    Dictionary of attribute as keys and corresponding values to match. Could be empty
# reserved_count      Attribute for the reserved instances count
# dimensions          Attribute(s) used for additional dimensions appended to the instance_type key

AWS_service = namedtuple('AWS_service',
    "describe_fn instances_listname instances_filters cluster_count  instance_type "
    "reserved_fn reserved_listname  reserved_filters  reserved_count dimensions")

AWS_services_dict = {
    # 'es' : AWS_service(
    #     'describe_elasticsearch_domains','DomainStatusList',{}, 'NodeType', 'NumberOfNodes',
    #     'describe_reserved_elasticsearch_instances','ReservedElasticsearchInstances',{},'NodeCount',''
    #     ),
    'rds' : AWS_service(
        'describe_db_instances', 'DBInstances',{'DBInstanceStatus':'available'}, '','DBInstanceClass',
        'describe_reserved_db_instances','ReservedDBInstances',{},'DBInstanceCount',
        ['MultiAZ']
        ),
    'ec2' : AWS_service(
        'describe_instances', 'Reservations',{'State':{'Code': 16, 'Name': 'running'}},'','InstanceType', 
        'describe_reserved_instances','ReservedInstances',{},'InstanceCount',
        ''
        ),
    'elasticache' : AWS_service(
        'describe_cache_clusters', 'CacheClusters',{}, 'NumCacheNodes','CacheNodeType', 
        'describe_reserved_cache_nodes','ReservedCacheNodes',{},'CacheNodeCount',
        ''
        ),

    'redshift' : AWS_service(
        'describe_clusters', 'Clusters',{}, 'NumberOfNodes', 'NodeType', 
        'describe_reserved_nodes','ReservedNodes',{},'NodeCount',
        ''
        ),
}

def getServiceInstances(service,regions,service_def):
    _instances = []
    svc=service_def[service]
    for region in regions:
        client = boto3.client(service, region_name=region) 
        service_client = getattr(client,svc.describe_fn)()
        service_instances = service_client[svc.instances_listname]
        # in ec2 instances are nested in Instances array
        if service == 'ec2':
            _groups_instances =[]
            for group in service_instances:
                _groups_instances += group['Instances']
            service_instances = _groups_instances
        for instance in service_instances:
            include=True
            for key in svc.instances_filters.keys():
                include = include and (instance[key] == svc.instances_filters[key])
            if not include:
                continue # Skip to the next loop (instance)
            instance['Region'] = region
            _instances.append(instance)
    # All done
    return _instances

def getServiceReservedInstances(service,regions,service_def):
    _instances = []
    svc=service_def[service]
    for region in regions:
        client = boto3.client(service, region_name=region)
        # Filter by hand since "Filters=" is not available in all services.
        service_client = getattr(client,svc.reserved_fn)()
        for reserved in service_client[svc.reserved_listname]:
             if reserved['State'] == 'active' :
                reserved['Region'] = region
                _instances.append(reserved)

    return _instances

def serviceReservedInstanceReportEx(service,regions,service_def):
    instances = getServiceInstances(service,regions,service_def)
    # reserved_instances = getServiceReservedInstances(service,regions,service_def)
    instances += getServiceReservedInstances(service,regions,service_def)

    svc=service_def[service]
    print("\n{}".format(service))
    print('=' * len(service))
    # Now see if we have enough of each type
    for region in regions:
        # merge structure: { 'm1.small': {'running':1,'reserved':5} }
        merged = {}
        
        for instance in [ i for i in instances if i['Region'] == region ]:
            key = instance[svc.instance_type]
            if svc.dimensions:
                key += ' (' 
                for dim in svc.dimensions:
                    key += dim+':'+str(instance[dim])+', '
                key = key[:len(key)-2]
                key += ')'
            if not key in merged :
                merged[key] = {'running':0,'reserved':0}
            if ( ('State' in instance) and (instance['State'] == 'active') ): 
                merged[key]['reserved'] += instance[svc.reserved_count]
            else:
                merged[key]['running'] += instance[svc.cluster_count] if svc.cluster_count else 1

        # Do we have any instances? next loop if none
        if not merged:
            continue

        # Okay ready for the output        
        maxlen = len(max(merged.keys(),key=len))

        print('\n {:^15s}\n {:^15s}'.format(region, '=' * (len(region)+2)))
        for item in sorted(merged.items()):
            if merged[item[0]]['running']>merged[item[0]]['reserved']:
                symbol = '>'
                status = '\u274C'
            elif merged[item[0]]['running']<merged[item[0]]['reserved']:
                symbol = '<'
                status = '\u26A0'
            else:
                symbol = '='
                status = '\u2705'
            # print(u'%30s  Usage: %3d %s Reserved: %3d : %s' % (item[0],merged[item[0]]['running'],
            #     symbol,merged[item[0]]['reserved'],status))
            print(u'  Usage:%3d %s Reserved:%3d : %s  - %s' % (merged[item[0]]['running'],
                symbol,merged[item[0]]['reserved'],status,item[0]))


def main():
    regions = ['us-east-1'] #,'us-west-2','eu-west-1','eu-central-1']
    for service in AWS_services_dict.keys():
        serviceReservedInstanceReportEx(service,regions,AWS_services_dict)
    
if __name__ == '__main__':
    main()
