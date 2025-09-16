import c4d
from difflib import SequenceMatcher
from datetime import datetime
import os

PLUGIN_ID = 1062602

today = datetime.today()
d_day = datetime(2199, 7, 27)

class MigrateTagsDialog(c4d.gui.GeDialog):
    _doc = c4d.documents.GetActiveDocument()
    TAGTYPE_LIST = list()
    ID_LINKBOX_A = 1000; ID_LINKBOX_B = 1001

    ID_COPYTAG_MATERIAL = 1100; ID_COPYTAG_UVW = 1101; ID_COPYTAG_SELECTION = 1102; ID_COPYTAG_PHONG = 1103; ID_COPYTAG_WEIGHT = 1104; ID_COPYTAG_VERTEXMAP = 1105
    ID_COPYTAG_OCTOBJECT = 1106; ID_COPYTAG_RSOBJECT = 1107; ID_COPYTAG_ALEMBIC = 1108

    ID_EXCLUDETEXT_SOURCE = 1200; ID_EXCLUDETEXT_TARGET = 1201
    ID_BUTTON_OBJECTNAME_SAME = 1300; ID_BUTTON_OBJECTNAME_SIMILAR = 1301; ID_BUTTON_OBJECT_ORDER = 1302

    ID_MULTILINE_LOG = 1400

    ID_BUTTON_SHOW_DESCRIPTION = 1500
    LOG_DESCRIPTION = "--- 사용 설명 ---\n\
Source Parent Object에 텍스쳐링 작업이 완료된 부모 오브젝트를 넣고\n\
Target Parent Object에 태그들이 적용되어야할 부모 오브젝트를 넣으세요.\n\
첫 번째 버튼은 자식 오브젝트들 중 같은 이름을 가진 오브젝트로 태그가 복사됩니다.\n\
두 번째 버튼은 자식 오브젝트들 중 가장 비슷한 이름을 가진 오브젝트로 태그가 복사됩니다.\n\n\
Exclue Text 입력란은 소스, 타겟 오브젝트 이름을 검색하는 과정에서 제외할 단어를 입력하면 됩니다.\n\n\
버튼을 누른 직후 복사된 태그들은 자동으로 선택됩니다.\n복사된 태그들을 확인하려면 오브젝트 매니저 창에서 S키를 눌러서 확인하실 수 있습니다."
    LOG_MESSAGE = LOG_DESCRIPTION

    def InitValues(self):
        MigrateTagsDialog.Load_UI_Settings(self)
        bc = c4d.plugins.GetWorldPluginData(PLUGIN_ID)

        # Load the saved checkbox state from the WorldContainer
        for i in range(self.ID_COPYTAG_MATERIAL,self.ID_COPYTAG_ALEMBIC+1):
            if bc[i] is not None:
                self.SetBool(i, bc[i])
        if bc[self.ID_EXCLUDETEXT_SOURCE] is not None:
            self.SetString(self.ID_EXCLUDETEXT_SOURCE, bc[self.ID_EXCLUDETEXT_SOURCE])
        if bc[self.ID_EXCLUDETEXT_TARGET] is not None:
            self.SetString(self.ID_EXCLUDETEXT_TARGET, bc[self.ID_EXCLUDETEXT_TARGET])
        return True
    
    def AutoSave_UI_Settings(self, save=True) :   #For saving the plugin's GUI Settings when the dioalog is closed  
        #Create a new container and store the gizmo data in it  
        data = c4d.BaseContainer()
        for i in range(self.ID_COPYTAG_MATERIAL,self.ID_COPYTAG_ALEMBIC+1):
            data[i] = self.GetBool(i)
        data[self.ID_EXCLUDETEXT_SOURCE] = self.GetString(self.ID_EXCLUDETEXT_SOURCE)
        data[self.ID_EXCLUDETEXT_TARGET] = self.GetString(self.ID_EXCLUDETEXT_TARGET)
        #Save the container in the WorldPluginData container
        if save:
            c4d.plugins.SetWorldPluginData(PLUGIN_ID, data)
        return data
    
    @classmethod
    def Load_UI_Settings(cls, instance): # cls =class ,  instance = self
        bc = c4d.plugins.GetWorldPluginData(PLUGIN_ID)  
        bc = bc or c4d.BaseContainer() 
        if instance:
            for i in [cls.ID_COPYTAG_MATERIAL, cls.ID_COPYTAG_UVW, cls.ID_COPYTAG_SELECTION, cls.ID_COPYTAG_PHONG, cls.ID_COPYTAG_WEIGHT, cls.ID_COPYTAG_VERTEXMAP]:
                instance.SetBool(i, bc.GetBool(i,False))
            instance.SetString(cls.ID_EXCLUDETEXT_SOURCE, bc.GetString(cls.ID_EXCLUDETEXT_SOURCE))
            instance.SetString(cls.ID_EXCLUDETEXT_TARGET, bc.GetString(cls.ID_EXCLUDETEXT_TARGET))
        return bc
    
    def DestroyWindow(self):
        self.AutoSave_UI_Settings()

    def CreateLayout(self):
        self.SetTitle("MW Migrate Tags")

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1)
        self.GroupBorderSpace(5, 5, 5, 5)

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=2)
        self.AddStaticText(0, c4d.BFH_LEFT,name='Source Parent Object')
        op_linkbox_a = self.AddCustomGui( self.ID_LINKBOX_A, pluginid = c4d.CUSTOMGUI_LINKBOX, name = "Source Parent Object", flags = c4d.BFH_SCALEFIT, minw = 600, minh = 15 )
        self.AddStaticText(0, c4d.BFH_LEFT,name='Target Parent Object')
        op_linkbox_b = self.AddCustomGui (self.ID_LINKBOX_B, pluginid = c4d.CUSTOMGUI_LINKBOX, name = "Target Parent Object", flags = c4d.BFH_SCALEFIT, minw = 600, minh = 15 )
        
        self._doc = c4d.documents.GetActiveDocument()
        if len(self._doc.GetActiveObjects(2)) == 2:
            op_linkbox_a.SetLink(self._doc.GetActiveObjects(2)[0])
            op_linkbox_b.SetLink(self._doc.GetActiveObjects(2)[1])
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=1); self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT); self.GroupEnd()

        self.AddStaticText(0, c4d.BFH_LEFT,name='Migrate Tag Types',borderstyle = c4d.BORDER_WITH_TITLE_BOLD)

        
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=6)
        self.AddCheckbox(self.ID_COPYTAG_MATERIAL, c4d.BFH_FIT,120,10,name = 'Material')
        self.AddCheckbox(self.ID_COPYTAG_UVW, c4d.BFH_FIT,120,10,name = 'UVW')
        self.AddCheckbox(self.ID_COPYTAG_SELECTION, c4d.BFH_FIT,120,10,name = 'Selection')
        self.AddCheckbox(self.ID_COPYTAG_PHONG, c4d.BFH_FIT,120,10,name = 'Phong')
        self.AddCheckbox(self.ID_COPYTAG_WEIGHT, c4d.BFH_FIT,120,10,name = 'Weight')
        self.AddCheckbox(self.ID_COPYTAG_VERTEXMAP, c4d.BFH_FIT,120,10,name = 'VertexMap')
        self.AddCheckbox(self.ID_COPYTAG_OCTOBJECT, c4d.BFH_FIT,160,10,name = 'Octane Object')
        self.AddCheckbox(self.ID_COPYTAG_RSOBJECT, c4d.BFH_FIT,160,10,name = 'Redshift Object')
        self.AddCheckbox(self.ID_COPYTAG_ALEMBIC, c4d.BFH_FIT,160,10,name = 'Alembic Tags')
        
        self.SetBool(self.ID_COPYTAG_MATERIAL, True)
        self.SetBool(self.ID_COPYTAG_UVW, False)
        self.SetBool(self.ID_COPYTAG_SELECTION, True)
        self.SetBool(self.ID_COPYTAG_PHONG, True)
        self.SetBool(self.ID_COPYTAG_WEIGHT, True)
        self.SetBool(self.ID_COPYTAG_VERTEXMAP, False)
        self.SetBool(self.ID_COPYTAG_OCTOBJECT, True)
        self.SetBool(self.ID_COPYTAG_RSOBJECT, True)
        self.SetBool(self.ID_COPYTAG_ALEMBIC, False)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=1); self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT); self.GroupEnd()

        self.AddStaticText(0, c4d.BFH_LEFT,name='Exclude Text',borderstyle = c4d.BORDER_WITH_TITLE_BOLD)

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=2)
        self.AddStaticText(0, c4d.BFH_LEFT,name='from Source Object')
        self.AddEditText(self.ID_EXCLUDETEXT_SOURCE, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 200, 1, editflags = c4d.EDITTEXT_ENABLECLEARBUTTON | c4d.EDITTEXT_HELPTEXT)
        self.AddStaticText(0, c4d.BFH_LEFT,name='from Target Object')
        self.AddEditText(self.ID_EXCLUDETEXT_TARGET, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 200, 1, editflags = c4d.EDITTEXT_ENABLECLEARBUTTON | c4d.EDITTEXT_HELPTEXT)
        self.SetString(self.ID_EXCLUDETEXT_SOURCE, '', c4d.BORDER_NONE, flags = c4d.EDITTEXT_HELPTEXT)
        self.SetString(self.ID_EXCLUDETEXT_TARGET, '', c4d.BORDER_NONE, flags = c4d.EDITTEXT_HELPTEXT)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=1)
        self.AddButton(self.ID_BUTTON_OBJECTNAME_SAME, c4d.BFH_SCALEFIT, name='Migrate Tags with Same Object Name')
        self.AddButton(self.ID_BUTTON_OBJECTNAME_SIMILAR, c4d.BFH_SCALEFIT, name='Migrate Tags with Similar Object Name')
        # self.AddButton(self.ID_BUTTON_OBJECT_ORDER, c4d.BFH_SCALEFIT, name='Migrate Tags With Object Hierarchy Order')
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, cols=1); self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT); self.GroupEnd()
        self.AddMultiLineEditText(self.ID_MULTILINE_LOG, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, inith = 50, style=c4d.DR_MULTILINE_READONLY)
        self.SetString(self.ID_MULTILINE_LOG, self.LOG_MESSAGE)
        self.AddButton(self.ID_BUTTON_SHOW_DESCRIPTION, c4d.BFH_SCALEFIT, name='Show Description')

        self.GroupEnd()

    def GetChildrenObject(self, child):
        children=[]
        children.append(child)
        if child.GetDown() != None:
            for kid in child.GetChildren():
                children.extend(self.GetChildrenObject(kid))
        return children
    
    def transfer_tags(self, op_a, op_b):
        op_a_tags = op_a.GetTags()
        op_b_tags = op_b.GetTags()
        
        #Remove Checked Tag Types
        for itag in op_b_tags:
            for itagtype in self.TAGTYPE_LIST:
                if itag.IsInstanceOf(itagtype):
                    self._doc.AddUndo(c4d.UNDOTYPE_DELETE, itag)
                    itag.Remove()
                    break

        new_tags = []
        for itag in op_a_tags:
            for itagtype in self.TAGTYPE_LIST:
                if itag.IsInstanceOf(itagtype):
                    new_tag = itag.GetClone()
                    new_tags.append(new_tag)

        # 리스트에 저장된 태그를 역순으로 삽입
        for new_tag in reversed(new_tags):
            op_b.InsertTag(new_tag)
            self._doc.AddUndo(c4d.UNDOTYPE_NEW, new_tag)
            self._doc.AddUndo(c4d.UNDOTYPE_BITS, new_tag)  # 언도 추가
            new_tag.SetBit(c4d.BIT_ACTIVE)
        return

    def Command(self, cid, bc):
        # if today > d_day:
        #     # print('MW Migrate Tags Demo Period is over.')
        #     self.LOG_MESSAGE = 'MW Migrate Tags Demo Period is over.'
        #     self.SetString(self.ID_MULTILINE_LOG, self.LOG_MESSAGE)
        #     return

        if cid in [self.ID_BUTTON_OBJECT_ORDER, self.ID_BUTTON_OBJECTNAME_SAME, self.ID_BUTTON_OBJECTNAME_SIMILAR]:
            self._doc = c4d.documents.GetActiveDocument()
            op_linkbox_a = self.FindCustomGui(self.ID_LINKBOX_A, pluginid=c4d.CUSTOMGUI_LINKBOX)
            op_linkbox_b = self.FindCustomGui(self.ID_LINKBOX_B, pluginid=c4d.CUSTOMGUI_LINKBOX)
            op_a = op_linkbox_a.GetLink(self._doc)
            op_b = op_linkbox_b.GetLink(self._doc)
            op_a_child = self.GetChildrenObject(op_a)
            op_b_child = self.GetChildrenObject(op_b)
            if not op_a or not op_b:
                self.LOG_MESSAGE = 'Select two parent object upper.'
                return

            self.TAGTYPE_LIST = list()
            if self.GetBool(self.ID_COPYTAG_MATERIAL): self.TAGTYPE_LIST.append(c4d.Ttexture)
            if self.GetBool(self.ID_COPYTAG_UVW): self.TAGTYPE_LIST.append(c4d.Tuvw)
            if self.GetBool(self.ID_COPYTAG_SELECTION): self.TAGTYPE_LIST.append(c4d.Tpolygonselection)
            if self.GetBool(self.ID_COPYTAG_PHONG): self.TAGTYPE_LIST.append(c4d.Tphong)
            if self.GetBool(self.ID_COPYTAG_WEIGHT): self.TAGTYPE_LIST.append(c4d.Tweights)
            if self.GetBool(self.ID_COPYTAG_VERTEXMAP): self.TAGTYPE_LIST.append(c4d.Tvertexmap)
            if self.GetBool(self.ID_COPYTAG_OCTOBJECT): self.TAGTYPE_LIST.append(1029603)
            if self.GetBool(self.ID_COPYTAG_RSOBJECT): self.TAGTYPE_LIST.append(1036222)
            if self.GetBool(self.ID_COPYTAG_ALEMBIC): self.TAGTYPE_LIST.append(1036222)

            self._doc.StartUndo()
            c4d.CallCommand(12113) #Deselect All Objects
            self.LOG_MESSAGE = ''
            if cid == self.ID_BUTTON_OBJECTNAME_SAME: # Same Name Button
                for iop_b in op_b_child:
                    iop_b_excluded = iop_b.GetName().replace(self.GetString(self.ID_EXCLUDETEXT_TARGET),'')
                    flag_migrate = False
                    for iop_a in op_a_child:
                        if iop_a.GetType() != iop_b.GetType() and iop_a.GetType() != 1028083 and iop_b.GetType() != 1028083:
                            continue # 소스 오브젝트와 타겟 오브젝트의 타입이 다르면 다음 오브젝트로.
                        iop_a_excluded = iop_a.GetName().replace(self.GetString(self.ID_EXCLUDETEXT_SOURCE),'')
                        if iop_a_excluded == iop_b_excluded:
                            self.transfer_tags(iop_a, iop_b)
                            self.LOG_MESSAGE += f"(T) {iop_b.GetName()} <- (S) {iop_a.GetName()}\n"
                            flag_migrate = True
                            break
                    if flag_migrate == False: self.LOG_MESSAGE += f"(T) {iop_b.GetName()} Can't Find Any Source Object!!!\n"
            elif cid == self.ID_BUTTON_OBJECTNAME_SIMILAR: # Similar Name Button
                for iop_b in op_b_child:
                    similarity = 0
                    iop_a_similiar = None
                    iop_b_excluded = iop_b.GetName().replace(self.GetString(self.ID_EXCLUDETEXT_TARGET),'')

                    for iop_a in op_a_child:
                        print('iop_a Name =', iop_a.GetName())
                        print(' =', iop_a.GetType())
                        print(' =', iop_b.GetType())
                        if iop_a.GetType() != iop_b.GetType() and iop_a.GetType() != 1028083 and iop_b.GetType() != 1028083:
                            continue # 소스 오브젝트와 타겟 오브젝트의 타입이 다르면 (+ 알렘빅 오브젝트가 아니면) 다음 오브젝트로.
                        iop_a_excluded = iop_a.GetName().replace(self.GetString(self.ID_EXCLUDETEXT_SOURCE),'')

                        similarity_new = SequenceMatcher(None, iop_a_excluded, iop_b_excluded).ratio()
                        if similarity_new > similarity:
                            similarity = similarity_new
                            iop_a_similiar = iop_a
                            if similarity >= 1: break

                    if iop_a_similiar is None:
                        self.LOG_MESSAGE += f"(T) {iop_b.GetName()} Can't Find Any Source Object!!!\n"
                        continue
                    self.transfer_tags(iop_a_similiar, iop_b)

                    similarity_percentage = round(similarity * 100, 2)
                    if similarity_percentage >= 100: similarity_percentage = 100
                    self.LOG_MESSAGE += f"(T) {iop_b.GetName()} <- (S) {iop_a_similiar.GetName()} | Similarity : {similarity_percentage}%\n"
            self._doc.EndUndo()
            c4d.EventAdd()

        if cid == self.ID_BUTTON_SHOW_DESCRIPTION:
            self.LOG_MESSAGE = self.LOG_DESCRIPTION
        self.SetString(self.ID_MULTILINE_LOG, self.LOG_MESSAGE)

class MigrateTagsDialogCommand(c4d.plugins.CommandData):
    """Command Data class that holds the ExampleDialog instance."""
    dialog = None

    def Init(self, op):
        return True
    
    def ExecuteOptionID(self, doc, plugid, subid):
        return True
    def Execute(self, doc):
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MigrateTagsDialog()
        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=1, defaulth=800)

    def RestoreLayout(self, sec_ref):
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MigrateTagsDialog()
        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

if __name__ == "__main__":
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "MW_Migrate_Tags.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")
    
    # Registers the plugin
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                      str="MW Migrate Tags",
                                      info=0,
                                      help="Migrate Tags A Object to B Object",
                                      dat=MigrateTagsDialogCommand(),
                                      icon=bmp)
