__author__ = 'ethan'
import sqlite3
import xml.etree.ElementTree as ET
import themeConvert.fileFormats


def _execute(cursor, *args):
    assert isinstance(cursor, sqlite3.Cursor)
    cursor.execute(*args)
    return cursor

class BetterCursor(sqlite3.Cursor):
    def iter_dicts(self):
        c_columns = tuple(i[0] for i in self.description)
        for row in self:
            yield {k: v for (k, v) in zip(c_columns, row)}


class ThemeDB(object):
    def __init__(self, db_filename, overwrite=True):
        self._conn = sqlite3.connect(db_filename)
        self._conn.row_factory = sqlite3.Row
        self._c = self._conn.cursor(BetterCursor)
        self._c2 = self._conn.cursor(BetterCursor)
        assert isinstance(self._c, BetterCursor)
        self._freeze_cursor = False
        self._table_names = set()
        self._tables = {}
        self._tables_view_keys = self._tables.viewkeys()
        if overwrite:
            self._tables_to_replace = ['theme']
        self.execute('''CREATE TABLE IF NOT EXISTS theme (selector text UNIQUE);''')
        self.write_buffer_values = []
        self.write_buffer_command = None
        self.commit()

    def close(self):
        self._conn.close()

    def commit(self):
        self.flush()
        self._conn.commit()
        assert not self.frozen
        self.update('table_names')
        self.update('tables')

    def execute(self, *args):
        _cur = self._c2 if self.frozen else self._c
        _execute(_cur, *args)
        return _cur

    def get_table(self, table_name):
        t1 = self.tables[table_name]
        assert isinstance(t1, Table)
        return t1

    def iter_cursor(self):
        self._freeze_cursor = True
        for row in self._c:
            yield row
        self._freeze_cursor = False

    def iter_cursor_to_dict(self):
        assert isinstance(self._c, BetterCursor)
        self._freeze_cursor = True
        for r in self._c.iter_dicts():
            yield r
        self._freeze_cursor = False

    def insert_dict_as_row(self, input_dict, table_name):
        self.get_table(table_name).insert_dict_as_row(input_dict)

    def select_all_from_table(self, table_name):
        return self.get_table(table_name).select_all()

    def update(self, *args):
        def table_names_():
            assert isinstance(self, ThemeDB)
            self._table_names = set(str(i[0]) for i in
                                    self.execute("SELECT name FROM sqlite_master WHERE type='table';"))

        def tables_():
            assert isinstance(self, ThemeDB)
            self._tables.update((t, Table(self, t)) for t in self._table_names)

        _functs = {'table_names': table_names_, 'tables': tables_}
        self.frozen = True
        for valid_call in _functs.viewkeys() & set(args):
            _functs[valid_call].__call__()
        self.frozen = False

    def flush(self):
        """
        Flush the buffer.

        Buffer implementation usually improves efficiency by ~ 20%!
        """
        try:
            assert isinstance(self.write_buffer_command, str)
            assert len(self.write_buffer_values) > 0
            self._c.executemany(self.write_buffer_command, self.write_buffer_values)
            self.write_buffer_values = []
            self.write_buffer_command = None
        except AssertionError:
            pass

    @property
    def frozen(self):
        """
        Is the cursor frozen?
        :rtype : bool
        """
        return self._freeze_cursor

    @frozen.setter
    def frozen(self, value):
        """
        Freeze cursor1 and use cursor2 instead
        :type value: bool
        """
        assert isinstance(value, bool)
        self._freeze_cursor = value

    @property
    def table_names(self):
        try:
            self.frozen = True
            self._table_names.clear()
            self._table_names |= set(str(i[0]) for i in
                                     self.execute("SELECT name FROM sqlite_master WHERE type='table';"))
        finally:
            self.frozen = False
        return self._table_names

    @property
    def tables(self):
        return self._tables


class Table(object):
    """
    convenient class to bind common methods and properties of an SQLite table
    """
    def __init__(self, theme_db, name):
        assert isinstance(theme_db, ThemeDB)
        assert isinstance(name, str)
        self._db = theme_db
        self.__name = name
        self._column_cache = set()

    def clear(self):
        """
        Delete all rows in this table.
        """
        self._db.execute("DELETE FROM %s;" % self.name)

    def select_all(self):
        """
        Select all rows in this table.
        """
        return self._db.execute("SELECT * FROM %s;" % self.name)

    def init_columns(self, *columns):
        changes = 0
        c_l = self.columns
        for a in set(columns) - c_l:
            self.add_column(a)
            self._db.commit()
            changes += 1
        return bool(changes % 2)

    def insert_dict_as_row(self, input_dict):
        assert isinstance(input_dict, dict)
        k_view = input_dict.viewkeys()
        v_view = input_dict.viewvalues()
        slot_str = '(?' + (',?' * (len(v_view) - 1)) + ')'

        new_cols = self.init_columns(*k_view)
        sql_str = str("INSERT OR REPLACE INTO %s %s VALUES %s;") % (self.name, repr(tuple(k_view)), slot_str)

        if not new_cols and sql_str == self._db.write_buffer_command:
            self._db.write_buffer_values.append(tuple(v_view))

        else:
            self._db.flush()
            self._db.execute(sql_str, tuple(v_view))

        self._db.write_buffer_command = sql_str

    def add_column(self, column, type_name=None):
        """
        Add a column to this table

        :param column: The name of the new column.
        :param type_name: Optional. Specify the SQLite type for the new column.
        """
        assert isinstance(column, str)
        assert type_name is None or isinstance(type_name, str)
        self._db.execute("ALTER TABLE %s ADD COLUMN %s;" %
                         (self.name, " ".join([column, type_name]) if type_name else column))

    @property
    def name(self):
        return self.__name

    @property
    def columns(self):
        if not self._db.frozen:
            self._column_cache = {str(i[1]) for i in self._db.execute("PRAGMA table_info('%s');" % self.name)}
        return self._column_cache

class Miscdb:
    def __init__(self, db_filename):
        self._theme_db = ThemeDB(db_filename)

    def close(self):
        assert isinstance(self._theme_db, ThemeDB)
        self._theme_db.close()

    def yield_table(self, table_name):
        assert isinstance(self._theme_db, ThemeDB)
        self._theme_db.select_all_from_table(table_name)
        for row in self._theme_db.iter_cursor():
            yield row

    def yield_table_dicts(self, table_name):
        assert isinstance(self._theme_db, ThemeDB)
        for row_dict in self._theme_db.select_all_from_table(table_name).iter_dicts():
            yield row_dict

    def write_props(self, result_dict):
        assert isinstance(self._theme_db, ThemeDB)
        self._theme_db.insert_dict_as_row(result_dict['props'], result_dict['table'])


class ICLSdb(Miscdb, themeConvert.fileFormats.ICLSProcessor):
    def __init__(self, db_filename):
        self._theme_db = ThemeDB(db_filename)
        self._theme_db.execute('''CREATE TABLE IF NOT EXISTS attributes (selector text UNIQUE);''')
        self._theme_db.execute('''CREATE TABLE IF NOT EXISTS attributes_conformed (selector text UNIQUE);''')
        self._theme_db.execute('''CREATE TABLE IF NOT EXISTS colors (FILESTATUS_UNKNOWN text);''')
        self._theme_db.commit()
        self._theme_db.get_table('colors').clear()
        self._theme_db.commit()

    def yield_entries(self, xml_str):
        root = ET.fromstring(xml_str)
        colors_root = root.find('colors')
        color_prop_dict = self.n_v_dict(colors_root.findall('./option'))
        self.write_props({'props': color_prop_dict, 'table': 'colors'})

        for child in root.find('attributes'):
            prop_dict = self.n_v_dict(child.findall('./value/option'))
            prop_dict['selector'] = child.get('name')
            # self.write_props({'props': prop_dict, 'table': 'attributes'})
            self.conform(prop_dict)
            self.write_props({'props': prop_dict, 'table': 'attributes_conformed'})
        self._theme_db.commit()

    def conform(self, dict_in):
        def to_hex_str(_dict_in, _key):
            assert isinstance(_dict_in, dict)
            frmt_str = "#{:0>6}"
            temp = _dict_in.pop(_key, None)
            if temp:
                _dict_in[_key] = frmt_str.format(temp)

        for x in ['FOREGROUND', 'BACKGROUND', 'EFFECT_COLOR', 'ERROR_STRIPE_COLOR']:
            to_hex_str(dict_in, x)


class SSSdb(Miscdb, themeConvert.fileFormats.SSSProcessor):
    def __init__(self, db_filename):
        self._theme_db = ThemeDB(db_filename)
        self._theme_db.commit()

    def yield_entries(self, text, preserve=False):
        for match in self.entry_pat.finditer(text):
            prop_dict = {}
            for prop_match in self.prop_pat.finditer(match.groupdict()['props']):
                prop_dict[str(prop_match.groupdict()['attr'])] = prop_match.groupdict()['value']
            prop_dict['selector'] = match.groupdict()['selector']
            self.conform(prop_dict, preserve=preserve)
            self.write_props({'props': prop_dict, 'table': 'theme'})
        self._theme_db.commit()

    def conform(self, dict_in, preserve=False):
        def rename(_dict_in, old_key, new_key):
            assert isinstance(_dict_in, dict)
            try:
                temp = _dict_in.pop(old_key)
                _dict_in[new_key] = temp
            except KeyError:
                pass

        if preserve:
            rename(dict_in, 'font-weight', 'font_weight')
            rename(dict_in, 'font-style', 'font_style')

        else:
            bold = int(dict_in.pop('font-weight', '') == 'bold')
            italic = int(dict_in.pop('font-style', '') == 'italic') * 2
            dict_in['FONT_TYPE'] = bold + italic

        rename(dict_in, 'background-color', 'background_color')


class SmartFormatdb(Miscdb, themeConvert.fileFormats.SmartFormat):
    def __init__(self, db_filename):
        self._theme_db = ThemeDB(db_filename)
        self._theme_db.execute('''CREATE TABLE IF NOT EXISTS theme1 (selector text UNIQUE);''')
        self._theme_db.execute('''CREATE TABLE IF NOT EXISTS theme2 (selector text UNIQUE);''')
        self._theme_db.commit()
        self._selectors = set()

    def add_selector(self, result_dict):
        self.write_props({'props': result_dict, 'table': 'theme1'})
        self._theme_db.commit()

    def add_selector_many(self, *result_dicts):
        for result_dict in result_dicts:
            self.write_props({'props': result_dict, 'table': 'theme1'})
        self._theme_db.commit()

    def query_selector(self, selector):
        self._theme_db.execute("""SELECT * FROM theme1 WHERE selector='%s';""" % selector)
        for d in self._theme_db.iter_cursor_to_dict():
            yield d

    @property
    def selectors(self):
        self._theme_db.frozen = True
        self._selectors = {str(r[0]) for r in self._theme_db.execute("SELECT selector from theme1;")}
        self._theme_db.frozen = False
        return self._selectors

