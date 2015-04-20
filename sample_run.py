__author__ = 'ethan'
# This demonstrates basic usage to convert WebStorm format to Coda2

import themeConvert.fileFormats as TC
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
sample_icls2 = os.path.join(samples_d, 'FireFox DE2.icls')      # ./Samples/FireFox DE2.icls
sample_icls3 = os.path.join(samples_d, 'Clouds Midnight.icls')      # ./Samples/Clouds Midnight.icls
sample_sss = os.path.join(samples_d, 'FirefoxDE.sss')           # ./Samples/FirefoxDE.sss
sample_tmtheme = os.path.join(samples_d, 'Clouds Midnight.tmTheme')  # ./Samples/Clouds Midnight.tmTheme
sample_sss2 = os.path.join(samples_d, 'Clouds Midnight.sss')         # ./Samples/Clouds Midnight.sss

smart_format = TC.SmartFormat()
smart_format2 = TC.SmartFormat()

icls_buf = buffer_file(sample_icls)
sss_buf = buffer_file(sample_sss)
sss_buf2 = buffer_file(sample_sss2)
tmtheme_buf = buffer_file(sample_tmtheme)

sss_fd = open(sample_sss, 'w')

icls_fd2 = open(sample_icls2, 'w')

icls_fd3 = open(sample_icls3, 'w')

new_icls = TC.ICLSFile('FireFox DE2', parent_scheme='Darcula')
new_icls3 = TC.ICLSFile('Clouds Midnight', parent_scheme='Darcula')

try:

    for generic_line in TC.ICLSProcessor.yield_entries(icls_buf):
        new_icls.insert_attribute_dict(generic_line)
        sss_fd.write(TC.SSSProcessor.to_string(generic_line))

    icls_fd2.write(new_icls.to_xml_str())

    for gen_sss_line in TC.SSSProcessor.yield_entries(sss_buf2):
        smart_format2.add_selector(gen_sss_line)

    for gen_tmtheme_line2 in TC.TmThemeProcessor.yield_entries(tmtheme_buf):
        smart_format.add_selector(gen_tmtheme_line2)
        new_icls3.insert_attribute_dict(gen_tmtheme_line2)
        pass

    icls_fd3.write(new_icls3.to_xml_str())
    # print smart_format.query_selector('style.at-rule')
    tm_selectors = dict()
    for x in smart_format.selectors:
        tm_selectors[x] = []
        y = smart_format.query_selector(x)
        print "Query Selector:      ", x
        print "Query Style:         ", y
        for z in smart_format2.query_style(y):
            tm_selectors[x].append(z)
            print "Matched Selector:    ", z

        print "=" * 50
        #for z in smart_format.query_style(y):
        #    print z
    print tm_selectors



finally:
    icls_fd2.close()
    icls_fd3.close()
    sss_fd.close()