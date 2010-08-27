#!/usr/bin/env python
#
# cacophony.py

"""
Tending to your IM social life on autopilot!
This be the __main__ program entry. :)
"""
import sys
import select
import glib

import pudgy

__author__ = 'brx'
__copyright__ = 'Copyright 2010, brx'
__license__ = 'GPLv3'

class CacoGraph(object):
   def __init__(self, buddies = None):
      self.edges = {}
      for buddy in buddies: self.add_buddy(buddy)

   def add_buddy(self, buddy): self.edges[buddy] = set()

   def link_buddy(self, buddy_from, buddy_to): self.edges[buddy_from].add(buddy_to)
   def unlink_buddy(self, buddy_from, buddy_to): self.edges[buddy_from].remove(buddy_to)

   def get_out_edges(self, buddy): return self.edges.get(buddy, set())

class CacoController(object):
   def __init__(self):
      self.pudgy = pudgy.Pudgy(self._process_msg)
      self.index_map = list(self.pudgy.get_buddies())
      self.graph = CacoGraph(self.index_map)

   def _link(self, idx_from, idx_to):
      self.graph.link_buddy(self.index_map[idx_from-1], self.index_map[idx_to-1])

   def _unlink(self, idx_from, idx_to):
      self.graph.unlink_buddy(self.index_map[idx_from-1], self.index_map[idx_to-1])

   def handle_input(self, input_line):
      try:
         link_indices = map(int, input_line.split())
         link_from = link_indices[0]
         for link_to in link_indices[1:]:
            try:
               if link_to < 0:  self._unlink(link_from, -link_to)
               else:            self._link(link_from, link_to)
            except LookupError:
               pass
      except:
         print "-- a command is a space-separated list of whole numbers --\n"

   def present_view(self):
      for i, buddy in enumerate(self.index_map):
         print "%d: %s [%s]" % (i+1, unicode(buddy),
                                ', '.join(map(unicode, self.graph.get_out_edges(buddy))))
      print '> ',
      sys.stdout.flush()

   def _process_msg(self, buddy, message):
      links = self.graph.get_out_edges(buddy)
      for link in links: link.send_message(message)

class Cacophony(object):
   def __init__(self):
      self.control = CacoController()

      self.poller = select.poll()
      self.poller.register(sys.stdin, select.POLLIN)

      self.main_loop = glib.MainLoop()
      glib.idle_add(self.handle_ui)

   def handle_ui(self):
      if (self.poller.poll(1)):
         input_line = sys.stdin.readline()[:-1]
         print
         if (input_line == 'q'):
            self.quit()
         else:
            self.control.handle_input(input_line)
            self.control.present_view()
      return True               # must return True! (see glib.idle_add)

   def run(self): self.main_loop.run()
   def quit(self): self.main_loop.quit()

if __name__ == '__main__':
   try:
      caco = Cacophony()
      caco.control.present_view()
      caco.run()
   except pudgy.InitError:
      sys.stderr.write("Failed to start Cacophony! (Is Pidgin running?)\n")
   finally:
      try: caco.quit()
      except NameError: pass
