import os,re

from logshipper.tail import Tail

from st2reactor.sensor.base import Sensor


class Syslog_Sensor(Sensor):
    def __init__(self, sensor_service, config=None):
        super(Syslog_Sensor, self).__init__(sensor_service=sensor_service,
                                              config=config)
        self._config = self._config['syslog_watch_sensor']
        self._file_paths = self._config.get('syslog_paths', [])
        self._triggers = self._config.get('triggers', [])        

        self._tail = None

        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)

    def setup(self):
        if not self._file_paths:
            raise ValueError('No file_paths configured to monitor')
        if not self._triggers:
            raise ValueError('No triggers to evaluate for matches')

        self._tail = Tail(filenames=self._file_paths)
        self._tail.handler = self._handle_line
        self._tail.should_run = True

    def run(self):
        self._tail.run()

    def cleanup(self):
        if self._tail:
            self._tail.should_run = False

            try:
                self._tail.notifier.stop()
            except Exception:
                pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

    def _handle_line(self, file_path, line):
        for trigger in self._triggers:
            regex = re.compile(trigger['regex'])
            match = regex.match(line)
	    if match:
                payload = {}
                for k,v in trigger['groups'].items():
                    payload.update({v: match.group(k)})
                self.sensor_service.dispatch(trigger=trigger['trigger'], payload=payload)
