__author__ = 'ethan'
import themeConvert.databaser
import cStringIO
import os.path


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
sample_sss = os.path.join(samples_d, 'FirefoxDE.sss')           # ./Samples/FirefoxDE.sss
sample_icls_db = os.path.join(samples_d, 'FireFox DE.db')        # ./Samples/FireFoxDE.db

icls_buf = buffer_file(sample_icls)
test_db1 = themeConvert.databaser.ICLSdb(sample_icls_db)
test_db1.yield_entries(icls_buf)
test_db1.close()

sss_buf = buffer_file(sample_sss)

test_db2 = themeConvert.databaser.SSSdb(sample_icls_db)
test_db2.yield_entries(sss_buf)

for line in test_db2.yield_table_dicts():
    print line

