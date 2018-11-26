import appdaemon.plugins.hass.hassapi as appapi
import os
import re
from datetime import datetime

#
# App to display a Persistent Notification on the Front End whenever AppDaemon has encountered
# an error
#
# Args: (set these in appdaemon.cfg)
# path_to_errorlog = full path of location of errorlog
# refresh_interval = time in seconds to check for new errors
#
#
# EXAMPLE appdaemon.cfg entry below
# 
# # Apps
# 
# [error_notifier]
# module = error_notifier
# class = ErrorNotifier
# path_to_errorlog = /home/homeassistant/.homeassistant/appdaemon/conf/errfile.log
# refresh_interval = 5
#

class ErrorNotifier(appapi.Hass):

    def handle_log(self, name, ts, level, message): 
        
        if level not in self.ignore_levels:
            self.call_service('persistent_notification/create',
                title="[AppDaemon] {}".format(level),
                message=("At {}, in app {}, in def {}"
                        .format(name, ts, message)))
        #    self.log("logggger" + level)
    

    def initialize(self):
        self.ignore_levels = { "INFO" }
        self.listen_log(self.handle_log)

    