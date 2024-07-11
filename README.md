# HeatmapUI

A user-interface created with python's tkinter library, designed to visualize the number of people in each specified room of a place.
Using csv files including data of room outline coordinates, hour, and # of people, the program is customizable to represent any place

## Usage

Before running the program, ensure that the filenames of your csv data and image for the floor are correct.
+/- buttons are for zooming in and out, respectively
The slider scale is for adjusting which hour is drawn
The play/pause button to start/stop a slideshow of every hour

## How it works

Using tkinter's tools, a window is set up along with frames, canvases, buttons, and a scale
A canvas class is initialized, and includes functions to zoom in/out, pan, draw out data given, and scale images
Using pandas, data from a csv file is easily digested and manipulated to cultivate data of a specified hour
Functions outside of the class are established to help fluency between class functions and global functions, as well as establishing playback features for the slideshow

