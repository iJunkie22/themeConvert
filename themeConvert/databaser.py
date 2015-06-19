__author__ = 'ethan'
import sqlite3
import xml.etree.ElementTree as ET
import themeConvert.fileFormats


def _execute(cursor, *args):
    assert isinstance(cursor, sqlite3.Cursor)
    cursor.execute(*args)
    return cursor


class ThemeDB(object):
    def __init__(self, db_filename, overwrite=True):
        self._conn = sqlite3.connect(db_filename)
        self._conn.row_factory = sqlite3.Row
        self._c = self._conn.cursor()
        self._c2 = self._conn.cursor()
        self._freeze_cursor = False
        self._table_names = set()
        self._tables = {}
        self._tables_view_keys = self._tables.viewkeys()
        if overwrite:
            self._tables_to_replace = ['theme']
        self.execute('''CREATE TABLE IF NOT EXISTS theme (selector text UNIQUE);''')
        self.commit()

    def close(self):
        self._conn.close()

    def commit(self):
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
        self._freeze_cursor = True
        c_columns = tuple(i[0] for i in self._c.description)
        for row in self._c:
            yield dict(zip(c_columns, row))
        self._freeze_cursor = False

    def insert_dict_as_row(self, input_dict, table_name):
        self.get_table(table_name).insert_dict_as_row(input_dict)

    def select_all_from_table(self, table_name):
        self.get_table(table_name).select_all()

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
        self._db.execute("SELECT * FROM %s;" % self.name)

    def init_columns(self, *columns):
        c_l = self.columns
        for a in set(columns) - c_l:
            self.add_column(a)
            self._db.commit()

    def insert_dict_as_row(self, input_dict):
        assert isinstance(input_dict, dict)
        k_view = input_dict.viewkeys()
        v_view = input_dict.viewvalues()
        slot_str = '(?' + (',?' * (len(v_view) - 1)) + ')'

        self.init_columns(*k_view)

        self._db.execute(str("INSERT OR REPLACE INTO %s %s VALUES %s;") %
                            (self.name, repr(tuple(k_view)), slot_str), tuple(v_view))

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
    def __init__(self):
        self._theme_db = None

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
        self._theme_db.select_all_from_table(table_name)
        for row_dict in self._theme_db.iter_cursor_to_dict():
            yield row_dict

    def write_props(self, result_dict):
        assert isinstance(self._theme_db, ThemeDB)
        self._theme_db.insert_dict_as_row(result_dict['props'], result_dict['table'])


class ICLSdb(Miscdb, themeConvert.fileFormats.ICLSProcessor):
    def __init__(self, db_filename):
        self._theme_db = ThemeDB(db_filename)
        self._theme_db.execute('''CREATE TABLE IF NOT EXISTS attributes (selector text UNIQUE);''')
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
            self.write_props({'props': prop_dict, 'table': 'attributes'})
        self._theme_db.commit()


class SSSdb(Miscdb, themeConvert.fileFormats.SSSProcessor):
    def __init__(self, db_filename):
        self._theme_db = ThemeDB(db_filename)
        self._theme_db.commit()

    def yield_entries(self, text):
        for match in self.entry_pat.finditer(text):
            prop_dict = {}
            for prop_match in self.prop_pat.finditer(match.groupdict()['props']):
                prop_dict[str(prop_match.groupdict()['attr']).replace('-', '_')] = prop_match.groupdict()['value']
            prop_dict['selector'] = match.groupdict()['selector']
            self.write_props({'props': prop_dict, 'table': 'theme'})
        self._theme_db.commit()

