#!/usr/bin/env python3
from typing import Dict

import rpm
import yaml
import os
import platform
import sys
import datetime
import logging
import logging.handlers
import psutil

loggerName = 'rpmlog'

def decode_if_bytes(element):
    ''' before rpm 4.14.2 all headers were returned as bytes '''
    if isinstance(element, bytes):
        return element.decode('utf-8')
    else:
        return element

def load_yaml(file, part):
     with open(file, 'r') as ymlfile:
         config_parameters = yaml.load(ymlfile, Loader=yaml.SafeLoader)[part]
     return config_parameters

def set_log(handler_type, socket, facility, level='INFO', stdout=False, filepath=False):
    log = logging.getLogger(loggerName)
    log.setLevel(level)
    formatter_syslog = logging.Formatter('%(module)s[%(process)d]: %(message)s')
    formatter_stdout = logging.Formatter('%(asctime)s %(module)s[%(process)d]: %(levelname)s: %(message)s')
    formatter_file   = logging.Formatter('%(asctime)s %(module)s[%(process)d]: %(message)s')

    if handler_type == 'syslog':
        handler_syslog = logging.handlers.SysLogHandler(address=socket, facility=facility)
        handler_syslog.setFormatter(formatter_syslog)
        handler_syslog.setLevel(level)
        log.addHandler(handler_syslog)
    if handler_type == 'file':
        if not filepath:
            return False
        oldumask = os.umask(0o0026)
        handler_file = logging.handlers.WatchedFileHandler(filepath, encoding='utf8')
        handler_file.setFormatter(formatter_file)
        handler_file.setLevel(level)
        log.addHandler(handler_file)
        os.umask(oldumask)
    if stdout:
        handler_out = logging.StreamHandler(sys.stdout)
        handler_out.setLevel(level)
        handler_out.setFormatter(formatter_stdout)
        log.addHandler(handler_out)
    return True


'''
Read Config
'''
# get the config from FHS conform dir
CONFIG = os.path.join(os.path.dirname("/etc/rpmlogger/"), "rpmlogger.conf")
if not os.path.isfile(CONFIG):
    # developing stage
    CONFIG = os.path.join(os.path.dirname(__file__), "etc/rpmlogger.conf")

if not os.path.isfile(CONFIG):
    # Try to copy dist file in first config file
    distconf = os.path.join(os.path.dirname(CONFIG), "rpmlogger.conf-dist")
    if os.path.isfile(distconf):
        print("First run? I don't find <rpmlogger.conf>, but <rpmlogger.conf-dist> exists. I try to rename it.")
        os.rename(distconf, os.path.join(os.path.dirname(distconf), "rpmlogger.conf"))

# get the configuration items
if os.path.isfile(CONFIG):
    logging_parameters =  load_yaml(CONFIG, "Logging")
    LOGFILE_DIR = logging_parameters['LOGFILE_DIR']
    LOGFILE_NAME = logging_parameters['LOGFILE_NAME']
    LOGSTDOUT = logging_parameters['LOGSTDOUT']
    LOGHANDLER = logging_parameters['TYPE']
    SYSLOG_FAC = logging_parameters['SYSLOG_FAC']
    SYSLOG_LEVEL = logging_parameters['LOG_LEVEL']
    SYSLOG_SOCKET = logging_parameters['SYSLOG_SOCKET']
    TAG = logging_parameters['TAG']

    pkg_parameters = load_yaml(CONFIG, "Packages")
    PKGS = pkg_parameters['NAMES']
else:
    sys.exit("Please check the config file! Config path: %s.\nHint: put a rpmlogger.conf in /etc/rpmlogger/ folder." % CONFIG)
# =============================================================================

# check if all config parameters are present
for confvar in (
        LOGFILE_DIR, LOGFILE_NAME, LOGSTDOUT, TAG,
        LOGHANDLER, SYSLOG_FAC, SYSLOG_LEVEL, SYSLOG_SOCKET, PKGS):
    if confvar is None:
        sys.exit("Please check the config file! Some parameters are missing. This is an YAML syntax file!")


if LOGHANDLER == 'file':
    LOGFILE_PATH = os.path.join(LOGFILE_DIR, LOGFILE_NAME)
    Path(LOGFILE_DIR).mkdir(exist_ok=True)
    Path(LOGFILE_PATH).touch()
else:
    LOGFILE_PATH = False

if not set_log(LOGHANDLER, SYSLOG_SOCKET, SYSLOG_FAC, SYSLOG_LEVEL, LOGSTDOUT, LOGFILE_PATH):
    print("Something wrong in log definition")
    sys.exit(1)

log = logging.getLogger(loggerName)
thishost: Dict[str, str] = {}

print("=== RPM packages logger utility ===\n")

for pkg in PKGS:
    ts = rpm.TransactionSet()
    mi = ts.dbMatch('name', pkg)
    #mi.pattern('name', rpm.RPMMIRE_GLOB, 'kernel*' )
    # you can see all header name with 'rpm --querytags'
    for h in mi:
        build_date = datetime.datetime.fromtimestamp(h['BUILDTIME'])
        install_date = datetime.datetime.fromtimestamp(h['INSTALLTID'])
        log.info('name="{}" version="{}" release="{}" build_date="{:%c}" install_date="{:%c}" group="{}" license="{}" build_host="{}" packager="{}" vendor="{}" url="{}" summary="{}" tos="{}"'.format(
            decode_if_bytes(h['name']), decode_if_bytes(h['version']), decode_if_bytes(h['release']), build_date, install_date, decode_if_bytes(h['group']),
            decode_if_bytes(h['license']), decode_if_bytes(h['buildhost']), decode_if_bytes(h['packager']), decode_if_bytes(h['vendor']), decode_if_bytes(h['url']), decode_if_bytes(h['summary']), TAG))

ncpu = os.cpu_count()
#print(platform.linux_distribution())
this = platform.uname()
thishost['plat'] = ' '.join(['{0}="{1}"'.format(k, getattr(this, k)) for k in this._fields])
try:
    this = psutil.virtual_memory()
    interesting_fields = ['total']
    thishost['mem'] = ' '.join(['mem_{0}="{1}"'.format(k, getattr(this, k)) for k in interesting_fields])
except psutil.Error:
    log.info('{} ncpu="{}" tos="{}"'.format(thishost['plat'], ncpu, TAG))
    sys.exit(1)

log.info('{} {} ncpu="{}" tos="{}"'.format(thishost['plat'], thishost['mem'], ncpu, TAG))
print("===================================")
