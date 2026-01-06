#from gz.msgs10.stringmsg_pb2 import StringMsg
from gz.msgs10.image_pb2 import Image
from gz.transport13 import Node
import os
import time
import numpy as np
from ultralytics import YOLO
import cv2
 
class camLinker():
    node = Node()
    image_topic = os.popen('gz topic --list | grep /camera_link/sensor/IMX214/image').read().split('\n')[0]
    image_rgb=np.zeros((640,360,3), np.uint8)

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
                cv2.imshow("Raw Image", cv2.resize(self.image_rgb, (640,360)))
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 27 is ESC key
                    break
                time.sleep(0.05)
            # out.write(image_rgb)
            
        except KeyboardInterrupt:
            pass
        cv2.destroyAllWindows()
        print("Done")


if __name__ == "__main__":
    linker = camLinker() 
    linker.main()

 
