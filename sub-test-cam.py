#from gz.msgs10.stringmsg_pb2 import StringMsg
from gz.msgs10.image_pb2 import Image
from gz.transport13 import Node
import os
import time
import numpy as np
from ultralytics import YOLO
import cv2
import argparse
 
class camLinker():
    parser = argparse.ArgumentParser(description="Run a YOLO model with a provided model path.")
    parser.add_argument(
        "--model",
        type=str,
        required=False,
        help="Path to the YOLO model (.pt file)"
    )
    args = parser.parse_args()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  
    out = cv2.VideoWriter('footage-3.avi',fourcc, 4, (640,360))
    #load model
    model = YOLO(args.model)  # load a partially trained model
    node = Node()
    image_topic = os.popen('gz topic --list | grep /camera_link/sensor/IMX214/image').read().split('\n')[0]
    image_rgb=np.zeros((640,360,3), np.uint8)
    detect_result=np.ones((640,360,3), np.uint8)



    def image_detection(self, msg: Image):
        self.detect_result = self.model(cv2.resize(self.image_rgb, (640,360)))[0]  # frame as input
        # plot the detect_result on the frame
        self.detect_result = self.detect_result.plot()
        # Exit the loop if 'q' is pressed
    # if cv2.waitKey(0):
    #     return #end this funciton

    def imagemsg_cb(self, msg: Image, dimension=(960,540)):
        image_data = np.frombuffer(msg.data, dtype=np.uint8)
        image = image_data.reshape((msg.height, msg.width, 3))
        self.image_rgb = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    def main(self):
        try:
            while True:
                #print("Unsubcribe done" if self.node.unsubscribe(self.image_topic) else "Nope")
                self.node.unsubscribe(self.image_topic)
                self.node.subscribe(msg_type=Image, topic=self.image_topic, callback=lambda msg: self.imagemsg_cb(msg=msg))
                cv2.imshow("Raw Image", cv2.resize(self.image_rgb, (320,180)))
                cv2.waitKey(1)
                self.image_detection(self.image_rgb)
                cv2.imshow("Detection", cv2.resize(self.detect_result, (480,270)))
                cv2.waitKey(1)
                time.sleep(0.05)
            # out.write(image_rgb)
            
        except KeyboardInterrupt:
            pass
        cv2.destroyAllWindows()
        self.out.release()
        print("Done")


if __name__ == "__main__":
    linker = camLinker() 
    linker.main()

 
