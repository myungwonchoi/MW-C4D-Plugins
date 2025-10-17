# https://developers.maxon.net/forum/topic/15955/treeview-rows-selected?_=1760714103110

import c4d
import random
from c4d import gui
# Welcome to the world of Python

NAME = 0
LINKTO = 1
LINK = 2
TYPE = 3


class TreeView_Item(object):

    def __init__(self,):

        self.type = 'psr'   
        self.selected = False  


        self.obj_name = str(random.randint(1,100)) 

        self.linkto_name = "" 



    @property
    def IsSelected(self):
        return self.selected

    def Select(self):
        self.selected = True

    def Deselect(self):
        self.selected = False

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.obj_name


class TreeView(c4d.gui.TreeViewFunctions):

    def __init__(self,items_list=None):

        self.items_list = items_list if items_list else []
    def GetLineHeight(self,root, userdata, obj, col, area):

        return area.DrawGetFontHeight()

    def IsResizeColAllowed(self, root, userdata, lColID):
        return True

    def IsTristate(self, root, userdata):
        return False

    def GetColumnWidth(self, root, userdata, obj, col, area):
        """Measures the width of cells.

        Although this function is called #GetColumnWidth and has a #col, it is
        not only executed by column but by cell. So, when there is a column
        with items requiring the width 5, 10, and 15, then there is no need
        for evaluating all items. Each item can return its ideal width and
        Cinema 4D will then pick the largest value.

        Args:
            root (any): The root node of the tree view.
            userdata (any): The user data of the tree view.
            obj (any): The item for the current cell.
            col (int): The index of the column #obj is contained in.
            area (GeUserArea): An already initialized GeUserArea to measure
             the width of strings.

        Returns:
            TYPE: Description
        """
        # The default width of a column is 80 units.
        width = 80
        # Replace the width with the text width. area is a prepopulated
        # user area which has already setup all the font stuff, we can
        # measure right away.

        if col == NAME:
            return area.DrawGetTextWidth(obj.obj_name) + 5
        if col == LINKTO:
            return area.DrawGetTextWidth("-->") + 5
        if col == LINK:
            return area.DrawGetTextWidth(obj.linkto_name) + 5

        if col == TYPE:
            return area.DrawGetTextWidth(obj.type) + 5

        return width


    def GetFirst(self, root, userdata):
        """
        Return the first element in the hierarchy, or None if there is no element.
        """
        rValue = None if not len(self.items_list) else self.items_list[0]
        return rValue


    def GetNext(self, root, userdata, obj):
        """
        Returns the next Object to display after arg:'obj'
        """
        rValue = None
        currentObjIndex = self.items_list.index(obj)
        nextIndex = currentObjIndex + 1
        if nextIndex < len(self.items_list):
            rValue = self.items_list[nextIndex]

        return rValue

    def GetPred(self, root, userdata, obj):
        """
        Returns the previous Object to display before arg:'obj'
        """
        rValue = None
        currentObjIndex = self.items_list.index(obj)
        predIndex = currentObjIndex - 1
        if 0 <= predIndex < len(self.items_list):
            rValue = self.items_list[predIndex]

        return rValue

    def GetId(self, root, userdata, obj):
        """
        Return a unique ID for the element in the TreeView.
        """
        return hash(obj)


    def Select(self, root, userdata, obj, mode):

        print(obj.obj_name)
        if mode == c4d.SELECTION_NEW:
            for item in self.items_list:
                item.Deselect()
            obj.Select()
        elif mode == c4d.SELECTION_ADD:
            obj.Select()
        elif mode == c4d.SELECTION_SUB:
            obj.Deselect()

    def IsSelected(self, root, userdata, obj):

        return obj.IsSelected

    def DeletePressed(self, root, userdata):
        "Called when a delete event is received."
        for item in reversed(self.items_list):
            if item.IsSelected:
                self.items_list.remove(item)

    def GetName(self, root, userdata, obj):
        """
        Returns the name to display for arg:'obj', only called for column of type LV_TREE
        """
        return str(obj)  # Or obj.texturePath

    def DrawCell(self, root, userdata, obj, col, drawinfo, bgColor):
        """
        Draw into a Cell, only called for column of type LV_USER
        """
        if col == NAME:
            text = obj.obj_name

        elif col == LINKTO:
            text = '-->'
        elif col == LINK:
            text = obj.linkto_name
        elif col == TYPE:
            text = obj.type
        else:
            text = ''

        canvas = drawinfo["frame"]

        xpos = drawinfo["xpos"]
        ypos = drawinfo["ypos"]

        txtColorDict = canvas.GetColorRGB(c4d.COLOR_TEXT_SELECTED) if obj.IsSelected else canvas.GetColorRGB(
            c4d.COLOR_TEXT)
        txtColorVector = c4d.Vector(txtColorDict["r"] / 255.0, txtColorDict["g"] / 255.0, txtColorDict["b"] / 255.0)
        canvas.DrawSetTextCol(txtColorVector, bgColor)
        canvas.DrawText(text, xpos, ypos)



    def DoubleClick(self, root, userdata, obj, col, mouseinfo):

        return True


class test_dialog(gui.GeDialog):
    def __init__(self):
        self._treegui = None
        self.treeview = TreeView()
    def CreateLayout(self):
        # Other than edit fields, buttons do not have a builtin bubble help.
        customgui = c4d.BaseContainer()
        customgui.SetBool(c4d.TREEVIEW_BORDER, c4d.BORDER_THIN_IN)
        customgui.SetBool(c4d.TREEVIEW_HAS_HEADER, True)  # True if the tree view may have a header line.
        customgui.SetBool(c4d.TREEVIEW_HIDE_LINES, False)  # True if no lines should be drawn.
        customgui.SetBool(c4d.TREEVIEW_MOVE_COLUMN, False)  # True if the user can move the columns.
        customgui.SetBool(c4d.TREEVIEW_RESIZE_HEADER, True)  # True if the column width can be changed by the user.
        customgui.SetBool(c4d.TREEVIEW_FIXED_LAYOUT, True)  # True if all lines have the same height.
        customgui.SetBool(c4d.TREEVIEW_ALTERNATE_BG, True)  # Alternate background per line.
        customgui.SetBool(c4d.TREEVIEW_CURSORKEYS, True)  # True if cursor keys should be processed.
        customgui.SetBool(c4d.TREEVIEW_NOENTERRENAME, True)  # Suppresses the rename popup when the user presses enter.
        customgui.SetBool(c4d.TREEVIEW_NO_MULTISELECT, False)  

        self._treegui = self.AddCustomGui(1000, c4d.CUSTOMGUI_TREEVIEW, "", c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 300,
                                          300, customgui)
        if not self._treegui:
            print("[ERROR]: Could not create TreeView")
            return False

        self.AddButton(1001, c4d.BFH_CENTER, name="Add")

        return True


    def InitValues(self) -> bool:
        layout = c4d.BaseContainer()
        layout.SetInt32(NAME, c4d.LV_USER)
        layout.SetInt32(LINKTO, c4d.LV_USER)
        layout.SetInt32(LINK, c4d.LV_USER)
        layout.SetInt32(TYPE, c4d.LV_USER)

        self.layout = layout
        self._treegui.SetLayout(4, layout)

        # Set the header titles.
        self._treegui.SetHeaderText(NAME, "Name")
        self._treegui.SetHeaderText(LINKTO, "")
        self._treegui.SetHeaderText(LINK, "Link")
        self._treegui.SetHeaderText(TYPE, "Type")


        # Set TreeViewFunctions instance used by our CUSTOMGUI_TREEVIEW
        self._treegui.SetRoot(self._treegui, self.treeview, None)
        self._treegui.Refresh()
        return True

    def Command(self, id, msg):
        if id == 1001:
            item = TreeView_Item()
            self.treeview.items_list.append(item)
            self._treegui.Refresh()
            return True
        return True


# Execute main()
if __name__=='__main__':


    dlg = test_dialog()

    dlg.Open(c4d.DLG_TYPE_ASYNC,0 -1,-1,400,400)
