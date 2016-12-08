from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
import sys, operator
from datetime import datetime
from pyspark.sql.functions import *

conf = SparkConf().setAppName('Tips Analysis')
sc = SparkContext(conf=conf)

sqlContext= SQLContext(sc)

s3 = 's3://taxidata.com/'
year1 = s3+'2010/'
year2 = s3+'2011/'
year3 = s3+'2012/'
year4 = s3+'2013/'

#parquet file
myParquet = sqlContext.read.parquet(year1,year2,year3,year4)

#getting data of pickupTime and tipAmount
pickupDistTip = myParquet.select('pickupTime','tipAmount').where('tipAmount > 0')

pickupDistTip = (myParquet.select(hour("pickupTime").alias("hour"),
                                dayofmonth("pickupTime").alias("day"),
                                'tipAmount'))

tipsAnalysis = (pickupDistTip
    .groupBy('day','hour')
    .agg(avg("tipAmount").alias("avgDailyTips")).coalesce(1))
    
#output to csv
tipsAnalysis.write.mode('overwrite').format("com.databricks.spark.csv") \
					.save('s3://taxidata.com/TipAnalysis/dailytips')

#getting data of driverid and tipAmount
pickupTimeTip = myParquet.select('driverId','tipAmount').where('tipAmount > 0')

#calculating average trips earned by a driver
average_driver_tip = (pickupTimeTip
    .groupBy("driverId")
    .agg(avg("tipAmount").alias("avgDriverTips"))
    .orderBy(desc("avgDriverTips")).coalesce(1))

average_driver_tip.write.mode('overwrite').format("com.databricks.spark.csv") \
						.save('s3://taxidata.com/TipAnalysis/averageDriverTips')