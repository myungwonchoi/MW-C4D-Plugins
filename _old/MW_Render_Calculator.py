"""
Name-US:MW Render Calculator
Description-US:Simple Calculation For Render Time
Last update: 2023.01.01
Author: ChoiMyungWon
Email: auddnjs135@naver.com
"""


import c4d
import os
from datetime import datetime, timedelta

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1060421

class RenderCalculator_Dialog(c4d.gui.GeDialog):
    ID_EX = 0
    ID_FRAMERANGE = 10
    ID_MULTILINE = int(100)
    ID_FRAME_START = 20
    ID_FRAME_END = 21
    ID_FRAME_TIME_MINIUTE = 22
    ID_FRAME_TIME_SECOND = 23
    ID_MULTI_RENDER = 24
    ID_EXPORT_ANNOTATIONS = 25

    SPACE_INITW_1 = 150
    SPACE_INITW_2 = 80
    SPACE_INITH = 12

    now = datetime.now()
    TIME_RENDER = [0,0,0,0]
    TIME_RENDER_STR = str(int(TIME_RENDER[0])).zfill(2) + '일 '\
                         + str(int(TIME_RENDER[1])).zfill(2) + '시 '\
                         + str(int(TIME_RENDER[2])).zfill(2) + '분 '\
                         + str(int(TIME_RENDER[3])).zfill(2) + '초 '
    TIME_CURRENT = now; TIME_CURRENT_STR = TIME_CURRENT.strftime('%d일 %H시 %M분 %S초')
    TIME_FINISHED = now; TIME_FINISHED_STR = TIME_FINISHED.strftime('%d일 %H시 %M분 %S초')
    TIME_RESULT = '렌더 시간 : ' + TIME_RENDER_STR +'\n---\n현재 시간 : ' + TIME_CURRENT_STR + '\n완료 시각 : ' + TIME_FINISHED_STR +'\n---\n'

    def InitValues(self):
        self.SetTimer(500)
        return True

    def Timer(self, msg):
        self.UpdateTime()

    def CreateLayout(self):
        """This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog."""
        # Defines the title of the Dialog
        #self.Gadget()
        self.SetTitle("Render Calculator")

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1)
        self.GroupBorderSpace(10, 10, 10, 10)
        
        #self.AddStaticText(0, c4d.BFH_LEFT,name='Settings',initw=self.SPACE_INITW,inith = self.SPACE_INITH,borderstyle = c4d.BORDER_WITH_TITLE_BOLD)

        #self.GroupBegin(0, c4d.BFH_LEFT | c4d.BFV_TOP, cols=1)
        #self.GroupBorderSpace(15, 0, 0, 0)
        self.GroupBegin(0, c4d.BFH_LEFT | c4d.BFV_TOP, cols=2)
        self.AddStaticText(0, c4d.BFH_LEFT,name='렌더 범위',initw=self.SPACE_INITW_1)
        self.AddComboBox(self.ID_FRAMERANGE, c4d.BFH_LEFT, initw=int(self.SPACE_INITW_2*2.5), specialalign=False, allowfiltering=True)
        self.AddChild(self.ID_FRAMERANGE, 11, 'Current Render Setting'); self.AddChild(self.ID_FRAMERANGE, 12, 'All frames'); self.AddChild(self.ID_FRAMERANGE, 13, 'Preview Range');
        self.SetInt32(self.ID_FRAMERANGE, 11)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_LEFT | c4d.BFV_TOP, cols=3)
        self.AddStaticText(0, c4d.BFH_CENTER,name='시작 프레임',initw=self.SPACE_INITW_1)
        self.AddEditNumberArrows(self.ID_FRAME_START, c4d.BFH_SCALEFIT,initw=self.SPACE_INITW_2)
        self.AddStaticText(0, c4d.BFH_CENTER,name='F')
        self.AddStaticText(0, c4d.BFH_LEFT,name='끝 프레임',initw=self.SPACE_INITW_1)
        self.AddEditNumberArrows(self.ID_FRAME_END, c4d.BFH_SCALEFIT,initw=self.SPACE_INITW_2)
        self.AddStaticText(0, c4d.BFH_CENTER,name='F')
        #self.AddStaticText(0, c4d.BFH_LEFT,name='0(0 to 0)',initw=self.SPACE_INITW_1)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_LEFT | c4d.BFV_TOP, cols=5)
        self.AddStaticText(0, c4d.BFH_LEFT,name='장당 소요시간',initw=self.SPACE_INITW_1)
        self.AddEditNumberArrows(self.ID_FRAME_TIME_MINIUTE, c4d.BFH_LEFT, initw = self.SPACE_INITW_2)
        self.AddStaticText(self.ID_EX, c4d.BFH_LEFT,name='분',initw=int(self.SPACE_INITW_2/2))
        self.AddEditNumberArrows(self.ID_FRAME_TIME_SECOND, c4d.BFH_LEFT, initw = self.SPACE_INITW_2)
        self.AddStaticText(self.ID_EX, c4d.BFH_LEFT,name='초',initw=self.SPACE_INITW_2)
        #self.AddStaticText(0, c4d.BFH_LEFT,name='ex) 01:30',initw=self.SPACE_INITW_1)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_LEFT | c4d.BFV_TOP, cols=3)
        self.AddStaticText(0, c4d.BFH_CENTER,name='부분렌더',initw=self.SPACE_INITW_1)
        self.AddEditNumberArrows(self.ID_MULTI_RENDER, c4d.BFH_SCALEFIT,initw=self.SPACE_INITW_2)
        self.AddStaticText(0, c4d.BFH_CENTER,name='대',initw=self.SPACE_INITW_1)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT, cols=1); self.AddSeparatorH(400, flags=c4d.BFH_SCALEFIT); self.GroupEnd()
        self.AddMultiLineEditText(self.ID_MULTILINE, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,inith = self.SPACE_INITH*10, style=c4d.DR_MULTILINE_READONLY)
        self.SetString(self.ID_MULTILINE, self.TIME_RESULT)
        # Creates a Ok and Cancel Button
        #self.AddDlgGroup(c4d.DLG_OK | c4d.DLG_CANCEL)
        self.AddButton(self.ID_EXPORT_ANNOTATIONS, c4d.BFH_SCALEFIT, name='Annotations에 출력')
        self.GroupEnd()

        doc = c4d.documents.GetActiveDocument()
        rdt = doc.GetActiveRenderData()
        rFrom = rdt[c4d.RDATA_FRAMEFROM].GetFrame(doc.GetFps())
        rTo = rdt[c4d.RDATA_FRAMETO].GetFrame(doc.GetFps())

        self.SetInt32(self.ID_MULTI_RENDER, 1,min = 1, max= 20)
        self.SetInt32(self.ID_FRAME_START, rFrom, min = 0, max = 999999)
        self.SetInt32(self.ID_FRAME_END, rTo, min = 0, max= 999999)
        self.SetInt32(self.ID_FRAME_TIME_MINIUTE, 0, min = 0, max = 999999)
        self.SetInt32(self.ID_FRAME_TIME_SECOND, 0, min = 0, max = 59)
        return True


    def Command(self, cid, bc):
        self.UpdateTime()
        #print('cid =',cid)
        if(cid == self.ID_FRAME_START and self.GetInt32(self.ID_FRAME_START) > self.GetInt32(self.ID_FRAME_END)):
            self.SetInt32(self.ID_FRAME_END, self.GetInt32(cid),min = 0,max = 999999)
        elif(cid == self.ID_FRAME_END and self.GetInt32(self.ID_FRAME_END) < self.GetInt32(self.ID_FRAME_START)):
            self.SetInt32(self.ID_FRAME_START, self.GetInt32(cid),min = 0,max = 999999)

        if cid == self.ID_FRAMERANGE:
            frPreset = self.GetInt32(cid)
            doc = c4d.documents.GetActiveDocument()
            rdt = doc.GetActiveRenderData()
            if frPreset == 11: #CURRENT RENDER SETTINGS
                rFrom = rdt[c4d.RDATA_FRAMEFROM].GetFrame(doc.GetFps())
                rTo = rdt[c4d.RDATA_FRAMETO].GetFrame(doc.GetFps())
            elif frPreset == 12: #ALL FRAMES
                rFrom = doc[c4d.DOCUMENT_MINTIME].GetFrame(doc.GetFps())
                rTo = doc[c4d.DOCUMENT_MAXTIME].GetFrame(doc.GetFps())
            elif frPreset == 13: #Preview Range
                rFrom = doc[c4d.DOCUMENT_LOOPMINTIME].GetFrame(doc.GetFps())
                rTo = doc[c4d.DOCUMENT_LOOPMAXTIME].GetFrame(doc.GetFps())
            self.SetInt32(self.ID_FRAME_START, rFrom, min = 0, max = 999999)
            self.SetInt32(self.ID_FRAME_END, rTo, min = 0, max= 999999)


        if cid == self.ID_EXPORT_ANNOTATIONS:
            doc = c4d.documents.GetActiveDocument()
            rdt = doc.GetActiveRenderData()
            rdt[c4d.RDATA_HELPTEXT] = self.TIME_RESULT
            c4d.EventAdd(flags=0)
        return True

    def UpdateTime(self):
        self.now = datetime.now()
        frameMulti = self.GetInt32(self.ID_MULTI_RENDER)
        frameRange = self.GetInt32(self.ID_FRAME_END) - self.GetInt32(self.ID_FRAME_START) + 1
        frameTime = (60*self.GetInt32(self.ID_FRAME_TIME_MINIUTE)) + self.GetInt32(self.ID_FRAME_TIME_SECOND)
        frameResult = frameRange * frameTime
        frameResult = (frameResult / frameMulti) + ((frameResult / frameMulti) % frameMulti)

        self.TIME_RENDER[0] = int(frameResult / (60*60*24)) #시간
        self.TIME_RENDER[1] = int((frameResult - self.TIME_RENDER[0] * 60 * 60 * 24) / 3600)
        self.TIME_RENDER[2] = int(((frameResult - (self.TIME_RENDER[0] * 60 * 60 * 24)) - (self.TIME_RENDER[1] * 3600)) / 60)
        self.TIME_RENDER[3] = int(frameResult % 60)
        self.TIME_RENDER_STR = str(self.TIME_RENDER[0]).zfill(2) + '일 '\
                             + str(self.TIME_RENDER[1]).zfill(2) + '시 '\
                             + str(self.TIME_RENDER[2]).zfill(2) + '분 '\
                             + str(self.TIME_RENDER[3]).zfill(2) + '초 '
        self.TIME_FINISHED = self.now + timedelta(seconds=frameResult)
        #print('frameResult =',frameResult)
        #print('self.TIME_RENDER =',self.TIME_RENDER)
        #print('self.TIME_FINISHED =',self.TIME_FINISHED)
        self.TIME_RESULT = '렌더 시간 : ' + self.TIME_RENDER_STR  +'\n---\n현재 시간 : ' + self.TIME_CURRENT_STR + '\n완료 시각 : ' + self.TIME_FINISHED_STR +'\n---\n'
        self.TIME_CURRENT_STR = self.now.strftime('%d일 %H시 %M분 %S초')
        self.TIME_FINISHED_STR = self.TIME_FINISHED.strftime('%d일 %H시 %M분 %S초')

        if frameMulti > 1 and frameRange != 1: #0 9
            mFrom = self.GetInt32(self.ID_FRAME_START) #0
            mDvide = int(frameRange / frameMulti) #10/6 = 1
            mTo = self.GetInt32(self.ID_FRAME_START) + mDvide - 1 # 0 4
            for i in range(0,frameMulti-1):
                self.TIME_RESULT += str(mFrom) + '-' + str(mTo) + '\n' #0 4
                mFrom = mTo + 1 #5 
                mTo = mFrom + mDvide - 1 #5 9
            self.TIME_RESULT += str(mFrom) + '-' + str(self.GetInt32(self.ID_FRAME_END)) + '\n'
            '''
            while self.GetInt32(self.ID_FRAME_START) + frameRange-1 - mTo > mDvide:
                self.TIME_RESULT += str(mFrom) + '-' + str(mTo) + '\n' #0 4
                mFrom = mTo + 1 #5 
                mTo = mFrom + mDvide - 1 #5 9
                if (self.GetInt32(self.ID_FRAME_START) + frameRange-1 - mTo) <= mDvide: #10
                    self.TIME_RESULT += str(mFrom) + '-' + str(mTo+int(frameRange % mDvide)) + '\n'
                    break
            '''
        self.SetString(self.ID_MULTILINE, self.TIME_RESULT)


class RenderCalculator_DialogCommand(c4d.plugins.CommandData):
    """Command Data class that holds the ExampleDialog instance."""
    dialog = None
    
    def Execute(self, doc):
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = RenderCalculator_Dialog()
        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=400)

    def RestoreLayout(self, sec_ref):
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = RenderCalculator_Dialog()
        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

# main
if __name__ == "__main__":
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "MW Render Calculator.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the plugin
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                      str="MW Render Calculator",
                                      info=0,
                                      help="Simple Render Time Calculator",
                                      dat=RenderCalculator_DialogCommand(),
                                      icon=bmp)