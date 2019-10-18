from goods.sellgoods.dataio.utils import sqooputil
from set_config import config
sqoop_import_info = config.crontab_sqoop_import
def sqoop_process(isfirst=False):
    for key in sqoop_import_info:
        mysqlhost, port, user, password, database = key['env_info'][0],key['env_info'][1],key['env_info'][2],key['env_info'][3],key['env_info'][4],key['env_info'][5]
        tables = key['tables']
        for table in tables:
            sqooputil.import_from_mysql(mysqlhost,port,user,password,database,table,isfirst=isfirst)

if __name__=='__main__':
    sqoop_process()