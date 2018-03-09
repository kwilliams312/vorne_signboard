#!/usr/bin/env python3

import signboard

# testing class functions
sb = signboard.Signboard("/dev/ttyUSB0")
sb.connect()
sb.clear()
sb.print_msg('Vorne signboard.',1,type="static")
