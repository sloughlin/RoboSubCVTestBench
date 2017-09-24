#!/usr/bin/python2.7

import argparse
import cv2
import os
import sys
import imp
import numpy
import time
import threading
import json

from Tkinter import *
from PIL import ImageTk, Image

from tools.buoyeditor import BuoyEditor
import util

"""
Buttons:
 AddTrackedItem

RightListBar:
  Holds list of tracked items
  When one is selected mouse allows adding, or adjusting its representation in the frame

TrackedItem:
  Types: Buoy(r,g,b), StartingGate(l,r), Hedge(t,b,r), Box(h,c,b1,b2)

"""

class MetaDataGenerator(threading.Thread):

  image_idx = 0

  scale = 1.0

  img_off_x = 0
  img_off_y = 0

  mouse_down_x = 0
  mouse_down_y = 0
  mouse_last_x = 0
  mouse_last_y = 0

  active_tool = None

  def __init__(self, images, meta_fn):

    self.images = images
    self.meta_fn = meta_fn

    threading.Thread.__init__(self)
    self.daemon = True
    self.start()

  def key(self, event):

    kc = event.keycode
    print kc

    if kc == 113: # Left
      if(self.image_idx > 0):
        self.image_idx = self.image_idx - 1
    elif kc == 114: # Right
      if(self.image_idx < len(self.images) - 1):
        self.image_idx = self.image_idx + 1
    elif kc == 39: # s
      util.save_meta(self.meta_fn, self.metadata)
    elif self.active_tool is not None:
      self.active_tool.key(event)

    self.update()

  def transform_coord(self, x, y):
    tx = int((x - self.img_w/2)/self.scale+self.img_w/2 - self.img_off_x/self.scale)
    ty = int((y - self.img_h/2)/self.scale+self.img_h/2 - self.img_off_y/self.scale)
    return tx, ty

  def mouse_b1_down(self, event):

    self.mouse_down_x, self.mouse_down_y = event.x, event.y
    self.mouse_last_x, self.mouse_last_y = event.x, event.y

    if self.active_tool is not None:
      self.active_tool.mouse_down(self.transform_coord(event.x, event.y))

  def mouse_b1_motion(self, event):

    if self.active_tool is not None:
      self.active_tool.mouse_move(self.transform_coord(event.x, event.y))
    else:
      dx, dy = self.mouse_last_x-event.x, self.mouse_last_y-event.y
      self.img_off_x, self.img_off_y = self.img_off_x - dx, self.img_off_y - dy

    self.mouse_last_x, self.mouse_last_y = event.x, event.y

    self.update()

  def mouse_b1_release(self, event):
    if self.active_tool is not None:
      self.active_tool.mouse_up(event.x, event.y)

  def mouse_wheel(self, event):

    if self.active_tool is not None:
      pass
    else:
      if event.num == 5 or event.delta == -120:
          self.scale = self.scale * 0.9
      if event.num == 4 or event.delta == 120:
          self.scale = self.scale * 1.1

    self.update()

  def terminate(self):
    util.save_meta(self.meta_fn, self.metadata)
    os._exit(0)

  def tool_change(self, event):
    w = event.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    if(value == "Pan"):
      self.active_tool = None
    elif(value == "RedBuoy"):
      self.active_tool = BuoyEditor("Red", self.get_meta, self.update)
    elif(value == "GreenBuoy"):
      self.active_tool = BuoyEditor("Green", self.get_meta, self.update)

  def run(self):

    # Window/Layout Setup
    self.root = Tk()

    self.root.protocol("WM_DELETE_WINDOW", self.terminate)
    self.root.bind("<Key>", self.key)

    self.img_h, self.img_w = self.images[0].shape[:2]

    self.w = Canvas(self.root, width=self.img_w, height=self.img_h, bd = 0, bg = 'black')
    self.w.grid(row = 0, column = 0, columnspan = 2)

    self.w.bind("<MouseWheel>", self.mouse_wheel) # Windows
    self.w.bind("<Button-4>", self.mouse_wheel) #linux
    self.w.bind("<Button-5>", self.mouse_wheel)
    self.w.bind("<Button-1>", self.mouse_b1_down)
    self.w.bind("<B1-Motion>", self.mouse_b1_motion)
    self.w.bind("<ButtonRelease-1>", self.mouse_b1_release)

    b = Button(width = 10, height = 2, text = 'Button1')
    b.grid(row = 1, column = 0)
    b2 = Button(width = 10, height = 2, text = 'Button2')
    b2.grid(row = 1,column = 1)

    listbox = Listbox(self.root, height=20)
    listbox.grid(row=0,column=2, rowspan=2, sticky="N")

    for item in ["Pan", "RedBuoy", "Gate Left", "Gate Right"]:
      listbox.insert(END, item)

    listbox.bind("<<ListboxSelect>>", self.tool_change)

    # Setup Metadata Frames
    try:
      self.metadata = util.load_meta(self.meta_fn)
    except:
      print "No Meta Data Loaded"
      self.metadata = []
      for i in xrange(len(self.images)):
        self.metadata.append({})

    #self.metadata[1]["RedBuoy"] = {"pos":(100,100), "rad":50}

    # Inital Draw
    self.update()

    self.root.mainloop()

  def get_meta(self):
    return self.metadata[self.image_idx]

  def update(self):

      # Update Image
      im = cv2.cvtColor(self.images[self.image_idx], cv2.COLOR_BGR2RGB)

      # Render metadata
      meta = self.metadata[self.image_idx]
      if("RedBuoy" in meta.keys()):
        buoy = meta["RedBuoy"]
        cv2.circle(im,tuple(buoy["pos"]),buoy["rad"],(255,0,0),2);

      # Scale image
      im = cv2.resize(im, (int(self.img_w*self.scale), int(self.img_h*self.scale)), interpolation = cv2.INTER_NEAREST)
      #im = im[0:0, self.img_w:self.img_h]

      im1 = Image.fromarray(im)
      self.img = ImageTk.PhotoImage(im1)

      self.w.create_image((self.img_w/2+self.img_off_x,self.img_h/2+self.img_off_y), image=self.img)

def main(sys_args):

  parser = argparse.ArgumentParser()
  parser.add_argument('--test-video')
  parser.add_argument('--output-data')
  args = parser.parse_known_args(sys_args)[0]

  images = util.load_video_images(args.test_video)

  mdg = MetaDataGenerator(images, args.output_data)

  while True:
    time.sleep(10)

if __name__ == "__main__":
  main(sys.argv[1:])
