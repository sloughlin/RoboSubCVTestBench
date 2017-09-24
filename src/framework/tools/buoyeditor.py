import numpy

class BuoyEditor():

  def __init__(self, color, get_meta, update):
    self.color = color
    self.get_meta = get_meta
    self.update = update

  def key(self, event):

    kc = event.keycode

    meta = self.get_meta()

    if kc == 40: # d
      if(self.color+"Buoy" in meta.keys()):
        del meta[self.color+"Buoy"]

  def mouse_down(self, pos):
    x, y = pos
    meta = self.get_meta()

    if(self.color+"Buoy" in meta.keys()):
      # Adjust existing
      buoy = meta[self.color+"Buoy"]
      buoy["pos"] = (x, y)
    else:
      # Make new
      meta[self.color+"Buoy"] = {"pos":(x,y), "rad":1}

    self.update()

  def mouse_move(self, pos):
    x, y = pos
    meta = self.get_meta()

    if(self.color+"Buoy" in meta.keys()):
      # Adjust existing
      buoy = meta[self.color+"Buoy"]
      p = buoy["pos"]
      buoy["rad"] = int(numpy.sqrt((p[0]-x)**2 + (p[1]-y)**2))
    else:
      # Make new
      meta[self.color+"Buoy"] = {"pos":(x,y), "rad":1}

    self.update()

  def mouse_up(self, x, y):
    pass
