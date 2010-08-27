# pudgy.py

"""
This module provides a simple wrapper to the Pidgin DBus API for
receiving and sending messages to IM contacts.
"""

import dbus
from dbus.mainloop.glib import DBusGMainLoop

class InitError(Exception):
   pass

class Pudgy(object):
   
   def __init__(self):
      DBusGMainLoop(set_as_default=True)

      self._init_dbus()

   def _init_dbus(self):
      try:
         self.bus = dbus.SessionBus()
         self.purple_object = self.bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
         self.purple = dbus.Interface(self.purple_object, "im.pidgin.purple.PurpleInterface")
      except:
         raise InitError()
