__author__ = 'ethan'
import sqlite3
import xml.etree.ElementTree as ET
import themeConvert.fileFormats


class ThemeDB(object):
    def __init__(self, db_filename, overwrite=True):
        self._conn = sqlite3.connect(db_filename)
        self._conn.row_factory = sqlite3.Row
        self._c = self._conn.cursor()
        self._freeze_cursor = False
        self._table_names = set()
        self._tables = {}
        self._tables_view_keys = self._tables.viewkeys()
        # self._selected_table = 'theme'
        if overwrite:
            self._tables_to_replace = ['theme']
        self.execute('''CREATE TABLE IF NOT EXISTS theme (selector text UNIQUE);''')
        self.commit()

    def commit(self):
        self._conn.commit()
        assert not self.frozen
        self.update('table_names')
        self.update('tables')

    def close(self):
        self._conn.close()

    def execute(self, *args):
        try:
            self._c.execute(*args)
            return self._c
        except sqlite3.OperationalError as _e:
            try:
                action = self._error_handlers[_e.message]
                if action:
                    self._c.execute(action)
            except KeyError:
                raise sqlite3.OperationalError(_e)

    @property
    def _error_handlers(self):
        handlers = []
        #for i in self._tables_to_replace:
        #    handlers.append(('table %s already exists' % i, 'DELETE FROM %s' % i))
        #if self._selected_table not in self._tables_to_replace:
        #    handlers.append(('table %s already exists' % self._selected_table, None))
        return dict(handlers)

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

    def init_columns(self, *columns):
        c_l = self.columns
        for a in set(columns) - c_l:
            t1 = self.tables[self._selected_table]
            assert isinstance(t1, Table)
            t1.add_column(a)
            self.commit()

    def choose_table(self, table_name):
        self._selected_table = table_name
        # self.select_all_from_table()

    def clear_table(self, table_name):
        self.execute('DELETE FROM ' + table_name)

    def select_all_from_table(self):
        self.execute('''SELECT * FROM ''' + self._selected_table + ''';''')

    def insert_dict_as_row(self, input_dict, table_name):
        assert isinstance(input_dict, dict)
        k_view = input_dict.viewkeys()
        v_view = input_dict.viewvalues()
        slot_str = '(?' + (',?' * (len(v_view) - 1)) + ')'

        self.choose_table(table_name)
        self.init_columns(*k_view)
        self.execute(str("INSERT OR REPLACE INTO %s %s VALUES %s;") %
                     (self._selected_table, repr(tuple(k_view)), slot_str),
                     tuple(v_view))

    def update(self, *args):
        def table_names_():
            assert isinstance(self, ThemeDB)
            self._table_names = set(str(i[0]) for i in
                                    self.execute("SELECT name FROM sqlite_master WHERE type='table';"))

        def tables_():
            assert isinstance(self, ThemeDB)
            self._tables.update((t, Table(self, t)) for t in self._table_names)

        for valid_call in locals().viewkeys() & set(("%s_" % _x1) for _x1 in args):
            locals()[valid_call].__call__()

    @property
    def current_table(self):
        return self._selected_table

    @property
    def table_names(self):
        self._table_names = set(str(i[0]) for i in
                                self.execute("SELECT name FROM sqlite_master WHERE type='table';"))
        return self._table_names

    @property
    def tables(self):
        # self._tables = dict((t, Table(self, t)) for t in self._table_names)
        return self._tables

    @property
    def columns(self):
        """

        :rtype : set
        """
        assert self._selected_table in self._tables_view_keys
        return self.tables[self._selected_table].columns

    @property
    def frozen(self):
        return self._freeze_cursor


class Table(object):
    def __init__(self, theme_db, name):
        assert isinstance(theme_db, ThemeDB)
        assert isinstance(name, str)
        self._db = theme_db
        self.__name = name
        self._column_cache = set()

    def clear(self):
        self._db.execute("DELETE FROM %s;" % self.name)

    def select_all(self):
        self._db.execute("SELECT * FROM %s;" % self.name)

    def add_column(self, column, type_name=None):
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


class ICLSdb(themeConvert.fileFormats.ICLSProcessor):
    def __init__(self, db_filename):
        self._theme_db = ThemeDB(db_filename)
        self._theme_db.execute('''CREATE TABLE IF NOT EXISTS attributes (selector text UNIQUE);''')
        self._theme_db.execute('''CREATE TABLE IF NOT EXISTS colors (FILESTATUS_UNKNOWN text);''')
        self._theme_db.commit()
        self._theme_db.tables['colors'].clear()
        self._theme_db.commit()

    def yield_table(self):
        self._theme_db.select_all_from_table()
        for row in self._theme_db.iter_cursor():
            yield row

    def yield_table_dicts(self):
        self._theme_db.select_all_from_table()
        for row_dict in self._theme_db.iter_cursor_to_dict():
            yield row_dict

    def yield_entries(self, xml_str):
        root = ET.fromstring(xml_str)
        colors_root = root.find('colors')
        color_prop_dict = self.n_v_dict(colors_root.findall('./option'))
        self.write_props({'props': color_prop_dict, 'table': 'colors'})

        attrs_root = root.find('attributes')
        for child in attrs_root:
            child_name = child.get('name')
            prop_dict = self.n_v_dict(child.findall('./value/option'))
            prop_dict['selector'] = child_name
            self.write_props({'props': prop_dict, 'table': 'attributes'})

    def write_props(self, result_dict):
        self._theme_db.insert_dict_as_row(result_dict['props'], result_dict['table'])
        self._theme_db.commit()

    def close(self):
        self._theme_db.close()

class SSSdb(themeConvert.fileFormats.SSSProcessor):
    def __init__(self, db_filename):
        self._theme_db = ThemeDB(db_filename)
        self._theme_db.commit()

    def yield_table(self):
        self._theme_db.select_all_from_table()
        for row in self._theme_db.iter_cursor():
            yield row

    def yield_table_dicts(self):
        self._theme_db.select_all_from_table()
        for row_dict in self._theme_db.iter_cursor_to_dict():
            yield row_dict

    def yield_entries(self, text):
        for match in self.entry_pat.finditer(text):
            prop_dict = {}
            for prop_match in self.prop_pat.finditer(match.groupdict()['props']):
                prop_dict[str(prop_match.groupdict()['attr']).replace('-', '_')] = prop_match.groupdict()['value']
            prop_dict['selector'] = match.groupdict()['selector']
            self.write_props({'props': prop_dict, 'table': 'theme'})

    def write_props(self, result_dict):
        self._theme_db.insert_dict_as_row(result_dict['props'], result_dict['table'])
        self._theme_db.commit()

    def close(self):
        self._theme_db.close()
