import c4d
import os

def execute():
    """
    선택된 오브젝트의 타입을 메시지 다이얼로그로 보여주는 함수
    """
    doc = c4d.documents.GetActiveDocument()
    selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    
    if not selected_objects:
        c4d.gui.MessageDialog("선택된 오브젝트가 없습니다.")
        return
    
    # 오브젝트 타입 매핑 (일부 예시)
    type_names = {
        c4d.Onull: "Null Object",
        c4d.Ocube: "Cube",
        c4d.Osphere: "Sphere",
        c4d.Oplane: "Plane",
        c4d.Ocylinder: "Cylinder",
        c4d.Ocone: "Cone",
        c4d.Otorus: "Torus",
        c4d.Olight: "Light",
        c4d.Ocamera: "Camera",
        c4d.Ospline: "Spline"
    }
    
    if len(selected_objects) == 1:
        obj = selected_objects[0]
        obj_type = obj.GetType()
        type_name = type_names.get(obj_type, f"Unknown Type ({obj_type})")
        c4d.gui.MessageDialog(f"오브젝트: {obj.GetName()}\n타입: {type_name}")
    else:
        result_text = "선택된 오브젝트들의 타입:\n\n"
        for obj in selected_objects:
            obj_type = obj.GetType()
            type_name = type_names.get(obj_type, f"Unknown ({obj_type})")
            result_text += f"{obj.GetName()}: {type_name}\n"
        
        c4d.gui.MessageDialog(result_text)

def get_script_info():
    """
    스크립트 정보를 반환하는 함수
    """
    # 현재 스크립트 파일의 디렉토리 경로
    script_dir = os.path.dirname(__file__)
    guide_image_path = os.path.join(script_dir, "IMfine_Show_Object_Type.png")
    
    return {
        "name": "Show Object Type",
        "description": "선택된 오브젝트의 타입을 표시합니다",
        "tags": ["Mesh"],
        "icon": None,
        "guide_image": guide_image_path if os.path.exists(guide_image_path) else None,
        "execute": execute
    }