import time
from subprocess import call
from threading import Thread, active_count
from picamera import PiCamera
from picamera.array import PiRGBArray
import threading_test as tt
import cv2
import io
import numpy as np
import Queue
##cmd = "python /home/pi/master-thesis/threading_test.py image"
f_report = open("Quality_Reports_Image/new_timing17_rpi3_lite.txt", "w")

def process_thread(image, counter):
    TT = tt.ThreadTest(image, 8, 4, 128, 24, 38, 4, 28, 22, counter, f_report)
    check = TT.mainprocess()

    
    
##    call([cmd], shell=True)


if __name__ == "__main__":
    camera = PiCamera()
    camera.resolution = (544, 400)
    rawCapture = PiRGBArray(camera, size = (544, 400))
    #start = time.time()
    camera.start_preview()
##    time.sleep(3)
##    camera.stop_preview()
##    time.sleep(2)
    time.sleep(5)
    counter = 0
    last = 0
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port = True):
        if last != 0:
            if (last + 0.1) - time.time() > 0:
                time.sleep((last + 0.1) - time.time())
            else:
                f_report.write('Under Real_time Point:' + str(time.time() - last) + '\n')
        start_time = time.time()
        f_report.write('Start time:' +str(start_time) + '\n')
        image = frame.array
        t = Thread(target = process_thread, args = (image, counter, ))
        t.start()
        
        rawCapture.truncate(0)
        counter += 1
        
        if counter == 100:
            break
        last = start_time
        
##    print "reached zero"
    #end = time.time()
    #f_report.write("Total time:", end - start)

    
