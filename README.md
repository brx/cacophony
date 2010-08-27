# Cacophony #

Cacophony is a utility for fostering your IM relationships on
autopilot. It tries to solve the problem of too many people hogging
your attention on [Pidgin](http://www.pidgin.im) without you appearing
to be too busy to talk to your friends!

## Warning ##

This half-assed README is as useless as Cacophony itself.

## How it works ##

Cacophony allows you to specify directed graphs where the nodes are IM
contacts and the edges represent routing instructions. It connects to
a running instance of [Pidgin](http://www.pidgin.im) via
[DBus](http://dbus.freedesktop.org) and routes incoming messages as
specified.

### Example ###

Given two contacts **A** and **B** and the following graph

     +++ ---> +++
     +A+      +B+
     +++ <--- +++

messages from **A** are routed to **B** and vice versa, freeing you to
get work done while satisfying both **A**'s and **B**'s desire to
converse with you!

## Setup ##

### Dependencies ###

- [python](http://www.python.org/) >= 2.6
- [pygobject](http://www.pygtk.org/) (tested with version 2.21.3)
- [dbus-python](http://cgit.freedesktop.org/dbus/dbus-python/) (tested with version 0.83.1)

## Usage ##

Make sure [Pidgin](http://www.pidgin.im) is running before starting
Cacophony. Run it from its directory in a terminal like this:

    $ python cacophony.py

    1: A [B, C]
    2: B []
    3: C []
    4: D []
    >

The above program output states that messages from **A** are routed to
**B** and **C**. The prompt accepts input in the following form:

    > 1 -2 4

Cacophony will then update the routes to

    1: A [C, D]
    2: B []
    3: C []
    4: D []
    >

This should be self-explanatory. Now have fun!

## License ##

Copyright (C) 2010 brx

Distributed under the GPLv3. See COPYING.
