import c4d
import os
import glob
import importlib.util
import sys

# Plugin ID
PLUGIN_ID = 1066547

class IMfineToolDialog(c4d.gui.GeDialog):
    """IMfine Tool 메인 다이얼로그"""
    
    # UI IDs
    ID_MAIN_GROUP = 1000
    ID_SCRIPT_GROUP = 1100
    ID_REFRESH_BUTTON = 1200
    ID_SCRIPT_BUTTON_BASE = 2000  # 스크립트 버튼들의 기본 ID
    
    def __init__(self):
        super().__init__()
        self.scripts = {}
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
        script_pattern = os.path.join(script_module_dir, "*.py") # IMfine_ScriptModule 폴더 내 모든 .py 파일
        script_files = glob.glob(script_pattern) # .py 파일 리스트
        
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
                        self.scripts[script_name] = script_info
                        print(f"IMfine Tool: 스크립트 로드됨 - {script_info['name']}")
                    else:
                        print(f"IMfine Tool: get_script_info 함수를 찾을 수 없습니다 - {script_name}")
                        
            except Exception as e:
                print(f"IMfine Tool: 스크립트 로드 실패 - {script_file}: {e}")
    
    def CreateLayout(self):
        """다이얼로그 레이아웃 생성"""
        self.SetTitle("IMfine Tool")
        
        # 메인 그룹
        self.GroupBegin(self.ID_MAIN_GROUP, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1)
        self.GroupBorderSpace(10, 10, 10, 10)
        
        # 타이틀
        self.AddStaticText(0, c4d.BFH_CENTER, name="IMfine Cinema4D Utility Tool", borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        
        # 새로고침 버튼
        self.AddButton(self.ID_REFRESH_BUTTON, c4d.BFH_SCALEFIT, name="스크립트 새로고침")
        
        # 구분선
        self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT)
        
        # 스크립트 버튼 그룹
        self.GroupBegin(self.ID_SCRIPT_GROUP, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1)
        self.CreateScriptButtons()
        self.GroupEnd()
        
        self.GroupEnd()
        
        return True
    
    def CreateScriptButtons(self):
        """스크립트 버튼들을 생성합니다"""
        if not self.scripts:
            self.AddStaticText(0, c4d.BFH_CENTER, name="로드된 스크립트가 없습니다.")
            return
        
        button_id = self.ID_SCRIPT_BUTTON_BASE
        for script_key, script_info in self.scripts.items():
            # 버튼 추가
            self.AddButton(button_id, c4d.BFH_SCALEFIT, name=script_info['name'])
            
            # 설명 텍스트 추가
            if 'description' in script_info:
                self.AddStaticText(0, c4d.BFH_LEFT, name=f"  → {script_info['description']}")
            
            # 구분선 추가
            self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT)
            
            button_id += 1
    
    def RefreshScriptButtons(self):
        """스크립트 버튼들을 새로고침합니다 (기존 버튼들을 제거하고 새로 생성)"""
        # 스크립트 그룹을 완전히 제거
        self.LayoutFlushGroup(self.ID_SCRIPT_GROUP)
        
        # 스크립트 버튼들을 다시 생성
        self.CreateScriptButtons()
        
        # 레이아웃 변경 사항을 적용
        self.LayoutChanged(self.ID_SCRIPT_GROUP)

    def Command(self, id, msg):
        """버튼 클릭 이벤트 처리"""
        if id == self.ID_REFRESH_BUTTON:
            # 스크립트 새로고침
            self.LoadScripts()
            self.RefreshScriptButtons()
            c4d.gui.MessageDialog("스크립트가 새로고침되었습니다.")
            
        elif id >= self.ID_SCRIPT_BUTTON_BASE:
            # 스크립트 버튼 클릭
            button_index = id - self.ID_SCRIPT_BUTTON_BASE
            script_keys = list(self.scripts.keys())
            
            if button_index < len(script_keys):
                script_key = script_keys[button_index]
                script_info = self.scripts[script_key]
                
                try:
                    # 스크립트 실행
                    if 'execute' in script_info and callable(script_info['execute']):
                        script_info['execute']()
                    else:
                        c4d.gui.MessageDialog(f"스크립트 '{script_info['name']}'의 실행 함수를 찾을 수 없습니다.")
                        
                except Exception as e:
                    c4d.gui.MessageDialog(f"스크립트 실행 중 오류가 발생했습니다:\n{str(e)}")
        
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
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=400, defaulth=500)
    
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