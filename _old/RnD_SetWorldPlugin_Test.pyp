import c4d
import os
from c4d import plugins, gui, bitmaps, documents, storage
from c4d.plugins import SetWorldPluginData, GetWorldPluginData

PLUGIN_ID = 1038198
PLUGIN_NAME = "World Container Example"
PLUGIN_INFO_HELP = "AP Ashton needs help with python code."

class PluginExample_Dialog(c4d.gui.GeDialog):
    Group_ID = 5000
    UI_0 = 5001
    UI_1 = 5002
    UI_2 = 5003
    UI_3 = 5004
    UI_4 = 5005   
    UI_LvlList = 5006
    UI_BTN_Set = 5007
    UI_ObjectLinkBox = 5008
    linkbox = None

    def CreateLayout(self):
        self.SetTitle(PLUGIN_NAME)

        self.GroupBegin(self.Group_ID, c4d.BFH_SCALEFIT, 3, 0, "")
        self.rootLinkBaseContainer = c4d.BaseContainer()
        self.linkBox = self.AddCustomGui(self.UI_ObjectLinkBox, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_SCALEFIT, 200, 10, self.rootLinkBaseContainer)
        IDList = self.UI_LvlList
        self.AddComboBox(IDList, c4d.BFH_MASK, 40, 0, False)
        self.AddChild(IDList, self.UI_0, '0')
        self.AddChild(IDList, self.UI_1, '1')
        self.AddChild(IDList, self.UI_2, '2')
        self.AddChild(IDList, self.UI_3, '3')
        self.AddChild(IDList, self.UI_4, '4')
        self.AddButton(self.UI_BTN_Set, c4d.BFH_MASK, initw=10, name="Set")
        self.GroupEnd()
        return True

    def __init__(self):
        super(PluginExample_Dialog, self).__init__()

    @classmethod   
    def Load_UI_Settings(cls, instance):
        bc = c4d.plugins.GetWorldPluginData(PLUGIN_ID)
        bc = bc or c4d.BaseContainer()
        if instance:              
            instance.SetLong(cls.UI_LvlList, bc.GetLong(cls.UI_LvlList, cls.UI_LvlList))
        return bc 

    def AutoSave_UI_Settings(self, save=True):   
        data = c4d.BaseContainer()
        data[self.UI_LvlList] = self.GetLong(self.UI_LvlList)
        data[self.UI_ObjectLinkBox] = self.linkBox.GetLink()

        if save:
            c4d.plugins.SetWorldPluginData(PLUGIN_ID, data)
            
        return data

    def DestroyWindow(self):
        self.AutoSave_UI_Settings()

    def InitValues(self):
        PluginExample_Dialog.Load_UI_Settings(self)
        bc = c4d.plugins.GetWorldPluginData(PLUGIN_ID)             
        if bc[5008] is not None:
            self.linkBox.SetLink(bc[5008])
        return True

    def Command(self, id, msg):   
        if (id == self.UI_BTN_Set):
            doc = c4d.documents.GetActiveDocument()
            obj = self.linkBox.GetLink().GetName()
            LevelListID = self.UI_LvlList   

            if self.GetLong(LevelListID) == self.UI_0:
                Link_Object = doc.SearchObject(obj)
                Set_lvl = 0.0
                Link_Object[c4d.ID_BASEOBJECT_REL_POSITION, c4d.VECTOR_Y] = Set_lvl
            c4d.EventAdd()                                   
            return True

        return True

    def Message(self, msg, result):
        doc = documents.GetActiveDocument()

        if msg.GetId() == c4d.MSG_DESCRIPTION_CHECKDRAGANDDROP:
            if self.linkBox.GetLink() != None:
                print(self.linkBox.GetLink().GetName())
      
        return gui.GeDialog.Message(self, msg, result)

class PluginExample_Data(c4d.plugins.CommandData):

    dialog = None

    def Init(self, op):
        return True

    def Message(self, type, data):
        return True

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = PluginExample_Dialog()   
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=400, defaulth=100)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = PluginExample_Dialog()       
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

    def ExecuteOptionID(self, doc, plugid, subid):
        return True

if __name__ == '__main__':   
    result = plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                           str=PLUGIN_NAME,
                                           info=0,
                                           icon=None,
                                           help=PLUGIN_INFO_HELP,
                                           dat=PluginExample_Data())
