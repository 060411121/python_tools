#!/usr/bin/python2.6

# Copyright (C) 2014 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Interface for a USB-connected Monsoon power meter
(http://msoon.com/LabEquipment/PowerMonitor/).
This file requires gflags, which requires setuptools.
To install setuptools: sudo apt-get install python-setuptools
To install gflags, see http://code.google.com/p/python-gflags/
To install pyserial, see http://pyserial.sourceforge.net/

Example usages:
  Set the voltage of the device 7536 to 4.0V
  python2.6 monsoon.py --voltage=4.0 --serialno 7536

  Get 5000hz data from device number 7536, with unlimited number of samples
  python2.6 monsoon.py --samples -1 --hz 5000 --serialno 7536

  Get 200Hz data for 5 seconds (1000 events) from default device
  python2.6 monsoon.py --samples 100 --hz 200

  Get unlimited 200Hz data from device attached at /dev/ttyACM0
  python2.6 monsoon.py --samples -1 --hz 200 --device /dev/ttyACM0
"""

import fcntl
import os
import select
import signal
import stat
import struct
import sys
import time
import collections

import gflags as flags  # http://code.google.com/p/python-gflags/

import serial           # http://pyserial.sourceforge.net/
# import monsoon_lib.py 
from monsoon_lib import *

FLAGS = flags.FLAGS

def main(argv):
  """ Simple command-line interface for Monsoon."""
  useful_flags = ["voltage", "status", "usbpassthrough", "samples", "current"]
  if not [f for f in useful_flags if FLAGS.get(f, None) is not None]:
    print __doc__.strip()
    print FLAGS.MainModuleHelp()
    return

  if FLAGS.avg and FLAGS.avg < 0:
    print "--avg must be greater than 0"
    return

  mon = Monsoon(device=FLAGS.device, serialno=FLAGS.serialno)

  if FLAGS.voltage is not None:
    if FLAGS.ramp is not None:
      mon.RampVoltage(mon.start_voltage, FLAGS.voltage)
    else:
      mon.SetVoltage(FLAGS.voltage)

  if FLAGS.current is not None:
    mon.SetMaxCurrent(FLAGS.current)

  if FLAGS.status:
    items = sorted(mon.GetStatus().items())
    print "\n".join(["%s: %s" % item for item in items])

  if FLAGS.usbpassthrough:
    if FLAGS.usbpassthrough == 'off':
      mon.SetUsbPassthrough(0)
    elif FLAGS.usbpassthrough == 'on':
      mon.SetUsbPassthrough(1)
    elif FLAGS.usbpassthrough == 'auto':
      mon.SetUsbPassthrough(2)
    else:
      sys.exit('bad passthrough flag: %s' % FLAGS.usbpassthrough)

  if FLAGS.samples:
    # Make sure state is normal
    mon.StopDataCollection()
    status = mon.GetStatus()
    native_hz = status["sampleRate"] * 1000
    print('zhuang >>> native_hz: %d' % native_hz)

    # Collect and average samples as specified
    mon.StartDataCollection()

    # In case FLAGS.hz doesn't divide native_hz exactly, use this invariant:
    # 'offset' = (consumed samples) * FLAGS.hz - (emitted samples) * native_hz
    # This is the error accumulator in a variation of Bresenham's algorithm.
    emitted = offset = 0
    collected = []
    history_deque = collections.deque() # past n samples for rolling average
    total_history_deque = collections.deque() # past n samples for rolling average
    print "zhuang >>> len(history_deque) %d" % len(history_deque)

    try:
      last_flush = time.time()
      print "zhuang >>> collected %d" % len(collected)
      while emitted < FLAGS.samples or FLAGS.samples == -1:
        # The number of raw samples to consume before emitting the next output
        need = (native_hz - offset + FLAGS.hz - 1) / FLAGS.hz
     #   print "zhuang >>> collected %d need=%d emitted=%d" %(len(collected),need,emitted)
        if need > len(collected):     # still need more input samples
          samples = mon.CollectData()
          if not samples: break
          collected.extend(samples)
        else:
          # Have enough data, generate output samples.
          # Adjust for consuming 'need' input samples.
          # print "zhuang >>> collected %d need=%d emitted=%d offset=%d FLAGS.samples=%d FLAGS.hz=%d" %(len(collected),need,emitted,offset,FLAGS.samples,FLAGS.hz)
          offset += need * FLAGS.hz
          # print "zhuang >>> collected %d need=%d emitted=%d offset=%d FLAGS.samples=%d FLAGS.hz=%d" %(len(collected),need,emitted,offset,FLAGS.samples,FLAGS.hz)
          while offset >= native_hz:  # maybe multiple, if FLAGS.hz > native_hz
            this_sample = sum(collected[:need]) / need
            total_history_deque.appendleft(this_sample)
            print "22 this_sample=%f [sum=%f/need=%d]" %(this_sample, sum(collected[:need]), need)

            # if FLAGS.timestamp: print int(time.time()),
            if FLAGS.timestamp: print time.time(),
            if FLAGS.timestamp: print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),
            if FLAGS.timestamp: print ",",

            if FLAGS.avg:
              history_deque.appendleft(this_sample)
              if len(history_deque) > FLAGS.avg: history_deque.pop()
              print "zhuang >>> len(history_deque) %d" % len(history_deque)
              print "%f --- %f" % (this_sample,
                               sum(history_deque) / len(history_deque))
            else:
              print "%f" % this_sample
            sys.stdout.flush()

            offset -= native_hz
            emitted += 1              # adjust for emitting 1 output sample
          collected = collected[need:]
          print "zhuang  <<<  >>> collected %d" % len(collected)
          now = time.time()
          if now - last_flush >= 0.99:  # flush every second
            sys.stdout.flush()
            last_flush = now
          print "\n"
    except KeyboardInterrupt:
      print >>sys.stderr, "interrupted"

    mon.StopDataCollection()
    print "zhuang >>> iiiiiiiilen(total_history_deque) %d" % len(total_history_deque)
    print " --- %f" % (sum(total_history_deque) / len(total_history_deque))


if __name__ == '__main__':
  # Define flags here to avoid conflicts with people who use us as a library
  flags.DEFINE_boolean("status", None, "Print power meter status")
  flags.DEFINE_integer("avg", None,
                       "Also report average over last n data points")
  flags.DEFINE_float("voltage", None, "Set output voltage (0 for off)")
  flags.DEFINE_float("current", None, "Set max output current")
  flags.DEFINE_string("usbpassthrough", None, "USB control (on, off, auto)")
  flags.DEFINE_integer("samples", None, "Collect and print this many samples")
  flags.DEFINE_integer("hz", 5000, "Print this many samples/sec")
  flags.DEFINE_string("device", None,
                      "Path to the device in /dev/... (ex:/dev/ttyACM1)")
  flags.DEFINE_integer("serialno", None, "Look for a device with this serial number")
  flags.DEFINE_boolean("timestamp", None,
                       "Also print integer (seconds) timestamp on each line")
  flags.DEFINE_boolean("ramp", True, "Gradually increase voltage")

  main(FLAGS(sys.argv))
