import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1060476

ID_NAME = 1001

ID_MAINGROUP: int = 100
ID_TEXT_SEARCH: int = 101
ID_TREEVIEW: int = 102
ID_BTN_FOLD: int = 103
ID_BTN_UNFOLD: int = 104
dlg = None

def BuildObjectData():
    global treeFlag, allObj, selObj, allObjLv, searchObj, searchObjLv, iClass
    
    #c4d.CallCommand(13957, 13957) #Clear Console
    treeFlag = 0
    allObj = []

    #Main Class
    iClass = []

    doc = c4d.documents.GetActiveDocument()
    selObj = doc.GetActiveObjects(1)
    allObjLv = []

    #Getting All Objects and Level
    op = doc.GetFirstObject()
    opLv = 0
    sortCnt = 0

    #Getting All Objects and Building Object Data(Sort, Levels)
    while op:
        if op in selObj:
            allObj.insert(sortCnt,op)
            allObjLv.insert(sortCnt,opLv)
            sortCnt +=1
        else:
            allObj.append(op)
            allObjLv.append(opLv)
        op, opLv = walk(op, opLv)

    #Copy allObj to searchObj
    searchObj = allObj
    searchObjLv = allObjLv

def walk(op, level): #object search fuction & memory object parent level
    if not op: return
    elif op.GetDown():
        level += 1
        return op.GetDown(), level
    while op.GetUp() and not op.GetNext():
        level -= 1
        op = op.GetUp()
    return op.GetNext(), level

def SelectObjectEnd(): #object select and close fuction
    global iClass
    c4d.CallCommand(100004767, 100004767) #Deselect All
    doc = c4d.documents.GetActiveDocument()
    doc.SetMode(m = c4d.Mobject) #모드를 Mobject모드로 변경
    for i,iObj in enumerate(iClass):
        if(iObj.IsSelected == True):
            iObj.objData.SetBit(c4d.BIT_ACTIVE) # Select Selecten Object
    c4d.CallCommand(100004769) #Scroll To Selection
    c4d.EventAdd()
    dlg.Close()

def SearchObjectList(selObjName):
    global searchObj, searchObjLv, iClass, allObj, allObjLv
    dlg._listView.listOfObjects = [] #Clear member list
    selObjName = selObjName.upper() #unify string
    searchObj = [] #clear searchObj list
    searchObjLv = [] #clear searchObjLv list
    iClass = [] #clear member variable list
    dlg._listView.listOfObjects = []

    if selObjName == '':
        for i,iObj in enumerate(allObj):
            iClass.append(ListObject(iObj))
            searchObj.append(iObj)
            searchObjLv.append(allObjLv[i])
            dlg._listView.listOfObjects.extend([iClass[len(iClass)-1]]) #iClass
    else: #when selObjName typed
        for i,iObj in enumerate(allObj):
            if selObjName in iObj.GetName().upper(): 
                iClass.append(ListObject(iObj))
                searchObj.append(iObj)
                searchObjLv.append(allObjLv[i])
                dlg._listView.listOfObjects.extend([iClass[len(iClass)-1]]) #iClass
                iClass[0].Select()
    return


class ListObject():
    """
    Class which represent a texture, aka an Item in our list
    """
    objName = None
    objData = None
    objSelected = False
    def __init__(self, obj):
        self.objName = obj[c4d.ID_BASELIST_NAME]
        self.objData = obj

    @property
    def IsSelected(self):
        return self.objSelected

     #if checkbox is enable
    def Select(self):
        self.objSelected = True

    def Deselect(self):
        self.objSelected = False
    '''
    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.objName
    '''

class ListView(c4d.gui.TreeViewFunctions):

    def __init__(self):
        global iClass
        self.listOfObjects = list() # Store all objects we need to display in this list

        for i,iObj in enumerate(searchObj):
            iClass.append(ListObject(iObj))
            self.listOfObjects.append(iClass[i])
    def GetColumnWidth(self, root, userdata, obj, col, area):
        return 270  # All have the same initial width

    def GetLineHeight(self, root, userdata, obj, col, area):
        return 20 # Return LineHeight

    def IsResizeColAllowed(self, root, userdata, lColID):
        return True

    def IsTristate(self, root, userdata):
        return False

    def IsMoveColAllowed(self, root, userdata, lColID):
        # The user is allowed to move all columns.
        # TREEVIEW_MOVE_COLUMN must be set in the container of AddCustomGui.
        return True

    def GetFirst(self, root, userdata):
        """
        Return the first element in the hierarchy, or None if there is no element.
        """
        rValue = None if not self.listOfObjects else self.listOfObjects[0]
        return rValue

    def GetDown(self, root, userdata, obj):
        """
        Return a child of a node, since we only want a list, we return None everytime
        """
        return None

    def GetNext(self, root, userdata, obj):
        """
        Returns the next Object to display after arg:'obj'
        """
        rValue = None
        currentObjIndex = self.listOfObjects.index(obj)
        nextIndex = currentObjIndex + 1
        if nextIndex < len(self.listOfObjects):
            rValue = self.listOfObjects[nextIndex]

        return rValue

    def GetPred(self, root, userdata, obj):
        """
        Returns the previous Object to display before arg:'obj'
        """
        rValue = None
        currentObjIndex = self.listOfObjects.index(obj)
        predIndex = currentObjIndex - 1
        if 0 <= predIndex < len(self.listOfObjects):
            rValue = self.listOfObjects[predIndex]

        return rValue

    def GetId(self, root, userdata, obj):
        """
        Return a unique ID for the element in the TreeView.
        """
        return hash(obj)

    def Select(self, root, userdata, obj, mode):
        """
        Called when the user selects an element.
        """
        global treeFlag
        treeFlag = 1
        if mode == c4d.SELECTION_NEW:
            for tex in self.listOfObjects:
                tex.Deselect()
            obj.Select()
        elif mode == c4d.SELECTION_ADD:
            obj.Select()
        elif mode == c4d.SELECTION_SUB:
            obj.Deselect()
        return obj

    def IsSelected(self, root, userdata, obj):
        """
        Returns: True if *obj* is selected, False if not.
        """

        return obj.IsSelected

    def SetCheck(self, root, userdata, obj, column, checked, msg):
        """
        Called when the user clicks on a checkbox for an object in a
        `c4d.LV_CHECKBOX` column.
        """
        if checked:
            obj.Select()
        else:
            obj.Deselect()

    def InputEvent(self, root, userdata, pArea, msg):
        """
        Called When InputEvnet Occurs
        """
        global iClass

        key = msg[c4d.BFM_INPUT_CHANNEL]
        iFlag = 0 #아무것도 선택되지 않았을 때 플래그 
        line = 0 #
        if(msg[c4d.BFM_INPUT_VALUE]):
            if(key == c4d.KEY_ENTER):
                SelectObjectEnd()
                return

            for i,iObj in enumerate(iClass):
                if(iObj.objSelected == True):
                    if(key == c4d.KEY_DOWN):
                        iClass[i].Deselect()
                        if(i+1 >= len(iClass)): iClass[0].Select(); line = 0
                        else: iClass[i+1].Select(); line = i+1
                    if(key == c4d.KEY_UP):
                        iClass[i].Deselect()
                        if(i-1 < 0): iClass[len(iClass)-1].Select(); line = len(iClass)-1
                        else: iClass[i-1].Select(); line = i-1
                    iFlag = 1
                    break
            if iFlag == 0 and len(iClass) > 0: #아무것도 선택되지 않고, 리스트 갯수가 하나 이상일때 첫번째 오브젝트 선택
                iClass[0].Select()


        dlg.TreeView_Refresh()

    def IsChecked(self, root, userdata, obj, column):
        """
        Returns: (int): Status of the checkbox in the specified *column* for *obj*.
        """

        if obj.IsSelected:
            return c4d.LV_CHECKBOX_CHECKED | c4d.LV_CHECKBOX_ENABLED
        else:
            return c4d.LV_CHECKBOX_ENABLED

    def GetName(self, root, userdata, obj):
        """
        Returns the name to display for arg:'obj', only called for column of type LV_TREE
        """
        return str(obj) # Or obj.texturePath

    def DrawCell(self, root, userdata, obj, col, drawinfo, bgColor):
        """
        Draw into a Cell, only called for column of type LV_USER
        """
        global searchObj, searchObjLv
        if col == ID_NAME:
            geUserArea = drawinfo["frame"]
            ICON_SIZE = drawinfo["height"]
            OBJ_NUMBER = drawinfo["line"]
            TEXT_SPACER = 2
            bgColor = c4d.COLOR_SB_TEXTHG1 if OBJ_NUMBER % 2 else c4d.COLOR_SB_TEXTHG2
            
            #Parent Level Spacing
            pObjLv = searchObjLv[OBJ_NUMBER]
            TEXT_SPACER_PARENT = pObjLv * 10
            # Draw icon bmp, Get object's icon with GetIconEx
            sIcon = searchObj[OBJ_NUMBER].GetIconEx()
            bmp = sIcon.GetGuiScalePart()
            
            geUserArea.DrawSetPen(bgColor)
            geUserArea.DrawBitmap(bmp, drawinfo["xpos"] + TEXT_SPACER_PARENT, \
                                 drawinfo["ypos"], ICON_SIZE, ICON_SIZE, 0, 0, \
                                 bmp.GetBw(), bmp.GetBh(), c4d.BMP_ALLOWALPHA)

            # Draw name
            name = str(searchObj[OBJ_NUMBER][c4d.ID_BASELIST_NAME])
            fontHeight = geUserArea.DrawGetFontHeight() 
            fontWidth = geUserArea.DrawGetTextWidth(name)

            x = drawinfo["xpos"] + ICON_SIZE + TEXT_SPACER + TEXT_SPACER_PARENT
            y = drawinfo["ypos"] + (ICON_SIZE - fontHeight) / 2

            txtColor = c4d.COLOR_SB_TEXT
            if obj.objData in selObj: txtColor = c4d.COLOR_SB_TEXT_ACTIVE2
            if obj.IsSelected: txtColor = c4d.COLOR_SB_TEXT_ACTIVE1
            geUserArea.DrawSetTextCol(txtColor, bgColor)
            geUserArea.DrawText(name, int(x), int(y))

            #dlg.TreeView_Focus(self.listOfObjects[OBJ_NUMBER]) #포커스 기능 함수 호출, 제대로 작동 안됨

    def DoubleClick(self, root, userdata, obj, col, mouseinfo):
        """
        Called when the user double-clicks on an entry in the TreeView.

        Returns:
          (bool): True if the double-click was handled, False if the
            default action should kick in. The default action will invoke
            the rename procedure for the object, causing `SetName()` to be
            called.
        """
        SelectObjectEnd()
        return True

    def DeletePressed(self, root, userdata):
        # Called when a delete event is received.
        pass
        '''
        for tex in reversed(self.listOfObjects):
            if tex.IsSelected:
                self.listOfObjects.remove(tex)
        '''

class ObjectManagerCommanderDialog(c4d.gui.GeDialog):
    _treegui = None # Our CustomGui TreeView
    BuildObjectData()
    _listView = ListView() # Our Instance of c4d.gui.TreeViewFunctions

    def InitValues(self):
        BuildObjectData()
        self._listView = ListView() # Our Instance of c4d.gui.TreeViewFunctions

        # Initialize the column layout for the TreeView.
        layout = c4d.BaseContainer()
        #layout.SetLong(ID_CHECKBOX, c4d.LV_CHECKBOX)
        layout.SetInt32(ID_NAME, c4d.LV_USERTREE)
        #layout.SetLong(ID_OTHER, c4d.LV_USER)

        self._treegui.SetLayout(3, layout) #Columns & layout Container

        # Set the header titles.
        #self._treegui.SetHeaderText(ID_CHECKBOX, "Check")
        #self._treegui.SetHeaderText(ID_NAME, "Name")
        #self._treegui.SetHeaderText(ID_OTHER, "Other")
        self.TreeView_Refresh()

        # Set TreeViewFunctions instance used by our CUSTOMGUI_TREEVIEW
        self._treegui.SetRoot(self._treegui, self._listView, None)
        
        return True

    def DestroyWindow(self):
        pass

    def TreeView_Refresh(self):
        self._treegui.Refresh()
        self.LayoutChanged(ID_TREEVIEW)

    
    ''' 
    #방향키 눌렀을 때 호출되는 포커스 함수, 지금 제대로 작동 안함
    def TreeView_Focus(self, obj):
        self._treegui.SetFocusItem(obj)
        pass
    '''

    def CreateLayout(self) -> bool:
        self.GroupBegin(ID_MAINGROUP, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1)
        self.GroupBorderSpace(0, 0, 0, 5)

        #Add EditText
        self.AddEditText(ID_TEXT_SEARCH, c4d.BFH_SCALEFIT, editflags = c4d.EDITTEXT_ENABLECLEARBUTTON) #ID, SCALEFIT TYPE BUTTON, HELPTEXT 
        doc =c4d.documents.GetActiveDocument()
        selObjList = doc.GetActiveObjects(0)
        self.SetString(ID_TEXT_SEARCH, 'Search Object Name...', flags = c4d.EDITTEXT_HELPTEXT)

        #Add TreeView
        self.GroupBegin(1000, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1)
        customgui = c4d.BaseContainer()
        customgui.SetBool(c4d.TREEVIEW_BORDER, c4d.BORDER_NONE)
        customgui.SetBool(c4d.TREEVIEW_HAS_HEADER, False) # True if the tree view may have a header line.
        customgui.SetBool(c4d.TREEVIEW_NO_MULTISELECT, False)
        customgui.SetBool(c4d.TREEVIEW_HIDE_LINES, True) # True if no lines should be drawn.
        customgui.SetBool(c4d.TREEVIEW_MOVE_COLUMN, False) # True if the user can move the columns.
        customgui.SetBool(c4d.TREEVIEW_RESIZE_HEADER, False) # True if the column width can be changed by the user.
        customgui.SetBool(c4d.TREEVIEW_FIXED_LAYOUT, True) # True if all lines have the same height.
        customgui.SetBool(c4d.TREEVIEW_ALTERNATE_BG, True) # Alternate background per line.
        customgui.SetBool(c4d.TREEVIEW_CURSORKEYS, False) # True if cursor keys should be processed.
        customgui.SetBool(c4d.TREEVIEW_NOENTERRENAME, True) # Suppresses the rename popup when the user presses enter.
        self._treegui = self.AddCustomGui(ID_TREEVIEW, c4d.CUSTOMGUI_TREEVIEW, \
                                        "", c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, \
                                        300, 200, customgui)
        self.GroupEnd()

        #Add Buttons
        self.GroupBegin(1000, c4d.BFH_SCALEFIT | c4d.BFV_BOTTOM, 2)
        self.AddButton(ID_BTN_FOLD, c4d.BFH_SCALEFIT, name="Fold All")
        self.AddButton(ID_BTN_UNFOLD, c4d.BFH_SCALEFIT, name="UnFold All")
        #return super().CreateLayout()

    def Command(self, cid: int, msg: c4d.BaseContainer ) -> bool:
        #When Search
        if cid == ID_TEXT_SEARCH:
            global treeFlag #트리뷰 선택됐는지 플래그 글로벌라이즈
            selObjName = self.GetString(ID_TEXT_SEARCH).upper() #EditText to selObjName, all upper alphabet
            treeFlag = 0 #텍스트뷰가 작동하고 있음을 알리는 플래그
            SearchObjectList(selObjName) #텍스트에 맞는 검색 결과 도출
            self.TreeView_Refresh() #트리뷰 리프레싱
        elif cid == ID_BTN_FOLD: # When Push Button Fold All
            c4d.CallCommand(100004749) # Fold All
        elif cid == ID_BTN_UNFOLD:
            c4d.CallCommand(100004748) # UnFold All

        self.GetInputState(c4d.BFM_INPUT_KEYBOARD,c4d.KEY_ENTER,msg) # if Enter Pressed than close
        if(msg[c4d.BFM_INPUT_VALUE]):
            SelectObjectEnd()
            self.Close()
        self.GetInputState(c4d.BFM_INPUT_KEYBOARD,c4d.KEY_ESC,msg)
        if(msg[c4d.BFM_INPUT_VALUE]):
            self.Close()
        return super().Command(cid, msg)
    
    def Message(self, msg: c4d.BaseContainer, result: c4d.BaseContainer) -> bool:
        global treeFlag, iClass
        if treeFlag == 0: #트리뷰가 선택되지 않았을 때,
            #키보드 입력 받기
            bc = c4d.BaseContainer()
            ok = c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, c4d.KEY_DOWN, bc)
            if ok and bc[c4d.BFM_INPUT_VALUE] == 1:
                treeFlag = 1
                if iClass[0].IsSelected == True and len(iClass) > 1: 
                    iClass[0].Deselect()
                    iClass[1].Select()
                    self.TreeView_Refresh()
                else: 
                    iClass[0].Select()
                self.Activate(ID_TREEVIEW) #After Selecting, Refreshing TreeView
                return True # 마지막에 True 반환 안하면 계속 눌리는걸로 인식
        if msg.GetId() == c4d.BFM_LOSTFOCUS: #close when lost focus
            self.Close()
        return super().Message(msg, result)

class ObjectManagerCommander(c4d.plugins.CommandData):
    """Command Data class that holds the ExampleDialog instance."""
    def Execute(self, doc):
        global dlg
        """Called when the user executes a command via either CallCommand() or a click on the Command from the extension menu.
        Args:
            doc (c4d.documents.BaseDocument): The current active document.

        Returns:
            bool: True if the command success.
        """
        # Creates the dialog if its not already exists
        if dlg is None:
            dlg = ObjectManagerCommanderDialog()

        #마우스 위치 정하기
        state = c4d.BaseContainer()
        c4d.gui.GetInputState(c4d.BFM_INPUT_MOUSE, c4d.BFM_INPUT_MOUSELEFT, state)
        x = state.GetInt32(c4d.BFM_INPUT_X)-20
        y = state.GetInt32(c4d.BFM_INPUT_Y)+10
        #Opens the dialog 
        return dlg.Open(dlgtype=c4d.DLG_TYPE_ASYNC_POPUP_RESIZEABLE, pluginid=PLUGIN_ID,xpos=x,ypos=y, defaultw=300, defaulth=200)

    def RestoreLayout(self, sec_ref):
        """Used to restore an asynchronous dialog that has been placed in the users layout.

        Args:
            sec_ref (PyCObject): The data that needs to be passed to the dialog.

        Returns:
            bool: True if the restore success
        """
        # Creates the dialog if its not already exists
        global dlg
        
        if dlg == None:
            dlg = ObjectManagerCommanderDialog()

        # Restores the layout
        return dlg.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

# main
if __name__ == "__main__":
    # Registers the plugin
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                      str="Object Manager Commander...",
                                      info=0,
                                      help="Commander For Objects",
                                      dat=ObjectManagerCommander(),
                                      icon=None)
