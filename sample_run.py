__author__ = 'ethan'
# This demonstrates basic usage to convert WebStorm format to Coda2

import themeConvert.fileFormats as TC
import cStringIO
import os.path

repo_root = os.path.dirname(__file__)                           # .
samples_d = os.path.join(repo_root, 'Samples')                  # ./Samples
sample_icls = os.path.join(samples_d, 'FireFox DE.icls')        # ./Samples/FireFox DE.icls
sample_icls2 = os.path.join(samples_d, 'FireFox DE2.icls')      # ./Samples/FireFox DE2.icls
sample_sss = os.path.join(samples_d, 'FirefoxDE.sss')           # ./Samples/FirefoxDE.sss
sample_tmtheme = os.path.join(samples_d, 'Blackboard.tmTheme')  # ./Samples/Blackboard.tmTheme
sample_sss2 = os.path.join(samples_d, 'Blackboard.sss')           # ./Samples/Blackboard.sss

smart_format = TC.SmartFormat()
smart_format2 = TC.SmartFormat()

icls_buf = cStringIO.StringIO()
sss_buf = cStringIO.StringIO()
sss_buf2 = cStringIO.StringIO()
tmtheme_buf = cStringIO.StringIO()

sss_fd = open(sample_sss, 'w')
sss_fd2 = open(sample_sss2, 'r')

tmtheme_fd = open(sample_tmtheme, 'r')

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

    for tmtheme_line1 in tmtheme_fd:
        tmtheme_buf.write(tmtheme_line1)

    for sss_line1 in sss_fd2:
        sss_buf2.write(sss_line1)

    for gen_sss_line in TC.SSSProcessor.yield_entries(sss_buf2.getvalue()):
        smart_format2.add_selector(gen_sss_line)

    for gen_tmtheme_line2 in TC.TmThemeProcessor.yield_entries(tmtheme_buf.getvalue()):
        smart_format.add_selector(gen_tmtheme_line2)
        pass
    # print smart_format.query_selector('style.at-rule')
    for x in smart_format.selectors:
        #print x
        y = smart_format.query_selector(x)
        #print y
        print "=" * 10, x, "=" * 10
        for z in smart_format2.query_style(y):
            print z

        print "=" * 50
        #for z in smart_format.query_style(y):
        #    print z

finally:
    icls_fd.close()
    icls_fd2.close()
    sss_fd.close()
    sss_buf.close()
    sss_buf2.close()
    sss_fd2.close()
    icls_buf.close()
    tmtheme_fd.close()
    tmtheme_buf.close()