CV Boilerplate Test Code
========================
[![Video Ovewview of this github](https://img.youtube.com/vi/4Iy04A7LdbQ/0.jpg)](https://www.youtube.com/watch?v=4Iy04A7LdbQ)

The CV boilerplate test code is broken down into several parts.

There are test videos that can be downloaded by a utility script.  All of our competition videos have been compressed at maximum quality as MP4's in the test_videos/bag folder.  There is also one video from you tube of a subs run at a lone red buoy.

To download the test videos run util/download_test_videos.py

There is the test_cv.py script.  This script loads the other test/demo scripts and connects them to the test video.  This way you can get up and running playing with open cv and doing operations on images as quickly as possible.  It takes several parameters.

This is the path to your CV Test class where you implement your process image function
--test-script=&lt;supply the path to your test script here&gt;
This is the path to the input video to your CV code
--test-video=&lt;supply the path to your test video here&gt;
If you want to generate an output video instead of just clicking through the results use this parameter
--output-video=&lt;supply the path to your output video here&gt;
If you want to draw the associated meta data of the video over your debug image you can specifiy --meta-overlay
If you want to have your algorithm scored against associated meta data specify --score
To select a metadata file to use:
--test-metadata=&lt;supply the path to your video metadata here&gt;

Remember you can specify your own parameters and decode them in the __init__ of your CVClass if you want to give tunable parameters to your code.

In src/demos/empty_cv_test there is the script test.py, this is an example script you can add code into the section labled #### CV CODE HERE and do operations on the input image from the video.  You can then draw over the image any debug information or detections of buoys and return a debug image showing what your code is seeing/thinking.

This code has an interface with 2 functions:
process_image(), this takes in an OpenCV image to analyze and returns a debug image to show what its thinking
output_dimensions(), this returns the size of your debug image, in case you want to add some extra width to show more versions of your output or rescale it.

If you run this code with no change you will simply see the video shown frame by frame.  Pressing a key will advance to the next frame.

python2.7 src/framework/test_cv.py --test-script=src/demos/empty_cv_test/test.py --test-video=test_videos/buoy/1/1.mp4

At the bare minimum to run the code you will need python2 python-opencv and python-numpy.  It was tested in an ubuntu enviorment and since Linux runs on the sub it is the best OS to do your CV code on.

If you need any help just post errors or whatever your confused about in the Computer Vision slack.

Meta Data Generator
===================
There is a Metadata generator that can be used to manualy draw featuers over the video and save them in a JSON file.  This JSON file can be used to score the accuracy of your CV code.  It works by comparing the orientation, location, and size of the detected features to those in the meta data and providing various error metrics as textual outputs.  Here is how you could run it to generate metadata for one of the videos:
python2.7 src/framework/meta_data_generator.py --test-video=test_videos/buoy/1/1.mp4 --output-data=test_videos/buoy/1/1.json

Right now it only supports the RedBuoy.  The menu on the right lets you select a tool, you can pan/zoom the image so you can more accuratly draw over features, and select one of the feature types to draw that feature to the image.  To navigate the video use the left and right arrow keys to change frames.  The s key will save the current state of the metadata as well as exiting the program.

Hough Circles Demo
==================
The hough circles demo is about as simple as it gets for doing a buoy detection.  In buoy test video 1 the only thing that really appears in the video is the red buoy so it is able to identify its circular shape, however it has many false positives when tried on other test videos but it is a good starting point to see how to make open cv do something and get back a debug image.

python2.7 src/framework/test_cv.py --test-script=src/demos/buoy/hough/hough.py --test-video=test_videos/buoy/1/1.mp4

Suggested Things To Try
====================
If you are not sure what to do one easy thing is to try a simple color thresholding.  In python this can be done as follows:
    above_bgr_thresh = [0,0,200]
    below_bgr_thresh = [150,150,255]
    matched = ((   img[:,:,0] > above_bgr_thresh[0])  \
                & (img[:,:,0] <= below_bgr_thresh[0]) \
                & (img[:,:,1] > above_bgr_thresh[1])  \
                & (img[:,:,1] <= below_bgr_thresh[1]) \
                & (img[:,:,2] > above_bgr_thresh[2])  \
                & (img[:,:,2] <= below_bgr_thresh[2]))
    print numpy.invert(matched)
    img[numpy.invert(matched)] = img[numpy.invert(matched)]/4

This code will darken any pixels in the debug image that aren't in the color threshold.  You can try and tune the threshold values to see if you can get the whole buoy to show up and no water.  This code also shows a gotya of opencv.  Its images use bgr not rgb.

My Buoy Detection Demo
======================
The buoy detection demo that I included has almost no false positives while also detecting the buoy at a considerable distance.  It is capable of detecting the Buoy color at closer distance.

It is designed by cascading several CV techniques.  First, it uses edge detection to make the image simpler,  Ideally just a circle indicating the location of the buoy.  That is then processed with MSER blob detection.  This give location and sizes of roundish blobs in the edge detected result image.  Using those blob detection a small image is cut from the larger original color image and resize to 32x32.  That feature is then classified by a Neural net to decide if it is a Buoy or not.  The Neural net is based on the character recognition Neural Net that is used by Keras (Neural Net Framework).  It was trained by creating a set of features, by simply saving all the MSER blob detected features from the video and classifying them by hand into a training set.  The next stage is a filter that makes sure the feature is in roughly the same place and same size between frames.  If the feature exists at roughly the same location for 10 frames we say that it is a real detection of a buoy.

If you want to run my cv test you will also need the demo_data which can be obtained with util/download_demo_data.py

To execute it and see the output frame by frame you can run this command from the repositorys root directory:
python2.7 src/framework/test_cv.py --test-script=src/demos/buoy/dryerzinia/dryerzinia_buoy.py --test-video=test_videos/buoy/1/1.mp4 --neural-net-model=demo_data/buoy/dryerzinia/buoy_feature_model.json --neural-net-weights=demo_data/buoy/dryerzinia/buoy_feature_model.h5

You will need to have python-opencv, python-numpy, keras and one of keras's back ends installed.

Simple Dice Feature Detectors
=============================
My scripts for detecting dice can be found in /src/demos/dice and run with a -i or --image option pointing to one of the test images in /test_videos/dice, or any other images. They technically function correctly but need a lot of cleanup.

