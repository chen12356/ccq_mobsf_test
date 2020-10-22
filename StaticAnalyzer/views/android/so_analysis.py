from StaticAnalyzer.models import SO_AND_SDK
import re


def so_analysis(so_list):
    # print(so_list)
    known_list=[]
    include_list=[]
    so_set=set(so_list)
    for i in so_set:
         pattern = re.compile('lib([0-9a-zA-Z\.\_\-\+]*)\.so').findall(i)[0]
         db_data=SO_AND_SDK.objects.all()
         for db_so in db_data:
            if db_so.SDK_NAME.lower() in pattern.lower():
                include_list.append({
                'SO_NAME':i,
                'SDK_NAME':pattern,
                'CN_NAME':db_so.CN_NAME,
                'CONTENT':db_so.CONTENT,
                'WEBADDRESS':db_so.WEBADDRESS,
                'STATE':str(db_so.STATE)
                })
                break
            else:
                pass
    if include_list:
        for known in include_list:
            known_list.append(known['SO_NAME'])
    
        unknown_list=so_set.difference(set(known_list))
        so_unknown=[]
        for unknown_so in unknown_list:
            so_unknown.append({
                'SO_NAME':unknown_so,
                'SDK_NAME':re.compile('lib([0-9a-zA-Z\.\_\-\+]*)\.so').findall(unknown_so)[0],
                'CN_NAME':'未知',
                'CONTENT':'',
                'WEBADDRESS':'',
                'STATE':str(0)
            })
        
        
        return include_list+so_unknown
    else:
        unknown_so_list=[]
        for unknown_so_other in so_set:
            unknown_so_list.append({
                'SO_NAME':unknown_so_other,
                'SDK_NAME':re.compile('lib([0-9a-zA-Z\.\_\-\+]*)\.so').findall(unknown_so_other)[0],
                'CN_NAME':'未知',
                'CONTENT':'',
                'WEBADDRESS':'',
                'STATE':str(0)

            })
        
        return unknown_so_list
    
