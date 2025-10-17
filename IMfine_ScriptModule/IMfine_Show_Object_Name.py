import c4d

def execute():
    """
    선택된 오브젝트의 이름을 메시지 다이얼로그로 보여주는 함수
    """
    doc = c4d.documents.GetActiveDocument()
    selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    
    if not selected_objects:
        c4d.gui.MessageDialog("선택된 오브젝트가 없습니다.")
        return
    
    if len(selected_objects) == 1:
        obj_name = selected_objects[0].GetName()
        c4d.gui.MessageDialog(f"선택된 오브젝트 이름: {obj_name}")
    else:
        obj_names = [obj.GetName() for obj in selected_objects]
        names_text = "\n".join(obj_names)
        c4d.gui.MessageDialog(f"선택된 오브젝트들:\n{names_text}")

def get_script_info():
    """
    스크립트 정보를 반환하는 함수
    """
    return {
        "name": "Show Object Name",
        "description": "선택된 오브젝트의 이름을 표시합니다",
        "execute": execute
    }