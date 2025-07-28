"""
Name-US:MW Remove Static Tracks
Description-US:Remove Static Animation Tracks
Last update: 2023.08.14
Author: ChoiMyungWon
Email: auddnjs135@naver.com
"""

import c4d
import os
from c4d import bitmaps

PLUGIN_ID = 1061496

def nextObj(op):
    if not op: return
    elif op.GetDown(): return op.GetDown()
    while op.GetUp() and not op.GetNext(): op = op.GetUp()
    return op.GetNext()

def RemoveTracks(activeList, decimalPoint :int = 5):
    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()

    RemovedTrackList = list()
    RemovedTrackMsg = '--- Removed Tracks --- \n'
    RemovedTrackCount = 0
    if activeList == []: #리스트에 아무 오브젝트도 없을 때 종료
        c4d.gui.MessageDialog('Please select any objects/materials/tags to remove static tracks')
        return

    for iObj in activeList:
        trackList = iObj.GetCTracks() # 오브젝트의 모든 트랙 불러오기
        for iTrack in trackList:
            delFlag = 0
            iCat = iTrack.GetTrackCategory() # Value = 1 , Data = 2 | 트랙의 카테고리 불러오기
            iCurve = iTrack.GetCurve() # 트랙의 커브 값 불러오기
            iCount = iCurve.GetKeyCount() # 커브값의 키프레임 갯수 불러오기
            iKey = iCurve.GetKey(0)
            
            if (iCount <= 0): # 해당 트랙의 키프레임이 없을때 빠져나가기 (flag가 0인 상태로 탈출해서 트랙 제거하기 위함)
                break

            if (iCat == c4d.CTRACK_CATEGORY_VALUE): # 트랙이 Value 트랙일 때
                #print('Value Track')
                iFirstKey = iCurve.GetKey(0)
                iLastKey = iCurve.GetKey(iCount-1)
                iFirstKeyValue = round(iFirstKey.GetValue(),decimalPoint)
                for iTime in range(iFirstKey.GetTime().GetFrame(doc.GetFps()), iLastKey.GetTime().GetFrame(doc.GetFps())):
                    iBaseTime = c4d.BaseTime(iTime / doc.GetFps())
                    iValue = round(iCurve.GetValue(iBaseTime,doc.GetFps()),decimalPoint)
                    #print('iValue =', iValue)
                    if iFirstKeyValue != iValue:
                        delFlag = 1
                        break
            elif (iCat == c4d.CTRACK_CATEGORY_DATA): # 트랙이 Data 트랙일 때
                #print('Data Track')
                for j in range(iCount):
                    iData = iKey.GetGeData()
                    jKey = iCurve.GetKey(j)
                    jData = jKey.GetGeData()
                    if jData != iData:
                        delFlag = 1
                        break
            else:
                break

            if delFlag == 0:
                
                RemovedTrackCount += 1
                #RemovedTrackList.append(f'{iObj.GetName()} : {iTrack.GetName()}')
                RemovedTrackMsg += f'{iObj.GetName()} : {iTrack.GetName()} \n'
                #print(RemovedTrackMsg)
                doc.AddUndo(c4d.UNDOTYPE_DELETE, iTrack)
                iTrack.Remove()
    
    if RemovedTrackCount:
        #RemovedTrackMsg += '\n' + f'{RemovedTrackCount} tracks were removed.'
        FinalMsg = f'{RemovedTrackCount} tracks were removed. \n\n' + RemovedTrackMsg
        c4d.gui.MessageDialog(FinalMsg)
    else: c4d.gui.MessageDialog('None of the tracks were removed.')

    doc.EndUndo()
    c4d.EventAdd()

class MWDialog(c4d.gui.GeDialog):
    ID_DECIMALPOINT: int = 1001
    ID_OBJECTS: int = 1011
    ID_MATERIALS: int = 1012
    ID_TAGS: int = 1013
    ID_BTN_APPLY: int = 1101
    ID_BTN_ALLAPPLY: int = 1102
    ID_BTN_CANCEL: int = 1103
    

    def CreateLayout(self) -> bool:
        self.SetTitle("MW Remove Static Tracks")
        #self.Enable()
        self.GroupBegin(1000, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1)
        self.GroupBorderSpace(10, 10, 10, 5)

        self.GroupBegin(1000, c4d.BFH_SCALEFIT, 2)
        self.AddStaticText(0, c4d.BFH_CENTER, name='Decimal Point(Threshold)')
        self.AddEditSlider(self.ID_DECIMALPOINT, c4d.BFH_SCALEFIT)
        self.SetInt32(self.ID_DECIMALPOINT, 5, min=1,max=8)
        self.GroupEnd()

        self.AddStaticText(0, c4d.BFH_CENTER, name='If some tracks are not removed, Decrease this value.')

        self.GroupBegin(1000, c4d.BFH_CENTER, 3)
        self.GroupBorderSpace(0, 10, 0, 0)
        self.AddCheckbox(self.ID_OBJECTS, c4d.BFH_CENTER,170,10,name = 'Selected Objects')
        self.SetBool(self.ID_OBJECTS, 0)
        self.AddCheckbox(self.ID_MATERIALS, c4d.BFH_CENTER,180,10,name = 'Selected Materials')
        self.SetBool(self.ID_MATERIALS, 0)
        self.AddCheckbox(self.ID_TAGS, c4d.BFH_CENTER,150,10,name = 'Selected Tags')
        self.SetBool(self.ID_TAGS, 0)
        self.GroupEnd()

        # And Buttons.
        self.GroupBegin(1002, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 3)
        self.GroupBorderSpace(5, 10, 5, 5)
        self.AddButton(self.ID_BTN_APPLY, c4d.BFH_SCALEFIT, name="Apply")
        self.AddButton(self.ID_BTN_ALLAPPLY, c4d.BFH_SCALEFIT, name="Apply Scene")
        self.AddButton(self.ID_BTN_CANCEL, c4d.BFH_SCALEFIT, name="Cancel")
        self.GroupEnd()

        return super().CreateLayout()

    def Command(self, cid: int, msg: c4d.BaseContainer ) -> bool:
        doc = c4d.documents.GetActiveDocument()
        activeList = []
        if cid == self.ID_BTN_APPLY: #Apply 버튼을 눌렀을 때
            if self.GetBool(self.ID_OBJECTS): activeList.extend(doc.GetActiveObjects(1)) #Selected Objects 체크되어 있으면 선택된 오브젝트 리스트에 추가
            if self.GetBool(self.ID_MATERIALS): activeList.extend(doc.GetActiveMaterials()) #Selected Materials 체크되어 있으면 선택된 매터리얼 리스트에 추가
            if self.GetBool(self.ID_TAGS): activeList.extend(doc.GetActiveTags()) #Selected Tags 체크되어 있으면 선택된 태그들 리스트에 추가
            RemoveTracks(activeList,self.GetInt32(self.ID_DECIMALPOINT)) #스태틱 트랙 제거 함수 호출
        elif cid == self.ID_BTN_ALLAPPLY: #Apply Scene 버튼을 눌렀을 때
            GetAllObjects = []
            GetAllTags = []
            obj_temp = doc.GetFirstObject()
            
            while obj_temp:
                GetAllObjects.append(obj_temp)
                GetAllTags.extend(obj_temp.GetTags())
                obj_temp = nextObj(obj_temp)
            
            activeList.extend(GetAllObjects)
            activeList.extend(doc.GetMaterials())
            activeList.extend(GetAllTags)

            RemoveTracks(activeList,self.GetInt32(self.ID_DECIMALPOINT)) #스태틱 트랙 제거 함수 호출
        if cid == self.ID_BTN_CANCEL:
            self.Close()
        return super().Command(cid, msg)
    
    def Message(self, msg: c4d.BaseContainer, result: c4d.BaseContainer) -> int:
        #if msg.GetId() == c4d.BFM_LOSTFOCUS:
        #    self.Close()
        return super().Message(msg, result)

class MWDialogCommand(c4d.plugins.CommandData):
    dialog = None
    def Execute(self, doc):
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MWDialog()

        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=400, defaulth=0)

    def RestoreLayout(self, sec_ref):
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MWDialog()

        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)



def main():
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "MW Remove Static Tracks.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                    str="MW Remove Static Tracks",
                                    info=0,
                                    help="Remove Static Tracks",
                                    dat=MWDialogCommand(),
                                    icon=bmp)

if __name__=='__main__':
    main()