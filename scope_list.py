__author__ = 'ethan'
import themeConvert.fileFormats as TC

for line in list(zip(TC.GenericFormat.selectors,
                     TC.SSSProcessor.selectors,
                     TC.ICLSProcessor.selectors,
                     TC.TmThemeProcessor.selectors)):
    print line