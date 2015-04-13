__author__ = 'ethan'
# This demonstrates basic usage to convert WebStorm format to Coda2

import themeConvert.fileFormats as TC
import cStringIO
import os.path

repo_root = os.path.dirname(__file__)
samples_d = os.path.join(repo_root, 'Samples')
sample_icls = os.path.join(samples_d, 'FireFox DE.icls')
sample_sss = os.path.join(samples_d, 'FirefoxDE.sss')

icls_buf = cStringIO.StringIO()
sss_buf = cStringIO.StringIO()

sss_fd = open(sample_sss, 'w')

icls_fd = open(sample_icls, 'r')
try:
    for icls_line in icls_fd:
        icls_buf.write(icls_line)

    for sss_line in TC.ICLSProcessor.yield_entries(icls_buf.getvalue()):
        sss_fd.write(TC.CSSProcessor.to_string(sss_line))

finally:
    icls_fd.close()
    sss_fd.close()
    sss_buf.close()
    icls_buf.close()