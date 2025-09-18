import c4d
import math
from c4d import bitmaps
from c4d import gui, plugins
from c4d.modules import snap 

import sys
import os
sys.path.append(os.path.dirname(__file__))
from utils import mw_utils

PLUGIN_ID = 1065393 # Plugin ID

class MWDynamicRenderRegion(gui.GeDialog):
    ID_BORDER = 2101
    ID_OBJECTSLIST = 2301
    ID_CALCULATE_CURFRAME = 2201
    ID_CALCULATE_ALLFRAME = 2202
    ID_BAKERENDERREGION = 2203
    ID_GET_SELECTED_OBJECTS = 2401  # Add: Get Selected Objects button ID

    INITW = 100
    INITH = 10

    border = 30
    op_Region = {}
    data_Region = []
    objList = None

    def CreateLayout(self):
        # Defines the title of the Dialog
        self.SetTitle("MW Dynamic Render Region(Octane)")

        self.GroupBegin(0, c4d.BFH_SCALEFIT, 1, 1)
        self.GroupBorderSpace(15, 5, 5, 5)

        # Add: Get Selected Objects button
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 1)
        self.AddStaticText(1000, c4d.BFH_LEFT | c4d.BFV_TOP, name="", initw=self.INITW, inith=self.INITH)

        self.AddButton(self.ID_GET_SELECTED_OBJECTS, c4d.BFH_LEFT, name="Get Selected Objects", inith=self.INITH)
        self.GroupEnd()

        # Add object list
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 1)
        self.AddStaticText(1000, c4d.BFH_LEFT | c4d.BFV_TOP, name="Objects", initw=self.INITW, inith=self.INITH)
        # Build accepted object types
        accepted = c4d.BaseContainer()
        accepted.InsData(c4d.Obase, "")
        settings = c4d.BaseContainer()
        # Set accepted object types into InExclude custom GUI settings  
        settings[c4d.DESC_ACCEPT] = accepted
        self.objList = self.AddCustomGui(self.ID_OBJECTSLIST, c4d.CUSTOMGUI_INEXCLUDE_LIST, "", c4d.BFH_SCALEFIT, self.INITW, self.INITH, settings)
        self.GroupEnd()

        # Add Border input field
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 1)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Border", initw=self.INITW, inith=self.INITH)
        self.SetInt32(self.ID_BORDER, self.border)
        self.AddEditNumberArrows(self.ID_BORDER, c4d.BFH_LEFT, initw=80, inith=self.INITH)
        self.GroupEnd()

        # Add Calculate buttons
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 3, 1)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Calculate", initw=self.INITW, inith=self.INITH)
        self.AddButton(self.ID_CALCULATE_CURFRAME, c4d.BFH_SCALEFIT, name="Current Frame", initw=self.INITW, inith=self.INITH)
        self.AddButton(self.ID_CALCULATE_ALLFRAME, c4d.BFH_SCALEFIT, name="All Frames", initw=self.INITW, inith=self.INITH)
        self.GroupEnd()
        
        # Separator
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=1)
        self.GroupBorderSpace(0,2,0,2)
        self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT)
        self.GroupEnd()

        # Add Bake button
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 1)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Bake", initw=self.INITW, inith=self.INITH)
        self.AddButton(self.ID_BAKERENDERREGION, c4d.BFH_SCALEFIT, name="Bake Render Region", initw=self.INITW, inith=self.INITH) # 버튼 추가
        self.Enable(self.ID_BAKERENDERREGION, False) # 버튼 비활성화
        self.GroupEnd()

        self.GroupEnd()
        return True

    def DestroyWindow(self):
        self.DeleteRenderRegionGuide(c4d.documents.GetActiveDocument())

    def Command(self, Id, msg):
        if Id == self.ID_GET_SELECTED_OBJECTS: # Get Selected Objects 버튼을 눌렀을 때
            doc = c4d.documents.GetActiveDocument()
            selected_objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_NONE | c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
            if not selected_objs:
                gui.MessageDialog("No objects selected.")
                return True
            # Convert to InExcludeData
            inexclude = c4d.InExcludeData()
            for obj in selected_objs:
                inexclude.InsertObject(obj, 1)
            self.objList.SetData(inexclude)
            c4d.EventAdd()
            return True
        elif Id == self.ID_CALCULATE_CURFRAME or Id == self.ID_CALCULATE_ALLFRAME: # Calculate 버튼을 눌렀을 때
            doc = c4d.documents.GetActiveDocument()
            doc.StartUndo()
            border = self.GetInt32(self.ID_BORDER)
            rdt = doc.GetActiveRenderData()
            rbd = doc.GetRenderBaseDraw()
            safeFrame = rbd.GetSafeFrame()
            safeFrame_width = safeFrame['cr'] - safeFrame['cl']
            safeFrame_height = safeFrame['cb'] - safeFrame['ct']

            op = []
            for iobj in range(self.objList.GetData().GetObjectCount()): # Get objects from InExcludeData
                op.append(self.objList.GetData().ObjectFromIndex(doc, iobj))

            if op == []: # 선택된 오브젝트가 없을 때
                gui.MessageDialog("Please drag and drop the object(s) to the Object List.")
                return False

            self.DeleteRenderRegionGuide(doc) # Delete previous guides

            objectFrameRange = self.GetObjectFrameRange(op, rbd)

            # Solo Mode 설정
            bc = snap.GetSnapSettings(doc)
            current_mode = bc[c4d.VIEWPORT_SOLO_MODE]
            # 0: off, 1: on(no hierarchy), 2: on+hierarchy
            
            mw_utils.SelectObjects(op, doc)
            if current_mode == 0 or current_mode is None: # 1. 솔로 off (0 or None)
                c4d.CallCommand(431000059) # Viewport Solo Single (on)
                c4d.CallCommand(431000060) # Viewport Solo Hierarchy (on)
            elif current_mode == 1: # 2. 솔로 on Hierarchy Off (1)
                c4d.CallCommand(431000059) # Viewport Solo (off)
                c4d.CallCommand(431000059) # Viewport Solo (on)
                c4d.CallCommand(431000060) # Viewport Solo Hierarchy (on)
            elif current_mode == 2: # 3. 솔로 on Hierarchy On (2)
                c4d.CallCommand(431000059) # Viewport Solo (off)
                c4d.CallCommand(431000059) # Viewport Solo (on)
            c4d.EventAdd()


            if objectFrameRange:
                if Id == self.ID_CALCULATE_CURFRAME: # Calculate Current Frame
                    self.op_Region['x1'], self.op_Region['x2'], self.op_Region['y1'], self.op_Region['y2'] = objectFrameRange
                    self.ShowObjectRegion(self.op_Region, doc, rbd)
                    self.data_Region = [{}]
                    self.data_Region[0]['x1'] = max((self.op_Region['x1'] - safeFrame['cl']) / safeFrame_width, 0.0)
                    self.data_Region[0]['x2'] = min((-self.op_Region['x2']  + safeFrame['cr']) / safeFrame_width, 1.0)
                    self.data_Region[0]['y1'] = max((self.op_Region['y1']  - safeFrame['ct']) / safeFrame_height, 0.0)
                    self.data_Region[0]['y2'] = min((-self.op_Region['y2'] + safeFrame['cb']) / safeFrame_height, 1.0)
                    self.data_Region[0]['x1'] = max((self.op_Region['x1'] - border - safeFrame['cl']) / safeFrame_width, 0.0)
                    self.data_Region[0]['x2'] = min((-(self.op_Region['x2'] + border) + safeFrame['cr']) / safeFrame_width, 1.0)
                    self.data_Region[0]['y1'] = max((self.op_Region['y1'] - border - safeFrame['ct']) / safeFrame_height, 0.0)
                    self.data_Region[0]['y2'] = min((-(self.op_Region['y2'] + border) + safeFrame['cb']) / safeFrame_height, 1.0)

                    self.Enable(self.ID_BAKERENDERREGION, True) # 버튼 활성화
                elif Id == self.ID_CALCULATE_ALLFRAME: # Calculate All Frames
                    def SetCurrentFrame(frame, doc):
                        doc.SetTime(c4d.BaseTime(frame, doc.GetFps()))
                        doc.ExecutePasses(None, True, True, True, 0)
                        c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)
                        c4d.DrawViews(c4d.DRAWFLAGS_NO_THREAD | c4d.DRAWFLAGS_FORCEFULLREDRAW)
                        c4d.EventAdd()
                    rdt = doc.GetActiveRenderData()
                    rbd = doc.GetRenderBaseDraw()
                    fps = doc.GetFps()
                    originFrame = doc.GetTime().GetFrame(fps)
                    startFrame = doc.GetLoopMinTime().GetFrame(fps)
                    endFrame = doc.GetLoopMaxTime().GetFrame(fps)
                    self.data_Region = []
                    for iFrame in range(startFrame, endFrame + 1):
                        SetCurrentFrame(iFrame, doc)
                        self.op_Region['x1'], self.op_Region['x2'], self.op_Region['y1'], self.op_Region['y2'] = self.GetObjectFrameRange(op, rbd)
                        self.data_Region.append({})
                        self.data_Region[-1]['x1'] = max((self.op_Region['x1'] - border - safeFrame['cl']) / safeFrame_width, 0.0)
                        self.data_Region[-1]['x2'] = min((-(self.op_Region['x2'] + border) + safeFrame['cr']) / safeFrame_width, 1.0)
                        self.data_Region[-1]['y1'] = max((self.op_Region['y1'] - border - safeFrame['ct']) / safeFrame_height, 0.0)
                        self.data_Region[-1]['y2'] = min((-(self.op_Region['y2'] + border) + safeFrame['cb']) / safeFrame_height, 1.0)
                        self.data_Region[-1]['frame'] = iFrame
                        self.ShowObjectRegion(self.op_Region, doc, rbd, iFrame)
                        c4d.DrawViews(c4d.DRAWFLAGS_NO_THREAD | c4d.DRAWFLAGS_FORCEFULLREDRAW)

                    self.Enable(self.ID_BAKERENDERREGION, True) # 버튼 활성화
                    SetCurrentFrame(originFrame, doc)
            
            doc.EndUndo()
            c4d.CallCommand(431000059) # Viewport Solo Off
            c4d.CallCommand(431000060) # Viewport Solo Off
            c4d.EventAdd()


        elif Id == self.ID_BAKERENDERREGION: # Bake Render Region 버튼을 눌렀을 때
            doc = c4d.documents.GetActiveDocument()
            rdt = doc.GetActiveRenderData() # Get render settings

            if rdt[c4d.RDATA_RENDERENGINE] != 1029525: # 옥테인 렌더 ID가 아닐 때
                gui.MessageDialog("Please set the Renderer to Octane Render.")
                return False
            
            octane = rdt.GetFirstVideoPost()
            confirm = gui.QuestionDialog("Are you sure you want to Bake the Render Region?"
                                " (Existing Render Region Keyframes will be overwritten)")
            if not confirm: return True
            
            if len(self.data_Region) == 1:
                # Remove existing tracks if they exist
                existing_track_x1 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_X1, c4d.DTYPE_REAL, 0)))
                existing_track_x2 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_X2, c4d.DTYPE_REAL, 0)))
                existing_track_y1 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_Y1, c4d.DTYPE_REAL, 0)))
                existing_track_y2 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_Y2, c4d.DTYPE_REAL, 0)))
                if existing_track_x1: existing_track_x1.Remove()
                if existing_track_x2: existing_track_x2.Remove()
                if existing_track_y1: existing_track_y1.Remove()
                if existing_track_y2: existing_track_y2.Remove()
                octane[c4d.VP_RENDERREGION] = True
                octane[c4d.VP_REGION_X1] = self.data_Region[0]['x1']
                octane[c4d.VP_REGION_X2] = self.data_Region[0]['x2']
                octane[c4d.VP_REGION_Y1] = self.data_Region[0]['y1']
                octane[c4d.VP_REGION_Y2] = self.data_Region[0]['y2']
                gui.MessageDialog("The Render Region has been applied to the current render settings.")
            elif len(self.data_Region) > 1:
                # Remove existing tracks if they exist
                existing_track_x1 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_X1, c4d.DTYPE_REAL, 0)))
                existing_track_x2 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_X2, c4d.DTYPE_REAL, 0)))
                existing_track_y1 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_Y1, c4d.DTYPE_REAL, 0)))
                existing_track_y2 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_Y2, c4d.DTYPE_REAL, 0)))
                if existing_track_x1: existing_track_x1.Remove()
                if existing_track_x2: existing_track_x2.Remove()
                if existing_track_y1: existing_track_y1.Remove()
                if existing_track_y2: existing_track_y2.Remove()
                track_x1 = c4d.CTrack(octane, c4d.DescID(c4d.DescLevel(c4d.VP_REGION_X1, c4d.DTYPE_REAL, 0)))
                track_x2 = c4d.CTrack(octane, c4d.DescID(c4d.DescLevel(c4d.VP_REGION_X2, c4d.DTYPE_REAL, 0)))
                track_y1 = c4d.CTrack(octane, c4d.DescID(c4d.DescLevel(c4d.VP_REGION_Y1, c4d.DTYPE_REAL, 0)))
                track_y2 = c4d.CTrack(octane, c4d.DescID(c4d.DescLevel(c4d.VP_REGION_Y2, c4d.DTYPE_REAL, 0)))
                octane.InsertTrackSorted(track_x1)
                octane.InsertTrackSorted(track_x2)
                octane.InsertTrackSorted(track_y1)
                octane.InsertTrackSorted(track_y2)
                curve_x1 = track_x1.GetCurve()
                curve_x2 = track_x2.GetCurve()
                curve_y1 = track_y1.GetCurve()
                curve_y2 = track_y2.GetCurve()
                for iData in self.data_Region:
                    key_x1 = c4d.CKey()
                    key_x1.SetTime(curve_x1, c4d.BaseTime(iData['frame'] / doc.GetFps()))
                    key_x1.SetValue(curve_x1, iData['x1'])
                    curve_x1.InsertKey(key_x1)
                    key_x2 = c4d.CKey()
                    key_x2.SetTime(curve_x2, c4d.BaseTime(iData['frame'] / doc.GetFps()))
                    key_x2.SetValue(curve_x2, iData['x2'])
                    curve_x2.InsertKey(key_x2)
                    key_y1 = c4d.CKey()
                    key_y1.SetTime(curve_y1, c4d.BaseTime(iData['frame'] / doc.GetFps()))
                    key_y1.SetValue(curve_y1, iData['y1'])
                    curve_y1.InsertKey(key_y1)
                    key_y2 = c4d.CKey()
                    key_y2.SetTime(curve_y2, c4d.BaseTime(iData['frame'] / doc.GetFps()))
                    key_y2.SetValue(curve_y2, iData['y2'])
                    curve_y2.InsertKey(key_y2)
                c4d.EventAdd()
                gui.MessageDialog("The Render Region has been applied to the current render settings.")

    def DeleteRenderRegionGuide(self, doc):
        """Delete all splines in the document."""
        for op in doc.GetObjects():
            if op.GetName().find('MW_OBJECT_RENDER_REGION') != -1:
                doc.AddUndo(c4d.UNDOTYPE_DELETE, op)
                op.Remove()
        c4d.EventAdd()

    def GetObjectFrameRange(self, op, rbd):
        pointX = []
        pointY = []
        if op is None:
            msg = "Please select an object."
            raise ValueError(msg)

        op_list = op if isinstance(op, list) else [op] # op가 하나면 리스트로 변환
        meshes = []
        for obj in op_list:
            meshes.extend(mw_utils.GetFullCache(obj, parent=True, deform=True))

        for mesh in meshes:
            if not isinstance(mesh, c4d.PointObject):
                continue
            mg = mesh.GetMg() # 오브젝트 매트릭스
            points = [p * mg for p in mesh.GetAllPoints()] # 월드 좌표로 변환
            for ipoint in points:
                pointPos = rbd.WS(ipoint)
                pointX.append(math.ceil(pointPos.x))
                pointY.append(math.ceil(pointPos.y))

        if not pointX or not pointY:
            gui.MessageDialog("No points found in the selected object(s).\n"
                              "If a Subdivision Surface is applied, please disable it and try again.")
            return False
        return [min(pointX), max(pointX), min(pointY), max(pointY)]


    def ShowObjectRegion(self, pos: dict, doc, rbd, frame=None):
        # Create a rectangle spline based on the object region
        rectSpline = c4d.BaseObject(c4d.Ospline)
        borderSpline = c4d.BaseObject(c4d.Ospline)
        safeFrame = rbd.GetSafeFrame() 
        rectSpline.ResizeObject(4)  # A rectangle spline has 4 points
        borderSpline.ResizeObject(4)  # A rectangle spline has 4 points

        temp_pos = {}
        rectSpline_pos = []
        borderSpline_pos = []
        border = self.GetInt32(self.ID_BORDER)

        temp_pos['x1'] = min(max(pos['x1'], safeFrame['cl']), safeFrame['cr'])
        temp_pos['x2'] = max(min(pos['x2'], safeFrame['cr']), safeFrame['cl'])
        temp_pos['y1'] = min(max(pos['y1'], safeFrame['ct']), safeFrame['cb'])
        temp_pos['y2'] = max(min(pos['y2'], safeFrame['cb']), safeFrame['ct'])

        rectSpline_pos.append(rbd.SW(c4d.Vector(temp_pos['x1'], temp_pos['y1'], 100)))
        rectSpline_pos.append(rbd.SW(c4d.Vector(temp_pos['x2'], temp_pos['y1'], 100)))
        rectSpline_pos.append(rbd.SW(c4d.Vector(temp_pos['x2'], temp_pos['y2'], 100)))
        rectSpline_pos.append(rbd.SW(c4d.Vector(temp_pos['x1'], temp_pos['y2'], 100)))

        temp_pos['x1'] = min(max(pos['x1'] - border, safeFrame['cl']), safeFrame['cr'])
        temp_pos['x2'] = max(min(pos['x2'] + border, safeFrame['cr']), safeFrame['cl'])
        temp_pos['y1'] = min(max(pos['y1'] - border, safeFrame['ct']), safeFrame['cb'])
        temp_pos['y2'] = max(min(pos['y2'] + border, safeFrame['cb']), safeFrame['ct'])

        borderSpline_pos.append(rbd.SW(c4d.Vector(temp_pos['x1'], temp_pos['y1'], 200)))
        borderSpline_pos.append(rbd.SW(c4d.Vector(temp_pos['x2'], temp_pos['y1'], 200)))
        borderSpline_pos.append(rbd.SW(c4d.Vector(temp_pos['x2'], temp_pos['y2'], 200)))
        borderSpline_pos.append(rbd.SW(c4d.Vector(temp_pos['x1'], temp_pos['y2'], 200)))

        # Set the points of the rectangle spline
        rectSpline.SetPoint(0, rectSpline_pos[0])
        rectSpline.SetPoint(1, rectSpline_pos[1])
        rectSpline.SetPoint(2, rectSpline_pos[2])
        rectSpline.SetPoint(3, rectSpline_pos[3])
        borderSpline.SetPoint(0, borderSpline_pos[0])
        borderSpline.SetPoint(1, borderSpline_pos[1])
        borderSpline.SetPoint(2, borderSpline_pos[2])
        borderSpline.SetPoint(3, borderSpline_pos[3])

        rectSpline[c4d.SPLINEOBJECT_CLOSED] = True # Close the spline
        rectSpline[c4d.ID_BASEOBJECT_USECOLOR] = 2 # Use Custom Color
        rectSpline[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1, 0, 0) # Red color
        borderSpline[c4d.SPLINEOBJECT_CLOSED] = True # Close the spline
        borderSpline[c4d.ID_BASEOBJECT_USECOLOR] = 2 # Use Custom Color
        borderSpline[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(.5, .5, .5) # Gray color
        
        rectSpline.SetName('MW_OBJECT_RENDER_REGION_RECTSPLINE')
        borderSpline.SetName('MW_OBJECT_RENDER_REGION_BORDERSPLINE')

        if frame is not None:
            self.AddVisibilityTrack(rectSpline, frame, doc)
            self.AddVisibilityTrack(borderSpline, frame, doc)

        # Insert the rectangle spline into the document
        rectSpline.ChangeNBit(c4d.NBIT_OHIDE, c4d.NBITCONTROL_SET)
        doc.InsertObject(rectSpline)
        doc.AddUndo(c4d.UNDOTYPE_NEW, rectSpline)

        borderSpline.ChangeNBit(c4d.NBIT_OHIDE, c4d.NBITCONTROL_SET)
        doc.InsertObject(borderSpline)
        doc.AddUndo(c4d.UNDOTYPE_NEW, borderSpline)
        return True

    def AddVisibilityTrack(self, op, frame, doc):
        if not op: return
        if not doc: return

        #create a new visibility track
        track = c4d.CTrack(op, c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, c4d.DTYPE_LONG, 0)))
        op.InsertTrackSorted(track)

        # 커브 가져오기
        curve = track.GetCurve()

        # Add a key at frame 0 with visibility value 0
        key_previous = c4d.CKey()
        key_previous.SetTime(curve, c4d.BaseTime(-1 / doc.GetFps()))
        key_previous.SetGeData(curve, 1)
        curve.InsertKey(key_previous)
        # 키 추가
        key = c4d.CKey()
        key.SetTime(curve, c4d.BaseTime(frame / doc.GetFps()))
        key.SetGeData(curve, 2)
        curve.InsertKey(key)
        # Add a key at the next frame with visibility value 1
        key_next = c4d.CKey()
        key_next.SetTime(curve, c4d.BaseTime((frame + 1)/ doc.GetFps()))
        key_next.SetGeData(curve, 1)
        curve.InsertKey(key_next)

    def CoreMessage(self, id, msg):
        return super().CoreMessage(id, msg)
    
        if id == c4d.EVMSG_CHANGE:
            # print("EVMSG_CHANGE")
            doc = c4d.documents.GetActiveDocument()
            selected_objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_NONE | c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
            if not selected_objs:
                return True
            # Convert to InExcludeData
            inexclude = c4d.InExcludeData()
            for obj in selected_objs:
                inexclude.InsertObject(obj, 1)
            self.objList.SetData(inexclude)
            c4d.EventAdd()
        


class MWDynamicRenderRegionCommand(plugins.CommandData):
    """Command Data class that holds the ExampleDialog instance."""
    dialog = None
    
    def Execute(self, doc):
        """Called when the user executes a command via either CallCommand() or a click on the Command from the extension menu.

        Args:
            doc (c4d.documents.BaseDocument): The current active document.

        Returns:
            bool: True if the command success.
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MWDynamicRenderRegion()

        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=300, defaulth=800)

    def RestoreLayout(self, sec_ref):
        """Used to restore an asynchronous dialog that has been placed in the users layout.

        Args:
            sec_ref (PyCObject): The data that needs to be passed to the dialog.

        Returns:
            bool: True if the restore success
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MWDynamicRenderRegion()

        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)


if __name__ == "__main__":
    # Registers the plugin
    iconFile=bitmaps.BaseBitmap()
    path, fn = os.path.split(__file__)
    iconFile.InitWith(os.path.join(path,"res","MW_Dynamic_Render_Region.tif"))

    plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                  str="MW Dynamic Render Region(Octane)",
                                  info=0,
                                  help="Set the Render Region of the selected object.",
                                  dat=MWDynamicRenderRegionCommand(),
                                  icon=iconFile)




"""
References:
Get PLA DATA
    https://developers.maxon.net/forum/topic/14305/get-spline-points-positions-from-pla-keyframes/2?_=1732456672668

    AliasTrans
    https://developers.maxon.net/forum/topic/6917/7764_how-to-clone-a-character-skin--skeleton-/3?_=1732504493195

    Object List GUI
    https://developers.maxon.net/forum/topic/10770/14214_inexclude-customgui-in-pythonplugin/2?_=1732760629379
"""