import xadmin
from .models import RecentScansDB,StaticAnalyzerAndroid


class RecentScansDBXadmin(object):
    list_display = ['id','FILE_NAME','FILE_NAME','MD5','URL','TIMESTAMP','APP_NAME','PACKAGE_NAME','VERSION_NAME','USER_ID']
    model_icon = 'fa fa-snowflake-o'


xadmin.site.register(RecentScansDB,RecentScansDBXadmin)


class StaticAnalyzerAndroidXadmin(object):
    list_display = ['id','FILE_NAME','APP_NAME','APP_TYPE','SIZE','MD5','SHA256','PACKAGE_NAME','MAIN_ACTIVITY']


xadmin.site.register(StaticAnalyzerAndroid,StaticAnalyzerAndroidXadmin)