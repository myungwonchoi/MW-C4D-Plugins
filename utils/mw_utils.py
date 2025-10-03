# mw_utils.py, 유틸리티 함수 모듈
import c4d # 모듈이여도 c4d는 항상 필요

def GetAllObjects(doc):
    """
    씬 내의 모든 오브젝트를 리스트로 반환합니다.
    """
    result = []
    def _collect(obj):
        while obj:
            result.append(obj)
            _collect(obj.GetDown())
            obj = obj.GetNext()
    _collect(doc.GetFirstObject())
    return result

def GetObjectsInLayer(doc, layer_obj):
    """
    주어진 레이어(layer_obj)에 할당된 모든 오브젝트를 리스트로 반환합니다.
    """
    all_objs = GetAllObjects(doc)
    return [obj for obj in all_objs if obj.GetLayerObject(doc) == layer_obj]

def GetAllChildren(objects, parent=True) -> list:
    """
    입력값은 단일 오브젝트 또는 오브젝트 리스트 모두 허용합니다.
    반환값은 항상 오브젝트들의 리스트입니다.
    (Accepts single object or list of objects, always returns a list)

    :param objects: 부모 오브젝트 또는 오브젝트 리스트 :type objects: c4d.BaseObject | list[c4d.BaseObject]
    :return: 자식 오브젝트들을 포함한 리스트 :rtype: list[c4d.BaseObject]
    """
    if objects is None:
        return []
    objs = objects if isinstance(objects, list) else [objects]
    
    children = []
    for o in objs:
        if o is None:
            continue
        if parent: children.append(o)
        child = o.GetDown()
        while child:
            children.extend(GetAllChildren(child))
            child = child.GetNext()
    return children


def GetFullCache(objects, parent=True, deform=True) -> list:
    """
    입력값은 단일 오브젝트 또는 오브젝트 리스트 모두 허용합니다.
    DeformCache, Cache, 하위 오브젝트까지 재귀적으로 탐색하여 모든 메쉬를 리스트로 반환합니다.
    deform=False로 지정하면 DeformCache는 무시하고 Cache만 탐색합니다. (최적화용)
    (Accepts single object or list of objects, always returns a list of meshes including Cache and children. If deform=False, ignores DeformCache.)

    :param objects: 오브젝트 또는 오브젝트 리스트 :type objects: c4d.BaseObject | list[c4d.BaseObject]
    :param parent: 입력 오브젝트도 결과에 포함할지 여부 :type parent: bool
    :param deform: DeformCache도 탐색할지 여부 :type deform: bool
    :return: 최종 캐시 메쉬 오브젝트 리스트 :rtype: list[c4d.PointObject]
    """
    # print("objects:", objects)
    if objects is None:
        return []
    object_list = objects if isinstance(objects, list) else [objects]
    result_meshes = []

    def _recurse(current_obj):
        if current_obj is None:
            return
        # DeformCache 우선 (옵션)
        if deform:
            deform_cache = current_obj.GetDeformCache()
            if deform_cache is not None:
                _recurse(deform_cache)
                # 하위 오브젝트는 DeformCache 내부에서만 탐색
                return
        cache_obj = current_obj.GetCache()
        if cache_obj is not None:
            _recurse(cache_obj)
        else:
            if not current_obj.GetBit(c4d.BIT_CONTROLOBJECT): # 제너레이터로 생성된 오브젝트는 무시
                if current_obj.IsInstanceOf(c4d.Opolygon):
                    result_meshes.append(current_obj)
        # 하위 오브젝트 재귀
        child_obj = current_obj.GetDown()
        while child_obj is not None:
            _recurse(child_obj)
            child_obj = child_obj.GetNext()

    for root_obj in object_list:
        if parent:
            _recurse(root_obj)
        else:
            # parent=False면 하위만 탐색
            child_obj = root_obj.GetDown()
            while child_obj is not None:
                _recurse(child_obj)
                child_obj = child_obj.GetNext()
    return result_meshes


def GetMergedObject(self, op, doc): #Deprecated
    """Create a merged clone of all input objects in a dummy document and return that merged object."""
    null = c4d.BaseObject(c4d.Onull)

    for node in op:
        aliastrans = c4d.AliasTrans()
        if not aliastrans or not aliastrans.Init(doc):
            return False
        if node.GetUp() is None:
            clone = node.GetClone(c4d.COPYFLAGS_NONE, aliastrans)
            clone.InsertUnderLast(null)
        elif node.GetUp() is not None:
            tempParent = c4d.BaseObject(c4d.Onull)
            tempParent.SetMg(node.GetUp().GetMg())
            clone = node.GetClone(c4d.COPYFLAGS_NONE, aliastrans)
            clone.InsertUnderLast(tempParent)
            tempParent.InsertUnderLast(null)
        aliastrans.Translate(True)

    doc.InsertObject(null)

    # The settings of the 'Join' tool.
    bc = c4d.BaseContainer()
    # Merge possibly existing selection tags.
    bc[c4d.MDATA_JOIN_MERGE_SELTAGS] = True

    # Execute the Join command in the dummy document.
    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_JOIN, 
                                        list=[null], 
                                        mode=c4d.MODELINGCOMMANDMODE_ALL, 
                                        bc=bc, 
                                        doc=doc, 
                                        flags=c4d.MODELINGCOMMANDFLAGS_CREATEUNDO)
    if not res:
        raise RuntimeError("Modelling command failed.")

    # The 'Join' command returns its result in the return value of SendModelingCommand()
    joinResult = res[0].GetClone()
    res[0].Remove()
    null.Remove() # Remove the null object from the dummy document.

    if not isinstance(joinResult, c4d.BaseObject):
        raise RuntimeError("Unexpected return value for Join tool.")
    if not isinstance(joinResult, c4d.PointObject):
        raise RuntimeError("Return value is not a point object.")

    return joinResult


def SelectObjects(objects, doc):
    c4d.CallCommand(12113)  # Deselect All
    for obj in objects:
        doc.AddUndo(c4d.UNDOTYPE_BITS, obj)  # 언도 추가
        doc.SetSelection(obj , mode=c4d.SELECTION_ADD)
    c4d.EventAdd()  # 뷰포트 업데이트

"""
# Note: The following function is commented out because it requires a specific plugin context to work properly.
static c4d.storage.GeGetPluginPath


"""