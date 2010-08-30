#
# pudgy.py

"""
This module provides a simple wrapper to the Pidgin DBus API for
receiving and sending messages to IM contacts.
"""
import sys
import dbus
import dbus.exceptions
from dbus.mainloop.glib import DBusGMainLoop

__author__ = 'brx'
__copyright__ = 'Copyright 2010, brx'
__license__ = 'GPLv3'

class InitError(Exception): pass

class _PurpleCaller(object):    # wrapper class for great justice and own exceptions
   def __init__(self):
      DBusGMainLoop(set_as_default=True)
      try:
         self.bus = dbus.SessionBus()
         self.purple = self.bus.get_object('im.pidgin.purple.PurpleService', '/im/pidgin/purple/PurpleObject')
      except:
         raise InitError()

   def __getattr__(self, attr):
      def wrapper(*args, **keys):
         try:
            return getattr(self.purple, attr)(*args, dbus_interface='im.pidgin.purple.PurpleInterface', **keys)
         except dbus.exceptions.DBusException:
            sys.stderr.write("\nFailed to contact Pidgin! Terminating!\n") # ugh.. signal handlers :(
            self.bus.close()
            return 0            # confusion!!!!
      return wrapper

class Account(object):
   def __init__(self, pcaller, account_id):
      self.pcaller = pcaller
      self.id = account_id

      self.username = pcaller.PurpleAccountGetUsername(account_id)
      self.protocol = pcaller.PurpleAccountGetProtocolName(account_id)

      self._init_buddies()

   def _init_buddies(self):
      self.buddies = {}
      for buddy_id in self.pcaller.PurpleFindBuddies(self.id, ""):
         self.buddies[buddy_id] = Buddy(self.pcaller, self, buddy_id)

   def get_buddy_by_name(self, buddy_name):
      buddy_id = self.pcaller.PurpleFindBuddy(self.id, buddy_name)
      return self.buddies.get(buddy_id, None)

class Buddy(object):
   def __init__(self, pcaller, account, buddy_id):
      self.pcaller = pcaller
      self.account = account

      self.id = buddy_id
      self.name = pcaller.PurpleBuddyGetName(buddy_id)
      self.alias = pcaller.PurpleBuddyGetAlias(buddy_id)

   def __str__(self):
      return self.alias + " (%s/%s)" % (self.name, self.account.protocol)

   def send_message(self, message):
      conv = self.pcaller.PurpleFindConversationWithAccount(1, self.name, self.account.id) or \
          self.pcaller.PurpleConversationNew(1, self.account.id, self.name)
      im = self.pcaller.PurpleConvIm(conv)
      self.pcaller.PurpleConvImSend(im, message)

class Pudgy(object):
   def __init__(self, msg_handler):
      self._msg_handler = msg_handler

      self.pcaller = _PurpleCaller()
      self.pcaller.connect_to_signal('ReceivedImMsg', self._process_recv_msg)

      self._init_accounts()

   def _init_accounts(self):
      self.accounts = {}
      for account_id in self.pcaller.PurpleAccountsGetAllActive():
         self.accounts[account_id] = Account(self.pcaller, account_id)

   def get_buddies(self):
      for account in self.accounts.itervalues():
         for buddy in account.buddies.itervalues():
            yield buddy

   def _process_recv_msg(self, account_id, sender_name, message, conversation, flags):
      buddy = self.accounts[account_id].get_buddy_by_name(sender_name)
      if buddy: self._msg_handler(buddy, message)
