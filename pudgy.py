# pudgy.py

"""
This module provides a simple wrapper to the Pidgin DBus API for
receiving and sending messages to IM contacts.
"""

import dbus
import dbus.exceptions
from dbus.mainloop.glib import DBusGMainLoop

__author__ = "brx"
__copyright__ = "Copyright 2010, brx"
__license__ = "GPLv3"

class InitError(Exception): pass
class CallError(Exception): pass

class _PurpleCaller(object):    # wrapper class for great justice and own exceptions
   def __init__(self):
      try:
         self._bus = dbus.SessionBus()
         self._purple_object = self._bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
         self.purple = dbus.Interface(self._purple_object, "im.pidgin.purple.PurpleInterface")
      except:
         raise InitError()

   def __getattr__(self, attr):
      def wrapper(*args, **keys):
         try:
            return getattr(self.purple, attr)(*args, **keys)
         except dbus.exceptions.DBusException:
            raise CallError()

      return wrapper

class Buddy(object):
   def __init__(self, pcaller, account_id, buddy_id, buddy_name, buddy_alias):
      self.pcaller = pcaller

      self.account_id = account_id
      self.buddy_id = buddy_id
      self.buddy_name = buddy_name
      self.buddy_alias = buddy_alias

   def __str__(self): return self.buddy_alias

   def send_message(self, message):
      conv = self.pcaller.PurpleConversationNew(1, self.account_id, self.buddy_name)
      im = self.pcaller.PurpleConvIm(conv)
      self.pcaller.PurpleConvImSend(im, message)

class Pudgy(object):
   def __init__(self, msg_handler):
      DBusGMainLoop(set_as_default=True)

      self._msg_handler = msg_handler
      self._buddy_map = {}

      self.pcaller = _PurpleCaller()
      self.pcaller.connect_to_signal("ReceivedImMsg", self._process_recv_msg)

   def _get_buddy(self, account_id, buddy_name):
      buddy_id = self.pcaller.PurpleFindBuddy(account_id, buddy_name)
      buddy_alias = self.pcaller.PurpleBuddyGetAlias(buddy_id)
      return self._buddy_map.setdefault((account_id, buddy_name),
                                        Buddy(self.pcaller,
                                              account_id, buddy_id,
                                              buddy_name, buddy_alias))

   def get_buddies(self):
      for account_id in self.pcaller.PurpleAccountsGetAllActive():
         for buddy_id in self.pcaller.PurpleFindBuddies(account_id, ""):
            buddy_name = self.pcaller.PurpleBuddyGetName(buddy_id)
            yield self._get_buddy(account_id, buddy_name)

   def _process_recv_msg(self, account_id, sender_name, message, conversation, flags):
      buddy = self._get_buddy(account_id, sender_name)
      self._msg_handler(buddy, message)
