import c4d
import os
from c4d import bitmaps

PLUGIN_ID = 1061265

class QuickAxisCenter(c4d.gui.GeDialog):
    doc = c4d.documents.GetActiveDocument()
    ID_CAL_CHILD = 1001
    ID_BOUNDINGBOX = 1051
    ID_REFRESH_BOUNDINGBOX = 1052
    ID_CENTER = 1101; ID_CENTER_Y_M = 1102; ID_CENTER_XZ = 1103
    ID_X_P = 1201; ID_X_C = 1202; ID_X_M = 1203 
    ID_Y_P = 1204; ID_Y_C = 1205; ID_Y_M = 1206
    ID_Z_P = 1207; ID_Z_C = 1208; ID_Z_M = 1209
    ID_WORLD_ZERO = 1210; ID_PARENT_ZERO = 1211; ID_LAST_OBJECT = 1212
    ID_RESET_ROTATION = 1301; ID_RESET_SCALE = 1302
    BOUNDINGBOXNAME = '_!BoundingBoxPreview!_'
    
    def DestroyWindow(self):
        """
        This function is called when the dialog window is destroyed.
        It is responsible for hiding the bounding box preview.

        Returns:
            None
        """
        # Get the active document
        self.doc = c4d.documents.GetActiveDocument()
        
        # Get the active objects
        op = self.doc.GetActiveObjects(1)
        
        # Hide the bounding box preview
        self.ShowBoundingBox(op, False)
        
        # Redraw the screen to reflect the changes
        c4d.EventAdd()
    
    def CreateLayout(self):
        """
        Create the layout of the Quick Axis Center dialog.

        Returns:
            bool: True if the layout was created successfully.
        """
        # Set the title of the dialog
        self.SetTitle("MW Quick Axis Center")

        # Create the main group
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=1)

        # Create the child calculation checkbox
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=2)
        self.GroupBorderSpace(10, 5, 10, 10)
        self.AddCheckbox(self.ID_CAL_CHILD, c4d.BFH_FIT,300,10,name = 'Calculate Children Bounding Box')
        self.SetBool(self.ID_CAL_CHILD, True)
        self.AddCheckbox(self.ID_BOUNDINGBOX, c4d.BFH_RIGHT,300,10,name = 'Show Bounding Box')
        self.SetBool(self.ID_BOUNDINGBOX, True)
        self.GroupEnd()

        # Create the refresh bounding box button
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=1)
        self.AddButton(self.ID_REFRESH_BOUNDINGBOX, c4d.BFH_SCALEFIT, name='Refresh Bounding Box')
        self.GroupEnd()

        # Create the separator
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1)
        self.GroupBorderSpace(0,2,0,2)
        self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT)
        self.GroupEnd()

        # Create the reset position buttons
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=3)
        self.AddButton(self.ID_CENTER, c4d.BFH_SCALEFIT, name='Axis to Center')
        self.AddButton(self.ID_CENTER_Y_M, c4d.BFH_SCALEFIT, name='Axis to Center -Y')
        self.GroupEnd()

        # Create the reset position buttons
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=3)
        self.AddButton(self.ID_X_P, c4d.BFH_SCALEFIT, name='+X')
        self.AddButton(self.ID_Y_P, c4d.BFH_SCALEFIT, name='+Y')
        self.AddButton(self.ID_Z_P, c4d.BFH_SCALEFIT, name='+Z')
        self.AddButton(self.ID_X_M, c4d.BFH_SCALEFIT, name='-X')
        self.AddButton(self.ID_Y_M, c4d.BFH_SCALEFIT, name='-Y')
        self.AddButton(self.ID_Z_M, c4d.BFH_SCALEFIT, name='-Z')
        self.GroupEnd()

        # Create the reset position buttons
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=1)
        self.GroupBorderSpace(0,2,0,0)
        self.AddButton(self.ID_WORLD_ZERO, c4d.BFH_SCALEFIT, name='Axis to World Zero')
        self.AddButton(self.ID_PARENT_ZERO, c4d.BFH_SCALEFIT, name='Axis to Parent Zero')
        self.AddButton(self.ID_LAST_OBJECT, c4d.BFH_SCALEFIT, name='Axis to Last Selected Object')
        self.GroupEnd()

        # Create the separator
        self.GroupBegin(9999, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1)
        self.GroupBorderSpace(0,2,0,2)
        self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT)
        self.GroupEnd()

        # Create the reset rotation section
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=1)
        self.GroupEnd()

        # Create the reset rotation buttons
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=2)
        self.AddButton(self.ID_RESET_SCALE, c4d.BFH_SCALEFIT, name='Reset Scale')
        self.AddButton(self.ID_RESET_ROTATION, c4d.BFH_SCALEFIT, name='Reset Rotation')
        self.GroupEnd()

        # End of the main group
        self.GroupEnd()

        # Get the active document and objects
        self.doc = c4d.documents.GetActiveDocument()
        op = self.doc.GetActiveObjects(1 | 2)

        # Show the bounding box based on the checkbox state
        self.ShowBoundingBox(op, self.GetBool(self.ID_BOUNDINGBOX))

        # Add an event
        c4d.EventAdd()

        # Return True to indicate success
        return True

    def Command(self, cid, bc):
        """
        This function is called when a command is executed.

        Args:
            cid (int): The ID of the command.
            bc (c4d.BaseContainer): The BaseContainer associated with the command.

        Returns:
            bool: True if the command was executed successfully.
        """
        # Get the active document
        self.doc = c4d.documents.GetActiveDocument()
        
        # Start an undo block
        self.doc.StartUndo()

        # Get the active objects
        op = self.doc.GetActiveObjects(1 | 2)

        # Check the ID of the command
        if cid == self.ID_BOUNDINGBOX or cid == self.ID_REFRESH_BOUNDINGBOX:
            # Show/hide the bounding box based on the checkbox state
            self.ShowBoundingBox(op, self.GetBool(self.ID_BOUNDINGBOX))
        elif cid >= self.ID_CENTER and cid <= self.ID_LAST_OBJECT: 
            # Reset the position of the objects based on the command ID
            self.ResetPosition(op, cid)
        elif cid == self.ID_RESET_SCALE:
            # Reset the scale of the objects
            self.ResetScale(op)
        elif cid == self.ID_RESET_ROTATION:
            # Reset the rotation of the objects
            self.ResetRotation(op)

        # End the undo block
        self.doc.EndUndo()

        # Add an event
        c4d.EventAdd()

        # Return True to indicate success
        return True

    def ShowBoundingBox(self, op, show_boundingbox):
        #Remove Previous Bounding Boxes
        top = self.doc.GetObjects()
        for iObj in top: 
            if self.BOUNDINGBOXNAME in iObj[c4d.ID_BASELIST_NAME] and iObj.GetType() == c4d.Onull:
                iObj.Remove()
        if show_boundingbox == False: return

        #Calculate Axis Position
        for iObj in op:
            pointX = []; pointY = []; pointZ = []
            pointX, pointY, pointZ = self.GetPointList(iObj, pointX, pointY, pointZ)
            
            m = iObj.GetMg()
            axisX = m.off.x; axisY = m.off.y; axisZ = m.off.z
            
            if pointX:
                axisX = (min(pointX) + max(pointX)) / 2
                axisY = (min(pointY) + max(pointY)) / 2
                axisZ = (min(pointZ) + max(pointZ)) / 2
                lenX = max(pointX) - min(pointX)
                lenY = max(pointY) - min(pointY)
                lenZ = max(pointZ) - min(pointZ)

                boundingBox = c4d.BaseObject(c4d.Onull)
                # boundingBox.SetRenderMode(c4d.MODE_OFF)
                boundingBox[c4d.ID_BASELIST_NAME] = iObj.GetName() + self.BOUNDINGBOXNAME
                boundingBox[c4d.ID_BASEOBJECT_REL_POSITION] = c4d.Vector(axisX, axisY, axisZ)
                boundingBox[c4d.NULLOBJECT_RADIUS] = 0.5
                boundingBox[c4d.NULLOBJECT_DISPLAY] = 11 # Cube Shape Null
                boundingBox[c4d.ID_BASEOBJECT_REL_SCALE] = c4d.Vector(lenX, lenY, lenZ)
                boundingBox[c4d.ID_BASEOBJECT_USECOLOR] = 2
                boundingBox[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(0,1,0)
                boundingBox.ChangeNBit(c4d.NBIT_OHIDE, c4d.NBITCONTROL_SET)
                
                # layerRoot = self.doc.GetLayerObjectRoot() # Get layer object root
                # layer = c4d.documents.LayerObject() # Initialize a layer object
                # layer.SetName(self.BOUNDINGBOXNAME) # Set layer's name
                # layer.InsertUnder(layerRoot) # Insert layer to layer root
                # layer[c4d.ID_LAYER_MANAGER] = False
                # # layer[c4d.ID_LAYER_RENDER] = False
                # boundingBox[c4d.ID_LAYER_LINK] = layer # Set layer to the null
                
                #userdatatag[c4d.ID_LAYER_LINK] = None

                self.doc = c4d.documents.GetActiveDocument()
                self.doc.InsertObject(boundingBox)
                
                # iObj.Message(c4d.MSG_UPDATE)
        return
        
    def GetNextObject(self, op, op_origin = None): #다음 오브젝트로 이동하는 함수
        if not op: return
        elif op.GetDown(): #자식 오브젝트가 있으면 자식 오브젝트로 리턴
            return op.GetDown()
        while op.GetUp() and not op.GetNext():
            op = op.GetUp()
            if(op == op_origin): return #부모 오브젝트를 찾다가 op_origin을 만나면 함수 종료.

        if(op == op_origin): return #윗 과정을 거쳤을때도 op와 op_origin이 같으면 함수 종료.
        return op.GetNext() #다음 오브젝트를 리턴.
    
    def GetChildMg(self, op):
        opList = list()
        for i,iObj in enumerate(op.GetChildren()): #자식 오브젝트 좌표 기억하기
            opList.append(iObj.GetMg())
        return opList

    def SetChildMg(self, op, opList):
        for i,iObj in enumerate(op.GetChildren()): #자식 오브젝트 좌표 기억하기
            self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, iObj) # Undo 추가
            iObj.SetMg(opList[i])
            iObj.Message(c4d.MSG_UPDATE)
        return
    
    def GetPointList(self, op, pointX: list, pointY: list, pointZ: list): #PointList를 추가해주는 함수
        calChildFlag = True
        top = op #tempObj

        #top의 자식 오브젝트가 없거나 Calculate Children Bounding Box의 체크가 해제되어있으면?
        if not top.GetChildren() or self.GetBool(self.ID_CAL_CHILD) == False:
            calChildFlag = False #자식 오브젝트가 없음을 알림

        while top:
            #자식 오브젝트가 없고 top가 op가 아니면? 종료
            if not calChildFlag and top != op: break 

            top_Cached = top

             #해당 오브젝트가 깰 수 있는 상태면? instance 형태거나 디포머가 들어있거나 제너레이터가 들어있거나 등등..
             #디폼캐시, 캐시 검사를 먼저해줘야 무슨 오브젝트인지 알 수 있고, 디폼된 포인트를 입력받을 수 있음. 그러므로 최우선으로 캐시를 검사해야함
            
            while True:
                #해당 오브젝트가 Cache 상태로 변환 할 수 있으면 계속 변환
                if(top_Cached.GetDeformCache()): top_Cached = top_Cached.GetDeformCache() #디폼캐시가 가능하면 top_Cached를 디폼캐시로 받아오기, 디포머 등
                elif(top_Cached.GetCache()): top_Cached = top_Cached.GetCache() #캐시가 가능하면 top_Cached를 캐시로 받아오기, instance나 제너레이터 등
                if top_Cached.GetDeformCache() or top_Cached.GetCache(): continue
                break

            #Cache 상태로 변환 했을 때, 자식 오브젝트가 있다면?
            if top_Cached.GetChildren():
                pointX, pointY, pointZ = self.GetPointList(top_Cached, pointX, pointY, pointZ) #자식 오브젝트가 또 Cache가 가능한 상태일 수도 있으므로 캐시된 오브젝트를(top_Cached) 기준으로(본인 포인트도 검사해야하므로) 재귀
                top = self.GetNextObject(top, op) #top_Cached까지 검사를 끝냈으므로 다음 오브젝트로 넘어가기
                continue
            
            #캐시된 오브젝트가 포인트 타입 오브젝트가 아니면?
            if not top_Cached.CheckType(c4d.Opoint):
                top = self.GetNextObject(top, op) #다음 오브젝트로 넘어가기
                continue

            pointlist = top_Cached.GetAllPoints() # 모든 포인트 입력받기
            top_Cached_mg = top_Cached.GetMg() # 캐시된 오브젝트의 글로벌 매트릭스 값 받아오기
            for ipoint in pointlist:
                pointVector = top_Cached_mg*ipoint #글로벌 매트릭스에 포인트 값(Vector)을 곱해서 포인트의 글로벌 좌표 계산
                pointX.append(pointVector.x)
                pointY.append(pointVector.y)
                pointZ.append(pointVector.z)
            top = self.GetNextObject(top, op)
        return pointX, pointY, pointZ
    
    def ResetPosition(self, op, axisCommand: int):
        for iObj in op:
            pointX = []; pointY = []; pointZ = []
            m = iObj.GetMg()
            axisX = m.off.x; axisY = m.off.y; axisZ = m.off.z
            if axisCommand == self.ID_WORLD_ZERO: 
                #print('WorldZero')
                axisX, axisY, axisZ = 0, 0, 0
            elif axisCommand == self.ID_PARENT_ZERO:
                if iObj.GetUp():
                    axisX = iObj.GetUp().GetMg().off.x
                    axisY = iObj.GetUp().GetMg().off.y
                    axisZ = iObj.GetUp().GetMg().off.z
                else: continue
            elif axisCommand == self.ID_LAST_OBJECT:
                axisX = op[-1].GetMg().off.x
                axisY = op[-1].GetMg().off.y
                axisZ = op[-1].GetMg().off.z
                #print(axisX, axisY, axisZ)
            else:   
                pointX, pointY, pointZ = self.GetPointList(iObj, pointX, pointY, pointZ)
            
            if pointX:
                if axisCommand == self.ID_CENTER:
                    axisX = (min(pointX) + max(pointX)) / 2
                    axisY = (min(pointY) + max(pointY)) / 2
                    axisZ = (min(pointZ) + max(pointZ)) / 2
                elif axisCommand == self.ID_CENTER_Y_M:
                    axisX = (min(pointX) + max(pointX)) / 2
                    axisY = min(pointY)
                    axisZ = (min(pointZ) + max(pointZ)) / 2
                elif axisCommand == self.ID_CENTER_XZ:
                    axisX = (min(pointX) + max(pointX)) / 2
                    axisZ = (min(pointZ) + max(pointZ)) / 2
                elif axisCommand == self.ID_X_P: axisX = max(pointX)
                elif axisCommand == self.ID_X_C: axisX= (min(pointX) + max(pointX)) / 2
                elif axisCommand == self.ID_X_M: axisX= min(pointX)
                elif axisCommand == self.ID_Y_P: axisY= max(pointY)
                elif axisCommand == self.ID_Y_C: axisY= (min(pointY) + max(pointY)) / 2
                elif axisCommand == self.ID_Y_M: axisY = min(pointY)            
                elif axisCommand == self.ID_Z_P: axisZ = max(pointZ)
                elif axisCommand == self.ID_Z_C: axisZ= (min(pointZ) + max(pointZ)) / 2
                elif axisCommand == self.ID_Z_M: axisZ = min(pointZ)


            iObjChild = self.GetChildMg(iObj)
            if not iObj.CheckType(c4d.Opoint) or (iObj.CheckType(c4d.Opoint) and iObj.GetPointCount() == 0):
                m = iObj.GetMg()
                new_m = c4d.Matrix(m)
                new_m.off = c4d.Vector(axisX, axisY, axisZ)
                self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, iObj) # Undo 추가
                iObj.SetMg(new_m)
            elif iObj.CheckType(c4d.Opoint):
                ps = iObj.GetAllPoints() #Points in Local coordinates List
                m = iObj.GetMg() #Object Global Matrix
                axis = c4d.Vector(axisX, axisY, axisZ) #Convert to Global coordinates center
                new_m = c4d.Matrix(m) #CiObjy matrix
                new_m.off = axis #Change its axis
                loc_m = ~new_m * m #Get local matrix
                self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, iObj) # Undo 추가
                iObj.SetAllPoints([loc_m.Mul(p) for p in ps])
                self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, iObj) # Undo 추가
                iObj.SetMg(new_m)

            self.SetChildMg(iObj, iObjChild)
            iObj.Message(c4d.MSG_UPDATE)
            c4d.EventAdd()

    def ResetScale(self, op):
        settings = c4d.BaseContainer()
        settings[c4d.MDATA_RESETSYSTEM_COMPENSATE] = True
        settings[c4d.MDATA_RESETSYSTEM_RECURSIVE] = True
        for iObj in op:
            self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, iObj)
            c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_RESETSYSTEM,
                                            list=[iObj],
                                            mode=c4d.MODELINGCOMMANDMODE_ALL,
                                            bc=settings,
                                            doc=self.doc)
        return

    def ResetRotation(self, op):
        for iObj in op:
            iObjChild = self.GetChildMg(iObj)
            if not iObj.CheckType(c4d.Opoint) or (iObj.CheckType(c4d.Opoint) and iObj.GetPointCount() == 0):
                m = iObj.GetMg()
                new_m = c4d.Matrix()
                new_m.off = m.off
                self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, iObj) # Undo 추가
                iObj.SetMg(new_m)
            elif iObj.CheckType(c4d.Opoint):
                mg = iObj.GetMg() # Get current Matrix
                scale = c4d.Vector( mg.v1.GetLength(),
                                    mg.v2.GetLength(),
                                    mg.v3.GetLength()) # extracts the scale of the current matrix
                # Builds a new matrix with the expected rotation
                HPB_rot = c4d.Vector()
                m = c4d.utils.HPBToMatrix(HPB_rot)
                m.off = mg.off
                m.v1 = m.v1.GetNormalized() * scale.x
                m.v2 = m.v2.GetNormalized() * scale.y
                m.v3 = m.v3.GetNormalized() * scale.z
                
                #Applies the new matrix, so scale and position should not change while rotation should be equal to #HPB_rot#
                self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, iObj)
                iObj.SetMg(m)
                #self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, iObj)
                iObj.SetRelRot(c4d.Vector(0,0,0)) # Rotation 값을 0으로 재정리, 360' 720' 등 변해도 되지 않은 값 깔끔하게 정리
                #Computes the transformation that happened from initial state to the current state
                transform = ~iObj.GetMg()*mg
                #Transforms all points to compensate the axis change
                transformedPoints: list[c4d.Vector] = [transform * p for p in iObj.GetAllPoints()]
                #self.doc.AddUndo(c4d.UNDOTYPE_CHANGE, iObj)
                iObj.SetAllPoints(transformedPoints)
                iObj.Message(c4d.MSG_UPDATE)
            self.SetChildMg(iObj, iObjChild)
        return

class QuickAxisCenterCommand(c4d.plugins.CommandData):
    dialog = None
    
    def Execute(self, doc):
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = QuickAxisCenter()

        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=400, defaulth=10)

    def RestoreLayout(self, sec_ref):
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = QuickAxisCenter()

        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

if __name__ == "__main__": # main
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "MW Quick Axis Center.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the plugin
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                      str="MW Quick Axis Center",
                                      info=0,
                                      help="Display a basic GUI Dialog",
                                      dat= QuickAxisCenterCommand(),
                                      icon=bmp)
