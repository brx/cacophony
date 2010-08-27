import sys
import select
import glib

import pudgy

class CacoDict(object):
   def __init__(self):
      self.link_dict = {}
      self.buddy_assoc = []

   def add_buddy(self, buddy):
      self.link_dict[buddy] = set()
      self.buddy_assoc.append(buddy)

   def link_buddy(self, buddy_from, buddy_to):
      self.link_dict[buddy_from].add(buddy_to)

   def unlink_buddy(self, buddy_from, buddy_to):
      self.link_dict[buddy_from].remove(buddy_to)

   def __str__(self):
      ret = u""
      for i, buddy in enumerate(self.buddy_assoc):
         ret += unicode(i+1) + u": " + unicode(buddy) + u" [" + \
             u", ".join(map(unicode, self.link_dict[buddy])) + \
             u"]\n"
      return ret

class Cacophony(object):
   def __init__(self):
      self.pudgy = pudgy.Pudgy(self.process_msg)

      self._init_caco()
      self._init_poll()

      self.main_loop = glib.MainLoop()
      glib.idle_add(self.handle_ui)

   def _init_caco(self):
      self.caco_dict = CacoDict()
      for buddy in self.pudgy.get_buddies():
         self.caco_dict.add_buddy(buddy)

   def _init_poll(self):
      self.pobj = select.poll()
      self.pobj.register(sys.stdin, select.POLLIN)

   def process_msg(self, buddy, message):
      links = self.caco_dict.link_dict.get(buddy, set())
      for link in links:
         link.send_message(message)

   def print_ui(self):
      print
      print unicode(self.caco_dict) + u"> ", 
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
