import c4d
import os
import glob
import importlib.util
import sys

# Plugin ID
PLUGIN_ID = 1066547

# Column IDs
COL_NAME = 0
COL_DESCRIPTION = 1

# 사용 가능한 태그 목록 - 순서대로 탭에 표시
AVAILABLE_TAGS = ["Mesh", "Animation", "Material", "Naming"]

# 각 태그의 UI ID (자동 생성)
TAG_ID_MAP = {
    "All": 1300,  # "All"은 항상 첫 번째
}
# 나머지 태그들의 ID 자동 할당
for idx, tag in enumerate(AVAILABLE_TAGS):
    TAG_ID_MAP[tag] = 1301 + idx

class ScriptItem(object):
    """TreeView의 각 스크립트를 나타내는 객체"""
    
    def __init__(self, script_key, script_info):
        self.script_key = script_key
        self.name = script_info.get('name', script_key)
        self.description = script_info.get('description', '')
        self.tags = script_info.get('tags', [])
        self.icon = script_info.get('icon', None)
        self.guide_image = script_info.get('guide_image', None)
        self.execute_func = script_info.get('execute', None)
        self.selected = False
    
    @property
    def IsSelected(self):
        """선택 상태 반환"""
        return self.selected
    
    def Select(self):
        """항목 선택"""
        self.selected = True
    
    def Deselect(self):
        """항목 선택 해제"""
        self.selected = False
    
    def Execute(self):
        """스크립트 실행"""
        if self.execute_func and callable(self.execute_func):
            try:
                self.execute_func()
            except Exception as e:
                c4d.gui.MessageDialog(f"스크립트 실행 중 오류가 발생했습니다:\n{str(e)}")
        else:
            c4d.gui.MessageDialog(f"스크립트 '{self.name}'의 실행 함수를 찾을 수 없습니다.")
    
    def __repr__(self):
        return f"ScriptItem({self.name})"
    
    def __str__(self):
        return self.name



class IMfineTreeViewFunctions(c4d.gui.TreeViewFunctions):
    """TreeView를 위한 함수들"""
    
    def __init__(self, dialog=None):
        self.items_list = []
        self.dialog = dialog  # 다이얼로그 참조 저장
        
        # 색상 설정
        self.color_item_normal = c4d.COLOR_TEXT
        self.color_item_selected = c4d.COLOR_TEXT_SELECTED
        self.color_background_normal = c4d.COLOR_BG_DARK2
        self.color_background_alternate = c4d.COLOR_BG_DARK1
        self.color_background_selected = c4d.COLOR_BG_HIGHLIGHT
        
        # 레이아웃 설정
        self.line_height = 26  # 각 행의 높이
        self.col_name_width = 200  # 이름 컬럼 기본 너비
        self.col_description_width = 300  # 설명 컬럼 기본 너비
        self.col_padding = 20  # 컬럼 내부 여유 공간
        self.text_offset_x = 5  # 텍스트 X 오프셋
        self.text_offset_y = 6  # 텍스트 Y 오프셋
    
    def SetItemsList(self, items_list):
        """스크립트 아이템 리스트를 설정합니다"""
        self.items_list = items_list
    
    def GetFirst(self, root, userdata):
        """첫 번째 항목을 반환합니다"""
        return self.items_list[0] if len(self.items_list) else None
    
    def GetNext(self, root, userdata, obj):
        """다음 항목을 반환합니다"""
        try:
            idx = self.items_list.index(obj)
            if idx + 1 < len(self.items_list):
                return self.items_list[idx + 1]
        except (ValueError, IndexError):
            pass
        return None
    
    def GetPred(self, root, userdata, obj):
        """이전 항목을 반환합니다"""
        try:
            idx = self.items_list.index(obj)
            if idx > 0:
                return self.items_list[idx - 1]
        except (ValueError, IndexError):
            pass
        return None
    
    def GetDown(self, root, userdata, obj):
        """하위 항목을 반환합니다 (평면 리스트이므로 None)"""
        return None
    
    def GetId(self, root, userdata, obj):
        """항목의 고유 ID를 반환합니다"""
        return hash(obj)
    
    def GetLineHeight(self, root, userdata, obj, col, area):
        """라인 높이를 반환합니다"""
        return self.line_height
    
    def IsResizeColAllowed(self, root, userdata, lColID):
        """컬럼 리사이즈 허용"""
        return True
    
    def IsTristate(self, root, userdata):
        """Tristate 사용 안 함"""
        return False
    
    def GetColumnWidth(self, root, userdata, obj, col, area):
        """컬럼 너비를 반환합니다"""
        if col == COL_NAME:
            if obj:
                return area.DrawGetTextWidth(obj.name) + self.col_padding
            return self.col_name_width
        elif col == COL_DESCRIPTION:
            if obj:
                return area.DrawGetTextWidth(obj.description) + self.col_padding
            return self.col_description_width
        return 100
    
    def GetHeaderColumnWidth(self, root, userdata, col, area):
        """헤더 컬럼 너비를 반환합니다"""
        return self.GetColumnWidth(root, userdata, None, col, area)
    
    def DrawCell(self, root, userdata, obj, col, drawinfo, bgColor):
        """셀을 그립니다 - 선택 상태에 따라 색상 변경"""
        if not obj:
            return
        
        # 텍스트 결정
        if col == COL_NAME:
            text = obj.name
        elif col == COL_DESCRIPTION:
            text = obj.description
        else:
            text = ''
        
        canvas = drawinfo["frame"]
        xpos = drawinfo["xpos"]
        ypos = drawinfo["ypos"]
        
        # 선택 상태에 따라 텍스트 색상 변경
        if obj.IsSelected:
            txtColorDict = canvas.GetColorRGB(self.color_item_selected)
        else:
            txtColorDict = canvas.GetColorRGB(self.color_item_normal)
        
        txtColorVector = c4d.Vector(
            txtColorDict["r"] / 255.0,
            txtColorDict["g"] / 255.0,
            txtColorDict["b"] / 255.0
        )
        
        # canvas.DrawSetFont(c4d.FONT_BIG) # 기본보다 큰 폰트 크기
        canvas.DrawSetTextCol(txtColorVector, bgColor)
        canvas.DrawText(text, xpos + self.text_offset_x, ypos + self.text_offset_y)

    
    def Select(self, root, userdata, obj, mode):
        """항목 선택 처리"""
        if mode == c4d.SELECTION_NEW:
            # 새로운 선택: 기존 선택 모두 해제
            for item in self.items_list:
                item.Deselect()
            obj.Select()
        elif mode == c4d.SELECTION_ADD:
            # 선택 추가 (Ctrl+클릭)
            obj.Select()
        elif mode == c4d.SELECTION_SUB:
            # 선택 제거
            obj.Deselect()
        
        # 다이얼로그에 선택 변경 알림
        print(f"IMfine Tool [DEBUG]: Select 함수 - dialog: {self.dialog}, obj: {obj}")
        if self.dialog and hasattr(self.dialog, 'UpdateGuideImage'):
            print(f"IMfine Tool [DEBUG]: UpdateGuideImage 호출 준비, obj.IsSelected: {obj.IsSelected if obj else 'obj is None'}")
            try:
                self.dialog.UpdateGuideImage(obj)
                print("IMfine Tool [DEBUG]: UpdateGuideImage 호출 성공")
            except Exception as e:
                print(f"IMfine Tool [ERROR]: 가이드 이미지 업데이트 오류 - {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"IMfine Tool [DEBUG]: UpdateGuideImage 호출 불가 - dialog: {self.dialog}, hasattr: {hasattr(self.dialog, 'UpdateGuideImage') if self.dialog else 'N/A'}")
    
    def IsSelected(self, root, userdata, obj):
        """항목이 선택되었는지 확인"""
        return obj.IsSelected
    
    def GetName(self, root, userdata, obj):
        """항목 이름을 반환합니다 (LV_TREE 타입용)"""
        return obj.name if obj else ''
    
    def SetName(self, root, userdata, obj, name):
        """항목 이름 설정 (사용 안 함)"""
        pass
    
    def IsOpened(self, root, userdata, obj):
        """항목이 열려있는지 (평면 리스트이므로 항상 False)"""
        return False
    
    def Open(self, root, userdata, obj, onoff):
        """항목 열기/닫기 (사용 안 함)"""
        pass
    
    def GetDragType(self, root, userdata, obj):
        """드래그 타입 (드래그 사용 안 함)"""
        return c4d.NOTOK
    
    def DragStart(self, root, userdata, obj):
        """드래그 시작 (사용 안 함)"""
        return c4d.NOTOK
    
    def AcceptDragObject(self, root, userdata, obj, dragtype, dragobject):
        """드래그 오브젝트 수락 (사용 안 함)"""
        return c4d.INSERT_NONE
    
    def InsertObject(self, root, userdata, obj, dragtype, dragobject, insertmode, bCopy):
        """오브젝트 삽입 (사용 안 함)"""
        pass
    
    def DoubleClick(self, root, userdata, obj, col, mouseinfo):
        """더블클릭 이벤트 - 스크립트 실행"""
        if obj:
            obj.Execute()
        return True
    
    def DeletePressed(self, root, userdata):
        """Delete 키 처리 (사용 안 함)"""
        pass
    
    def GetBackgroundColor(self, root, userdata, obj, line, col):
        """셀의 배경색을 반환합니다"""
        if not obj:
            return
        
        if obj.IsSelected:
            bg_color = self.color_background_selected
        else:
            if line % 2 == 0:
                bg_color = self.color_background_normal
            else:
                bg_color = self.color_background_alternate
        
        return bg_color



class IMfineToolDialog(c4d.gui.GeDialog):
    """IMfine Tool 메인 다이얼로그"""
    
    # UI IDs
    ID_MAIN_GROUP = 1000
    ID_FILTER_TAB = 1050
    ID_TREEVIEW = 1100
    ID_REFRESH_BUTTON = 1200
    ID_GUIDE_TEXT = 1250
    ID_GUIDE_IMAGE = 1260
    
    def __init__(self):
        super().__init__()
        self.scripts = {}
        self.treeview = None
        self.treeview_funcs = IMfineTreeViewFunctions(dialog=self)  # self 참조 전달
        self.current_filter = "All"
        self.guide_bitmap_button = None
        self.current_guide_image = None
        self.LoadScripts()
    
    def LoadScripts(self):
        """IMfine_ScriptModule 폴더에서 모든 .py 스크립트를 로드합니다"""
        self.scripts.clear()
        
        # 현재 플러그인 파일의 디렉토리 경로 가져오기
        plugin_dir = os.path.dirname(__file__)
        script_module_dir = os.path.join(plugin_dir, "IMfine_ScriptModule")
        
        if not os.path.exists(script_module_dir):
            print(f"IMfine Tool: 스크립트 모듈 디렉토리를 찾을 수 없습니다: {script_module_dir}")
            return
        
        # glob을 사용하여 모든 .py 파일 찾기
        script_pattern = os.path.join(script_module_dir, "*.py")
        script_files = glob.glob(script_pattern)
        
        for script_file in script_files:
            try:
                # 파일명에서 확장자 제거
                script_name = os.path.splitext(os.path.basename(script_file))[0]
                
                # 동적으로 모듈 로드
                spec = importlib.util.spec_from_file_location(script_name, script_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # get_script_info 함수가 있는지 확인
                    if hasattr(module, 'get_script_info'):
                        script_info = module.get_script_info()
                        # 태그가 없으면 빈 리스트 설정
                        if 'tags' not in script_info:
                            script_info['tags'] = []
                        if 'icon' not in script_info:
                            script_info['icon'] = None
                        
                        # 가이드 이미지 경로 자동 설정
                        if 'guide_image' not in script_info:
                            guide_image_path = os.path.join(script_module_dir, f"{script_name}.png")
                            if os.path.exists(guide_image_path):
                                script_info['guide_image'] = guide_image_path
                            else:
                                script_info['guide_image'] = None
                        
                        self.scripts[script_name] = script_info
                        print(f"IMfine Tool: 스크립트 로드됨 - {script_info['name']}")
                        print(f"IMfine Tool [DEBUG]: - guide_image: {script_info.get('guide_image', 'None')}")
                    else:
                        print(f"IMfine Tool: get_script_info 함수를 찾을 수 없습니다 - {script_name}")
                        
            except Exception as e:
                print(f"IMfine Tool: 스크립트 로드 실패 - {script_file}: {e}")
    
    def CreateLayout(self):
        """다이얼로그 레이아웃 생성"""
        self.SetTitle("IMfine Tool")
        
        # 메인 그룹
        self.GroupBegin(self.ID_MAIN_GROUP, c4d.BFH_SCALEFIT, cols=1)
        self.GroupBorderSpace(10, 10, 10, 10)
        
        # 타이틀
        self.AddStaticText(0, c4d.BFH_CENTER, name="IMfine Cinema4D Utility Tool", borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        
        # 필터 탭 추가 (동적 생성)
        bc = c4d.BaseContainer()
        bc.SetBool(c4d.QUICKTAB_SHOWSINGLE, True)
        bc.SetBool(c4d.QUICKTAB_SPRINGINGFOLDERS, False)
        self.filter_tab = self.AddCustomGui(self.ID_FILTER_TAB, c4d.CUSTOMGUI_QUICKTAB, '',
                                           c4d.BFH_SCALEFIT, 0, 0, bc)
        
        if self.filter_tab:
            # "All" 탭 먼저 추가
            self.filter_tab.AppendString(TAG_ID_MAP["All"], "All", True)
            
            # AVAILABLE_TAGS에서 동적으로 탭 추가
            for tag in AVAILABLE_TAGS:
                self.filter_tab.AppendString(TAG_ID_MAP[tag], tag, False)
        
        # 새로고침 버튼
        self.AddButton(self.ID_REFRESH_BUTTON, c4d.BFH_SCALEFIT, name="스크립트 새로고침")
        
        # 구분선
        self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT)
        
        # TreeView 추가 및 설정
        customgui = c4d.BaseContainer()
        customgui.SetBool(c4d.TREEVIEW_BORDER, True) # 테두리 표시
        customgui.SetBool(c4d.TREEVIEW_HAS_HEADER, True) # 헤더 표시
        customgui.SetBool(c4d.TREEVIEW_HIDE_LINES, True) # 왼쪽 선 숨기기
        customgui.SetBool(c4d.TREEVIEW_RESIZE_HEADER, True) # 컬럼 크기 조절 허용
        customgui.SetBool(c4d.TREEVIEW_MOVE_COLUMN, False) # 컬럼 이동 방지
        customgui.SetBool(c4d.TREEVIEW_FIXED_LAYOUT, False) # 가변 높이 허용
        customgui.SetBool(c4d.TREEVIEW_NOENTERRENAME, True) # 엔터로 이름 변경 방지
        customgui.SetBool(c4d.TREEVIEW_NO_MULTISELECT, True) # 다중 선택 불가
        # customgui.SetBool(c4d.TREEVIEW_ALTERNATE_BG, False) # GetBackgroundColor 사용하므로 False

        
        self.treeview = self.AddCustomGui(self.ID_TREEVIEW, c4d.CUSTOMGUI_TREEVIEW, "",
                                         c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 100, customgui)
        
        if self.treeview:
            # TreeView Functions 설정
            self.treeview.SetRoot(self.treeview, self.treeview_funcs, None)
            self.PopulateTreeView()
        
        # 구분선
        self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT)
        
        # Guide 섹션
        self.AddStaticText(self.ID_GUIDE_TEXT, c4d.BFH_LEFT, name="Guide", borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        
        # Guide 이미지 표시용 BitmapButton
        print("IMfine Tool [DEBUG]: BitmapButton 생성 시작")
        settings = c4d.BaseContainer()
        settings[c4d.BITMAPBUTTON_BUTTON] = False
        settings[c4d.BITMAPBUTTON_BORDER] = False
        settings[c4d.BITMAPBUTTON_TOGGLE] = False
        settings[c4d.BITMAPBUTTON_DISABLE_FADING] = True
        settings[c4d.BITMAPBUTTON_ICONID1] = c4d.Ocube # 기본 아이콘 설정

        print(f"IMfine Tool [DEBUG]: BitmapButton 설정: {settings}")
        
        self.guide_bitmap_button = self.AddCustomGui(
            self.ID_GUIDE_IMAGE, 
            c4d.CUSTOMGUI_BITMAPBUTTON, 
            "",
            c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 
            600, 300,
            settings
        )
        
        if self.guide_bitmap_button:
            print("IMfine Tool [DEBUG]: BitmapButton 생성 성공")
            # 빈 비트맵 생성 (가이드 이미지 선택 전까지 비어있음)
            print("IMfine Tool [DEBUG]: 초기 빈 상태로 유지")
        else:
            print("IMfine Tool [DEBUG]: BitmapButton 생성 실패")
        
        self.GroupEnd()
        
        return True
    
    def GetFilteredScripts(self):
        """현재 필터에 따라 스크립트 목록을 반환합니다"""
        if self.current_filter == "All":
            return self.scripts
        
        filtered = {}
        for key, script_info in self.scripts.items():
            if self.current_filter in script_info.get('tags', []):
                filtered[key] = script_info
        return filtered
    
    def PopulateTreeView(self):
        """TreeView에 스크립트 목록을 채웁니다"""
        if not self.treeview:
            return
        
        # TreeView 초기화
        layout = c4d.BaseContainer()
        layout.SetLong(COL_NAME, c4d.LV_USER)
        layout.SetLong(COL_DESCRIPTION, c4d.LV_USER)
        self.treeview.SetLayout(2, layout)
        
        # 헤더 설정
        self.treeview.SetHeaderText(COL_NAME, "Script Name")
        self.treeview.SetHeaderText(COL_DESCRIPTION, "Description")
        
        # 데이터 준비
        filtered_scripts = self.GetFilteredScripts()
        items_list = []
        
        for script_key, script_info in filtered_scripts.items():
            item = ScriptItem(script_key, script_info)
            items_list.append(item)
        
        # TreeView Functions에 아이템 리스트 설정
        self.treeview_funcs.SetItemsList(items_list)
        
        # TreeView 새로고침
        self.treeview.Refresh()
    
    def RefreshTreeView(self):
        """TreeView를 새로고침합니다"""
        if self.treeview:
            self.PopulateTreeView()
    
    def UpdateGuideImage(self, script_item):
        """가이드 이미지를 업데이트합니다"""
        print(f"IMfine Tool [DEBUG]: UpdateGuideImage 호출됨, script_item: {script_item}")
        
        if not self.guide_bitmap_button:
            print("IMfine Tool [DEBUG]: guide_bitmap_button이 None입니다")
            return
        
        print(f"IMfine Tool [DEBUG]: guide_bitmap_button 존재함: {self.guide_bitmap_button}")
        
        if script_item and script_item.guide_image and os.path.exists(script_item.guide_image):
            print(f"IMfine Tool [DEBUG]: 가이드 이미지 경로: {script_item.guide_image}")
            print(f"IMfine Tool [DEBUG]: 파일 존재 확인: {os.path.exists(script_item.guide_image)}")
            
            # 가이드 이미지 로드
            bitmap = c4d.bitmaps.BaseBitmap()
            print(f"IMfine Tool [DEBUG]: BaseBitmap 생성됨: {bitmap}")
            
            result = bitmap.InitWith(script_item.guide_image)
            print(f"IMfine Tool [DEBUG]: InitWith 결과: {result}")
            
            if result[0] == c4d.IMAGERESULT_OK:
                print("IMfine Tool [DEBUG]: 이미지 로드 성공")
                self.guide_bitmap_button.SetImage(bitmap, False)
                print("IMfine Tool [DEBUG]: SetImage 완료")
                self.current_guide_image = script_item.guide_image
            else:
                print(f"IMfine Tool [DEBUG]: 이미지 로드 실패, 결과 코드: {result[0]}")
                # 이미지 로드 실패 시 빈 비트맵
                empty_bitmap = c4d.bitmaps.BaseBitmap()
                empty_bitmap.Init(600, 300)
                self.guide_bitmap_button.SetImage(empty_bitmap, False)
                print("IMfine Tool [DEBUG]: 빈 비트맵 설정 완료")
                self.current_guide_image = None
        else:
            print(f"IMfine Tool [DEBUG]: 가이드 이미지 없음")
            if script_item:
                print(f"IMfine Tool [DEBUG]: - script_item.guide_image: {script_item.guide_image}")
                if script_item.guide_image:
                    print(f"IMfine Tool [DEBUG]: - 파일 존재: {os.path.exists(script_item.guide_image)}")
            
            # 가이드 이미지가 없으면 빈 비트맵
            empty_bitmap = c4d.bitmaps.BaseBitmap()
            empty_bitmap.Init(600, 300)
            self.guide_bitmap_button.SetImage(empty_bitmap, False)
            print("IMfine Tool [DEBUG]: 빈 비트맵 설정 완료")
            self.current_guide_image = None

    def Command(self, id, msg):
        """버튼 클릭 이벤트 처리"""
        if id == self.ID_REFRESH_BUTTON:
            # 스크립트 새로고침
            self.LoadScripts()
            self.RefreshTreeView()
            c4d.gui.MessageDialog("스크립트가 새로고침되었습니다.")
            
        elif id == self.ID_FILTER_TAB:
            # 필터 탭 변경 (동적 처리)
            if self.filter_tab:
                # 선택된 탭 찾기
                for tag_name, tag_id in TAG_ID_MAP.items():
                    if self.filter_tab.IsSelected(tag_id):
                        self.current_filter = tag_name
                        break
                
                # TreeView 새로고침
                self.RefreshTreeView()
        
        elif id == self.ID_GUIDE_IMAGE:
            # 가이드 이미지 버튼 클릭 무시 (뷰어 역할만 수행)
            return True
        
        return True

class IMfineToolCommand(c4d.plugins.CommandData):
    """플러그인 커맨드 클래스"""
    
    dialog = None
    
    def Execute(self, doc):
        """플러그인 실행"""
        # 다이얼로그가 없으면 생성
        if self.dialog is None:
            self.dialog = IMfineToolDialog()
        
        # 다이얼로그 열기
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=500, defaulth=600)
    
    def RestoreLayout(self, sec_ref):
        """레이아웃 복원"""
        # 다이얼로그가 없으면 생성
        if self.dialog is None:
            self.dialog = IMfineToolDialog()
        
        # 레이아웃 복원
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

# 플러그인 등록
if __name__ == "__main__":
    # 아이콘 로드 (선택사항)
    bmp = c4d.bitmaps.BaseBitmap()
    
    # 플러그인 등록
    c4d.plugins.RegisterCommandPlugin(
        id=PLUGIN_ID,
        str="IMfine Tool",
        info=0,
        help="IMfine Cinema4D Utility Tool - 다양한 유틸리티 스크립트를 실행할 수 있는 도구입니다.",
        dat=IMfineToolCommand(),
        icon=bmp
    )
    
    print("IMfine Tool 플러그인이 등록되었습니다.")