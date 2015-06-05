__author__ = 'ethan'
import sqlite3
import xml.etree.ElementTree as ET
import themeConvert.fileFormats


class ThemeDB(object):
    def __init__(self, db_filename):
        self._conn = sqlite3.connect(db_filename)
        self._conn.row_factory = sqlite3.Row
        self._c = self._conn.cursor()
        self._freeze_cursor = False
        self._error_handlers = {'table theme already exists': 'DELETE FROM theme;'}
        self.execute('''CREATE TABLE theme (selector text);''')
        self.commit()

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def execute(self, *args):
        try:
            self._c.execute(*args)
        except sqlite3.OperationalError as _e:
            try:
                self._c.execute(self._error_handlers[_e.message])
            except KeyError:
                raise sqlite3.OperationalError(_e)

    def iter_cursor(self):
        self._freeze_cursor = True
        for row in self._c:
            yield row
        self._freeze_cursor = False

    def iter_cursor_to_dict(self):
        self._freeze_cursor = True
        for row in self._c:
            yield dict(zip(self.columns, row))
        self._freeze_cursor = False

    def init_columns(self, *columns):
        for a in columns:
            if a not in self.columns:
                self.execute('''ALTER TABLE theme ADD COLUMN ''' + a + ";")
                self.commit()

    @property
    def columns(self):
        if not self._freeze_cursor:
            self.execute('''SELECT * FROM theme;''')
        return tuple(i[0] for i in self._c.description)


class ICLSdb(themeConvert.fileFormats.ICLSProcessor):
    def __init__(self, db_filename):
        self._theme_db = ThemeDB(db_filename)

    def yield_table(self):
        self._theme_db.execute('''SELECT * FROM theme;''')
        for row in self._theme_db.iter_cursor():
            yield row

    def yield_table_dicts(self):
        self._theme_db.execute('''SELECT * FROM theme;''')
        for row_dict in self._theme_db.iter_cursor_to_dict():
            yield row_dict

    def yield_entries(self, xml_str):
        root = ET.fromstring(xml_str)
        attrs_root = root.find('attributes')
        for child in attrs_root:
            child_name = child.get('name')

            prop_dict = dict((sc.get('name'), sc.get('value')) for sc in child.findall('./value/option'))

            self.write_props({'selector': child_name, 'props': prop_dict})

    def write_props(self, result_dict):
        entry_k_list = ['selector']
        entry_v_list = [result_dict['selector']]
        for k, v in result_dict['props'].items():
            entry_k_list.append(k)
            entry_v_list.append(v)
        key_tuple = tuple(entry_k_list)
        value_tuple = tuple(entry_v_list)
        slot_str = '(?' + ',?' * (len(entry_v_list) - 1) + ')'
        self._theme_db.init_columns(*key_tuple)
        self._theme_db.execute(str("INSERT INTO theme " + repr(key_tuple) + " VALUES " + slot_str), value_tuple)
        self._theme_db.commit()