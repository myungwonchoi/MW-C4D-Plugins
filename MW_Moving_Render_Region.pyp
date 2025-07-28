import c4d
import math
from c4d import gui, plugins

PLUGIN_ID = 1065393
AAAA = 100

class MWMovingRenderRegion(gui.GeDialog):
    ID_BORDER = 2101
    ID_OBJECTSLIST = 2301
    ID_CALCULATE_CURFRAME = 2201
    ID_CALCULATE_ALLFRAME = 2202
    ID_BAKERENDERREGION = 2203
    ID_RENDERER = 2001
    ID_RENDERER_OCT = 2002
    ID_RENDERER_RS = 2003

    border = 0
    
    op_Region = {}
    data_Region = []
    renderTab = None
    objList = None

    def CreateLayout(self):
        """This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog."""
        # Defines the title of the Dialog
        self.SetTitle("MW Object Render Region")

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 1)
        self.GroupBorderSpace(5, 5, 5, 5)

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 2, 1, "", 0)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Renderer", initw=120)

        bc = c4d.BaseContainer()
        bc.SetBool(c4d.QUICKTAB_SHOWSINGLE, True)
        bc.SetBool(c4d.QUICKTAB_NOMULTISELECT, True)
        self.renderTab = self.AddCustomGui(1003, c4d.CUSTOMGUI_QUICKTAB, '',
                            c4d.BFH_LEFT | c4d.BFV_SCALEFIT, 450, 0, bc)
        self.renderTab.AppendString(self.ID_RENDERER_OCT, "Octane", True)
        self.renderTab.AppendString(self.ID_RENDERER_RS, "Redshift (C4D)", False)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT, 3, 1)
        self.AddStaticText(1002, c4d.BFH_LEFT, name="Border (px)", initw=120)
        self.SetInt32(self.ID_BORDER, self.border)
        self.AddEditNumberArrows(self.ID_BORDER, c4d.BFH_LEFT, initw=80)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 1)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Calculate", initw=120)
        self.AddButton(self.ID_CALCULATE_CURFRAME, c4d.BFH_SCALEFIT, name="Calculate Object Region (Current Frame)")
        self.AddStaticText(0, c4d.BFH_LEFT, name="", initw=120)
        self.AddButton(self.ID_CALCULATE_ALLFRAME, c4d.BFH_SCALEFIT, name="Calculate Object Region (All Frames)")
        self.GroupEnd()
        
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=1)
        self.GroupBorderSpace(0,2,0,2)
        self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT)
        self.GroupEnd()
        
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 1)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Bake", initw=120)
        self.AddButton(self.ID_BAKERENDERREGION, c4d.BFH_SCALEFIT, name="Bake Render Region")        
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 2, 1)
        self.AddStaticText(1000, c4d.BFH_LEFT | c4d.BFV_TOP, name="Objects", initw=120)
    
        # Build accepted object types
        accepted = c4d.BaseContainer()
        accepted.InsData(c4d.Obase, "")
        settings = c4d.BaseContainer()
        # Set accepted object types into InExclude custom GUI settings  
        settings[c4d.DESC_ACCEPT] = accepted
        self.objList = self.AddCustomGui(self.ID_OBJECTSLIST, c4d.CUSTOMGUI_INEXCLUDE_LIST, "", c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, 0, 0, settings)
        # self.AddMultiLineEditText(self.ID_OBJECTSLIST, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
        # doc = c4d.documents.GetActiveDocument()
        # self.SetString(self.ID_OBJECTSLIST, "\n".join([obj.GetName() for obj in doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_NONE | c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)]))
        # self.Enable(self.ID_OBJECTSLIST, False)
        self.GroupEnd()

        self.GroupEnd()
        return True

    def DestroyWindow(self):
        self.DeleteRenderRegionGuide()

    def Command(self, Id, msg):
        if Id == self.ID_CALCULATE_CURFRAME or Id == self.ID_CALCULATE_ALLFRAME:
            doc = c4d.documents.GetActiveDocument()

            doc.StartUndo()

            border = self.GetInt32(self.ID_BORDER)
            rdt = doc.GetActiveRenderData()
            rbd = doc.GetRenderBaseDraw()
            safeFrame = rbd.GetSafeFrame()
            safeFrame_width = safeFrame['cr'] - safeFrame['cl']
            safeFrame_height = safeFrame['cb'] - safeFrame['ct']

            # op = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_NONE | c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
            op = []
            for iobj in range(self.objList.GetData().GetObjectCount()):
                op.append(self.objList.GetData().ObjectFromIndex(doc, iobj))

            if op == []:
                gui.MessageDialog("Please Drag and Drop the object(s) to the Object List.")
                return False
            
            self.DeleteRenderRegionGuide()

            if Id == self.ID_CALCULATE_CURFRAME: # 현재 프레임 영역 계산
                self.data_Region = [{}]
                merged_object = self.GetMergedObject(op, doc)

                self.op_Region['x1'], self.op_Region['x2'], self.op_Region['y1'], self.op_Region['y2'] \
                = self.GetObjectFrameRange(merged_object, doc, rbd)
                self.ShowObjectRegion(self.op_Region, doc, rbd)
                merged_object.Remove()


                self.data_Region[0]['x1'] = max((self.op_Region['x1'] - safeFrame['cl']) / safeFrame_width, 0.0)
                self.data_Region[0]['x2'] = min((-self.op_Region['x2']  + safeFrame['cr']) / safeFrame_width, 1.0)
                self.data_Region[0]['y1'] = max((self.op_Region['y1']  - safeFrame['ct']) / safeFrame_height, 0.0)
                self.data_Region[0]['y2'] = min((-self.op_Region['y2'] + safeFrame['cb']) / safeFrame_height, 1.0)
                print('Object Region: ', self.data_Region[0])

                self.data_Region[0]['x1'] = max((self.op_Region['x1'] - border - safeFrame['cl']) / safeFrame_width, 0.0)
                self.data_Region[0]['x2'] = min((-(self.op_Region['x2'] + border) + safeFrame['cr']) / safeFrame_width, 1.0)
                self.data_Region[0]['y1'] = max((self.op_Region['y1'] - border - safeFrame['ct']) / safeFrame_height, 0.0)
                self.data_Region[0]['y2'] = min((-(self.op_Region['y2'] + border) + safeFrame['cb']) / safeFrame_height, 1.0)
                print('self.op_Region: ', self.op_Region)
                print('border: ', border)
                print('safeFrame: ', safeFrame)
                print('Object Region: ', self.data_Region[0])

                c4d.CallCommand(12113)  # Deselect All
                for obj in op:
                    doc.AddUndo(c4d.UNDOTYPE_BITS, obj)  # 언도 추가
                    doc.SetSelection(obj , mode=c4d.SELECTION_ADD)
            elif Id == self.ID_CALCULATE_ALLFRAME: # 전체 프레임 영역 계산
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
                
                if self.renderTab.IsSelected(self.ID_RENDERER_OCT): # Octane Render
                    for iFrame in range(startFrame, endFrame + 1):
                        SetCurrentFrame(iFrame, doc)

                        merged_object = self.GetMergedObject(op, doc)

                        self.op_Region['x1'], self.op_Region['x2'], self.op_Region['y1'], self.op_Region['y2'] \
                        = self.GetObjectFrameRange(merged_object, doc, rbd)

                        self.data_Region.append({})
                        self.data_Region[-1]['x1'] = max((self.op_Region['x1'] - border - safeFrame['cl']) / safeFrame_width, 0.0)
                        self.data_Region[-1]['x2'] = min((-(self.op_Region['x2'] + border) + safeFrame['cr']) / safeFrame_width, 1.0)
                        self.data_Region[-1]['y1'] = max((self.op_Region['y1'] - border - safeFrame['ct']) / safeFrame_height, 0.0)
                        self.data_Region[-1]['y2'] = min((-(self.op_Region['y2'] + border) + safeFrame['cb']) / safeFrame_height, 1.0)
                        self.data_Region[-1]['frame'] = iFrame

                        merged_object.Remove()
                        self.ShowObjectRegion(self.op_Region, doc, rbd, iFrame)
                        c4d.DrawViews(c4d.DRAWFLAGS_NO_THREAD | c4d.DRAWFLAGS_FORCEFULLREDRAW)   
                elif self.renderTab.IsSelected(self.ID_RENDERER_RS): # Redshift | Cinema 4D
                    op_Region_Previous = {}
                    self.data_Region = []

                    for iFrame in range(startFrame, endFrame + 1):
                        SetCurrentFrame(iFrame, doc)
                        merged_object = self.GetMergedObject(op, doc)

                        self.op_Region['x1'], self.op_Region['x2'], self.op_Region['y1'], self.op_Region['y2'] \
                        = self.GetObjectFrameRange(merged_object, doc, rbd)

                        if iFrame == startFrame:
                            op_Region_Previous['x1'], op_Region_Previous['x2'], op_Region_Previous['y1'], op_Region_Previous['y2'] \
                            = self.op_Region['x1'], self.op_Region['x2'], self.op_Region['y1'], self.op_Region['y2']
                        
                        self.op_Region['x1'] = min(self.op_Region['x1'], op_Region_Previous['x1'])
                        self.op_Region['x2'] = max(self.op_Region['x2'], op_Region_Previous['x2'])
                        self.op_Region['y1'] = min(self.op_Region['y1'], op_Region_Previous['y1'])
                        self.op_Region['y2'] = max(self.op_Region['y2'], op_Region_Previous['y2'])

                        self.data_Region.append({})
                        self.data_Region[-1]['x1'] = max((self.op_Region['x1'] - border - safeFrame['cl']) / safeFrame_width, 0.0)
                        self.data_Region[-1]['x2'] = min((-(self.op_Region['x2'] + border) + safeFrame['cr']) / safeFrame_width, 1.0)
                        self.data_Region[-1]['y1'] = max((self.op_Region['y1'] - border - safeFrame['ct']) / safeFrame_height, 0.0)
                        self.data_Region[-1]['y2'] = min((-(self.op_Region['y2'] + border) + safeFrame['cb']) / safeFrame_height, 1.0)                        
                        self.data_Region[-1]['frame'] = iFrame


                        op_Region_Previous['x1'], op_Region_Previous['x2'], op_Region_Previous['y1'], op_Region_Previous['y2'] \
                            = self.op_Region['x1'], self.op_Region['x2'], self.op_Region['y1'], self.op_Region['y2']
                        
                        merged_object.Remove()
                        self.ShowObjectRegion(self.op_Region, doc, rbd, iFrame)   
                        c4d.DrawViews(c4d.DRAWFLAGS_NO_THREAD | c4d.DRAWFLAGS_FORCEFULLREDRAW)      
                
                SetCurrentFrame(originFrame, doc)
                c4d.CallCommand(12113)  # Deselect All
                for obj in op:
                    doc.AddUndo(c4d.UNDOTYPE_BITS, obj)  # 언도 추가
                    doc.SetSelection(obj , mode=c4d.SELECTION_ADD)

            doc.EndUndo()
            c4d.EventAdd()   

        if Id == self.ID_BAKERENDERREGION:
            doc = c4d.documents.GetActiveDocument()
            rdt = doc.GetActiveRenderData()
            octane = rdt.GetFirstVideoPost()

            if len(self.data_Region) == 1:
                if self.renderTab.IsSelected(self.ID_RENDERER_OCT):
                    if rdt[c4d.RDATA_RENDERENGINE] != 1029525: # Check Octane Render
                        gui.MessageDialog("Please set the render engine to Octane Render.")
                        return False 
                    rdt[c4d.RDATA_RENDERREGION] = False

                    # Remove existing tracks if they exist
                    existing_track_x1 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_X1, c4d.DTYPE_REAL, 0)))
                    existing_track_x2 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_X2, c4d.DTYPE_REAL, 0)))
                    existing_track_y1 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_Y1, c4d.DTYPE_REAL, 0)))
                    existing_track_y2 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_Y2, c4d.DTYPE_REAL, 0)))

                    octane[c4d.VP_RENDERREGION] = True
                    octane[c4d.VP_REGION_X1] = self.data_Region[0]['x1']
                    octane[c4d.VP_REGION_X2] = self.data_Region[0]['x2']
                    octane[c4d.VP_REGION_Y1] = self.data_Region[0]['y1']
                    octane[c4d.VP_REGION_Y2] = self.data_Region[0]['y2']
                elif self.renderTab.IsSelected(self.ID_RENDERER_RS):
                    if (rdt[c4d.RDATA_RENDERENGINE] != 1036219 and
                        rdt[c4d.RDATA_RENDERENGINE] != 0 and
                        rdt[c4d.RDATA_RENDERENGINE] != 1023342 and
                        rdt[c4d.RDATA_RENDERENGINE] != 300001061):
                        gui.MessageDialog("Please set the render engine to Redshift or Standard or Physical Render.")
                        return False
                    rdt[c4d.RDATA_RENDERREGION] = True
                    rdt[c4d.RDATA_RENDERREGION_LEFT] = self.data_Region[0]['x1'] * rdt[c4d.RDATA_XRES_VIRTUAL]
                    rdt[c4d.RDATA_RENDERREGION_RIGHT] = self.data_Region[0]['x2'] * rdt[c4d.RDATA_XRES_VIRTUAL]
                    rdt[c4d.RDATA_RENDERREGION_TOP] = self.data_Region[0]['y1'] * rdt[c4d.RDATA_YRES_VIRTUAL]
                    rdt[c4d.RDATA_RENDERREGION_BOTTOM] = self.data_Region[0]['y2'] * rdt[c4d.RDATA_YRES_VIRTUAL]
                c4d.EventAdd()
            elif len(self.data_Region) > 1:
                if self.renderTab.IsSelected(self.ID_RENDERER_OCT):
                    if rdt[c4d.RDATA_RENDERENGINE] != 1029525: # Check Octane Render
                        gui.MessageDialog("Please set the render engine to Octane Render.")
                        return False 
                        # Create a new visibility track for Octane render region
                    # Remove existing tracks if they exist
                    existing_track_x1 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_X1, c4d.DTYPE_REAL, 0)))
                    existing_track_x2 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_X2, c4d.DTYPE_REAL, 0)))
                    existing_track_y1 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_Y1, c4d.DTYPE_REAL, 0)))
                    existing_track_y2 = octane.FindCTrack(c4d.DescID(c4d.DescLevel(c4d.VP_REGION_Y2, c4d.DTYPE_REAL, 0)))

                    if existing_track_x1: track_x1 = existing_track_x1.Remove()
                    if existing_track_x2: track_x2 = existing_track_x2.Remove()
                    if existing_track_y1: track_y1 = existing_track_y1.Remove()
                    if existing_track_y2: track_y2 = existing_track_y2.Remove()
                    
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

                    print('Data Region: ', self.data_Region)
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
                elif self.renderTab.IsSelected(self.ID_RENDERER_RS):
                    if (rdt[c4d.RDATA_RENDERENGINE] != 1036219 and
                        rdt[c4d.RDATA_RENDERENGINE] != 0 and
                        rdt[c4d.RDATA_RENDERENGINE] != 1023342 and
                        rdt[c4d.RDATA_RENDERENGINE] != 300001061):
                        gui.MessageDialog("Please set the render engine to Redshift or Standard or Physical Render.")
                        return False
                    rdt[c4d.RDATA_RENDERREGION] = True
                    rdt[c4d.RDATA_RENDERREGION_LEFT] = int(self.data_Region[0]['x1'] * rdt[c4d.RDATA_XRES_VIRTUAL])
                    rdt[c4d.RDATA_RENDERREGION_RIGHT] = int(self.data_Region[0]['x2'] * rdt[c4d.RDATA_XRES_VIRTUAL])
                    rdt[c4d.RDATA_RENDERREGION_TOP] = int(self.data_Region[0]['y1'] * rdt[c4d.RDATA_YRES_VIRTUAL])
                    rdt[c4d.RDATA_RENDERREGION_BOTTOM] = int(self.data_Region[0]['y2'] * rdt[c4d.RDATA_YRES_VIRTUAL])
                
                c4d.EventAdd()
        return True
    
    def DeleteRenderRegionGuide(self):
        doc = c4d.documents.GetActiveDocument()
        """Delete all splines in the document."""
        for op in doc.GetObjects():
            if op.GetName().find('MW_OBJECT_RENDER_REGION') != -1:
                doc.AddUndo(c4d.UNDOTYPE_DELETE, op)
                op.Remove()
        c4d.EventAdd()

    def GetMergedObject(self, op, doc):
        # Insert clones of all input objects under a new null object and insert that null object into
        # the dummy document.
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
        # doc.InsertObject(joinResult)

        if not isinstance(joinResult, c4d.BaseObject):
            raise RuntimeError("Unexpected return value for Join tool.")
        if not isinstance(joinResult, c4d.PointObject):
            raise RuntimeError("Return value is not a point object.")

    
        # print('Join Result: ', joinResult)
        return joinResult

    def GetObjectFrameRange(self, op, doc, rbd):
        rbd = doc.GetRenderBaseDraw()

        pointX = list(); pointY = list()

        if op is None:
            msg = "Please select an object."
            raise ValueError(msg)
        if not isinstance(op, c4d.PointObject):
            raise TypeError("Please select a point object.")
        mg = op.GetMg()  # the global transform of the node
        points = [p * mg for p in op.GetAllPoints()]
        # print('Points: ', points)
        for ipoint in points:
            pointPos = rbd.WS(ipoint)
            pointX.append(math.ceil(pointPos.x))
            pointY.append(math.ceil(pointPos.y))

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

        # Close the spline
        rectSpline[c4d.SPLINEOBJECT_CLOSED] = True
        rectSpline[c4d.ID_BASEOBJECT_USECOLOR] = 2
        rectSpline[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1, 0, 0)
        borderSpline[c4d.SPLINEOBJECT_CLOSED] = True
        borderSpline[c4d.ID_BASEOBJECT_USECOLOR] = 2
        borderSpline[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(.5, .5, .5)
        
        rectSpline.SetName('MW_OBJECT_RENDER_REGION_RECTSPLINE')
        borderSpline.SetName('MW_OBJECT_RENDER_REGION_BORDERSPLINE')

        if frame is not None:
            self.AddVisibilityTrack(rectSpline, frame)
            self.AddVisibilityTrack(borderSpline, frame)

        # Insert the rectangle spline into the document
        rectSpline.ChangeNBit(c4d.NBIT_OHIDE, c4d.NBITCONTROL_SET)
        doc.InsertObject(rectSpline)
        doc.AddUndo(c4d.UNDOTYPE_NEW, rectSpline)

        borderSpline.ChangeNBit(c4d.NBIT_OHIDE, c4d.NBITCONTROL_SET)
        doc.InsertObject(borderSpline)
        doc.AddUndo(c4d.UNDOTYPE_NEW, borderSpline)
        return True

    def AddVisibilityTrack(self, op, frame):
        if not op: return

        doc = c4d.documents.GetActiveDocument()
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
        if id == c4d.EVMSG_CHANGE:
            doc = c4d.documents.GetActiveDocument()
            op = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_NONE | c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)

            op_name = "\n".join([obj.GetName() for obj in op])
            self.SetString(self.ID_OBJECTSLIST, op_name)
        return super().CoreMessage(id, msg)


class MWMovingREnderRegionCommand(plugins.CommandData):
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
            self.dialog = MWMovingRenderRegion()

        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=300, defaulth=450)

    def RestoreLayout(self, sec_ref):
        """Used to restore an asynchronous dialog that has been placed in the users layout.

        Args:
            sec_ref (PyCObject): The data that needs to be passed to the dialog.

        Returns:
            bool: True if the restore success
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MWMovingRenderRegion()

        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)


if __name__ == "__main__":
    plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                  str="MW Moving Render Region",
                                  info=0,
                                  help="Set the render region of the selected object.",
                                  dat=MWMovingREnderRegionCommand(),
                                  icon=None)

"""
References:

Get PLA DATA
https://developers.maxon.net/forum/topic/14305/get-spline-points-positions-from-pla-keyframes/2?_=1732456672668

AliasTrans
https://developers.maxon.net/forum/topic/6917/7764_how-to-clone-a-character-skin--skeleton-/3?_=1732504493195

Object List GUI
https://developers.maxon.net/forum/topic/10770/14214_inexclude-customgui-in-pythonplugin/2?_=1732760629379
"""