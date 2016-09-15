import json
from lib import actions, Excel_Reader


class GetInventoryAction(actions.SessionAction):
    def __init__(self, config):
        super(GetInventoryAction, self).__init__(config)
        self._template_dir = self.config['template_dir']
        self._excel_file = self.config['excel_file']

    def run(self, sheetname, key, variables):
        data = json.loads(variables)
        excel = Excel_Reader.Excel_Reader(self._excel_file,
                                          sheetname, variable_start_column=2)
        excel.set_values_for_variables(key, data)
        excel.save()
        return (True, 'Success')
