from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
from PIL import Image
import io
import base64
import numpy as np

app = FastAPI(title="Garbage Classification API")

# โหลดโมเดลเพียงครั้งเดียวตอนเปิด API
model = YOLO('best.pt')

@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    # 1. อ่านไฟล์รูปภาพที่ส่งมาจาก Streamlit
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    # 2. นำรูปเข้าโมเดล YOLO ทำนายผล
    results = model(image)
    
    # 3. วาดกรอบลงบนรูป (plot จะคืนค่าเป็น numpy array แบบ BGR)
    res_plotted = results[0].plot()
    
    # แปลง BGR เป็น RGB ก่อนสร้างเป็นภาพ
    res_plotted_rgb = res_plotted[:, :, ::-1]
    img_pil = Image.fromarray(res_plotted_rgb)
    
    # 4. แปลงรูปที่วาดกรอบแล้วเป็น Base64 String เพื่อส่งกลับไปให้หน้าเว็บ
    buffered = io.BytesIO()
    img_pil.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    # 5. ดึงข้อมูลว่าเจอขยะอะไรบ้าง
    detections = []
    for box in results[0].boxes:
        class_id = int(box.cls[0])
        label = model.names[class_id]
        conf = float(box.conf[0])
        detections.append({
            "label": label,
            "confidence": conf
        })
        
    # ส่งข้อมูลกลับไปเป็น JSON
    return {
        "image_base64": img_str,
        "detections": detections
    }


    # รัน API ด้วยคำสั่ง: uvicorn api:app --reload