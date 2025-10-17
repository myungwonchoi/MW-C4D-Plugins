import c4d

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
    return {
        "name": "Count Objects",
        "description": "선택된 오브젝트의 개수를 표시합니다",
        "tags": ["Mesh"],
        "icon": None,
        "execute": execute
    }