__author__ = 'ethan'
# This demonstrates basic usage to convert WebStorm format to Coda2

import themeConvert.fileFormats as TC
import cStringIO
import os.path

repo_root = os.path.dirname(__file__)                       # .
samples_d = os.path.join(repo_root, 'Samples')              # ./Samples
sample_icls = os.path.join(samples_d, 'FireFox DE.icls')    # ./Samples/FireFox DE.icls
sample_icls2 = os.path.join(samples_d, 'FireFox DE2.icls')    # ./Samples/FireFox DE2.icls
sample_sss = os.path.join(samples_d, 'FirefoxDE.sss')       # ./Samples/FirefoxDE.sss

icls_buf = cStringIO.StringIO()
sss_buf = cStringIO.StringIO()

sss_fd = open(sample_sss, 'w')

icls_fd = open(sample_icls, 'r')
icls_fd2 = open(sample_icls2, 'w')

new_icls = TC.ICLSFile('FireFox DE2')
try:
    for icls_line in icls_fd:
        icls_buf.write(icls_line)

    for generic_line in TC.ICLSProcessor.yield_entries(icls_buf.getvalue()):
        new_icls.insert_attribute_dict(generic_line)
        sss_fd.write(TC.SSSProcessor.to_string(generic_line))

    icls_fd2.write(new_icls.xml_str)

finally:
    icls_fd.close()
    icls_fd2.close()
    sss_fd.close()
    sss_buf.close()
    icls_buf.close()