# Get AWS Reserved Instance Coverage

This script summarises the current usage by instance type in each region and compares this against the active
reserved instances in that region. This allows you to know whether you currently have coverage for your resource 
usage and where to reserve more instances if required. 

Also considers the case when you have unutilized reserved instances.

Currently the script checks Elasticache, EC2, RDS, Redshift, and Elasticsearch instances. 


## Usage

  ./getRICoverage.py

## Update

### 2020-01-05
+ Added ElasticSearch support
+ Able to access value in multi level Dictionary like in ES by flatting it accessing it like objects. i.e Using a['foo.bar'] instead of a['foo']['bar']

### 2020-01-04
+ Major restructure: Generic functions, Filters, etc
+ Added Redshift support
+ Added RDS MultiAZ support
+ Remove Color module. Already using color coded unicode symbol

## Sample Output 
```
  rds
===

    us-east-1   
   ===========  
  Usage:  2 = Reserved:  2 : ✅  - db.m3.medium (MultiAZ:False)
  Usage:  0 < Reserved:  1 : ⚠  - db.m3.medium (MultiAZ:True)
  Usage:  1 > Reserved:  0 : ❌  - db.m4.large (MultiAZ:False)

ec2
===

    us-east-1   
   ===========  
  Usage:  1 > Reserved:  0 : ❌  - c5.xlarge
  Usage:  4 = Reserved:  4 : ✅  - m1.medium
  Usage:  2 < Reserved:  3 : ⚠  - m1.small

elasticache
===========

    us-east-1   
   ===========  
  Usage:  5 = Reserved:  5 : ✅  - cache.m3.medium
  Usage:  4 > Reserved:  0 : ❌  - cache.t2.micro
  Usage:  0 < Reserved:  4 : ⚠  - cache.t3.micro

redshift
========

    us-east-1   
   ===========  
  Usage:  6 > Reserved:  0 : ❌  - dc2.large

```

## Todo

+ Handle the case where ES cluster has separate master. Maybe consider it like RDS MultiAZ as additional dimension
+ Additional Code documentation
+ Pass regions and services as command line parameters. Other assume all regions and all supported services