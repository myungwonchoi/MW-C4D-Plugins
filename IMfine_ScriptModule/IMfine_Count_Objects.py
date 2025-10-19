import c4d
import os

def execute():
    """
    선택된 오브젝트의 개수를 메시지 다이얼로그로 보여주는 함수
    """
    doc = c4d.documents.GetActiveDocument()
    selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    
    count = len(selected_objects)
    c4d.gui.MessageDialog(f"선택된 오브젝트 개수: {count}개")

def get_script_info():
    """
    스크립트 정보를 반환하는 함수
    """
    # 현재 스크립트 파일의 디렉토리 경로
    script_dir = os.path.dirname(__file__)
    guide_image_path = os.path.join(script_dir, "IMfine_Count_Objects.png")
    
    return {
        "name": "Count Objects",
        "description": "선택된 오브젝트의 개수를 표시합니다",
        "tags": ["Mesh"],
        "icon": None,
        "guide_image": guide_image_path if os.path.exists(guide_image_path) else None,
        "execute": execute
    }