# Get AWS Reserved Instance Coverage

This script summarises the current usage by instance type in each region and compares this against the active
reserved instances in that region. This allows you to know whether you currently have coverage for your resource 
usage and where to reserve more instances if required. 

Currently the script checks Elasticache, EC2 and RDS instances. 


## Usage

  ./getRICoverage.py

## Update

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

+ For RDS the AZ Type must match the RI purchased type itherwise it doesn't count as a match - DONE
+ Add Redshift - DONE
+ Add any other reserved instance types supported. ie ES