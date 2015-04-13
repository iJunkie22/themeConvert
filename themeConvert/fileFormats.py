__author__ = 'ethan'
import re
import xml.etree.ElementTree as ET


class GenericFormat(object):
    def __init__(self):
        pass


class CSSProcessor(object):
    selectors = ['markup.tag.attribute.name',
                 'markup.tag.attribute.value',
                 'markup.comment',
                 'markup.constant.entity',
                 'markup.inline.cdata',
                 'markup.tag',
                 'comment',
                 'keyword',
                 'string',
                 'style.comment',
                 'style.value.color.rgb-value',
                 'style.at-rule',
                 'style.value.numeric',
                 'style.property.name',
                 'style.value.string',
                 'meta.important',
                 'style.value.keyword',
                 'meta.default',
                 'language.operator',
                 'keyword.type',
                 'language.function',
                 'constant.numeric',
                 'support']
    attributes = ['color',
                  'background-color']
    entry_pat = re.compile('(?P<selector>[a-zA-Z.]+)\s\{\n(?P<props>(.*;\n)+)\}', re.M)
    prop_pat = re.compile('(?:\s*)(?P<attr>[a-zA-Z-]+)\s*:\s*(?P<value>.*);\n', re.M)

    def __init__(self):
        pass

    @classmethod
    def yield_entries(cls, text):
        for match in cls.entry_pat.finditer(text):
            result_dict = dict()
            for prop_match in cls.prop_pat.finditer(match.groupdict()['props']):
                result_dict[prop_match.groupdict()['attr']] = prop_match.groupdict()['value']

            yield {'selector': match.groupdict()['selector'], 'props': result_dict}

    @classmethod
    def to_string(cls, style_dict):
        output_str = "%s {" % style_dict['selector']
        for k, v in style_dict['props'].items():
            output_str += "\n  %s:%s;" % (k, v)
        output_str += "\n}\n"
        return output_str


class ICLSProcessor(object):
    selectors = ['HTML_ATTRIBUTE_NAME',
                 'HTML_ATTRIBUTE_VALUE',
                 'HTML_COMMENT',
                 'HTML_ENTITY_REFERENCE',
                 'HTML_TAG',
                 'HTML_TAG_NAME',
                 'DEFAULT_BLOCK_COMMENT',
                 'DEFAULT_KEYWORD',
                 'DEFAULT_STRING',
                 'CSS.COMMENT',
                 'CSS.COLOR',
                 'CSS.KEYWORD',
                 'CSS.NUMBER',
                 'CSS.PROPERTY_NAME',
                 'CSS.STRING',
                 'CSS.IMPORTANT',
                 'CSS.IDENT',
                 'TEXT',
                 'DEFAULT_OPERATION_SIGN',
                 'Type parameter',
                 'DEFAULT_FUNCTION_DECLARATION',
                 'Number',
                 'DEFAULT_INSTANCE_FIELD']
    attributes = ['FOREGROUND',
                  'BACKGROUND',
                  'FONT_TYPE']

    def __init__(self):
        pass

    @classmethod
    def yield_entries(cls, xml_str):
        root = ET.fromstring(xml_str)
        attrs_root = root.find('attributes')
        for child in attrs_root:
            if child.get('name') not in cls.selectors:
                continue
            child_name = CSSProcessor.selectors[cls.selectors.index(child.get('name'))]

            result_dict = dict()
            for sub_child in child.findall('./value/option'):
                k, v = sub_child.get('name'), sub_child.get('value')
                if k not in cls.attributes:
                    continue
                if k == 'FOREGROUND' or k == 'BACKGROUND':
                    k = CSSProcessor.attributes[cls.attributes.index(k)]
                    v = '#' + v

                if k == 'FONT_TYPE':
                    k, v = [('font-weight', 'normal'),
                            ('font-weight', 'bold'),
                            ('font-style', 'italic')][int(v)]

                result_dict[k] = v

            yield {'selector': child_name, 'props': result_dict}