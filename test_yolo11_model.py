from ultralytics import YOLO

#model = YOLO("yolo11n.pt")
model = YOLO("best.pt")
#predict from video; track function to tack item;
model("2025-12-04_16.15.12.mp4", save = True, show = True)


