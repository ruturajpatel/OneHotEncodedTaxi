'''
@author:ruturajp

The purpose of this program is to find the trend of number of trips paid by credit card and cash
over different attributes.

We want to analyze the amount in cash still used to pay for taxi rides in NYC over the amount paid
with credit cards.

The output filtered data will be imported to Tableau inorder to find details with visualizations.

The program includes following details-
-Cash and credit card payments for trips over the period of different months and years 
from 2010 till 2013
- Amount being paid via cash and credit cards over different months and years from 2010 till 2013

'''
from pyspark import SparkConf, SparkContext
from pyspark.sql import  Row
from pyspark.sql import SQLContext
import sys, operator
from pyspark.sql.functions import *

conf = SparkConf().setAppName('Payment Type Analysis')
sc = SparkContext(conf=conf)

sqlContext= SQLContext(sc)

s3 = 's3://taxidata.com/'
year1 = s3+'2010/'
year2 = s3+'2011/'
year3 = s3+'2012/'
year4 = s3+'2013/'

#parquet file
myParquet = sqlContext.read.parquet(year1,year2,year3,year4)

#selecting required data with conditions
transDF = myParquet.select(trim(upper(myParquet.paymentType)).alias('paymentType'), \
                    year('pickupTime').alias('year') \
                    ,month('pickupTime').alias('month'), \
                    'totalAmount').where('totalAmount > 0')

#Cleaning the data
transDF = (transDF.withColumn('paymentType',
    regexp_replace('paymentType', 'CAS', 'CSH'))
    .withColumn('paymentType',
    regexp_replace('paymentType', 'CRD', 'CRE')))


#All trips count of cash and cc 
cash_cc_trips = (transDF
     .groupBy('year','month','paymentType')
     .agg(count("paymentType").alias("tripsCount"))
     .where(col("paymentType").isin({"CRE", "CSH"}))
     .orderBy("month").coalesce(1))

#Output to csv
cash_cc_trips.write.mode('overwrite') \
                        .format("com.databricks.spark.csv") \
                        .save('s3://taxidata.com/PaymentTypeAnalysis/cashCCTrips')

#Amount paid by CC or Cash every month a year
charges_cash_cc = (transDF
     .groupBy('year','month','paymentType')
     .sum("totalAmount").alias("amountPaid")
     .where(col("paymentType").isin({"CRE", "CSH"}))
     .orderBy("month").coalesce(1))

#Output to csv
charges_cash_cc.write.mode('overwrite') \
                        .format("com.databricks.spark.csv") \
                        .save('s3://taxidata.com/PaymentTypeAnalysis/amountPaidCSHCC')

    

