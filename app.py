import base64
import io
import boto3
import streamlit as st
from PIL import Image
import os
import json

# AWS SDK Client Setup
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")  # Sửa lại region nếu cần

# Constants
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
KNOWLEDGE_BASE_ID = "QSDX9TVNUP"
MODEL_ARN = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0" 

# Streamlit Page Setup
st.set_page_config(
    layout="wide",
    page_title="Transaction Assistance Chatbot",
    page_icon="💳"
)

def image_to_base64(image):
    """Chuyển đổi ảnh thành base64."""
    buffered = io.BytesIO()  # Đảm bảo đã import io
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def process_image_and_text(image, user_text):
    """Xử lý hình ảnh và văn bản người dùng, gửi yêu cầu tới AWS Bedrock."""
    # Chuyển hình ảnh thành base64
    img_base64 = image_to_base64(image)

    # Tạo payload cho Bedrock với hình ảnh base64 và văn bản người dùng
    payload = {
        "modelArn": MODEL_ARN,
        "inputs": [
            {
                "name": "image",
                "value": img_base64
            },
            {
                "name": "user_input",
                "value": user_text
            }
        ]
    }

    # Gửi yêu cầu tới Bedrock và nhận kết quả
    response = bedrock_client.invoke_model(**payload)

    # Xử lý dữ liệu trả về từ Bedrock (giả sử đây là văn bản đã được xử lý)
    if 'body' in response:
        result = json.loads(response['body'].read().decode('utf-8'))
        return result.get("response_text", "Không có kết quả")
    return "Lỗi khi nhận kết quả từ Bedrock"

def submit_callback(image, user_text):
    """Hàm xử lý khi người dùng nhấn nút submit."""
    extracted_text = process_image_and_text(image, user_text)
    st.write(f"Thông tin truy vấn từ Bedrock: {extracted_text}")
    
    # Ở đây bạn có thể truy vấn vào Knowledge Base (ví dụ OpenSearch)
    # và trả về kết quả truy vấn cho người dùng

def main():
    """Chạy ứng dụng Streamlit."""
    st.title("OCR và Truy Vấn Knowledge Base")
    
    # Upload hình ảnh từ người dùng
    uploaded_image = st.file_uploader("Tải lên hình ảnh (JPEG, PNG, JPG)", type=ALLOWED_EXTENSIONS)
    user_input = st.text_input("Nhập văn bản mô tả của bạn")
    
    if uploaded_image is not None and user_input:
        image = Image.open(uploaded_image)
        
        # Thêm nút submit để thực hiện xử lý khi nhấn
        if st.button("Submit"):
            submit_callback(image, user_input)

if __name__ == "__main__":
    main()
