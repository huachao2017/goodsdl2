import logging
import subprocess
import time
import datetime
logger = logging.setLoggerClass("detect")

def import_from_mysql(mysqlhost,port,user,password,database,table,isfirst=False):
    shell_str1 = 'hadoop fs -rm -f -R /user/root/'+table
    shell_str2=None
    if isfirst:
        shell_str2 ='nohup sqoop import  --connect jdbc:mysql://{0}:{1}/{2}  -username "{3}"  -password "{4}" --table {5} --hive-import --hive-table {6}  --hive-database bdl --hive-overwrite --create-hive-table -m 5 --fields-terminated-by "\0001" & '
        shell_str2 = shell_str2.format(mysqlhost,port,database,user,password,table,str(database)+"_"+str(table))
    else:
        # 增量导入 7天之前 截止到 启动脚本时刻的 数据
        exe_time = str(time.strftime('%Y-%m-%d', time.localtime()))
        exe_time = str(
            (datetime.datetime.strptime(exe_time, "%Y-%m-%d") + datetime.timedelta(days=-7)).strftime("%Y-%m-%d"))
        exe_time = exe_time + " 00:00:00"
        shell_str2 = 'nohup sqoop import  --connect jdbc:mysql://{0}:{1}/{2}  -username "{3}"  -password "{4}" --table {5} --hive-import --hive-table {6}  --hive-database bdl --hive-overwrite --create-hive-table -m 5 --fields-terminated-by "\0001"  --incremental append --check-column CREATE_TIME --last-value "{7}" & '
        shell_str2 = shell_str2.format(mysqlhost, port, database, user, password, table,
                                       str(database) + "_" + str(table), exe_time)
    return_code1 = subprocess.call(shell_str1, shell=True)
    logger.info("remove hdfs table,table = %s,return_code=%s" % (str(table), str(return_code1)))
    return_code2 = subprocess.call(shell_str2, shell=True)
    logger.info("sqoop import table,hive_table = %s,return_code=%s,isfirst=%s" % (str(str(database)+"_"+str(table)), str(return_code2),str(isfirst)))



