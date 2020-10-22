
import re
import logging
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class AnalysisUrlsEmails(object):
    def __init__(self, datas: list):
        self.datas = datas

    def extract_access_urls(self):  # 插入源码第一个函数，对code_an_dic['urls']进行解析，获取可以访问的urls
        """
        提取可访问的url
        :param urls: 需处理的url数据
        :return: 格式['urls':[],'path':'']，urls可访问
        """
        url_list = []
        for url in self.datas:
            need_url = []
            for url_ in url['urls']:
                if url_.lower().startswith('http'):
                    need_url.append(url_)
                elif url_.lower().startswith('www'):
                    url_ = 'http://' + url_
                    need_url.append(url_)
            if need_url:
                need_url = list(set(need_url))
                url_list.append({'urls': need_url, 'path': url['path']})
        return url_list

    @staticmethod
    def extract_phone_card_passport(data: str):
        """
        提取 手机号、身份证号、护照号
        :param data:需要利用re提取的数据
        :return:{'phones:[],'cards':[],'passports':[]}返回一个Dict类型
        """
        phones = list(set([numbers[0] for numbers in re.findall(r'((\+|[0-9])\d+)', data) if
                           (len(numbers[0]) == 11 or len(numbers[0]) == 14 or len(numbers[0]) == 15) and re.match(
                               r'^(1|00861|\+861)[3-9]\d{9}$', numbers[0])]))

        pattern_card_18 = re.compile(
            (r'(([1-6][1-9]|50)\d{4}(19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx])'),
            re.UNICODE)
        pattern_card_15 = re.compile((
            r'(([1-6][1-9]|50)\d{4}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d+)'
        ), re.UNICODE)
        card_18 = [c_18[0] for c_18 in pattern_card_18.findall(data)]
        card_15 = [c_15[0] for c_15 in pattern_card_15.findall(data) if len(c_15[0]) == 15]
        cards = list(set(card_15.extend(card_18) if card_15.extend(card_18) else []))
        pattern_passport = re.compile(
            (r'([EeGg]\d{8})|(([Ee][a-hjklmnp-zA-HJKLMNP-Z])\d{7})'),
            re.UNICODE)
        passports = list(set([passport[1].upper() if passport[0] == '' else passport[0].upper() for passport in
                              pattern_passport.findall(data)]))

        pattern_gps_lng = re.compile(
            (r'((\-|\+)?(((\d|[1-9]\d|1[0-7]\d|0{1,3})\.\d+)|(\d|[1-9]\d|1[0-7]\d|0{1,3})|180\.0{0,7}|180))'),
            re.UNICODE
        )
        pattern_gps_lat = re.compile(
            (r'((\-|\+)?[0-8]?\d{1}\.\d+|90\.0{0,7}|[0-8]?\d{1}|90)'),
            re.UNICODE
        )
        lng = list(set([lg[0] for lg in pattern_gps_lng.findall(data) if
                        '.' in lg[0] and (73.00000000 < float(lg[0]) < 135.00000000) and (
                                    6 <= len(lg[0].split('.')[1]) <= 8)]))  # 经度 lng
        lat = list(set([la[0] for la in pattern_gps_lat.findall(data) if
                        '.' in la[0] and (18.00000000 < float(la[0]) < 53.56000000) and (
                                    6 <= len(la[0].split('.')[1]) <= 8)]))  # 经度 lat
        gps_lng_lat = [(ln, la) for ln in lng for la in lat]

        total = len(phones) + len(cards) + len(passports)
        if total != 0:
            return {'phones': phones, 'cards': cards, 'passports': passports, 'gps_lng_lat': gps_lng_lat}

    def handle_urls_emails(self):
        """
        处理url与email数据
        :param datas: datas可以是url/email的列表
        :return:返回样式 [{},{}] --> {'urls'/'emails':[{'phones':[],'cards':[],'passports':[],'url/email':'xx'}],'path':'',}
        """
        # 判断参数是否存在urls与emails的key，如果是urls需要进行re处理，否则直接进行re处理邮箱
        if not len(self.datas):
            return []
        key = 'urls' if self.datas[0].get('urls') else 'emails'
        datas = self.extract_access_urls() if key == 'urls' else self.datas  # 对urls与emails做选择
        for data in datas:
            data_dict, need_datas = {}, []
            try:
                for tag in data[key]:  # 处理data里面子列表
                    result = self.extract_phone_card_passport(tag)  # 进行正则处理
                    if result:
                        result[key.replace('s', '')] = tag  # 添加具体哪个目标数据被解析出结果
                        need_datas.append(result)  # 将结果存入一个列表中
                data['results'] = need_datas  # 在源数据中插入结果列表的数据
            except KeyError as e:
                logger.info('Key missing from re parsing data：%s' % e)
        return datas


class AnalysisResponse(object):
    def __init__(self, urls: list, total=None, connect=None, sock_connect=15, sock_read=None):
        self.urls = urls
        self.total = total
        self.connect = connect
        self.sock_connect = sock_connect
        self.sock_read = sock_read

    async def get(self, url):
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=self.total, connect=self.connect,
                                        sock_connect=self.sock_connect,
                                        sock_read=self.sock_read)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.get(url) as rep:
                if rep.status == 200:
                    return {'url': url, 'resp': await rep.text()}  # 返回响应内容

    async def request(self, url):
        try:
            result = await self.get(url)
            return result
        except aiohttp.ClientConnectionError as e:
            pass
        except ValueError as e:
            pass
        except UnicodeEncodeError as e:
            pass

    def handle_resp(self, tasks):
        need_datas = []
        for task in tasks:
            if task.result():
                need_datas.append(task.result())
        return need_datas

    def run(self):
        logger.info('Asynchronous request for a large number of URLs')
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        tasks = [asyncio.ensure_future(self.request(url)) for url in self.urls]
        loop.run_until_complete(asyncio.wait(tasks))
        return self.handle_resp(tasks)


def main(types: str, datas: list):
    logger.info('Start Parsing %s' % types)
    AUE = AnalysisUrlsEmails(datas=datas)
    first_result = AUE.handle_urls_emails()
    if types == "urls":
        need_urls = set([l for u in first_result for l in u['urls']])
        excludes = ['ali', 'baidu', 'taobao', 'tmall', 'tencent', 'qq', 'map', 'mob', 'google', 'jabber', 'github',
                    'weibo', 'meituan', 'facebook', 'amazon','huawei','douyin']
        ignore_url = set()
        for url in need_urls:
            for exc in excludes:
                if exc in url:
                    ignore_url.add(url)
                    break
        total_urls = list(need_urls - ignore_url)
        if total_urls:
            resp_result = AnalysisResponse(urls=total_urls).run()  # 得到response对象
            for data in first_result:
                data_dict, need_datas = {}, []
                for task in resp_result:
                    res = AnalysisUrlsEmails.extract_phone_card_passport(task['resp'])
                    if res:
                        res['url'] = task['url']
                        if res['url'] in data['urls']:
                            if not data['results']:
                                need_datas.append(res)
                            else:
                                for r in data['results']:
                                    if r['url'] == res['url']:
                                        r['phones'].extend(res['phones'])
                                        r['cards'].extend(res['cards'])
                                        r['passports'].extend(res['passports'])
                                        r['gps_lng_lat'].extend(res['gps_lng_lat'])
                                    else:
                                        need_datas.append(res)
                if need_datas:
                    data['results'].extend(need_datas)
    return first_result

from django_redis import get_redis_connection

RDS_DB5 = get_redis_connection('default')
