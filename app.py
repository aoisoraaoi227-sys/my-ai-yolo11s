import streamlit as st
import requests
from PIL import Image
import io
import base64

# กำหนด URL ของ API
API_URL = "http://localhost:8000/predict/"

# --- กำหนดชื่อเต็มภาษาไทยของขยะ ---
THAI_NAMES = {
    "office_paper": "กระดาษสำนักงาน (กระดาษขาว-ดำ)",
    "cardboard": "กระดาษลัง",
    "pet_bottle": "ขวดพลาสติก PET (ขวดใส)",
    "hdpe_bottle": "ขวดพลาสติก HDPE (ขวดขุ่น/ขวดน้ำยา)",
    "alu_can": "กระป๋องอลูมิเนียม",
    "tin_can": "กระป๋องเหล็ก/สังกะสี",
    "clear_glass": "ขวดแก้วใส",
    "colored_glass": "ขวดแก้วสี",
    "scrap_metal": "เศษโลหะ/เศษเหล็ก",
    "uht_carton": "กล่องเครื่องดื่ม UHT"
}

# --- กำหนดราคารับซื้อขยะโดยประมาณ (บาท/กิโลกรัม) ---
PRICE_LIST = {
    "office_paper": "3 - 5",
    "cardboard": "2 - 4",
    "pet_bottle": "8 - 10",
    "hdpe_bottle": "10 - 15",
    "alu_can": "40 - 50",
    "tin_can": "3 - 5",
    "clear_glass": "1 - 2",
    "colored_glass": "0.5 - 1",
    "scrap_metal": "8 - 10",
    "uht_carton": "1 - 2"
}

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="การคัดแยกขยะด้วยรูปภาพ", layout="centered")

# CSS ปรับแต่งสี
st.markdown("""
    <style>
    .main {
        background-color: #E2F9C2;
    }
    .header-box {
        background-color: #61D384;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: black;
        font-size: 30px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ส่วนหัวข้อ ---
st.markdown('<div class="header-box">♻️ AI ตรวจจับขยะเพื่อธุรกิจรีไซเคิลในระดับชุดชน</div>', unsafe_allow_html=True)

# --- ส่วนเนื้อหาหลัก ---
with st.container():
    st.write("### นำรูปที่ต้องการมาใส่")
    
    uploaded_file = st.file_uploader("อัปโหลดรูปเพื่อทำนายผล", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='รูปภาพที่อัปโหลด', use_container_width=True)
        
        if st.button('ตกลง'):
            with st.spinner('กำลังส่งรูปไปให้ API ประมวลผล...'):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(API_URL, files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        img_bytes = base64.b64decode(data["image_base64"])
                        result_image = Image.open(io.BytesIO(img_bytes))
                        
                        st.write("### แสดงข้อมูลขยะในรูปออกมาว่าเป็นขยะอะไร")
                        st.image(result_image, caption='ผลการทำนายจาก API', use_container_width=True)
                        
                        # --- ส่วนแสดงผลลัพธ์และนับจำนวน ---
                        if data["detections"]:
                            # สร้าง Dictionary เพื่อเก็บจำนวนขยะแต่ละประเภท
                            item_counts = {}
                            
                            st.write("#### รายละเอียดแต่ละชิ้น")
                            for det in data["detections"]:
                                label_en = det['label']
                                conf = det['confidence']
                                
                                label_th = THAI_NAMES.get(label_en, label_en)
                                price = PRICE_LIST.get(label_en, "ไม่มีข้อมูล")
                                
                                # นับจำนวนขยะ (ถ้ามีชื่อนี้ใน dict แล้วให้บวก 1 ถ้ายังไม่มีให้ตั้งค่าเป็น 1)
                                if label_th in item_counts:
                                    item_counts[label_th] += 1
                                else:
                                    item_counts[label_th] = 1
                                
                                st.success(f"ตรวจพบ: **{label_th}** (ความมั่นใจ: {conf:.2f}) | 💰 **ราคาประมาณ: {price} บาท/กก.**")
                            
                            # --- ส่วนแสดงสรุปจำนวนรวม ---
                            st.write("---") # เส้นคั่น
                            st.write("### 📊 สรุปจำนวนขยะที่พบ")
                            for item_name, count in item_counts.items():
                                st.info(f"🔹 **{item_name}**: จำนวน {count} ชิ้น")
                                
                        else:
                            st.warning("ไม่พบขยะในรูปภาพนี้")
                    else:
                        st.error(f"เกิดข้อผิดพลาดจาก API: {response.status_code}")
                
                except requests.exceptions.ConnectionError:
                    st.error("ไม่สามารถเชื่อมต่อกับ API ได้ กรุณาตรวจสอบว่าเปิด API Server (FastAPI) แล้วหรือยัง")
    else:
        st.info("กรุณาอัปโหลดไฟล์ภาพด้านบน")


        # รัน Streamlit ด้วยคำสั่ง: streamlit run app.py