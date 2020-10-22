# -*- coding: utf_8 -*-
"""
Shared Functions.

Module providing the shared functions for static analysis of iOS and Android
"""
import hashlib
import io
import json
import logging
import os
import pickle
import platform
import re
import shutil
import subprocess
import zipfile
from urllib.parse import urlparse

import requests

import MalwareAnalyzer.views.VirusTotal as VirusTotal

from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from django.utils.html import escape

from MobSF import settings
from MobSF.utils import (print_n_send_error_response,
                         upstream_proxy)

from StaticAnalyzer.models import (RecentScansDB,
                                   StaticAnalyzerAndroid,
                                   StaticAnalyzerIOS,
                                   StaticAnalyzerWindows)
from StaticAnalyzer.views.comparer import generic_compare
from StaticAnalyzer.views.android.db_interaction import (
    get_context_from_db_entry as adb)
from StaticAnalyzer.views.ios.db_interaction import (
    get_context_from_db_entry as idb)
from StaticAnalyzer.views.url_email_analysis import RDS_DB5
from StaticAnalyzer.views.windows.db_interaction import (
    get_context_from_db_entry as wdb)
from StaticAnalyzer.views.rules_properties import (
    Level,
)

logger = logging.getLogger(__name__)
try:
    import pdfkit
except ImportError:
    logger.warning(
        'wkhtmltopdf is not installed/configured properly.'
        ' PDF Report Generation is disabled')
logger = logging.getLogger(__name__)
ctype = 'application/json; charset=utf-8'


def hash_gen(app_path) -> tuple:
    """Generate and return sha1 and sha256 as a tuple."""
    try:
        logger.info('Generating Hashes')
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        block_size = 65536
        with io.open(app_path, mode='rb') as afile:
            buf = afile.read(block_size)
            while buf:
                sha1.update(buf)
                sha256.update(buf)
                buf = afile.read(block_size)
        sha1val = sha1.hexdigest()
        sha256val = sha256.hexdigest()
        return sha1val, sha256val
    except Exception:
        logger.exception('Generating Hashes')


def unzip(app_path, ext_path):
    logger.info('Unzipping')
    try:
        files = []
        with zipfile.ZipFile(app_path, 'r') as zipptr:
            for fileinfo in zipptr.infolist():
                filename = fileinfo.filename
                if not isinstance(filename, str):
                    filename = str(
                        filename, encoding='utf-8', errors='replace')
                files.append(filename)
                zipptr.extract(filename, ext_path)
        return files
    except Exception:
        logger.exception('Unzipping Error')
        if platform.system() == 'Windows':
            logger.info('Not yet Implemented.')
        else:
            logger.info('Using the Default OS Unzip Utility.')
            try:
                unzip_b = shutil.which('unzip')
                subprocess.call(
                    [unzip_b, '-o', '-q', app_path, '-d', ext_path])
                dat = subprocess.check_output([unzip_b, '-qq', '-l', app_path])
                dat = dat.decode('utf-8').split('\n')
                files_det = ['Length   Date   Time   Name']
                files_det = files_det + dat
                return files_det
            except Exception:
                logger.exception('Unzipping Error')


def pdf(request, api=False, jsonres=False):
    try:
        if api:
            checksum = request.POST['hash']
        else:
            checksum = request.GET['md5']
        hash_match = re.match('^[0-9a-f]{32}$', checksum)
        if not hash_match:
            if api:
                return {'error': 'Invalid scan hash'}
            else:
                return HttpResponse(
                    json.dumps({'md5': 'Invalid scan hash'}),
                    content_type=ctype, status=500)
        # Do Lookups
        android_static_db = StaticAnalyzerAndroid.objects.filter(
            MD5=checksum)
        ios_static_db = StaticAnalyzerIOS.objects.filter(
            MD5=checksum)
        win_static_db = StaticAnalyzerWindows.objects.filter(
            MD5=checksum)

        if android_static_db.exists():
            key = settings.MODEL_K %('StaticAnalyzerAndroid',checksum)
            context, template = handle_pdf_android(android_static_db,key)
        elif ios_static_db.exists():
            context, template = handle_pdf_ios(ios_static_db)
        elif win_static_db.exists():
            context, template = handle_pdf_win(win_static_db)
        else:
            if api:
                return {'report': 'Report not Found'}
            else:
                return HttpResponse(
                    json.dumps({'report': 'Report not Found'}),
                    content_type=ctype,
                    status=500)
        # Do VT Scan only on binaries
        context['virus_total'] = None
        ext = os.path.splitext(context['file_name'].lower())[1]
        if settings.VT_ENABLED and ext != '.zip':
            app_bin = os.path.join(
                settings.UPLD_DIR,
                checksum + '/',
                checksum + ext)
            vt = VirusTotal.VirusTotal()
            context['virus_total'] = vt.get_result(app_bin, checksum)
        # Get Local Base URL
        proto = 'file://'
        host_os = 'nix'
        if platform.system() == 'Windows':
            proto = 'file:///'
            host_os = 'windows'
        context['base_url'] = proto + settings.BASE_DIR
        context['dwd_dir'] = proto + settings.DWD_DIR
        context['host_os'] = host_os
        # 增加：返回时间
        time = RecentScansDB.objects.get(MD5=checksum).TIMESTAMP
        context['time'] = time
        # 增加：证书subject和issuer提取
        certificate_info = context['certificate_analysis']['certificate_info']
        subject = re.search(r'Subject:.*', certificate_info).group().split(':')[1]
        issuer = re.search(r'Issuer:.*', certificate_info).group().split(':')[1]
        context['cer_subject'] = subject
        context['cer_issuer'] = issuer
        # 增加：permmision排序
        perm_dict_items = context['permissions'].items()
        sorted_perm = sorted(perm_dict_items, key=lambda x: x[1]['status'])
        context['sorted_perm'] = sorted_perm
        #测试url
        context['test_url'] = [
            {
                "urls": [
                    "http://192.168.1.201:12345/ad_monitor/uploadReceiver.php?os=android&platform=domob"
                ],
                "path": "cn/domob/android/ads/C0027o.java",
                "results": [
                    {
                        "phones": ["18337258710", "15160578228"],
                        "cards": [],
                        "passports": ["E16728736"],
                        "gps_lng_lat": [(78.356287, 120.834628)],
                        "sources": "http://192.168.1.201:12345/ad_monitor/uploadReceiver.php?os=android&platform=domob"
                    }
                ]
            },
            {
                "urls": [
                    "http://www.google.com/loc/json"
                ],
                "path": "cn/domob/android/ads/C0029q.java",
                "results": [{
                    "phones": [],
                    "cards": [],
                    "passports": [],
                    "gps_lng_lat": [],
                    "sources": ""

                }]
            },
            {
                "urls": [
                    "http://r.domob.cn/a/"
                ],
                "path": "cn/domob/android/ads/C0032t.java",
                "results": [{
                    "phones": [],
                    "cards": [],
                    "passports": [],
                    "gps_lng_lat": [],
                    "sources": ""

                }]
            },
            {
                "urls": [
                    "http://e.domob.cn/event_report",
                    "http://r.domob.cn/a/"
                ],
                "path": "cn/domob/android/ads/C0017e.java",
                "results": [
                    {
                        "phones": ["18337258710", "15160578228"],
                        "cards": [],
                        "passports": ["E16728736"],
                        "gps_lng_lat": [(78.356287, 120.834628)],
                        "sources": "http://e.domob.cn/event_report"
                    }
                ]
            },
            {
                "urls": [
                    "http://r.domob.cn/a/"
                ],
                "path": "cn/domob/android/ads/C0022j.java",
                "results": [
                    {
                        "phones": ["18337258710", "15160578228"],
                        "cards": [],
                        "passports": ["E16233236"],
                        "gps_lng_lat": [(78.356287, 120.834628)],
                        "sources": "http://r.domob.cn/a/"
                    }
                ]
            },
        ]
        try:
            if api and jsonres:
                return {'report_dat': context}
            else:
                options = {
                    'page-size': 'A4',
                    'quiet': '',
                    'no-collate': '',
                    'margin-top': '15mm',
                    'margin-right': '10mm',
                    'margin-bottom': '15mm',
                    'margin-left': '10mm',
                    'encoding': 'UTF-8',
                    'header-line': '',
                    # 页脚与正文之间的距离(默认为零)
                    'header-spacing': 2,
                    'footer-spacing': 2,
                    # 设置页码
                    'footer-center': '第 [page] 页',
                    # 'custom-header': [
                    #     ('Accept-Encoding', 'gzip'),
                    # ],

                    # 'dump-outline':'toc.xml',
                    # 'dump-default-toc-xsl': 'my.xsl',
                    'outline': '',
                    # 大纲的深度
                    'outline-depth': '2',

                }
                xsl_path = os.path.join(settings.BASE_DIR, "templates/my.xsl"),
                toc = {
                    # 'toc-header-text':'目录',
                    'toc-level-indentation': '100',
                    'disable-dotted-lines': '',
                    'xsl-style-sheet': xsl_path,
                }
                # cover = os.path.join(settings.BASE_DIR, 'templates/cover.html')
                html = template.render(context)
                # Added proxy support to wkhtmltopdf
                proxies, _ = upstream_proxy('https')
                if proxies['https']:
                    options['proxy'] = proxies['https']
                # pdf_dat = pdfkit.from_string(html,False,options,toc,cover,cover_first=True)
                pdf_dat = pdfkit.from_string(html, False, options, toc)
                if api:
                    return {'pdf_dat': pdf_dat}
                return HttpResponse(pdf_dat,
                                    content_type='application/pdf')
        except Exception as exp:
            logger.exception('Error Generating PDF Report')
            if api:
                return {
                    'error': 'Cannot Generate PDF/JSON',
                    'err_details': str(exp)}
            else:
                return HttpResponse(
                    json.dumps({'pdf_error': 'Cannot Generate PDF',
                                'err_details': str(exp)}),
                    content_type=ctype,
                    status=500)
    except Exception as exp:
        logger.exception('Error Generating PDF Report')
        msg = str(exp)
        exp = exp.__doc__
        if api:
            return print_n_send_error_response(request, msg, True, exp)
        else:
            return print_n_send_error_response(request, msg, False, exp)


def handle_pdf_android(static_db,key):
    logger.info(
        'Fetching data from DB for '
        'PDF Report Generation (Android)')
    con = RDS_DB5.get(key)
    context = pickle.loads(con) if con else None
    if not context:
        logger.info('SEARCH MYSQL, INSERT REDIS:%s' % key)
        context = adb(static_db)
        RDS_DB5.set(key, pickle.dumps(context))
    context['average_cvss'], context[
        'security_score'] = score(context['code_analysis'])
    if context['file_name'].lower().endswith('.zip'):
        logger.info('Generating PDF report for android zip')
        template = get_template(
            'pdf/android_report.html')
    else:
        logger.info('Generating PDF report for android apk')
        template = get_template(
            'pdf/android_report.html')
    return context, template


def handle_pdf_ios(static_db):
    logger.info('Fetching data from DB for '
                'PDF Report Generation (IOS)')
    context = idb(static_db)
    if context['file_name'].lower().endswith('.zip'):
        logger.info('Generating PDF report for IOS zip')
        context['average_cvss'], context[
            'security_score'] = score(context['code_analysis'])
        template = get_template(
            'pdf/ios_report.html')
    else:
        logger.info('Generating PDF report for IOS ipa')
        context['average_cvss'], context[
            'security_score'] = score(
                context['binary_analysis'])
        template = get_template(
            'pdf/ios_report.html')
    return context, template


def handle_pdf_win(static_db):
    logger.info(
        'Fetching data from DB for '
        'PDF Report Generation (APPX)')
    context = wdb(static_db)
    template = get_template(
        'pdf/windows_report.html')
    return context, template


def url_n_email_extract(dat, relative_path):
    """Extract URLs and Emails from Source Code."""
    urls = []
    emails = []
    urllist = []
    url_n_file = []
    email_n_file = []
    # URLs Extraction My Custom regex
    pattern = re.compile(
        (
            r'((?:https?://|s?ftps?://|'
            r'file://|javascript:|data:|www\d{0,3}[.])'
            r'[\w().=/;,#:@?&~*+!$%\'{}-]+)'
        ),
        re.UNICODE)
    urllist = re.findall(pattern, dat)
    uflag = 0
    for url in urllist:
        if url not in urls:
            urls.append(url)
            uflag = 1
    if uflag == 1:
        url_n_file.append(
            {'urls': urls, 'path': escape(relative_path)})

    # Email Extraction Regex
    regex = re.compile(r'[\w.-]+@[\w-]+\.[\w]{2,}')
    eflag = 0
    for email in regex.findall(dat.lower()):
        if (email not in emails) and (not email.startswith('//')):
            emails.append(email)
            eflag = 1
    if eflag == 1:
        email_n_file.append(
            {'emails': emails, 'path': escape(relative_path)})
    return urllist, url_n_file, email_n_file


# This is just the first sanity check that triggers generic_compare
def compare_apps(request, hash1: str, hash2: str):
    if hash1 == hash2:
        error_msg = 'Results with same hash cannot be compared'
        return print_n_send_error_response(request, error_msg, False)
    logger.info(
        'Starting App compare for %s and %s', hash1, hash2)
    return generic_compare(request, hash1, hash2)


def score(findings):
    # Score Apps based on AVG CVSS Score
    cvss_scores = []
    avg_cvss = 0
    app_score = 100
    for _, finding in findings.items():
        if 'cvss' in finding:
            if finding['cvss'] != 0:
                cvss_scores.append(finding['cvss'])
        if finding['level'] == Level.high.value:
            app_score = app_score - 15
        elif finding['level'] == Level.warning.value:
            app_score = app_score - 10
        elif finding['level'] == Level.good.value:
            app_score = app_score + 5
    if cvss_scores:
        avg_cvss = round(sum(cvss_scores) / len(cvss_scores), 1)
    if app_score < 0:
        app_score = 10
    elif app_score > 100:
        app_score = 100

    return avg_cvss, app_score


def update_scan_timestamp(scan_hash):
    # Update the last scan time.
    tms = timezone.now()
    RecentScansDB.objects.filter(MD5=scan_hash).update(TIMESTAMP=tms)


def open_firebase(url):
    # Detect Open Firebase Database
    try:
        purl = urlparse(url)
        base_url = '{}://{}/.json'.format(purl.scheme, purl.netloc)
        proxies, verify = upstream_proxy('https')
        headers = {
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
                           ' AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/39.0.2171.95 Safari/537.36')}
        resp = requests.get(base_url, headers=headers,
                            proxies=proxies, verify=verify)
        if resp.status_code == 200:
            return base_url, True
    except Exception:
        logger.warning('Open Firebase DB detection failed.')
    return url, False


def firebase_analysis(urls):
    # Detect Firebase URL
    firebase_db = []
    logger.info('Detecting Firebase URL(s)')
    for url in urls:
        if 'firebaseio.com' in url:
            returl, is_open = open_firebase(url)
            fbdic = {'url': returl, 'open': is_open}
            if fbdic not in firebase_db:
                firebase_db.append(fbdic)
    return firebase_db
