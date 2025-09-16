# mw_utils.py
# 유틸리티 함수 모듈
import c4d

def GetAllChildren(obj, parent=True) -> list:
    """
    입력값은 단일 오브젝트 또는 오브젝트 리스트 모두 허용합니다.
    반환값은 항상 오브젝트들의 리스트입니다.
    (Accepts single object or list of objects, always returns a list)

    :param obj: 부모 오브젝트 또는 오브젝트 리스트 :type obj: c4d.BaseObject | list[c4d.BaseObject]
    :return: 자식 오브젝트들을 포함한 리스트 :rtype: list[c4d.BaseObject]
    """
    if obj is None:
        return []
    objs = obj if isinstance(obj, list) else [obj]
    
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


def GetFullCache(obj, parent=True, deform=True) -> list:
    """
    입력값은 단일 오브젝트 또는 오브젝트 리스트 모두 허용합니다.
    DeformCache, Cache, 하위 오브젝트까지 재귀적으로 탐색하여 모든 메쉬를 리스트로 반환합니다.
    deform=False로 지정하면 DeformCache는 무시하고 Cache만 탐색합니다. (최적화용)
    (Accepts single object or list of objects, always returns a list of meshes including Cache and children. If deform=False, ignores DeformCache.)

    :param obj: 오브젝트 또는 오브젝트 리스트 :type obj: c4d.BaseObject | list[c4d.BaseObject]
    :param parent: 입력 오브젝트도 결과에 포함할지 여부 :type parent: bool
    :param deform: DeformCache도 탐색할지 여부 :type deform: bool
    :return: 최종 캐시 메쉬 오브젝트 리스트 :rtype: list[c4d.PointObject]
    """
    if obj is None:
        return []
    objs = obj if isinstance(obj, list) else [obj]
    meshes = []

    def _recurse(op):
        if op is None:
            return
        # DeformCache 우선 (옵션)
        if deform:
            tp = op.GetDeformCache()
            if tp is not None:
                _recurse(tp)
                # 하위 오브젝트는 DeformCache 내부에서만 탐색
                return
        tp2 = op.GetCache()
        if tp2 is not None:
            _recurse(tp2)
        else:
            if not op.GetBit(c4d.BIT_CONTROLOBJECT):
                if op.IsInstanceOf(c4d.Opolygon):
                    meshes.append(op)
        # 하위 오브젝트 재귀
        child = op.GetDown()
        while child is not None:
            _recurse(child)
            child = child.GetNext()

    for o in objs:
        if parent:
            _recurse(o)
        else:
            # parent=False면 하위만 탐색
            child = o.GetDown()
            while child is not None:
                _recurse(child)
                child = child.GetNext()
    return meshes