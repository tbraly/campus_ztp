"""
Copyright 2016 Brocade Communications Systems, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from openpyxl import Workbook,load_workbook

import sys

class Excel_Reader(object):

        def __init__(self,excel_file, sheet_name = 'SWITCHES', variable_name_row = 1, key_column = 1, template_column = 2, variable_start_column = 3):
                ''' Loads the excel configuration file '''
                try:
                        self._wb = load_workbook(excel_file)
                except:
                        raise Exception("Could not load spreadsheet '%s'" % excel_file)

                self.set_excel_sheet(sheet_name)
                self.set_variable_name_row(variable_name_row)
                self.set_variable_start_column(variable_start_column)
                self.set_key_column(key_column)
                self.set_template_column(template_column)

        def set_variable_name_row(self, variable_name_row):
                ''' Set the row where the variable names are '''
                self._variable_name_row = variable_name_row
                self._data_start_row = variable_name_row + 1

        def set_data_start_row(self, data_start_row):
                ''' Set the row in the sheet where the data starts '''
                self._data_start_row = data_start_row

        def set_key_column(self, key_column):
                ''' Set the key column in the template '''
                self._key_column = key_column
                self._keys = {}
                r = self._data_start_row
                while (True):
                        key = self._ws.cell(column=self._key_column, row = r);
                        if (key.value):
                                # Check for duplicate key
                                if not key.value in self._keys:
                                        self._keys[key.value] = r
                                else:
                                        raise Exception("Duplicate key '%s' found at row '%s'." % (key.value,r))
                
                        else:
                                break
                        r+=1

        def set_template_column(self, template_column):
                ''' Set the template column in the template '''
                self._template_column = template_column

        def set_variable_start_column(self, variable_start_column):
                ''' Set the template column in the template '''
                c = self._variable_start_column = variable_start_column
		while (True):
			cell = self._ws.cell(column=c,row = self._variable_name_row)
			if (cell.value):
				c+=1	
			else:
				self._variable_end_column = c
				break	

        def set_excel_sheet(self, sheet_name):
                ''' Sets the current sheet '''
                self._sheet_name = sheet_name
                try:
                        self._ws = self._wb.get_sheet_by_name(self._sheet_name)
                except:
                        raise Exception("Could not find the sheet named '%s'" % self._sheet_name)

        def get_row_for_key(self, key):
                ''' Returns the row for a given key, or -1 if not matched '''
                if key in self._keys:
                        return self._keys[key]
                return -1

        def get_variables_for_key(self, key):
                ''' Returns the variables for a particular key '''
                variables = {}
                col = self._variable_start_column
                row = self.get_row_for_key(key)
                while (col<=self._variable_end_column):
                        variable = self._ws.cell(column=col, row=self._variable_name_row)
                        if (variable.value):
                                variables[variable.value] = self._ws.cell(column=col, row=row).value
                        col+=1  
                return variables

        def get_template_name_for_key(self,key):
                ''' Returns the template to file use '''
                row = self.get_row_for_key(key)
                if (row>=0):
                        return self._ws.cell(column=self._template_column, row=row).value
                return ""

