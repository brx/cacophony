import sys
import select
import glib

import pudgy

class Buddy(object):
   def __init__(self, account_id, buddy_id, buddy_name, buddy_alias):
      self.account_id = account_id
      self.buddy_id = buddy_id
      self.buddy_name = unicode(buddy_name)
      self.buddy_alias = unicode(buddy_alias)

   def __str__(self): return self.buddy_alias

class CacoDict(object):
   def __init__(self):
      self.link_dict = {}
      self.buddy_assoc = []

   def add_buddy(self, buddy):
      self.link_dict[buddy.buddy_id] = set()
      self.buddy_assoc.append(buddy)

   def link_buddy(self, buddy_from, buddy_to):
      self.link_dict[buddy_from.buddy_id].add(buddy_to)

   def unlink_buddy(self, buddy_from, buddy_to):
      self.link_dict[buddy_from.buddy_id].remove(buddy_to)

   def __str__(self):
      ret = u""
      for i, buddy in enumerate(self.buddy_assoc):
         ret += unicode(i+1) + u": " + unicode(buddy) + u" [" + \
             ", ".join(map(unicode, self.link_dict[buddy.buddy_id])) + \
             u"]\n"
      return ret

class Cacophony(object):
   def __init__(self):
      self.pudgy = pudgy.Pudgy(self.process_msg)

      self._init_dbus()
      self._init_caco()
      self._init_poll()

      # self.purple.connect_to_signal("ReceivedImMsg", self.process_msg)

      self.main_loop = glib.MainLoop()
      glib.idle_add(self.handle_ui)

   def _init_dbus(self):
      # DBusGMainLoop(set_as_default=True)
      # self.bus = dbus.SessionBus()
      # self.purple_object = self.bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
      # self.purple = dbus.Interface(self.purple_object, "im.pidgin.purple.PurpleInterface")
      self.bus = self.pudgy.pcaller.bus
      self.purple_object = self.pudgy.pcaller.purple_object
      self.purple = self.pudgy.pcaller.purple

   def _init_caco(self):
      self.caco_dict = CacoDict()
      for account_id in self.purple.PurpleAccountsGetAllActive():
         for buddy_id in self.purple.PurpleFindBuddies(account_id, ""):
            self.caco_dict.add_buddy(Buddy(account_id,
                                           buddy_id,
                                           self.purple.PurpleBuddyGetName(buddy_id),
                                           self.purple.PurpleBuddyGetAlias(buddy_id)))

   def _init_poll(self):
      self.pobj = select.poll()
      self.pobj.register(sys.stdin, select.POLLIN)

   def process_msg(self, account, sender, message, conversation, flags):
      buddy_id = self.purple.PurpleFindBuddy(account, sender)
      links = self.caco_dict.link_dict.get(buddy_id, set())
      for link in links:
         conv = self.purple.PurpleConversationNew(1, link.account_id, link.buddy_name)
         im = self.purple.PurpleConvIm(conv)
         self.purple.PurpleConvImSend(im, message)

   def print_ui(self):
      print
      print unicode(self.caco_dict) + "> ", 
      sys.stdout.flush()

   def link(self, idx_from, idx_to):
      self.caco_dict.link_buddy(self.caco_dict.buddy_assoc[idx_from-1],
                                self.caco_dict.buddy_assoc[idx_to-1])

   def unlink(self, idx_from, idx_to):
      self.caco_dict.unlink_buddy(self.caco_dict.buddy_assoc[idx_from-1],
                                  self.caco_dict.buddy_assoc[idx_to-1])

   def handle_input(self, input_line):
      try:
         link_indices = map(int, input_line.split())
         link_from = link_indices[0]
         for link_to in link_indices[1:]:
            if link_to < 0:
               self.unlink(link_from, -link_to)
            else:
               self.link(link_from, link_to)
      except:
         pass

   def handle_ui(self):
      if (self.pobj.poll(1)):
         for v in self.pudgy._buddy_map.itervalues(): print v
         input_line = sys.stdin.readline()[:-1]
         if (input_line == "q"):
            self.main_loop.quit()
         else:
            self.handle_input(input_line)
            self.print_ui()
      return True

   def run(self):
      self.main_loop.run()

if __name__ == "__main__":
   caco = Cacophony()
   caco.print_ui()
   caco.run()
