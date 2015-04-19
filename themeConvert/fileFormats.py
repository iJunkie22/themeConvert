__author__ = 'ethan'
import re
import xml.etree.ElementTree as ET
import plistlib
import ast


class GenericFormat(object):
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
                 'meta.link',
                 'meta.default',
                 'language.operator',
                 'keyword.type',
                 'language.function',
                 'constant.numeric',
                 'support',
                 'constant.numeric.keyword',
                 'keyword.control']

    attributes = ['fg_color',
                  'bg_color',
                  'bold',
                  'italic',
                  'underline']

    def __init__(self):
        pass


class SmartFormat(object):
    def __init__(self):
        self._root = ET.Element('smart_format')
        self._selectors = []

    def add_selector(self, result_dict):
        sub_root = ET.Element('props', {'selector': result_dict['selector']})

        for k, v in result_dict['props'].items():
            new_el = ET.Element('option', {'name': k, 'value': str(v)})
            sub_root.append(new_el)

        self._root.append(sub_root)
        self._selectors.append(result_dict['selector'])

    def findall(self, xpath):
        for x in self._root.findall(xpath):
            yield x

    def query_selector(self, selector):
        o_dict = dict()
        for o_el in self._root.findall("./props[@selector='%s']/option" % selector):
            try:
                o_dict[o_el.get('name')] = ast.literal_eval(o_el.get('value'))
            except SyntaxError:
                o_dict[o_el.get('name')] = o_el.get('value')
        return o_dict

    def query_style(self, style_dict):
        query_list = ['./props']
        kc = len(style_dict.keys())

        for k, v in style_dict.items():
            query_list.append("/option[@name='%s'][@value='%s'].." % (k, v))

        for s in self.findall("".join(query_list)):
            if kc > 0 or len(s) == 0:   # This keeps greedy matches away
                yield s.get('selector')

    @property
    def selectors(self):
        return self._selectors

    @property
    def root_xml_string(self):
        return ET.tostring(self._root)


class SSSProcessor(object):
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
                 'meta.link',
                 'meta.default',
                 'language.operator',
                 'keyword.type',
                 'language.function',
                 'constant.numeric',
                 'support',
                 'constant.numeric.keyword',
                 'keyword.control']
    attributes = ['color',
                  'background-color']

    entry_pat = re.compile('(?P<selector>[a-zA-Z.]+)\s\{\n(?P<props>(.*;\n)+)\}', re.M)
    prop_pat = re.compile('(?:\s*)(?P<attr>[a-zA-Z-]+)\s*:\s*(?P<value>.*);\n', re.M)

    def __init__(self):
        pass

    @classmethod
    def yield_entries(cls, text):
        for match in cls.entry_pat.finditer(text):
            prop_dict = dict()
            for prop_match in cls.prop_pat.finditer(match.groupdict()['props']):
                prop_dict[prop_match.groupdict()['attr']] = prop_match.groupdict()['value']

            yield cls.write_props({'selector': match.groupdict()['selector'], 'props': prop_dict})

    @classmethod
    def to_string(cls, style_dict):
        style_dict = cls.read_props(style_dict)
        output_str = "%s {" % style_dict['selector']
        for k, v in style_dict['props'].items():
            output_str += "\n  %s:%s;" % (k, v)
        output_str += "\n}\n"
        return output_str

    @classmethod
    def read_props(cls, result_dict):
        props_dict = result_dict['props']
        new_selector = cls.selectors[GenericFormat.selectors.index(result_dict['selector'])]
        new_prop_dict = dict()
        for k, v in props_dict.items():
            if k == 'fg_color':
                # expect #a3a3a3 format
                new_prop_dict['color'] = v
                continue
            if k == 'bg_color':
                # expect #a3a3a3 format
                new_prop_dict['background-color'] = v
                continue
            if k == 'bold':
                # expect a boolean
                new_prop_dict['font-weight'] = ('normal', 'bold')[int(v)]
                continue
            if k == 'italic':
                # expect a boolean
                new_prop_dict['font-style'] = ('normal', 'italic')[int(v)]
                continue
            if k == 'underline':
                # expect a boolean
                new_prop_dict['font-underline'] = ('none', 'underline')[int(v)]
                continue
        return {'selector': new_selector, 'props': new_prop_dict}

    @classmethod
    def write_props(cls, result_dict):
        props_dict = result_dict['props']
        try:
            new_selector = GenericFormat.selectors[cls.selectors.index(result_dict['selector'])]
        except ValueError:
            new_selector = result_dict['selector']

        new_prop_dict = dict()
        for k, v in props_dict.items():
            if k == 'color':
                # expect #a3a3a3 format
                new_prop_dict['fg_color'] = v.upper()
                continue
            if k == 'background-color':
                # expect #a3a3a3 format
                new_prop_dict['bg_color'] = v.upper()
                continue
            if k == 'font-weight':
                # expect a boolean
                new_prop_dict['bold'] = bool(('normal', 'bold').index(v))
                continue
            if k == 'font-style':
                # expect a boolean
                new_prop_dict['italic'] = bool(('normal', 'italic').index(v))
                continue
            if k == 'font-underline':
                # expect a boolean
                new_prop_dict['underline'] = bool(('none', 'underline').index(v))
                continue
        return {'selector': new_selector, 'props': new_prop_dict}


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
                 'CSS.URL',
                 'TEXT',
                 'DEFAULT_OPERATION_SIGN',
                 'Type parameter',
                 'DEFAULT_FUNCTION_DECLARATION',
                 'Number',
                 'DEFAULT_INSTANCE_FIELD',
                 'constant.numeric.keyword',
                 'keyword.control']
    attributes = ['FOREGROUND',
                  'BACKGROUND',
                  'FONT_TYPE',
                  'EFFECT_TYPE',
                  'EFFECT_COLOR']

    @classmethod
    def yield_entries(cls, xml_str):
        root = ET.fromstring(xml_str)
        attrs_root = root.find('attributes')
        for child in attrs_root:
            if child.get('name') not in cls.selectors:
                continue
            child_name = child.get('name')

            prop_dict = dict()
            for sub_child in child.findall('./value/option'):
                k, v = sub_child.get('name'), sub_child.get('value')
                if k not in cls.attributes:
                    continue

                prop_dict[k] = v

            yield cls.write_props({'selector': child_name, 'props': prop_dict})

    @classmethod
    def to_string(cls, style_dict):
        return ET.tostring(cls.to_element(style_dict))

    @classmethod
    def to_element(cls, style_dict):
        style_dict = cls.read_props(style_dict)
        root = ET.Element('option', {'name': style_dict['selector']})
        sub_root = ET.Element('value')

        for k, v in style_dict['props'].items():
            new_el = ET.Element('option', {'name': k, 'value': str(v)})
            sub_root.append(new_el)

        root.append(sub_root)
        return root

    @classmethod
    def read_props(cls, result_dict):
        props_dict = result_dict['props']
        new_selector = cls.selectors[GenericFormat.selectors.index(result_dict['selector'])]
        new_prop_dict = dict()

        if 'bold' in props_dict.keys() or 'italic' in props_dict.keys():
            new_prop_dict['FONT_TYPE'] = 0

        for k, v in props_dict.items():
            if k == 'fg_color':
                # expect #a3a3a3 format
                new_prop_dict['FOREGROUND'] = v.strip('#')
                continue
            if k == 'bg_color':
                # expect #a3a3a3 format
                new_prop_dict['BACKGROUND'] = v.strip('#')
                continue
            if k == 'bold' and v:
                # expect a boolean
                new_prop_dict['FONT_TYPE'] += 1
                continue
            if k == 'italic' and v:
                # expect a boolean
                new_prop_dict['FONT_TYPE'] += 2
                continue
            if k == 'underline':
                # expect a boolean
                new_prop_dict['font-underline'] = ('none', 'underline')[int(v)]
                continue
        return {'selector': new_selector, 'props': new_prop_dict}

    @classmethod
    def write_props(cls, result_dict):
        props_dict = result_dict['props']
        new_selector = GenericFormat.selectors[cls.selectors.index(result_dict['selector'])]
        new_prop_dict = dict()
        for k, v in props_dict.items():
            if k == 'FOREGROUND':
                # expect a3a3a3 format
                new_prop_dict['fg_color'] = '#' + v
                continue

            if k == 'BACKGROUND':
                # expect a3a3a3 format
                new_prop_dict['bg_color'] = '#' + v
                continue

            if k == 'FONT_TYPE':
                v = int(v)
                # expect an int
                if v == 0:
                    new_prop_dict['bold'] = False
                    continue

                if v == 1 or v == 3:
                    new_prop_dict['bold'] = True

                if v == 2 or v == 3:
                    new_prop_dict['italic'] = True

            if k == 'EFFECT_TYPE':
                v = int(v)
                # expect an int
                if v == 1 or v == 4:
                    new_prop_dict['underline'] = False

        return {'selector': new_selector, 'props': new_prop_dict}


class TmThemeProcessor(object):
    selectors = ['markup.tag.attribute.name',
                 'markup.tag.attribute.value',
                 'markup.comment',
                 'markup.constant.entity',
                 'markup.inline.cdata',
                 'meta.tag',
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
                 'meta.link',
                 'meta.default',
                 'language.operator',
                 'keyword.type',
                 'language.function',
                 'constant.numeric',
                 'support',
                 'constant.numeric.keyword',
                 'keyword.control']

    @classmethod
    def yield_entries(cls, plist_string):
        pl_root = plistlib.readPlistFromString(plist_string)
        for entry in dict(pl_root).get('settings'):
            try:
                for scope in entry['scope'].split(','):
                    result_dict = cls.write_props({'selector': scope, 'props': entry['settings']})
                    yield result_dict

            except KeyError:
                try:
                    result_dict = cls.write_props({'selector': 'settings', 'props': entry['settings']})
                    yield result_dict
                except KeyError:
                    pass

    @classmethod
    def to_string(cls, style_dict):
        return str()

    @classmethod
    def read_props(cls, result_dict):
        props_dict = result_dict['props']
        try:
            new_selector = cls.selectors[GenericFormat.selectors.index(result_dict['selector'])]
        except ValueError:
            new_selector = result_dict['selector']

        new_prop_dict = dict()
        for k, v in props_dict.items():
            if k == 'fg_color':
                # expect #a3a3a3 format
                new_prop_dict['foreground'] = v
                continue
            if k == 'bg_color':
                # expect #a3a3a3 format
                new_prop_dict['background'] = v
                continue
            if k == 'bold' and v:
                # expect a boolean
                new_prop_dict['fontStyle'] = 'bold'
                continue
            if k == 'italic' and v:
                # expect a boolean
                new_prop_dict['fontStyle'] = 'italic'
                continue
            if k == 'underline' and v:
                # expect a boolean
                new_prop_dict['fontStyle'] = 'underline'
                continue
        return {'selector': new_selector, 'props': new_prop_dict}

    @classmethod
    def write_props(cls, result_dict):
        props_dict = result_dict['props']
        new_prop_dict = dict()
        for k, v in props_dict.items():
            if k == 'foreground':
                # expect #a3a3a3 format
                new_prop_dict['fg_color'] = v
                continue
            if k == 'background':
                # expect #a3a3a3 format
                new_prop_dict['bg_color'] = v
                continue
            if k == 'fontStyle' and v != '':
                # expect a string
                new_prop_dict[v] = True
                continue

        return {'selector': result_dict['selector'], 'props': new_prop_dict}

    @classmethod
    def to_scope(cls, result_dict):
        result_dict = cls.read_props(result_dict)
        return {'name': result_dict['selector'],
                'scope': result_dict['selector'],
                'settings': result_dict['props']}


class TmThemeFile(TmThemeProcessor, object):
    def __init__(self):
        self._root = {'author': '',
                      'gutterSettings': {},
                      'name': '',
                      'semanticClass': '',
                      'settings': [],
                      'uuid': ''}

    def insert_settings_dict(self, result_dict):
        if result_dict['selector'] != 'settings':
            self.settings.append(self.to_scope(result_dict))
        else:
            self.settings.append(self.read_props(result_dict))

    def query_scope(self, scope):
        for d in self.settings:
            if d.get('scope') == scope:
                yield d

    def to_plist_str(self):
        return plistlib.writePlistToString(self._root)

    @property
    def author(self):
        return self._root['author']

    @property
    def gutter_settings(self):
        return self._root['gutterSettings']

    @property
    def name(self):
        return self._root['name']

    @property
    def semantic_class(self):
        return self._root['semanticClass']

    @property
    def settings(self):
        return self._root['settings']

    @property
    def uuid(self):
        return self._root['uuid']


class ICLSFile(ICLSProcessor):
    def __init__(self, name, parent_scheme='Default'):
        # ONLY set parent_scheme if you are feeling lucky
        self.root = ET.Element('scheme', {'name': name, 'version': "1", 'parent_scheme': parent_scheme})
        self.root.append(ET.Element('colors'))
        self.root.append(ET.Element('attributes'))

    def to_xml_str(self):
        return ET.tostring(self.root).replace('><', '>\n<')

    @property
    def attribute_tree(self):
        return self.root.find('attributes')

    @property
    def colors_tree(self):
        return self.root.find('colors')

    def insert_attribute_element(self, element):
        self.attribute_tree.append(element)

    def insert_attribute_dict(self, result_dict):
        self.insert_attribute_element(self.to_element(result_dict))