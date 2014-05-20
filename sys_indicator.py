#!/usr/bin/env python

import gobject
import gtk
import appindicator
import time
import datetime
import svgwrite
import psutil
import sys
import math

svg_file = '/tmp/sys_indicator.svg'
values = []

def generate_icon():
  graph_height = 16
  graph_width = 24
  stroke_width = 3

  dwg = svgwrite.Drawing(svg_file, profile='tiny', size=(graph_width, graph_height))
  #dwg = svgwrite.Drawing('cpu.svg', profile='tiny')
  #dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='rgb(50,50,50)'))

  for i in range(len(values)):
    dwg.add(dwg.line((i*stroke_width+1, graph_height), (i*stroke_width+1, graph_height - values[i]), stroke=svgwrite.rgb(223, 219, 210, 'RGB'), stroke_width=stroke_width))
  dwg.save()

def iterate_processes(procs, sort_key, func):
  processes = sorted(procs, key=sort_key, reverse=True)
  for p in processes[:3]:
    func(p)

def change_icon():
  cpu_percent = psutil.cpu_percent()
  p = math.ceil(cpu_percent/(100.0/16.0))
  #print(cpu_percent)
  values.append(p)
  if len(values) > 8:
    values.pop(0)
  #print values
  generate_icon()
  ind.set_icon("")
  ind.set_icon(svg_file)
  gtk.timeout_add(3 * 1000, change_icon)

def change_menu():
  procs = []
  for proc in psutil.process_iter():
      proc.cpu = proc.cpu_percent()
      proc.mem = proc.memory_percent()
      procs.append(proc)

  menu = gtk.Menu()

  def add_menu_item(s):
    menu_items = gtk.MenuItem(s)
    menu.append(menu_items)
    # this is where you would connect your menu item up with a function:
    #menu_items.connect("activate", menuitem_response, s)
    menu_items.show()

  add_menu_item('Top CPU Processes')

  def func(p):
    buf = str(p.cpu) + '%\t' + p.name() + '\t' #+ ' ' + str(p.mem) + ' ' + str(p.memory_info().rss/(1024*1024))
    add_menu_item(buf)

  iterate_processes(procs, lambda p: p.cpu, func)

  menu_items = gtk.SeparatorMenuItem()
  menu.append(menu_items)
  menu_items.show()

  add_menu_item('Top Memory Processes')

  def func_m(p):
    buf = "%.1f%s\t%dMB\t%s" % (p.mem, '%', p.memory_info().rss/(1024*1024), p.name())
    add_menu_item(buf)

  iterate_processes(procs, lambda p: p.mem, func_m)

  menu_items = gtk.SeparatorMenuItem()
  menu.append(menu_items)
  menu_items.show()

  menu_items = gtk.MenuItem("Quit")
  menu.append(menu_items)
  menu_items.connect("activate", quit)
  menu_items.show()


  ind.set_menu(menu)
  gtk.timeout_add(3 * 1000, change_menu)

def quit(w):
  sys.exit(0)

if __name__ == "__main__":
  ind = appindicator.Indicator ("simple-system-monitor-indicator",
                              "sys-mon-ind",
                              appindicator.CATEGORY_APPLICATION_STATUS)
  ind.set_status (appindicator.STATUS_ACTIVE)
  #ind.set_attention_icon ("indicator-messages-new")

  gtk.timeout_add(1 * 1000, change_icon)
  gtk.timeout_add(1 * 1000, change_menu)

  gtk.main()

