__author__ = 'ethan'
import themeConvert.databaser
import cStringIO
import os.path
import collections


def buffer_file(fp):
    new_buf = cStringIO.StringIO()
    new_fd = open(fp, 'r')
    try:
        for line in new_fd:
            new_buf.write(line)
    finally:
        new_str = new_buf.getvalue()
        new_fd.close()
        new_buf.close()
        return new_str

repo_root = os.path.dirname(__file__)                           # .
samples_d = os.path.join(repo_root, 'Samples')                  # ./Samples
sample_icls = os.path.join(samples_d, 'FireFox DE.icls')        # ./Samples/FireFox DE.icls
#sample_icls = os.path.join(samples_d, 'Twilight2.icls')        # ./Samples/FireFox DE.icls
sample_sss = os.path.join(samples_d, 'FirefoxDE.sss')           # ./Samples/FirefoxDE.sss

sample_icls_db = os.path.join(samples_d, 'FireFox DE.db')        # ./Samples/FireFoxDE.db
#sample_icls_db = os.path.join(samples_d, 'Twilight2.db')        # ./Samples/FireFoxDE.db
sample_smart_db = os.path.join(samples_d, 'SmartFormat.db')      # ./Samples/SmartFormat.db

def db_test1(db=None, icls=None, sss=None):
    fp_dict = {'db': os.path.join(samples_d, db),
               'icls': [os.path.join(samples_d, icls)] if icls else [],
               'sss': [os.path.join(samples_d, sss)] if sss else []
               }
    for icls_fp in fp_dict['icls']:
        icls_buf = buffer_file(icls_fp)
        test_db1 = themeConvert.databaser.ICLSdb(fp_dict['db'])
        test_db1.yield_entries(icls_buf)
        test_db1.close()

    for sss_fp in fp_dict['sss']:
        sss_buf = buffer_file(sss_fp)
        test_db1 = themeConvert.databaser.SSSdb(fp_dict['db'])
        test_db1.yield_entries(sss_buf, preserve=False)
        test_db1.close()

    test_db2 = themeConvert.databaser.Miscdb(fp_dict['db'])
    for line in test_db2.yield_table_dicts('theme'):
        print line

def db_test2(db1=None, db2=None):
    fp_dict = {'db1': os.path.join(samples_d, db1),
               'db2': os.path.join(samples_d, db2)
               }

    test_db1 = themeConvert.databaser.Miscdb(fp_dict['db1'])
    lines = []
    for line in test_db1.yield_table_dicts('theme'):
        lines.append(line)

    test_db2 = themeConvert.databaser.SmartFormatdb(fp_dict['db2'])
    test_db2.add_selector_many(*lines)
    for line in test_db2.yield_table_dicts('theme1'):
        print line


db_test1(icls='FireFox DE.icls', sss='FirefoxDE.sss', db='FireFox DE.db')
db_test2(db1='FireFox DE.db', db2='SmartDB.db')
