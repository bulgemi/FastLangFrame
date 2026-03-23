import base64
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage

def encode_image_to_base64(file_bytes: bytes) -> str:
    """이미지 바이트를 base64 문자열로 인코딩합니다."""
    return base64.b64encode(file_bytes).decode('utf-8')

def create_multimodal_message(text: str, image_bytes: Optional[bytes] = None) -> HumanMessage:
    """
    텍스트와 선택적 이미지를 포함하는 멀티모달 HumanMessage를 생성합니다.
    """
    if not image_bytes:
        return HumanMessage(content=text)
    
    base64_str = encode_image_to_base64(image_bytes)
    
    # LangChain 멀티모달 메시지 포맷 구성
    content: List[Dict[str, Any]] = [
        {"type": "text", "text": text},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_str}"}
        }
    ]
    
    return HumanMessage(content=content)  # ty:ignore[no-matching-overload]
