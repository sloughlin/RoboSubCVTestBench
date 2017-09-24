#!/usr/bin/python2.7

import argparse
import cv2
import sys
import imp
import json
import numpy
import time
import util

def main(sys_args):

  parser = argparse.ArgumentParser()
  parser.add_argument('--test-script')
  parser.add_argument('--test-video')
  parser.add_argument('--test-metadata')
  parser.add_argument('--output-video')
  parser.add_argument('--score', action='store_true', default=False)
  parser.add_argument('--overlay-meta', action='store_true', default=False)
  args = parser.parse_known_args(sys_args)[0]

  test_script = imp.load_source('CVModule', args.test_script)
  cv_test = test_script.CVModule(sys_args)

  images = util.load_video_images(args.test_video)
  if(args.test_metadata is not None):
    v_meta = util.load_meta(args.test_metadata)

  debug_video = False
  if args.output_video is not None:
    debug_video = True
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter(args.output_video,fourcc, 30.0, cv_test.output_dimensions())

  if args.score:
    start_time = time.time()

  for  i in xrange(len(images)):

    image = images[i]
    debug_image = cv_test.process_image(image)

    if args.overlay_meta:
      if "RedBuoy" in v_meta[i].keys():
        pos = tuple(v_meta[i]["RedBuoy"]["pos"])
        rad = v_meta[i]["RedBuoy"]["rad"]
        cv2.circle(debug_image, pos, rad, (55, 55, 150), 2)
        cv2.circle(debug_image, pos, rad, (200, 200, 250), 1)

    # Note: when this code is integrating with the sub we will
    # publish frames to a topic instead of showing debug images
    if debug_video:
      # write debug image to file
      out.write(debug_image)
    elif args.score:
      pass
    else:
      # Show user debug image
      cv2.imshow('debug_image', debug_image)
      cv2.waitKey(0)

  if args.score:
    end_time = time.time()

  if args.score:

    t_meta = cv_test.get_meta()

    stats = {"total":0,"miss":0,"false":0,"size_error":0,"good":0}

    for i in xrange(len(v_meta)):
      v_rb = None
      t_rb = None
      if "RedBuoy" in v_meta[i].keys():
        v_rb = v_meta[i]["RedBuoy"]
        stats["total"] = stats["total"]+1
      if len(t_meta) > i and "RedBuoy" in t_meta[i].keys():
        t_rb = t_meta[i]["RedBuoy"]

      if v_rb is None and t_rb is not None:
        stats["false"] = stats["false"]+1
      elif t_rb is None and v_rb is not None:
        stats["miss"] = stats["miss"]+1
      elif v_rb is not None and t_rb is not None:
        pd = util.percent_difference(v_rb["rad"], t_rb["rad"])
        dist = util.distance(v_rb["pos"], t_rb["pos"])
        if dist > v_rb["rad"]:
          stats["false"] = stats["false"]+1
        elif pd > 80.0:
          stats["size_error"] = stats["size_error"]+1
        else:
          stats["good"] = stats["good"]+1

    print("Script:  %s" % args.test_script)
    print("Runtime: %.2fs" % (end_time - start_time))
    print("")
    print("Red Buoy:")
    print("  Detected: %.2f%%" % (float(stats["good"])/float(stats["total"])*100.0))
    print("  Accuracy: %.2f%%" % (float(stats["good"])/float(stats["good"]+stats["false"])*100.0))
    print("")
    print("  Total Detections Expected: %d" % stats["total"])
    print("  Good Detections:           %d" % stats["good"])
    print("  Missed Detections:         %d" % stats["miss"])
    print("  False Detections:          %d" % stats["false"])
    print("  Bad Size:                  %d" % stats["size_error"])

  if debug_video:
    cap.release()
    out.release()

if __name__ == "__main__":
  main(sys.argv[1:])
