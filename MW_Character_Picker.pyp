import c4d
import os
import json
import copy
import webbrowser
import c4d.storage
from c4d import gui, plugins, bitmaps

# Unique plugin ID
PLUGIN_ID = 1064459

PATH_ID = 1064519
SIZE_BUTTON_X = 20
SIZE_BUTTON_Y = 20
SIZE_BUTTON_MIN = 5
SIZE_BUTTON_MAX = 300
SIZE_BUTTON_STEP = 1
ZOOM_INTENSITY = 1 / 400

# GUI
COLOR_BACKGROUND = c4d.Vector(0.1, 0.1, 0.1)
COLOR_DEFAULT = c4d.Vector(0.3, 0.3, 0.3)
COLOR_SELECT = c4d.Vector(190 / 255, 112 / 255, 40 / 255)
COLOR_DRAG = c4d.Vector(0.9, 0.9, 0.9)
COLOR_TEXT = c4d.Vector(0.9, 0.9, 0.9)

# IDs used in the Main GeDialog
ID_MAINGROUP = 100000  # Main group that holds the SubDialogs
ID_TABGROUP = 110000  # TabGroup ID

ID_SUBDIALOG_GROUP = 120000  # Base ID for Group of SubDialog
ID_SUBDIALOG = 120001  # Base ID for each SubDialog
ID_FILTER_GROUP = 121000  # SubDialog Namespace Group
ID_PARENTOBJ_ENABLE = 122000  # SubDialog Parent Object Enable
ID_PARENTOBJ = 122100  # SubDialog Parent Object
ID_NAMESPACE_ENABLE = 123000  # SubDialog Namespace Enable
ID_NAMESPACE = 123100  # SubDialog Namespace
ID_NAMESPACE_PICK = 123200  # SubDialog Namespace Pick Button

ID_USERAREA_GROUP = 130000
ID_USERAREA = 130010  # SubDialog ID

# Button Properties IDs
ID_BUTTONGROUP = 140000
ID_COLOR = 140010
ID_SIZE_X = 140020
ID_SIZE_Y_ENABLE = 140021
ID_SIZE_Y = 140022
ID_OBJNAME = 140030
ID_TEXT = 140040

class AboutDialog(gui.GeDialog):
    def CreateLayout(self):
        self.SetTitle("MW Character Picker")

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 1, "", 0)
        self.GroupBorderSpace(5, 5, 5, 5)
        self.AddStaticText(0, c4d.BFH_LEFT,name='MW Character Picker',borderstyle = c4d.BORDER_WITH_TITLE_BOLD)
        self.AddMultiLineEditText(1000, c4d.BFH_SCALEFIT |
         c4d.BFV_SCALEFIT, style=c4d.DR_MULTILINE_READONLY)
        self.SetString(1000, 
                    "Version : 1.0\n" + \
                    "Author : Choi Myung Won / @dding_one\n" + \
                    "Instagram : https://www.instagram.com/dding_one/\n" + \
                    "Instagram (Choice Plugins) : https://www.instagram.com/choice_plugins/\n" + \
                    "Gumroad : https://ddingone.gumroad.com/")
        self.GroupEnd()
        return True

# Mirror Buttons Dialog
class MirrorButtonsDialog(gui.GeDialog):
    ID_REPLACE = 1001
    ID_WITH = 1002
    ID_GUIDETEXT = 1003
    ID_OFFSET_X = 1004
    ID_OFFSET_Y = 1005
    ID_COPY_AXIS = 1006
    ID_COPY_XAXIS = 1007
    ID_COPY_YAXIS = 1008
    ID_COLOR = 1009
    ID_OK_BUTTON = 1010
    ID_CANCEL_BUTTON = 1011
    flag_OKORCANCLE = "Cancel"

    def __init__(self, user_area):
        self.user_area = user_area
        self._mirrored_buttons = self.user_area.duplicated_buttons
        self.flag_OKORCANCLE == "Cancel"

        self._mirrored_buttons_original = []
        for button in self._mirrored_buttons:
            self._mirrored_buttons_original.append({
            'objname': button['objname'][:],
            'x': button['x'],
            'y': button['y'],
            'size_x': button['size_x'],
            'size_y_enable': button['size_y_enable'],
            'size_y': button['size_y'],
            'color': c4d.Vector(button['color'].x, button['color'].y, button['color'].z),
            'text': button['text']
            })
        
        self.center_x = (min([ibutton['x'] for ibutton in self._mirrored_buttons]) \
                        + max([ibutton['x'] for ibutton in self._mirrored_buttons])) // 2
        self.center_y = (min([ibutton['y'] for ibutton in self._mirrored_buttons]) \
                        + max([ibutton['y'] for ibutton in self._mirrored_buttons])) // 2
        self.user_area.Redraw()

    def CreateLayout(self):
        self.SetTitle("MW Character Picker")

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 1, "", 0)
        self.GroupBorderSpace(5, 5, 5, 5)

        self.AddStaticText(0, c4d.BFH_LEFT, name="Mirror Buttons", borderstyle=c4d.BORDER_WITH_TITLE_BOLD)

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 2, 1, "", 0)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Axis", initw=80)
        bc = c4d.BaseContainer()
        bc.SetBool(c4d.QUICKTAB_SHOWSINGLE, True)
        bc.SetBool(c4d.QUICKTAB_NOMULTISELECT, True)
        self._quickTabRadio = self.AddCustomGui(self.ID_COPY_AXIS, c4d.CUSTOMGUI_QUICKTAB, '',
                                           c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 0, bc)
        self._quickTabRadio.AppendString(self.ID_COPY_XAXIS , "Copy X Axis", True)
        self._quickTabRadio.AppendString(self.ID_COPY_YAXIS , "Copy Y Axis", False)
        self.GroupEnd()
        
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 3, 1, "", 0)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Offset", initw= 80)
        self.AddEditNumberArrows(self.ID_OFFSET_X, c4d.BFH_LEFT, initw = 70)
        self.SetInt32(id= self.ID_OFFSET_X, value=0)

        self.AddEditNumberArrows(self.ID_OFFSET_Y, c4d.BFH_LEFT, initw = 70)
        self.SetInt32(id= self.ID_OFFSET_Y, value=0)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 2, 1, "", 0)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Replace", initw=80)
        self.AddEditText(self.ID_REPLACE, c4d.BFH_SCALEFIT)
        self.AddStaticText(0, c4d.BFH_LEFT, name="With")
        self.AddEditText(self.ID_WITH, c4d.BFH_SCALEFIT)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Color")

        self.AddColorField(self.ID_COLOR, c4d.BFH_LEFT)
        self.SetColorField(self.ID_COLOR, self._mirrored_buttons_original[0]['color'], 1.0, 1.0, 0)
        self.GroupEnd()

        # Multiline Edit Text Read Only, for information
        self.AddMultiLineEditText(self.ID_GUIDETEXT, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, style=c4d.DR_MULTILINE_READONLY, inith = 200)
        self.Enable(self.ID_GUIDETEXT, False)

        text_guide = ""
        for ibutton in self._mirrored_buttons_original:
            if self.GetString(self.ID_REPLACE) in ibutton['objname'][0]:
                text_replace = ibutton['objname'][0].replace(self.GetString(self.ID_REPLACE), self.GetString(self.ID_WITH))
            else:
                text_replace = ibutton['objname'][0]
            text_guide += ibutton['objname'][0] + " -> " + text_replace + '\n'
        self.SetString(self.ID_GUIDETEXT, text_guide)

        # OK and Cancel buttons
        self.GroupBegin(self.ID_OK_BUTTON, c4d.BFH_RIGHT | c4d.BFV_BOTTOM, 2, 1, "", 0)
        # self.GroupBorderSpace(5, 5, 5, 5)
        self.AddButton(self.ID_OK_BUTTON, c4d.BFH_SCALE, name="OK")
        self.AddButton(self.ID_CANCEL_BUTTON, c4d.BFH_SCALE, name="Cancel")
        self.GroupEnd()

        self.GroupEnd()

        self.ShowMirrorButtons()
        return True

    def DestroyWindow(self):
        if self.flag_OKORCANCLE == "Cancel":
            for ibuttons in self._mirrored_buttons:
                self.user_area.buttons.remove(ibuttons)
        return

    def ShowMirrorButtons(self):
        if self._quickTabRadio.IsSelected(self.ID_COPY_XAXIS):
            for i, ibutton in enumerate(self._mirrored_buttons):
                new_pos_x = self.center_x * 2 - self._mirrored_buttons_original[i]['x'] # symmetrical x
                new_pos_y = self._mirrored_buttons_original[i]['y'] # same y
                ibutton['x'] = new_pos_x + self.GetInt32(self.ID_OFFSET_X)
                ibutton['y'] = new_pos_y + self.GetInt32(self.ID_OFFSET_Y)
        elif self._quickTabRadio.IsSelected(self.ID_COPY_YAXIS):
            for i, ibutton in enumerate(self._mirrored_buttons):
                new_pos_x = self._mirrored_buttons_original[i]['x'] # same x
                new_pos_y = self.center_y * 2 - self._mirrored_buttons_original[i]['y'] # symmetrical y
                ibutton['x'] = new_pos_x + self.GetInt32(self.ID_OFFSET_X)
                ibutton['y'] = new_pos_y + self.GetInt32(self.ID_OFFSET_Y)
        self.user_area.Redraw()

    def Command(self, id, msg):
        if id == self.ID_OFFSET_X or id == self.ID_OFFSET_Y or self.ID_COPY_XAXIS or self.ID_COPY_YAXIS:
            self.ShowMirrorButtons()
        if id == self.ID_COLOR:
            color = self.GetColorField(self.ID_COLOR)['color']
            for ibutton in self._mirrored_buttons:
                ibutton['color'] = color
            self.user_area.Redraw()
        if id == self.ID_REPLACE or id == self.ID_WITH:
            text_guide = ""
            for i, ibutton in enumerate(self._mirrored_buttons_original):
                if self.GetString(self.ID_REPLACE) in ibutton['objname'][0]:
                    text_replace = ibutton['objname'][0].replace(
                        self.GetString(self.ID_REPLACE), self.GetString(self.ID_WITH))
                else:
                    text_replace = ibutton['objname'][0]
                
                iobjnames = []
                for iobjname in ibutton['objname']:
                    if self.GetString(self.ID_REPLACE) in iobjname:
                        changed_name = iobjname.replace(
                            self.GetString(self.ID_REPLACE), self.GetString(self.ID_WITH))
                        iobjnames.append(changed_name)
                    else:
                        iobjnames.append(iobjname)
                self._mirrored_buttons[i]['objname'] = iobjnames
                text_guide += ibutton['objname'][0] + " -> " + text_replace + '\n'
            self.SetString(self.ID_GUIDETEXT, text_guide)
        
        if id == self.ID_OK_BUTTON:
            self.flag_OKORCANCLE = "OK"
            self.Close()
        elif id == self.ID_CANCEL_BUTTON:
            self.flag_OKORCANCLE = "Cancel"
            for ibuttons in self._mirrored_buttons:
                self.user_area.buttons.remove(ibuttons)
            self.Close()
        return True



class PickerImageSettingsDialog(gui.GeDialog):
    ID_IMAGE_PATH = 1001
    ID_IMAGE_X = 1002
    ID_IMAGE_Y = 1003
    ID_IMAGE_SCALE = 1004
    ID_IMAGE_OPACITY = 1005
    ID_OK_BUTTON = 1006
    ID_CANCEL_BUTTON = 1007
    ID_IMAGE_OPEN = 1008

    def __init__(self, user_area):
        self.user_area = user_area

    def InitValues(self):
        self.old_path = self.user_area.pickerimage_path
        self.old_x = self.user_area.pickerimage_x
        self.old_y = self.user_area.pickerimage_y
        self.old_scale = self.user_area.pickerimage_scale
        self.old_opacity = self.user_area.pickerimage_opacity

        return True

    def CreateLayout(self):
        self.SetTitle("Picker Image Settings")

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 1, "", 0)
        self.GroupBorderSpace(5, 0, 5, 0)

        # Line break
        # self.GroupBegin(9999, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1); self.AddSeparatorH(0, flags=c4d.BFH_SCALEFIT); self.GroupEnd()

        # X, Y, Scale, Opacity    
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 3, 1, "", 0)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Path", initw= 80)
        self.AddEditText(self.ID_IMAGE_PATH, c4d.BFH_SCALEFIT, editflags=c4d.EDITTEXT_ENABLECLEARBUTTON)
        # 커스텀 버튼 설정
        bc = c4d.BaseContainer()
        bc[c4d.BITMAPBUTTON_BUTTON] = True
        bc[c4d.BITMAPBUTTON_BORDER] = False
        bc[c4d.BITMAPBUTTON_TOGGLE] = False
        bc[c4d.BITMAPBUTTON_DISABLE_FADING] = False
        bc[c4d.BITMAPBUTTON_ICONID1] = c4d.RESOURCEIMAGE_TIMELINE_FOLDER4 # 아이콘 ID 설정
        bc[c4d.BITMAPBUTTON_TOOLTIP] = 'Open Picker Image File...'

        # 커스텀 버튼 추가
        self.imageopenbutton = self.AddCustomGui(self.ID_IMAGE_OPEN,
                                              c4d.CUSTOMGUI_BITMAPBUTTON, "",
                                              c4d.BFH_RIGHT | c4d.BFV_CENTER, 25, 15, bc)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 3, 1, "", 0)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Offset", initw= 80)
        self.AddEditNumberArrows(self.ID_IMAGE_X, c4d.BFH_LEFT, initw = 70)
        self.AddEditNumberArrows(self.ID_IMAGE_Y, c4d.BFH_LEFT, initw = 70)
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 2, 1, "", 0)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Scale", initw = 80)
        self.AddEditSlider(self.ID_IMAGE_SCALE, c4d.BFH_SCALEFIT)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Opacity", initw = 80)
        self.AddEditSlider(self.ID_IMAGE_OPACITY, c4d.BFH_SCALEFIT)
        self.GroupEnd()

        # OK and Cancel buttons
        self.GroupBegin(self.ID_OK_BUTTON, c4d.BFH_RIGHT | c4d.BFV_BOTTOM, 2, 1, "", 0)
        self.GroupBorderSpace(5, 5, 5, 5)
        self.AddButton(self.ID_OK_BUTTON, c4d.BFH_SCALE, name="OK")
        self.AddButton(self.ID_CANCEL_BUTTON, c4d.BFH_SCALE, name="Cancel")
        self.GroupEnd()

        self.SetString(self.ID_IMAGE_PATH, self.user_area.pickerimage_path or "")
        self.SetInt32(self.ID_IMAGE_X, self.user_area.pickerimage_x)
        self.SetInt32(self.ID_IMAGE_Y, self.user_area.pickerimage_y)
        self.SetFloat(self.ID_IMAGE_SCALE, self.user_area.pickerimage_scale, min=0.1, max=10.0, step=0.1)
        self.SetFloat(self.ID_IMAGE_OPACITY, self.user_area.pickerimage_opacity,
                       min=0.0, max=1.0, step=0.01,
                       format=c4d.FORMAT_PERCENT,
                       min2=0.0, max2=1.0)
        return True

    def Command(self, id, msg):
        self.user_area.pickerimage_path = self.GetString(self.ID_IMAGE_PATH)
        self.user_area.pickerimage_x = self.GetInt32(self.ID_IMAGE_X)
        self.user_area.pickerimage_y = self.GetInt32(self.ID_IMAGE_Y)
        self.user_area.pickerimage_scale = self.GetFloat(self.ID_IMAGE_SCALE)

        if id == self.ID_IMAGE_OPEN:
            pickerimage_path = c4d.storage.LoadDialog(title="Load Image",
            force_suffix="png", type=c4d.FILESELECTTYPE_IMAGES)
            if pickerimage_path is None: return True
            else:
                self.SetString(self.ID_IMAGE_PATH, pickerimage_path)
                self.user_area.pickerimage_path = pickerimage_path
                self.user_area.SetPickerImage()
        if id == self.ID_IMAGE_OPACITY:
            self.user_area.pickerimage_opacity = self.GetFloat(self.ID_IMAGE_OPACITY)
            self.user_area.SetPickerImage()
        if id == self.ID_OK_BUTTON:
            self.user_area.SetPickerImage()
            self.Close()
        elif id == self.ID_CANCEL_BUTTON:
            self.user_area.pickerimage_path = self.old_path
            self.user_area.pickerimage_x = self.old_x
            self.user_area.pickerimage_y = self.old_y
            self.user_area.pickerimage_scale = self.old_scale
            self.user_area.pickerimage_opacity = self.old_opacity
            self.user_area.SetPickerImage()
            self.Close()
        self.user_area.Redraw()
        return True

    def Message(self, msg, result):
        return c4d.gui.GeDialog.Message(self, msg, result)


def ObjName_to_String(objname):
    if len(objname) < 2:
        return objname[0]
    else:
        name_text = ' && '.join(objname)
        return name_text

def String_to_ObjName(edit_text):
    if '&&' in edit_text:
        objname = [name.strip() for name in edit_text.split('&&')]
    else:
        objname = [edit_text.strip()]
    return objname


class MWCharacterPickerUserArea(gui.GeUserArea):

    ID_POPUP_ADDBUTTON = 1001
    ID_POPUP_ADDBUTTONS = 1002
    ID_POPUP_DELETEBUTTON = 1003
    ID_POPUP_HORIZONTAL_ALIGN = 1004
    ID_POPUP_VERTICAL_ALIGN = 1005
    ID_POPUP_HORIZONTAL_DISTRIBUTE = 1006
    ID_POPUP_VERTICAL_DISTRIBUTE = 1007
    ID_POPUP_MIRROR_BUTTONS = 1008
    ID_POPUP_SELECT_MIRROR_BUTTONS = 1009
    def __init__(self, dialog, subdialog):
        super().__init__()
        self.dialog = dialog
        self.subdialog = subdialog  # 부모 클래스 인스턴스를 저장
        self.prev_objs = []

        self.parentobjname_enable = False
        self.parentobjname = ""

        self.namespace_enable = False
        self.namespace = ""

        self.pickerimage_path = ""
        self.pickerimage = self.SetPickerImage()
        self.pickerimage_x = 0
        self.pickerimage_y = 0
        self.pickerimage_scale = 1.0
        self.pickerimage_opacity = 0.5

        self.buttons = []
        self.selected_buttons = []
        self.addmultiple_objs = []

        self.mouse_pos = {'x': 0, 'y': 0}
        self.clickedPos = None  # None if not dragging, tuple(X, Y) if dragged

        self.drag_button = None
        self.dragStartPos = None
        self.dragRelPos = {'x': 0, 'y': 0}

        self.pan_pos = {'x': 0, 'y': 0}
        self.zoom = 1.0

        self.flag_coreMessage = False
        self.flag_Mode = None
    def Init(self):
        return True
 
    def ChangeButtonObjectNameSpace(self):
        if self.namespace_enable == True:
            if self.namespace == "":
                for button in self.buttons:
                    button['objname'] = [name.split("::")[-1] for name in button['objname']]
            else:
                for button in self.buttons:
                    button['objname'] = [self.namespace + "::" + name.split("::")[-1] for name in button['objname']]
        elif self.namespace_enable == False:
            for button in self.buttons:
                button['objname'] = [name.split("::")[-1] for name in button['objname']]
        return True

    def FindObjectbyParentObjectAndNameSpace(self, objname):
        doc = c4d.documents.GetActiveDocument()

        if self.parentobjname_enable == True:
            parentobj = doc.SearchObject(self.parentobjname)
            if parentobj is not None:
                def find_recursive(parent, objname):
                    for childobj in parent.GetChildren():
                        if childobj.GetName() == objname:
                            return childobj
                        found = find_recursive(childobj, objname)
                        if found:
                            return found
                    return None
                if parentobj.GetName() == objname:
                    return parentobj
                return find_recursive(parentobj, objname)
            else:
                return None
        elif self.parentobjname_enable == False:
            return doc.SearchObject(objname)

    def DrawAxisLine(self):
        # self.DrawSetPen(COLOR_DEFAULT)
        self.DrawSetPen(c4d.Vector(0.2, 0.2, 0.2))
        
        x1, y1, x2, y2 = 0, 0, 5000, 5000
        x1, y1, x2, y2 = self.AdjustPanAndZoom(x1, y1, x2, y2)
        x1 -= 1; y1 -= 1; x2 -= 1; y2 -= 1

        self.DrawLine(-x2, y1, x2, y1)
        self.DrawLine(x1, -y2, x1, y2)

    def DrawMsg(self, x1, y1, x2, y2, msg_ref):
        self.OffScreenOn() # 더블 버퍼링 활성화
        self.DrawSetPen(COLOR_BACKGROUND)
        self.DrawRectangle(x1, y1, x2, y2) # 배경 그리기

        self.DrawPickerImage()

        self.DrawButton() # 버튼 그리기
        self.DrawSelectedButton() # 선택된 버튼 그리기
        self.DrawDraggingButton() # 드래그 중인 버튼 그리기
        self.DrawDraggedRect() # 드래그 구역 그리기

        self.DrawAxisLine()  
        # AddMultipleButtons 모드일 때, 추가할 버튼들 보여주기
        if self.flag_Mode == "AddMultipleButtons": self.ShowMultipleButtons()

    def DrawDraggedRect(self):
        """DrawMsg에서 호출됩니다.
        드래그된 사각형을 그립니다
        """
        if self.drag_button or self.clickedPos is None:
            return
        
        startX, startY = self.dragStartPos['x'], self.dragStartPos['y']
        x, y = self.clickedPos['x'], self.clickedPos['y']

        self.DrawBorder(c4d.BORDER_ACTIVE_1, startX, startY, x, y)

    def AddButton(self, obj, x, y):
        if obj == []:
            gui.MessageDialog("To create a button, select objects.")
            return False
        x = (x / self.zoom) - (self.pan_pos['x'])
        y = (y / self.zoom) - (self.pan_pos['y'])
        objname = []
        for iobj in obj:
            objname.append(iobj.GetName())

        button_color = c4d.Vector(COLOR_DEFAULT)
        if (len(obj) < 2 and 
            (obj[0][c4d.ID_BASEOBJECT_USECOLOR] == 2 or
             obj[0][c4d.ID_BASEOBJECT_USECOLOR] == 1)): # Custom Display Color
            button_color = obj[0][c4d.ID_BASEOBJECT_COLOR]
        else:
            if all((obj[i][c4d.ID_BASEOBJECT_USECOLOR] == 2 or
                    obj[i][c4d.ID_BASEOBJECT_USECOLOR] == 1) and
                    obj[i][c4d.ID_BASEOBJECT_COLOR] == obj[0][c4d.ID_BASEOBJECT_COLOR] for i in range(len(obj))):
                button_color = obj[0][c4d.ID_BASEOBJECT_COLOR]

        # 버튼 추가

        self.buttons.append({
            'objname': objname,
            'x': x,
            'y': y,
            'size_x': SIZE_BUTTON_X,
            'size_y_enable' : False,
            'size_y': SIZE_BUTTON_Y,
            'color': button_color,
            'text' : ''
        })

        self.UpdateTabSavedState() # 탭 저장 상태 업데이트
        self.Redraw()  # 다시 그리기 호출

    def SetPickerImage(self):
        if self.pickerimage_path is None: return
        if not os.path.exists(self.pickerimage_path): return
        image = c4d.bitmaps.BaseBitmap()
        image.InitWith(self.pickerimage_path) # 이미지 로드
        if image is None: return
        alphaBit = image.GetChannelNum(0) # 알파 채널 얻기
        if alphaBit == None:
            image.AddChannel(True, True) # 알파 채널 추가
            alphaBit = image.GetChannelNum(0) # 알파 채널 얻기
            for x in range(0, image.GetBw()):
                for y in range(0, image.GetBh()):
                    alpha = int(self.pickerimage_opacity * 255) # 알파 채널 값 얻기
                    image.SetAlphaPixel(alphaBit, x, y, alpha) # 알파 채널 설정
        else:
            for x in range(0, image.GetBw()):
                for y in range(0, image.GetBh()):
                    alpha = int(image.GetAlphaPixel(alphaBit, x, y) * self.pickerimage_opacity) # 알파 채널 값 얻기
                    image.SetAlphaPixel(alphaBit, x, y, alpha) # 알파 채널 설정
        self.pickerimage = image

        # dialog의 tablist 값 바꾸기



        self.Redraw()
        return True

    def DrawPickerImage(self):
        if self.pickerimage_path is None: return
        if not os.path.exists(self.pickerimage_path): return
        self.pickerimage_x1 = int((self.pan_pos['x'] + self.pickerimage_x) * self.zoom)
        self.pickerimage_y1 = int((self.pan_pos['y'] + self.pickerimage_y) * self.zoom)
        self.pickerimage_x2 = int(self.pickerimage.GetBw() * self.pickerimage_scale * self.zoom)
        self.pickerimage_y2 = int(self.pickerimage.GetBh() * self.pickerimage_scale * self.zoom)

        self.DrawBitmap(self.pickerimage, self.pickerimage_x1, self.pickerimage_y1, self.pickerimage_x2 , self.pickerimage_y2, 0, 0,
         self.pickerimage.GetBw(), self.pickerimage.GetBh(), c4d.BMP_NORMAL | c4d.BMP_ALLOWALPHA)
   
    def DrawButton(self):
        for btn in self.buttons:
            if btn in self.selected_buttons: continue
            self.DrawSetPen(btn['color'])  # 버튼 색상
            # 중앙 좌표와 크기를 사용해 버튼 범위를 설정
            x1 = int(btn['x'] - (btn['size_x'] // 2))
            y1 = int(btn['y'] - (btn['size_y'] // 2))
            x2 = int(btn['x'] + (btn['size_x'] // 2))
            y2 = int(btn['y'] + (btn['size_y'] // 2))

            x1, y1, x2, y2 = self.AdjustPanAndZoom(x1, y1, x2, y2)
            self.DrawRectangle(x1, y1, x2, y2)
            self.DrawSetTextCol(COLOR_TEXT, c4d.COLOR_TRANS)

            x = btn['x']
            y = btn['y'] + (btn['size_y'] // 2 + 10)
            x, y = self.AdjustPanAndZoom(x, y)
            self.DrawText(btn['text'], x, y, c4d.DRAWTEXT_HALIGN_CENTER | c4d.DRAWTEXT_VALIGN_CENTER)

    def DrawSelectedButton(self):
        # 드래그 중이면 그리지 않기.
        if self.drag_button: return
        # 펜 색상을 강조 색상으로 설정
        self.DrawSetPen(COLOR_SELECT)

        # 버튼을 다시 그리면서 강조
        for btn in self.selected_buttons:

            # 중앙 좌표와 크기를 사용해 버튼 범위를 설정
            x1 = int(btn['x'] - (btn['size_x'] // 2))
            y1 = int(btn['y'] - (btn['size_y'] // 2))
            x2 = int(btn['x'] + (btn['size_x'] // 2))
            y2 = int(btn['y'] + (btn['size_y'] // 2))

            x1, y1, x2, y2 = self.AdjustPanAndZoom(x1, y1, x2, y2)

            self.DrawRectangle(x1, y1, x2, y2)
            self.DrawSetTextCol(COLOR_SELECT, c4d.COLOR_TRANS)
            x = btn['x']
            y = btn['y'] + (btn['size_y'] // 2 + 10)
            x, y = self.AdjustPanAndZoom(x, y)
            self.DrawText(btn['text'], x, y, c4d.DRAWTEXT_HALIGN_CENTER | c4d.DRAWTEXT_VALIGN_CENTER)

    def DrawDraggingButton(self):
        if self.drag_button is None or self.clickedPos is None:
            return None

        x = self.clickedPos['x'] - self.dragRelPos['x']
        y = self.clickedPos['y'] - self.dragRelPos['y']

        if self.flag_Mode == "DragWithShift":
            distance_x = abs(x - (self.dragStartPos['x'] - self.dragRelPos['x']))
            distance_y = abs(y - (self.dragStartPos['y'] - self.dragRelPos['y']))
            if distance_x > distance_y:
                y = int(self.dragStartPos['y'] - self.dragRelPos['y'])
            elif distance_x < distance_y:
                x = int(self.dragStartPos['x'] - self.dragRelPos['x'])

        for btn in self.selected_buttons:
            size_x = btn['size_x']  # 선택된 버튼의 X 사이즈
            size_y = btn['size_y']  # 선택된 버튼의 Y 사이즈
            if btn == self.drag_button:  # 드래그한 버튼의 포지션은 유지
                rx1 = int(x - (size_x // 2))
                rx2 = int(x + (size_x // 2))
                ry1 = int(y - (size_y // 2))
                ry2 = int(y + (size_y // 2))
            else:  # 나머지 선택된 버튼의 포지션 오프셋
                rx1 = int(x + btn['x'] - (self.dragStartPos['x'] - self.dragRelPos['x']) - (size_x // 2))
                rx2 = int(x + btn['x'] - (self.dragStartPos['x'] - self.dragRelPos['x']) + (size_x // 2))
                ry1 = int(y + btn['y'] - (self.dragStartPos['y'] - self.dragRelPos['y']) - (size_y // 2))
                ry2 = int(y + btn['y'] - (self.dragStartPos['y'] - self.dragRelPos['y']) + (size_y // 2))

            rx1, ry1, rx2, ry2 = self.AdjustPanAndZoom(rx1, ry1, rx2, ry2)
            # 드래그된 버튼을 중심 좌표와 크기로 설정

            self.DrawSetPen(COLOR_DRAG)
            self.DrawRectangle(rx1, ry1, rx2, ry2)

    def SelectButton(self, x1, y1, x2, y2):
        """(x1, y1)과 (x2, y2)로 정의된 드래그 범위 내의 버튼 ID를 검색합니다."""
        selected_buttons = []

        # 드래그 범위 좌표를 정규화
        drag_x_min = min(x1, x2)
        drag_x_max = max(x1, x2)
        drag_y_min = min(y1, y2)
        drag_y_max = max(y1, y2)

        for button in self.buttons:
            if button:
                # 버튼 중심 좌표와 크기를 기준으로 범위 계산
                button_x_min = button['x'] - (button['size_x'] // 2)
                button_x_max = button['x'] + (button['size_x'] // 2)
                button_y_min = button['y'] - (button['size_y'] // 2)
                button_y_max = button['y'] + (button['size_y'] // 2)

                button_x_min, button_y_min, button_x_max, button_y_max = \
                self.AdjustPanAndZoom(button_x_min, button_y_min, button_x_max, button_y_max)
                # 버튼 사각형이 드래그 영역과 겹치는지 확인
                if (button_x_min < drag_x_max and button_x_max > drag_x_min and
                    button_y_min < drag_y_max and button_y_max > drag_y_min):
                    selected_buttons.append(button)

        return selected_buttons

    def ShowMultipleButtons(self):
        # draw background
        # self.DrawSetPen(COLOR_BACKGROUND + 0.1)   
        # self.DrawRectangle(5, 5, (5 + self.GetWidth()) // 2, 55)

        # draw text
        self.DrawSetFont(c4d.FONT_BOLD)  # 폰트 설정
        self.DrawSetTextCol(COLOR_SELECT, c4d.COLOR_TRANS)
        self.DrawText(self.addmultiple_objs[0].GetName(), 10, 10, c4d.DRAWTEXT_HALIGN_LEFT | c4d.DRAWTEXT_VALIGN_TOP)

        # draw left multiple buttons
        for i, iobj in enumerate(self.addmultiple_objs):
            self.DrawSetPen(COLOR_SELECT)
            x = int(i * SIZE_BUTTON_X + 10)
            self.DrawRectangle( x, 30, x + (SIZE_BUTTON_X // 2), 30 + (SIZE_BUTTON_X // 2))

    def isCurrentlyDragged(self):
        """드래그 작업이 현재 발생 중인지 확인합니다."""
        return self.clickedPos is not None and self.drag_button is not None

    def AdjustPanAndZoom(self, x1, y1, x2 = None, y2 = None):
        new_x1 = int((x1 + self.pan_pos['x']) * self.zoom)
        new_y1 = int((y1 + self.pan_pos['y']) * self.zoom)
        if x2 is None and y2 is None:
            return new_x1, new_y1
        new_x2 = int((x2 + self.pan_pos['x']) * self.zoom)
        new_y2 = int((y2 + self.pan_pos['y']) * self.zoom)
        return new_x1, new_y1, new_x2, new_y2

    def ShowPopupDialog(self, x, y, selected_obj):
        # 팝업 다이얼로그에 사용할 BaseContainer 생성
        popup_menu = c4d.BaseContainer()
        if selected_obj: popup_menu.InsData(self.ID_POPUP_ADDBUTTON, 'Add a Button')
        else:            popup_menu.InsData(self.ID_POPUP_ADDBUTTON, 'Add a Button&d&')

        if len(selected_obj) >= 2: popup_menu.InsData(self.ID_POPUP_ADDBUTTONS, 'Add Multiple Buttons')
        else:                      popup_menu.InsData(self.ID_POPUP_ADDBUTTONS, 'Add Multiple Buttons&d&')
        
        popup_menu.InsData(0, '')  # Append separator

        if self.selected_buttons: popup_menu.InsData(self.ID_POPUP_DELETEBUTTON, 'Delete Button')
        else:            popup_menu.InsData(self.ID_POPUP_DELETEBUTTON, 'Delete Button&d&')

        popup_menu.InsData(0, '')  # Append separator

        # Add new items to the popup menu
        if self.selected_buttons: popup_menu.InsData(self.ID_POPUP_HORIZONTAL_ALIGN, 'Horizontal Align')
        else: popup_menu.InsData(self.ID_POPUP_HORIZONTAL_ALIGN, 'Horizontal Align&d&')

        if self.selected_buttons: popup_menu.InsData(self.ID_POPUP_VERTICAL_ALIGN, 'Vertical Align')
        else: popup_menu.InsData(self.ID_POPUP_VERTICAL_ALIGN, 'Vertical Align&d&')

        popup_menu.InsData(0, '')  # Append separator

        if self.selected_buttons: popup_menu.InsData(self.ID_POPUP_HORIZONTAL_DISTRIBUTE, 'Horizontal Distribute')
        else: popup_menu.InsData(self.ID_POPUP_HORIZONTAL_DISTRIBUTE, 'Horizontal Distribute&d&')

        if self.selected_buttons: popup_menu.InsData(self.ID_POPUP_VERTICAL_DISTRIBUTE, 'Vertical Distribute')
        else: popup_menu.InsData(self.ID_POPUP_VERTICAL_DISTRIBUTE, 'Vertical Distribute&d&')

        popup_menu.InsData(0, '')  # Append separator

        if self.selected_buttons: popup_menu.InsData(self.ID_POPUP_MIRROR_BUTTONS, 'Mirror Buttons...')
        else: popup_menu.InsData(self.ID_POPUP_MIRROR_BUTTONS, 'Mirror Buttons...&d&')

        l2s = self.Local2Screen()
        x += l2s['x']
        y += l2s['y']

        # 팝업 다이얼로그 표시
        result = c4d.gui.ShowPopupDialog(
            cd=None,
            bc=popup_menu,
            x=x,
            y=y,
            flags = c4d.POPUP_ALLOW_FILTERING | c4d.POPUP_RIGHT
        )

        return result

    def DeleteButton(self):
        # self.buttons에서 self.selected_buttons에 있는 요소들을 제거
        self.buttons = [btn for btn in self.buttons if btn not in self.selected_buttons]
        self.selected_buttons.clear()  # 선택된 버튼 목록 초기화
        self.Redraw()  # 변경 사항 반영을 위해 다시 그리기 호출

    def GetKeyboardInput(self, msg):
        # 키보드 입력 상태를 확인하고, 특정 키가 눌렸는지 플래그 반환
        if c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, c4d.BFM_INPUT_CHANNEL, msg):
            if msg[c4d.BFM_INPUT_QUALIFIER] & c4d.QSHIFT:
                return "SHIFT"
            if msg[c4d.BFM_INPUT_QUALIFIER] & c4d.QCTRL:
                return "CTRL"
            if msg[c4d.BFM_INPUT_QUALIFIER] & c4d.QALT:
                return "ALT"
        
        if c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, ord('A'), msg):
            if msg[c4d.BFM_INPUT_VALUE] == 1:
                return "A"
        if c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, ord('M'), msg):
            if msg[c4d.BFM_INPUT_VALUE] == 1:
                return "M"

    def AlignButtonsHorizontally(self):
        if not self.selected_buttons:
            return

        # Calculate the average Y position
        avg_y = sum(btn['y'] for btn in self.selected_buttons) // len(self.selected_buttons)

        # Align all selected buttons to the average Y position
        for btn in self.selected_buttons:
            btn['y'] = avg_y

    def AlignButtonsVertically(self):
        if not self.selected_buttons:
            return

        # Calculate the average X position
        avg_x = sum(btn['x'] for btn in self.selected_buttons) // len(self.selected_buttons)

        # Align all selected buttons to the average X position
        for btn in self.selected_buttons:
            btn['x'] = avg_x
    
    def DistributeButtonsHorizontally(self):
        if not self.selected_buttons:
            return

        # Sort the selected buttons by Y position
        sorted_buttons = sorted(self.selected_buttons, key=lambda btn: btn['x'])

        # Calculate the distance between each button
        distance = (sorted_buttons[-1]['x'] - sorted_buttons[0]['x']) // (len(sorted_buttons) - 1)

        # Distribute the buttons horizontally
        for i, btn in enumerate(sorted_buttons):
            btn['x'] = sorted_buttons[0]['x'] + i * distance
        if not self.selected_buttons:
            return
    
    def DistributeButtonsVertically(self):
        if not self.selected_buttons:
            return

        # Sort the selected buttons by X position
        sorted_buttons = sorted(self.selected_buttons, key=lambda btn: btn['y'])

        # Calculate the distance between each button
        distance = (sorted_buttons[-1]['y'] - sorted_buttons[0]['y']) // (len(sorted_buttons) - 1)

        # Distribute the buttons vertically
        for i, btn in enumerate(sorted_buttons):
            btn['y'] = sorted_buttons[0]['y'] + i * distance

    def MirrorButtons(self):
        if not self.selected_buttons:
            return

        # Duplicate selected_buttons to buttons
        self.duplicated_buttons = []
        for btn in self.selected_buttons:
            new_btn = {
                'objname': btn['objname'][:],
                'x': btn['x'],
                'y': btn['y'],
                'size_x': btn['size_x'],
                'size_y_enable': btn['size_y_enable'],
                'size_y': btn['size_y'],
                'color': c4d.Vector(btn['color'].x, btn['color'].y, btn['color'].z),
                'text': btn['text']
            }
            self.duplicated_buttons.append(new_btn)

        self.buttons.extend(self.duplicated_buttons)

        # Mirror the buttons
        dialog = MirrorButtonsDialog(self)
        dialog.Open(c4d.DLG_TYPE_MODAL, defaultw=500, defaulth=50)

    def InputEvent(self, msg):
        # 마우스 관련 액션이 아닐때 종료
        if msg[c4d.BFM_INPUT_DEVICE] != c4d.BFM_INPUT_MOUSE:
            return True

        # 마우스 클릭 위치 가져오기
        g2l = self.Global2Local()
        self.mouse_pos = {
            'x': int(msg[c4d.BFM_INPUT_X] + g2l['x']),
            'y': int(msg[c4d.BFM_INPUT_Y] + g2l['y'])
        }
        
        """
        # 마우스 더블 좌클릭
        # if msg[c4d.BFM_INPUT_DEVICE] == c4d.BFM_INPUT_MOUSE and None:
        #     if (msg[c4d.BFM_INPUT_CHANNEL] == c4d.BFM_INPUT_MOUSELEFT):
        #         if (msg[c4d.BFM_INPUT_DOUBLECLICK]):
        #             select_btn = self.SelectButton(self.mouse_pos['x'], self.mouse_pos['y'], self.mouse_pos['x'], self.mouse_pos['y'])
        #             if select_btn:
        #                 button_property = MWCharacterPickerButtonDialog(select_btn[0])
        #                 button_property.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE, defaultw=500, defaulth=50)
        """

        # 마우스 왼클릭 (AddMultipleButtons 모드일 때)
        if self.flag_Mode == "AddMultipleButtons" and msg[c4d.BFM_INPUT_DEVICE] == c4d.BFM_INPUT_MOUSE \
            and msg[c4d.BFM_INPUT_CHANNEL] == c4d.BFM_INPUT_MOUSELEFT:
            self.AddButton([self.addmultiple_objs[0]], self.mouse_pos['x'], self.mouse_pos['y'])
            self.addmultiple_objs.pop(0)
            if self.addmultiple_objs == []: self.flag_Mode = None
            self.Redraw()
            return True
        elif self.flag_Mode == "AddMultipleButtons": # AddMultipleButtons 모드일 때, 왼클릭 이벤트만 받기
            return True
        

        flag_mouseButton = None
        if msg[c4d.BFM_INPUT_DEVICE] == c4d.BFM_INPUT_MOUSE and msg[c4d.BFM_INPUT_CHANNEL] == c4d.BFM_INPUT_MOUSELEFT:
            flag_mouseButton = "LEFT"
            self.MouseDragStart(c4d.BFM_INPUT_MOUSELEFT, self.mouse_pos['x'], self.mouse_pos['y'], c4d.MOUSEDRAGFLAGS_DONTHIDEMOUSE | c4d.MOUSEDRAGFLAGS_NOMOVE)
        elif msg[c4d.BFM_INPUT_DEVICE] == c4d.BFM_INPUT_MOUSE and msg[c4d.BFM_INPUT_CHANNEL] == c4d.BFM_INPUT_MOUSERIGHT:
            flag_mouseButton = "RIGHT"
            self.MouseDragStart(c4d.BFM_INPUT_MOUSERIGHT, self.mouse_pos['x'], self.mouse_pos['y'], c4d.MOUSEDRAGFLAGS_DONTHIDEMOUSE | c4d.MOUSEDRAGFLAGS_NOMOVE)
        elif msg[c4d.BFM_INPUT_DEVICE] == c4d.BFM_INPUT_MOUSE and msg[c4d.BFM_INPUT_CHANNEL] == c4d.BFM_INPUT_MOUSEMIDDLE:
            flag_mouseButton = "MIDDLE"
            self.MouseDragStart(c4d.BFM_INPUT_MOUSEMIDDLE, self.mouse_pos['x'], self.mouse_pos['y'], c4d.MOUSEDRAGFLAGS_DONTHIDEMOUSE | c4d.MOUSEDRAGFLAGS_NOMOVE)

        # 키보드 입력 받기
        flag_keyboard = self.GetKeyboardInput(msg)

        # 플래그 초기화
        isFirstTick = True
        flag_click = True
        self.dragStartPos = {'x': self.mouse_pos['x'], 'y': self.mouse_pos['y']}
        
        """ 
        # 마우스 스크롤 업/다운
        if msg[c4d.BFM_INPUT_DEVICE] == c4d.BFM_INPUT_MOUSE and \
          msg[c4d.BFM_INPUT_CHANNEL] == c4d.BFM_INPUT_MOUSEWHEEL:
            if msg[c4d.BFM_INPUT_VALUE] > 0: self.zoom += 0.1 # 스크롤 업
            elif msg[c4d.BFM_INPUT_VALUE] < 0: self.zoom -= 0.1 # 스크롤 다운
            # print('self.zoom', self.zoom)
            self.Redraw()
            return True
        """

        # 마우스 ALT + 우클릭 드래그
        if flag_keyboard == "ALT" and flag_mouseButton == "RIGHT":
            while True:
                # 현재 마우스 정보 업데이트
                result, deltaX, deltaY, channels = self.MouseDrag()
                if result != c4d.MOUSEDRAGRESULT_CONTINUE:
                    break

                if isFirstTick: # 첫 틱은 무시 (클릭 동작 포함)
                    isFirstTick = False
                    self.clickedPos = {'x': self.dragStartPos['x'], 'y': self.dragStartPos['y']}
                    continue
                
                # 마우스가 움직이지 않았다면
                if deltaX == 0.0 and deltaY == 0.0: continue
                
                # 클릭이 아니고 드래그임을 알리는 플래그
                flag_click = False
                # 업데이트된 델타로 마우스 위치 갱신
                self.mouse_pos['x'] -= deltaX
                self.mouse_pos['y'] -= deltaY
                # self.clickedPos = {'x': self.mouse_pos['x'], 'y': self.mouse_pos['y']}
                self.zoom -= (deltaX * ZOOM_INTENSITY) # 스크롤 업
                # self.pan_pos["x"] += (self.dragStartPos['x'] - self.mouse_pos['x']) * ZOOM_INTENSITY * 100
                # self.pan_pos["y"] += (self.dragStartPos['y'] - self.mouse_pos['y']) * ZOOM_INTENSITY * 100
                self.Redraw()
            endState = self.MouseDragEnd()
            if flag_click == True: #ALT 우클릭, 팝업 다이얼로그 실행
                pass
            else:
                if endState == c4d.MOUSEDRAGRESULT_FINISHED:
                    pass
                return True
        if flag_mouseButton == "RIGHT": # 마우스 우클릭
            self.MouseDragEnd()
            select_btn = self.SelectButton(self.mouse_pos['x'], self.mouse_pos['y'],
            self.mouse_pos['x'], self.mouse_pos['y'])

            if select_btn and select_btn[0] not in self.selected_buttons: 
                self.selected_buttons = select_btn
            self.Redraw()
            self.ShowButtonProperties()

            doc = c4d.documents.GetActiveDocument()
            selected_objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN | c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)

            # 팝업 다이얼로그 표시
            result = self.ShowPopupDialog(self.mouse_pos['x'], self.mouse_pos['y'], selected_objs)

            # 사용자 선택 처리
            if result == self.ID_POPUP_ADDBUTTON:
                self.AddButton(selected_objs, self.mouse_pos['x'], self.mouse_pos['y'])  # 마우스 위치에서 버튼 추가
            elif result == self.ID_POPUP_ADDBUTTONS:  # Add Multiple Buttons
                self.flag_Mode = "AddMultipleButtons"  # Add Multiple Buttons 모드로 변경
                self.addmultiple_objs = selected_objs
            elif result == self.ID_POPUP_DELETEBUTTON:  # Delete Button
                self.DeleteButton()
            elif result == self.ID_POPUP_HORIZONTAL_ALIGN:  # Horizontal Align
                self.AlignButtonsHorizontally()
            elif result == self.ID_POPUP_VERTICAL_ALIGN:  # Vertical Align
                self.AlignButtonsVertically()
            elif result == self.ID_POPUP_HORIZONTAL_DISTRIBUTE:  # Horizontal Distribute
                self.DistributeButtonsHorizontally()
            elif result == self.ID_POPUP_VERTICAL_DISTRIBUTE:  # Vertical Distribute
                self.DistributeButtonsVertically()
            elif result == self.ID_POPUP_MIRROR_BUTTONS:  # Mirror Buttons
                self.MirrorButtons()
            elif result == self.ID_POPUP_SELECT_MIRROR_BUTTONS:  # Select Mirror Buttons
                self.SelectMirrorButtons()
            else:
                pass
            
            c4d.gui.ActiveObjectManager_SetObjects(c4d.ACTIVEOBJECTMODE_OBJECT, selected_objs, flags= c4d.ACTIVEOBJECTMANAGER_SETOBJECTS_OPEN)
            self.Redraw()
            self.UpdateTabSavedState()
            return True

        # 마우스 왼클릭 CTRL 드래그, 선택된 버튼이 있다면?
        if flag_keyboard == "CTRL" and flag_mouseButton == "LEFT":
            self.drag_button = None
            select_btn = self.SelectButton(self.mouse_pos['x'], self.mouse_pos['y'], self.mouse_pos['x'], self.mouse_pos['y'])
            
            if not select_btn: # 드래그 시작 점에 버튼이 없으면?
                pass #넘겨서 왼클릭 드래그로 넘어감
            elif select_btn: # 드래그 시작 점에 버튼이 있으면? 버튼 드래그 실행
                # 기존에 선택한 버튼 기억.
                prev_btn = self.selected_buttons

                # Ctrl + 기존에 선택한 버튼을 드래그 했을 때
                if select_btn[0] in self.selected_buttons:
                    pass
                # Ctrl + 기존에 선택되지 않은 버튼을 드래그 했을 때
                else: 
                    self.selected_buttons = [select_btn[0]] # 선택 안된 버튼만 드래그

                # Defines the drag_button only if the user clicked on a square and is not yet already defined
                self.drag_button = select_btn[0]
                #드래그할때 마우스와 버튼 사이 오차 포지션 설정
                self.dragRelPos['x'] = self.dragStartPos['x'] - self.drag_button['x']
                self.dragRelPos['y'] = self.dragStartPos['y'] - self.drag_button['y']

                self.clickedPos = {'x': self.dragStartPos['x'], 'y': self.dragStartPos['y']}
                self.Redraw()
                while True:
                    # 현재 마우스 정보 업데이트
                    result, deltaX, deltaY, channels = self.MouseDrag()
                    if result != c4d.MOUSEDRAGRESULT_CONTINUE:
                        break

                    if isFirstTick: # 첫 틱은 무시 (클릭 동작 포함)
                        isFirstTick = False
                        continue
                    
                    # 마우스가 움직이지 않았다면
                    if deltaX == 0.0 and deltaY == 0.0: continue
                    
                    # 클릭이 아니고 드래그임을 알리는 플래그
                    flag_click = False
                    # 업데이트된 델타로 마우스 위치 갱신
                    self.mouse_pos['x'] -= deltaX / self.zoom
                    self.mouse_pos['y'] -= deltaY / self.zoom
                    self.clickedPos = {'x': self.mouse_pos['x'], 'y': self.mouse_pos['y']}
                    # 키보드 입력 받기
                    flag_keyboard = self.GetKeyboardInput(msg)
                    if flag_keyboard == "SHIFT":
                        self.flag_Mode = "DragWithShift"
                    else:
                        self.flag_Mode = None

                    self.Redraw()

                endState = self.MouseDragEnd()
                if flag_click == True: #Ctrl 클릭만 했다면? 선택 해제 실행해야함.
                    pass
                else:
                    if endState == c4d.MOUSEDRAGRESULT_FINISHED:
                        if self.drag_button:
                            for btn in self.selected_buttons:
                                x = int(self.clickedPos['x'] - self.dragRelPos['x'])
                                y = int(self.clickedPos['y'] - self.dragRelPos['y'])
                                x2 = int(self.clickedPos['x'] - self.dragRelPos['x']) + (btn['x'] - (self.dragStartPos['x'] - self.dragRelPos['x']))
                                y2 = int(self.clickedPos['y'] - self.dragRelPos['y']) + (btn['y'] - (self.dragStartPos['y'] - self.dragRelPos['y']))

                                if self.flag_Mode == "DragWithShift":
                                    distance_x = abs(x - (self.dragStartPos['x'] - self.dragRelPos['x']))
                                    distance_y = abs(y - (self.dragStartPos['y'] - self.dragRelPos['y']))
                                    if distance_x > distance_y:
                                        y = int(self.dragStartPos['y'] - self.dragRelPos['y'])
                                        y2 = btn['y']
                                    elif distance_x < distance_y:
                                        x = int(self.dragStartPos['x'] - self.dragRelPos['x'])
                                        x2 = btn['x']
                                        
                                if btn == self.drag_button:
                                    btn['x'] = x
                                    btn['y'] = y
                                else:
                                    btn['x'] = x2
                                    btn['y'] = y2
                            self.flag_Mode = None
                            self.selected_buttons = prev_btn
                            self.SelectObjectFromButton()
                            self.flag_coreMessage = True
                            self.clickedPos = None
                            self.drag_button = None 
                            self.UpdateTabSavedState()
                            self.Redraw()
                            return True


        # A 누르고 왼클릭
        # if flag_keyboard == "A" and flag_mouseButton == "LEFT": 
        #     doc = c4d.documents.GetActiveDocument()
        #     selected_objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
        #     self.AddButton(selected_objs, self.mouse_pos['x'], self.mouse_pos['y'])  # 마우스 위치에서 버튼 추가
        # # M 누르고 왼클릭
        # elif flag_keyboard == "M" and flag_mouseButton == "LEFT": 
        #     doc = c4d.documents.GetActiveDocument()
        #     selected_objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN | c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
        #     self.flag_Mode = "AddMultipleButtons" # Add Multiple Buttons 모드로 변경
        #     self.addmultiple_objs = selected_objs
        # 그냥 왼클릭 드래그
        if flag_mouseButton == "LEFT":
            while True:
                result, deltaX, deltaY, channels = self.MouseDrag()
                if result != c4d.MOUSEDRAGRESULT_CONTINUE: break
                if isFirstTick:
                    isFirstTick = False
                    self.clickedPos = {'x': self.dragStartPos['x'], 'y': self.dragStartPos['y']}
                    continue
                if deltaX == 0.0 and deltaY == 0.0: continue

                # 클릭이 아니고 드래그임을 알리는 플래그
                flag_click = False
                self.mouse_pos['x'] -= deltaX
                self.mouse_pos['y'] -= deltaY
                self.clickedPos = {'x': int(self.mouse_pos['x']), 'y': int(self.mouse_pos['y'])}
                self.Redraw()
            
            endState = self.MouseDragEnd()
            if endState == c4d.MOUSEDRAGRESULT_FINISHED or flag_click == True:
                if self.isCurrentlyDragged:
                    # 드래그 범위 내에 선택된 버튼 받기
                    select_btn = self.SelectButton(self.dragStartPos['x'], self.dragStartPos['y'], self.clickedPos['x'], self.clickedPos['y'])
                    if flag_keyboard == "SHIFT": # shift 누르고 드래그 완료
                        for btn in select_btn:
                            # 선택된 버튼들 self.selected_buttons에 포함
                            if btn not in self.selected_buttons: self.selected_buttons.append(btn)
                    elif flag_keyboard == "CTRL": # ctrl 누르고 드래그 완료
                        for btn in select_btn:
                            # 선택된 버튼들 self.selected_buttons에서 제외
                            if btn in self.selected_buttons: self.selected_buttons.remove(btn)
                    elif flag_keyboard == None: # 그냥 드래그 완료
                        self.selected_buttons.clear() # 기존 선택된 버튼 선택 해제
                        c4d.CallCommand(12113)  # Deselect All
                        self.selected_buttons = select_btn
                    self.SelectObjectFromButton()

        if flag_keyboard == "ALT" and flag_mouseButton == "MIDDLE": # ALT 누르고 미들클릭
            while True:
                result, deltaX, deltaY, channels = self.MouseDrag()
                if result != c4d.MOUSEDRAGRESULT_CONTINUE: break
                if isFirstTick:
                    isFirstTick = False
                    self.clickedPos = {'x': self.dragStartPos['x'], 'y': self.dragStartPos['y']}
                    continue

                if deltaX == 0.0 and deltaY == 0.0: continue
                
                # 클릭이 아니고 드래그임을 알리는 플래그
                flag_click = False
                self.pan_pos['x'] -= int(deltaX)
                self.pan_pos['y'] -= int(deltaY)
                self.Redraw()
            endState = self.MouseDragEnd()
        if flag_keyboard != "ALT" and flag_mouseButton == "MIDDLE": # 미들 클릭 드래그
            while True:
                result, deltaX, deltaY, channels = self.MouseDrag()
                if result != c4d.MOUSEDRAGRESULT_CONTINUE: break
                if isFirstTick:
                    isFirstTick = False
                    self.clickedPos = {'x': self.dragStartPos['x'], 'y': self.dragStartPos['y']}
                    continue
                if deltaX == 0.0 and deltaY == 0.0: continue
                
                # 클릭이 아니고 드래그임을 알리는 플래그
                flag_click = False
                self.mouse_pos['x'] -= deltaX
                self.mouse_pos['y'] -= deltaY
                self.clickedPos = {'x': int(self.mouse_pos['x']), 'y': int(self.mouse_pos['y'])}
                self.Redraw()

            endState = self.MouseDragEnd()
            if endState == c4d.MOUSEDRAGRESULT_FINISHED or flag_click == True:
                if self.isCurrentlyDragged:
                    # 드래그 범위 내에 선택된 버튼 받기
                    select_btn = self.SelectButton(self.dragStartPos['x'], self.dragStartPos['y'], self.clickedPos['x'], self.clickedPos['y'])
                    if flag_keyboard == "SHIFT":
                        if select_btn and select_btn[0] not in self.selected_buttons: 
                            self.selected_buttons.extend(select_btn) # 클릭한 버튼 선택
                    elif flag_keyboard == "CTRL": # ctrl 누르고 드래그 완료
                        for btn in select_btn:
                            # 선택된 버튼들 self.selected_buttons에서 제외
                            if btn in self.selected_buttons: self.selected_buttons.remove(btn)
                    else:
                        self.selected_buttons = select_btn
                    self.ShowButtonProperties()

        if self.clickedPos is not None or self.drag_button is not None: # 리프레쉬, 클릭 위치와 드래그 중인 버튼 초기화.
            self.clickedPos = None
            self.drag_button = None
            self.Redraw()
        return True

    def SelectObjectFromButton(self):
        doc = c4d.documents.GetActiveDocument()
        doc.StartUndo()

        c4d.CallCommand(12113)  # Deselect All

        if self.selected_buttons:
            for btn in self.selected_buttons:
                for btn_objname in btn['objname']:
                    btn_obj = self.FindObjectbyParentObjectAndNameSpace(btn_objname)
                    if btn_obj:
                        doc.AddUndo(c4d.UNDOTYPE_BITS, btn_obj)  # 언도 추가
                        doc.SetSelection(btn_obj , mode=c4d.SELECTION_ADD)
                        self.flag_coreMessage = True
        
        self.flag_coreMessage = True # CoreMessage 호출

        doc.EndUndo()
        c4d.EventAdd()
        return True

    def ShowButtonProperties(self):
        if self.selected_buttons == []:
            self.dialog.SetColorField(ID_COLOR, c4d.Vector(0,0,0), 1.0, 1.0, 0)
            self.dialog.SetInt32(ID_SIZE_X, SIZE_BUTTON_X, min= SIZE_BUTTON_MIN, max= SIZE_BUTTON_MAX, step= SIZE_BUTTON_STEP)
            self.dialog.SetInt32(ID_SIZE_Y, SIZE_BUTTON_Y, min= SIZE_BUTTON_MIN, max= SIZE_BUTTON_MAX, step= SIZE_BUTTON_STEP)
            self.dialog.SetBool(ID_SIZE_Y_ENABLE, False)
            self.dialog.Enable(ID_SIZE_Y, False)
            self.dialog.SetString(ID_OBJNAME, '')
            self.dialog.SetString(ID_TEXT, '')

            self.dialog.Enable(ID_COLOR, False)
            self.dialog.Enable(ID_SIZE_X, False)
            self.dialog.Enable(ID_SIZE_Y_ENABLE, False)
            self.dialog.Enable(ID_SIZE_Y, False)
            self.dialog.Enable(ID_OBJNAME, False)
            self.dialog.Enable(ID_TEXT, False)
            return
        else:
            self.dialog.Enable(ID_COLOR, True)
            self.dialog.Enable(ID_SIZE_X, True)
            self.dialog.Enable(ID_SIZE_Y_ENABLE, True)
            self.dialog.Enable(ID_SIZE_Y, True)
            self.dialog.Enable(ID_OBJNAME, True)
            self.dialog.Enable(ID_TEXT, True)

        if len(self.selected_buttons) == 1:
            self.dialog.SetColorField(ID_COLOR, self.selected_buttons[0]['color'],1.0,1.0,0)
            self.dialog.SetInt32(ID_SIZE_X, self.selected_buttons[0]['size_x'], min= SIZE_BUTTON_MIN, max= SIZE_BUTTON_MAX, step= SIZE_BUTTON_STEP)
            self.dialog.SetBool(ID_SIZE_Y_ENABLE, self.selected_buttons[0]['size_y_enable'])
            self.dialog.Enable(ID_SIZE_Y, self.selected_buttons[0]['size_y_enable'])
            self.dialog.SetInt32(ID_SIZE_Y, self.selected_buttons[0]['size_y'], min= SIZE_BUTTON_MIN, max= SIZE_BUTTON_MAX, step= SIZE_BUTTON_STEP)
            self.dialog.SetString(ID_OBJNAME, ObjName_to_String(self.selected_buttons[0]['objname']))
            self.dialog.SetString(ID_TEXT, self.selected_buttons[0]['text'])
        else:
            ibuttons = {'color' : None,
                'size_x' : None,
                'size_y_enable' : True,
                'size_y' : None,
                'objname' : None,
                'text' : None}
            ibuttons_multiflag = {'color' : False,
                'size_x' : False,
                'size_y_enable' : False,
                'size_y' : False,
                'objname' : False,
                'text' : False}
            for i,ibutton in enumerate(self.selected_buttons):
                if i == 0:
                    ibuttons['color'] = ibutton['color']
                    ibuttons['size_x'] = ibutton['size_x']
                    ibuttons['size_y_enable'] = ibutton['size_y_enable']
                    ibuttons['size_y'] = ibutton['size_y']
                    ibuttons['objname'] = ibutton['objname']
                    ibuttons['text'] = ibutton['text']
                if ibuttons['color'] != ibutton['color']: ibuttons_multiflag['color'] = True
                if ibuttons['size_x'] != ibutton['size_x']: ibuttons_multiflag['size_x'] = True
                if ibuttons['size_y_enable'] != ibutton['size_y_enable']: ibuttons_multiflag['size_y_enable'] = True
                if ibuttons['size_y'] != ibutton['size_y']: ibuttons_multiflag['size_y'] = True
                if ibuttons['objname'] != ibutton['objname']: ibuttons_multiflag['objname'] = True
                if ibuttons['text'] != ibutton['text']: ibuttons_multiflag['text'] = True
                
            if not ibuttons_multiflag['color']:   self.dialog.SetColorField(ID_COLOR, ibuttons['color'],1.0,1.0,0)
            else:                                 self.dialog.SetColorField(ID_COLOR, c4d.Vector(1,1,1),1.0,1.0,0)
            if not ibuttons_multiflag['size_x']:    self.dialog.SetInt32(ID_SIZE_X, ibuttons['size_x'], min= SIZE_BUTTON_MIN, max= SIZE_BUTTON_MAX, step= SIZE_BUTTON_STEP)
            else:                                 self.dialog.SetInt32(ID_SIZE_X, ibuttons['size_x'], min= SIZE_BUTTON_MIN, max= SIZE_BUTTON_MAX, step= SIZE_BUTTON_STEP, tristate=True)
            if not ibuttons_multiflag['size_y_enable']: 
                self.dialog.SetBool(ID_SIZE_Y_ENABLE, ibuttons['size_y_enable'])
                self.dialog.Enable(ID_SIZE_Y, ibuttons['size_y_enable'])
            else:                                 
                self.dialog.SetBool(ID_SIZE_Y_ENABLE, False)
                self.dialog.Enable(ID_SIZE_Y, False)
            if not ibuttons_multiflag['size_y']:    self.dialog.SetInt32(ID_SIZE_Y, ibuttons['size_y'], min= SIZE_BUTTON_MIN, max= SIZE_BUTTON_MAX, step= SIZE_BUTTON_STEP)
            else:                                 self.dialog.SetInt32(ID_SIZE_Y, ibuttons['size_y'], min= SIZE_BUTTON_MIN, max= SIZE_BUTTON_MAX, step= SIZE_BUTTON_STEP, tristate=True)
            if not ibuttons_multiflag['objname']: self.dialog.SetString(ID_OBJNAME, ObjName_to_String(ibuttons['objname']))
            else:                                 self.dialog.SetString(ID_OBJNAME, '', tristate = True)
            if not ibuttons_multiflag['text']:    self.dialog.SetString(ID_TEXT, ibuttons['text'])
            else:                                 self.dialog.SetString(ID_TEXT, '', tristate = True)
    
        return True

    def UpdateTabSavedState(self):
        active_tab_data = self.dialog.GetActiveTab()
        if active_tab_data:
            if active_tab_data['saved']:
                active_tab_data['saved'] = False
                self.dialog.DrawTabGroup(active_tab_data)

    def SelectButtonFromObject(self):
        doc = c4d.documents.GetActiveDocument()

        current_objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN | c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
        
        if self.parentobjname_enable:
            for obj in current_objs:
                parent = obj
                flag_parentexist = False
                while parent:
                    if parent.GetName() == self.parentobjname:
                        flag_parentexist = True
                        break
                    parent = parent.GetUp()
                if flag_parentexist == False:
                    current_objs.remove(obj)

        current_objs_name = [iobj.GetName() for iobj in current_objs]

        # 선택된 오브젝트가 바뀌었나? = 오브젝트를 선택했나?
        if current_objs != self.prev_objs or self.flag_coreMessage == True:
            self.flag_coreMessage = False
            self.selected_buttons = []
            for ibutton in self.buttons:
                if all(item in current_objs_name and item for item in ibutton['objname']):
                    if len(ibutton['objname']) <= 1:
                        self.selected_buttons.append(ibutton)
            self.prev_objs = current_objs

            self.ShowButtonProperties()

            self.Redraw()
            c4d.gui.ActiveObjectManager_SetObjects(c4d.ACTIVEOBJECTMODE_OBJECT,
            current_objs, flags= c4d.ACTIVEOBJECTMANAGER_SETOBJECTS_OPEN)
            c4d.EventAdd()
            return True

    def CoreMessage(self, id, msg):
        # 시포디 아무 이벤트나 감지
        if id == c4d.EVMSG_CHANGE:
            self.SelectButtonFromObject()
        return True

class MWSubDialog(gui.SubDialog):
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog # 부모 클래스 인스턴스를 저장
        self.user_area = MWCharacterPickerUserArea(dialog, self)

    def CreateLayout(self):
        # GeUserArea 추가
        area = self.AddUserArea(id=ID_USERAREA, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
        self.AttachUserArea(self.user_area, area)

        return True

class MWCharacterPickerDialog(gui.GeDialog):
    # MENU-FILE ID
    ID_MENU_NEWPICKER = 1001
    # ----
    ID_MENU_OPENPICKER = 1002
    # ----
    ID_MENU_SAVEPICKER = 1011
    ID_MENU_SAVEPICKERAS = 1012
    # ----
    ID_MENU_RELOADSCENEPICKER = 1021
    ID_MENU_SAVESCENEPICKER = 1022
    # ----
    ID_MENU_CLOSEPICKER = 1031

    # MENU-PICKER ID
    # ID_MENU_RENAMEPICKER = 1101
    # ----
    ID_MENU_LOADPICKERIMAGE = 1101
    ID_MENU_CLEARPICKERIMAGE = 1102
    # ----
    ID_MENU_PICKERIMAGESETTINGS = 1111
    # ----
    ID_MENU_PICKERTOLEFT = 1121
    ID_MENU_PICKERTORIGHT = 1122
    # ----
    ID_MENU_AUTOSETUPPICKER = 1131 # PRO
    # ----
    ID_MENU_DELETEUNLINKEDBUTTON = 1141
    ID_MENU_SELECTUNLINKEDBUTTON = 1142

    # MENU-ABOUT
    ID_MENU_TUTORIAL = 1901
    ID_MENU_ABOUT = 1902
    doc = None

    def __init__(self):
        self._tabList = []  # 탭 이름과 SubDialog를 저장하는 리스트
        self.doc = c4d.documents.GetActiveDocument()
    
    def InitValues(self):
        self.activeDoc = c4d.documents.GetActiveDocument()
        self.ReloadScenePicker()
        return True

    def DestroyWindow(self):
        # print("DestroyWindow")
        pass

    def ReloadScenePicker(self):
        self._tabList = []

        self.doc = c4d.documents.GetActiveDocument()
        if self.doc.GetDataInstance().GetContainerInstance(PATH_ID) is None:
            print("No Picker Data in the Project File.")
            # gui.MessageDialog("No Picker Data in the Project File.")
        elif self.doc.GetDataInstance().GetContainerInstance(PATH_ID) is not None:
            for cid, path in self.doc.GetDataInstance().GetContainerInstance(PATH_ID):
                if path is not None: self.LoadScenePickerData(path)
       
       # 기본적으로 'Untitled' 탭 추가
        if self._tabList == []:
            cg1 = MWSubDialog(self)
            self.AppendTab('Untitled', cg1, active=True, saved=False)
        return True

    @property
    def activeDoc(self):
        doc = getattr(self, '_activeDoc', None)
        if doc is None:
            return None

        if not doc.IsAlive():
            return None
        return doc

    @activeDoc.setter
    def activeDoc(self, value):
        if not isinstance(value, c4d.documents.BaseDocument):
            raise TypeError("value is not a c4d.documents.BaseDocument.")
        self._activeDoc = value

    def CreateMenuLayout(self):
        # 메뉴 생성
        self.MenuFlushAll()

        # File 메뉴 생성
        self.MenuSubBegin("File")
        self.MenuAddString(self.ID_MENU_NEWPICKER, "New Picker")
        self.MenuAddSeparator()
        self.MenuAddString(self.ID_MENU_OPENPICKER, "Open Picker File...")
        self.MenuAddSeparator()
        self.MenuAddString(self.ID_MENU_SAVEPICKER, "Save Picker File")
        self.MenuAddString(self.ID_MENU_SAVEPICKERAS, "Save Picker File as...")
        self.MenuAddSeparator()
        self.MenuAddString(self.ID_MENU_RELOADSCENEPICKER, "Reload Picker from Project File")
        self.MenuAddString(self.ID_MENU_SAVESCENEPICKER, "Save Picker to Project File")
        self.MenuAddSeparator()
        self.MenuAddString(self.ID_MENU_CLOSEPICKER, "Close Picker")
        self.MenuSubEnd()

        # Picker 메뉴 생성
        self.MenuSubBegin("Picker")
        # self.MenuAddString(self.ID_MENU_RENAMEPICKER, "Rename Picker")
        # self.MenuAddSeparator()


        self.MenuAddString(self.ID_MENU_LOADPICKERIMAGE, "Load Picker Image...")
        self.MenuAddString(self.ID_MENU_CLEARPICKERIMAGE, "Clear Picker Image")
        self.MenuAddSeparator()
        self.MenuAddString(self.ID_MENU_PICKERIMAGESETTINGS, "Picker Image Settings...")
        self.MenuAddSeparator()
        self.MenuAddString(self.ID_MENU_PICKERTOLEFT, "Move Picker to Left")
        self.MenuAddString(self.ID_MENU_PICKERTORIGHT, "Move Picker to Right")
        self.MenuAddSeparator()
        # self.MenuAddString(self.ID_MENU_AUTOSETUPPICKER, "Auto Setup Picker (PRO)&d&")  # PRO
        self.MenuAddSeparator()
        # self.MenuAddString(self.ID_MENU_DELETEUNLINKEDBUTTON, "Delete Unlinked Buttons (PRO)&d&")
        # self.MenuAddString(self.ID_MENU_SELECTUNLINKEDBUTTON, "Select Unlinked Buttons (PRO)&d&")
        self.MenuSubEnd()

        # About 메뉴 생성
        self.MenuSubBegin("About")
        
        self.MenuAddString(self.ID_MENU_TUTORIAL, "Tutorial...")
        self.MenuAddString(self.ID_MENU_ABOUT, "About...")
        self.MenuSubEnd()     

        return True   

    def CreateLayout(self):
        self.SetTitle("MW Character Picker")

        self.CreateMenuLayout()

        # 핵심 TAB 그룹 생성
        self.GroupBegin(ID_MAINGROUP, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 0, '', 0)
        # TabGroup, SubDialog, UserArea 포함
        self.GroupEnd()

        # 버튼 속성 그룹 생성
        self.GroupBegin(ID_BUTTONGROUP, c4d.BFH_SCALEFIT | c4d.BFV_BOTTOM, 10, 0, '', 0, 0, 20)
        self.GroupBorderSpace(8, 0, 8, 0)
    
        # Color 선택 필드 추가 (라벨 없이 컬러 필드만 1열로 차지)
        # self.AddStaticText(0, c4d.BFH_LEFT, name="Color")
        self.AddColorField(id = ID_COLOR, flags = c4d.BFH_LEFT | c4d.BFV_CENTER, initw = 40, inith = 12)
        
        # Size X 추가
        self.AddStaticText(0, c4d.BFH_LEFT, name="Size")
        self.AddEditNumberArrows(id=ID_SIZE_X, flags=c4d.BFH_LEFT | c4d.BFV_CENTER, initw=18)
        self.SetInt32(ID_SIZE_X, SIZE_BUTTON_X, min=SIZE_BUTTON_MIN, max=SIZE_BUTTON_MAX, step=SIZE_BUTTON_STEP)

        # Uniform Scale Checkbox 추가
        self.AddCheckbox(ID_SIZE_Y_ENABLE, c4d.BFH_LEFT | c4d.BFV_CENTER, initw = 22, inith = 14, name = "")
        self.SetBool(ID_SIZE_Y_ENABLE, False)

        # Size Y 추가
        # self.AddStaticText(0, c4d.BFH_LEFT, name="Size Y")
        self.AddEditNumberArrows(id=ID_SIZE_Y, flags=c4d.BFH_LEFT | c4d.BFV_CENTER, initw=18)
        self.SetInt32(ID_SIZE_Y, SIZE_BUTTON_Y, min=SIZE_BUTTON_MIN, max=SIZE_BUTTON_MAX, step=SIZE_BUTTON_STEP)
        self.Enable(ID_SIZE_Y, False)

        # Objname 추가
        # self.AddStaticText(0, c4d.BFH_LEFT, name="Object Name")
        self.AddEditText(id = ID_OBJNAME, flags = c4d.BFH_SCALEFIT | c4d.BFV_CENTER, editflags = c4d.EDITTEXT_HELPTEXT)
        self.SetString(ID_OBJNAME, 'Button Object Name...', c4d.BORDER_NONE,  flags = c4d.EDITTEXT_HELPTEXT)
        
        # Text 추가
        self.AddStaticText(0, c4d.BFH_LEFT, name="Text")
        self.AddEditText(id = ID_TEXT, flags = c4d.BFH_RIGHT | c4d.BFH_FIT | c4d.BFV_CENTER, initw = 70, editflags = c4d.EDITTEXT_HELPTEXT)
        self.SetString(ID_TEXT, 'Text...', c4d.BORDER_NONE,  flags = c4d.EDITTEXT_HELPTEXT)

        # 그룹 종료
        self.GroupEnd()

        return True

    def DrawTabGroup(self, active_tab=None):
        # 메인 그룹의 내용을 초기화
        self.LayoutFlushGroup(ID_MAINGROUP)
        # TabGroup 생성
        self.TabGroupBegin(ID_TABGROUP, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, tabtype=c4d.TAB_TABS)

        # 각 탭에 대응하는 SubDialog 추가
        for tabId, tabData in enumerate(self._tabList):
            # geuserarea에서 coremessage에서 변화가 있거나 path가 없다면 탭 이름에 '*'를 추가
            tab_name = tabData['tabname'] + ' *' if not tabData['saved'] else tabData['tabname']
            
            self.GroupBegin(id = ID_SUBDIALOG_GROUP + tabId, flags = c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
                             title = tab_name, cols = 1)
            self.AddSubDialog(ID_SUBDIALOG + tabId, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
            self.AttachSubDialog(tabData['subdialog'], ID_SUBDIALOG + tabId)
            
            # ID_NAMESPACE EditText를 추가
            self.GroupBegin(id = ID_FILTER_GROUP + tabId, flags = c4d.BFH_SCALEFIT | c4d.BFV_TOP, title = 'Namespace', cols=2)
            self.GroupBorderSpace(3, 0, 3, 0)
            
            self.AddCheckbox(ID_PARENTOBJ_ENABLE + tabId, c4d.BFH_LEFT | c4d.BFV_CENTER, name="Parent Object", initw = 160, inith = 12)
            self.AddEditText(ID_PARENTOBJ + tabId, c4d.BFH_SCALEFIT | c4d.BFV_TOP, initw = 1, inith = 12, editflags=c4d.EDITTEXT_HELPTEXT)
            self.AddCheckbox(ID_NAMESPACE_ENABLE + tabId, c4d.BFH_LEFT | c4d.BFV_CENTER, name="Name Space", initw = 160, inith = 12)
            self.AddEditText(ID_NAMESPACE + tabId, c4d.BFH_SCALEFIT | c4d.BFV_TOP, initw = 1, inith = 12, editflags=c4d.EDITTEXT_HELPTEXT)

            self.SetBool(ID_PARENTOBJ_ENABLE + tabId, tabData['parentobjname_enable'])
            self.Enable(ID_PARENTOBJ + tabId, tabData['parentobjname_enable'])
            self.SetString(ID_PARENTOBJ + tabId, tabData['parentobjname'], c4d.BORDER_NONE)

            self.SetBool(ID_NAMESPACE_ENABLE + tabId, tabData['namespace_enable'])
            self.Enable(ID_NAMESPACE + tabId, tabData['namespace_enable'])
            self.SetString(ID_NAMESPACE + tabId, tabData['namespace'], c4d.BORDER_NONE)

            self.SetString(ID_PARENTOBJ + tabId, 'Parent Object Name...', c4d.BORDER_NONE,  flags = c4d.EDITTEXT_HELPTEXT)
            self.SetString(ID_NAMESPACE + tabId, 'Name Space... (for XRef)', c4d.BORDER_NONE,  flags = c4d.EDITTEXT_HELPTEXT)

            tabData['subdialog'].user_area.ShowButtonProperties()

            self.GroupEnd()
            self.GroupEnd()
        self.GroupEnd()  # TabGroup 종료

        # Set the Active Tab
        if active_tab:
            self.SetInt32(ID_TABGROUP, ID_SUBDIALOG_GROUP + self._tabList.index(active_tab))

        # 그룹 변경 사항을 알림
        self.LayoutChanged(ID_MAINGROUP)
        return True
    
    def AppendTab(self, tabName, subdialog, active=False, path="", saved=False,
                  parentobjname_enable=False, parentobjname="",
                  namespace_enable=False, namespace="", 
                  pickerimage_path="",
                  pickerimage_x=0, pickerimage_y=0,
                  pickerimage_scale=1.0,
                  pickerimage_opacity=0.5):
        """새로운 탭과 해당 내용을 추가합니다."""
        # Updates our current tabList with tabName and the SubDialog to be linked
        self._tabList.append({
            'tabname': tabName, 'subdialog': subdialog, 'path': path, 'saved': saved, 
            'parentobjname_enable': parentobjname_enable, 'parentobjname': parentobjname,
            'namespace_enable': namespace_enable, 'namespace': namespace,
            'pickerimage_path': pickerimage_path, 
            'pickerimage_x': pickerimage_x, 'pickerimage_y': pickerimage_y,
            'pickerimage_scale': pickerimage_scale,
            'pickerimage_opacity': pickerimage_opacity
        })
        
        # 추가된 탭을 활성화
        if active == True: self.DrawTabGroup(self._tabList[-1]) 
        else: self.DrawTabGroup()

        return True

    def GetActiveTab(self):
        # 활성화된 탭의 ID와 인덱스를 얻어 해당 탭의 이름과 SubDialog를 반환
        active_tab_id = self.GetInt32(ID_TABGROUP)
        active_tab_index = active_tab_id - ID_SUBDIALOG_GROUP

        # 유효한 인덱스인지 확인 후 탭 이름 가져오기
        if 0 <= active_tab_index < len(self._tabList):
            active_tab_data = self._tabList[active_tab_index]
            return active_tab_data
        else:
            print("Invalid tab index:", active_tab_index)
            return None

    def SavePickerAs(self):
        # 활성화된 탭 이름과 SubDialog 가져오기
        active_tab_data = self.GetActiveTab()
        doc = c4d.documents.GetActiveDocument()
        def_path = doc.GetDocumentPath() if doc else ""
        def_file = active_tab_data['tabname']
        save_path = c4d.storage.SaveDialog(title="Save Picker As", force_suffix="json",
         type=c4d.FILESELECTTYPE_ANYTHING, def_path=def_path, def_file=def_file)

        if not save_path: return True  # 사용자가 취소한 경우
        # 저장한 파일 이름으로 active_tab_data['tabname']을 업데이트
        active_tab_data['tabname'] = os.path.splitext(os.path.basename(save_path))[0]

        self.SavePickerData(active_tab_data, save_path)

    def Command(self, id, msg):
        # ("Menu command:", id)
        # 메뉴 커맨드 함수

        if id == ID_TABGROUP:
            self.GetInt32(ID_TABGROUP)
            active_tab_data = self.GetActiveTab()
            active_tab_data['subdialog'].user_area.flag_coreMessage = True
            active_tab_data['subdialog'].user_area.SelectButtonFromObject()
            active_tab_data['subdialog'].user_area.ShowButtonProperties()
            active_tab_data['subdialog'].user_area.Redraw()
            c4d.EventAdd()


        if self.ID_MENU_NEWPICKER <= id <= self.ID_MENU_ABOUT:
            return self.Command_Menu(id, msg)
        
        # Parent Object Name Enable
        if ID_PARENTOBJ_ENABLE <= id <= ID_PARENTOBJ_ENABLE + 50:
            active_tab_data = self.GetActiveTab()
            if active_tab_data:
                self.Enable(ID_PARENTOBJ + id - ID_PARENTOBJ_ENABLE, self.GetBool(id))
                active_tab_data['parentobjname_enable'] = self.GetBool(id)
                active_tab_data['subdialog'].user_area.parentobjname_enable = active_tab_data['parentobjname_enable'] 
                active_tab_data['parentobjname'] = self.GetString(ID_PARENTOBJ + id - ID_PARENTOBJ_ENABLE)
                active_tab_data['subdialog'].user_area.parentobjname = active_tab_data['parentobjname']
                active_tab_data['saved'] = False


        # ParentObjectName
        if ID_PARENTOBJ <= id <= ID_PARENTOBJ + 50:
            active_tab_data = self.GetActiveTab()
            if active_tab_data:
                active_tab_data['parentobjname'] = self.GetString(id)
                active_tab_data['subdialog'].user_area.parentobjname = active_tab_data['parentobjname']
                active_tab_data['saved'] = False

        # NameSpace Enable
        if ID_NAMESPACE_ENABLE <= id <= ID_NAMESPACE_ENABLE + 50:
            active_tab_data = self.GetActiveTab()
            if active_tab_data:
                self.Enable(ID_NAMESPACE + id - ID_NAMESPACE_ENABLE, self.GetBool(id))
                active_tab_data['namespace_enable'] = self.GetBool(id)
                active_tab_data['subdialog'].user_area.namespace_enable = active_tab_data['namespace_enable']
                active_tab_data['namespace'] = self.GetString(ID_NAMESPACE + id - ID_NAMESPACE_ENABLE)
                active_tab_data['subdialog'].user_area.namespace = active_tab_data['namespace']
                active_tab_data['subdialog'].user_area.ChangeButtonObjectNameSpace()
                active_tab_data['saved'] = False


        # NameSpace
        if ID_NAMESPACE <= id <= ID_NAMESPACE + 50:
            active_tab_data = self.GetActiveTab()
            if active_tab_data:
                active_tab_data['namespace'] = self.GetString(id)
                active_tab_data['subdialog'].user_area.namespace = active_tab_data['namespace']
                active_tab_data['subdialog'].user_area.ChangeButtonObjectNameSpace()
                active_tab_data['saved'] = False


        # Button Properties
        if self._tabList is not None and (id == ID_COLOR or id == ID_SIZE_X or id == ID_SIZE_Y_ENABLE or id == ID_SIZE_Y or id == ID_OBJNAME or id == ID_TEXT):
            active_tab_data = self.GetActiveTab()
            for ibutton in active_tab_data['subdialog'].user_area.selected_buttons:
                if id == ID_COLOR:
                    ibutton['color'] = self.GetColorField(ID_COLOR)['color']
                if id == ID_SIZE_X:
                    ibutton['size_x'] = self.GetInt32(ID_SIZE_X)
                    if self.GetBool(ID_SIZE_Y_ENABLE) == False:
                        ibutton['size_y'] = ibutton['size_x']
                        self.SetInt32(ID_SIZE_Y, ibutton['size_y'], min= SIZE_BUTTON_MIN, max= SIZE_BUTTON_MAX, step= SIZE_BUTTON_STEP)
                if id == ID_SIZE_Y_ENABLE:
                    if self.GetBool(ID_SIZE_Y_ENABLE) == True:
                        ibutton['size_y_enable'] = True
                        self.Enable(ID_SIZE_Y, True)
                        ibutton['size_y'] = self.GetInt32(ID_SIZE_Y)
                    elif self.GetBool(ID_SIZE_Y_ENABLE) == False:
                        ibutton['size_y_enable'] = False
                        self.Enable(ID_SIZE_Y, False)
                        ibutton['size_y'] = ibutton['size_x']
                        self.SetInt32(ID_SIZE_Y, ibutton['size_x'], min= SIZE_BUTTON_MIN, max= SIZE_BUTTON_MAX, step= SIZE_BUTTON_STEP)
                if id == ID_SIZE_Y:
                    ibutton['size_y'] = self.GetInt32(ID_SIZE_Y)
                if id == ID_OBJNAME:
                    ibutton['objname'] = String_to_ObjName(self.GetString(ID_OBJNAME))
                if id == ID_TEXT:
                    ibutton['text'] = self.GetString(ID_TEXT)
                active_tab_data['subdialog'].user_area.Redraw()
            active_tab_data['saved'] = False  # 저장 상태 업데이트


        return True

    def Command_Menu(self, id, msg):
        
        if id == self.ID_MENU_TUTORIAL: # Tutorial
            webbrowser.open('https://ddingone.notion.site/MW-Character-Picker-EN-1455d2f9e5c580149ffcec36169ba19c')

        if id == self.ID_MENU_NEWPICKER: # New Picker
            # 새로운 탭 생성
            new_tab = MWSubDialog(self)
            untitled_count = sum(1 for tab in self._tabList if tab['tabname'].startswith('Untitled'))

            if untitled_count > 0: new_tab_name = f'Untitled.{untitled_count + 1}'
            else: new_tab_name = 'Untitled'
            new_tab = MWSubDialog(self)
            self.AppendTab(new_tab_name, new_tab, active=True, saved=False)
        if id == self.ID_MENU_CLOSEPICKER: # Close Picker
            active_tab_data = self.GetActiveTab()
            if active_tab_data['saved'] == False:
                if active_tab_data['subdialog'].user_area.buttons == []: # 버튼이 없는 탭은 저장하지 않음
                    self._tabList.remove(active_tab_data)
                elif active_tab_data['path'] == "":
                    result = c4d.gui.MessageDialog(f"Do you want to save the changes to your\n" +
                                                   f"picker \"{active_tab_data['tabname']}\"\n" +
                                                   f"before closing?", c4d.GEMB_YESNOCANCEL)
                    if result == c4d.GEMB_R_V_YES:
                        self.SavePickerAs()
                    if result == c4d.GEMB_R_V_NO:
                        self._tabList.remove(active_tab_data)
                    if result == c4d.GEMB_R_V_CANCEL:
                        return True
                else:
                    result = c4d.gui.MessageDialog(f"Do you want to save the changes to your\n" +
                                                   f"picker \"{active_tab_data['tabname']}\"\n" +
                                                   f"before closing?", c4d.GEMB_YESNOCANCEL)
                    if result == c4d.GEMB_R_V_YES:
                        self.SavePickerData(active_tab_data, active_tab_data['path'])
                    if result == c4d.GEMB_R_V_NO:
                        self._tabList.remove(active_tab_data)
                    if result == c4d.GEMB_R_V_CANCEL:
                        return True
            elif active_tab_data['saved'] == True:
                self._tabList.remove(active_tab_data)

            if self._tabList == []: # 만약 self._tablist == [] 이면 새로운 탭 생성
                cg1 = MWSubDialog(self)
                self.AppendTab('Untitled', cg1, active=True, saved=False)
            self.DrawTabGroup()
        if id == self.ID_MENU_OPENPICKER: # Open Picker...
            active_tab_data = self.GetActiveTab()
            # 파일 열기 창 열기
            doc = c4d.documents.GetActiveDocument()
            def_path = doc.GetDocumentPath() if doc else ""
            def_file = active_tab_data['tabname']
            path = c4d.storage.LoadDialog(title="Open Picker", force_suffix="json",
             type=c4d.FILESELECTTYPE_ANYTHING, def_path=def_path, def_file=def_file)
            if not path: return True  # 사용자가 취소한 경우
            self.LoadScenePickerData(path)
        if id == self.ID_MENU_RELOADSCENEPICKER: # Reload Scene Picker
            self.ReloadScenePicker()
        if id == self.ID_MENU_SAVEPICKERAS:  # Save Picker as...
            self.SavePickerAs()
        if id == self.ID_MENU_SAVEPICKER: # Save Picker
            # 활성화된 탭 이름과 SubDialog 가져오기
            active_tab_data = self.GetActiveTab()
            # path가 없으면 Save As 다이얼로그 띄우기 
            if not active_tab_data['path']:
                self.SavePickerAs()
            else:
                save_path = active_tab_data['path']
                self.SavePickerData(active_tab_data, save_path)
        if id == self.ID_MENU_SAVESCENEPICKER: # Save Scene Picker
            self.SaveScenePickerData()
        if id == self.ID_MENU_LOADPICKERIMAGE: # Load Image
            active_tab_data = self.GetActiveTab()
            pickerimage_path = c4d.storage.LoadDialog(title="Load Image",
            force_suffix="png", type=c4d.FILESELECTTYPE_IMAGES)
            if pickerimage_path is None: return True
            active_tab_data['pickerimage_path'] = pickerimage_path

            active_tab_data['subdialog'].user_area.pickerimage_path = pickerimage_path
            active_tab_data['subdialog'].user_area.pickerimage_x = 0
            active_tab_data['subdialog'].user_area.pickerimage_y = 0
            active_tab_data['subdialog'].user_area.pickerimage_scale = 1.0
            active_tab_data['subdialog'].user_area.pickerimage_opacity = 0.5
            active_tab_data['subdialog'].user_area.SetPickerImage()

            active_tab_data['subdialog'].user_area.Redraw()
        if id == self.ID_MENU_CLEARPICKERIMAGE: # Clear Image
            active_tab_data = self.GetActiveTab()
            active_tab_data['imagepath'] = None
            active_tab_data['subdialog'].user_area.imagepath = None
            active_tab_data['subdialog'].user_area.Redraw()
        if id == self.ID_MENU_PICKERIMAGESETTINGS: # Picker Image Settings
            active_tab_data = self.GetActiveTab()
            picker_image_settings_dialog = PickerImageSettingsDialog(active_tab_data['subdialog'].user_area)
            picker_image_settings_dialog.Open(dlgtype=c4d.DLG_TYPE_MODAL, defaultw=600, defaulth=0)
        if id == self.ID_MENU_PICKERTOLEFT: # Move Picker to Left
            active_tab_data = self.GetActiveTab()
            current_index = self._tabList.index(active_tab_data)
            if current_index > 0:
                self._tabList.insert(current_index - 1, self._tabList.pop(current_index))
                self.DrawTabGroup(active_tab_data)
        if id == self.ID_MENU_PICKERTORIGHT: # Move Picker to Right
            active_tab_data = self.GetActiveTab()
            current_index = self._tabList.index(active_tab_data)
            if current_index < len(self._tabList) - 1:
                self._tabList.insert(current_index + 1, self._tabList.pop(current_index))
                self.DrawTabGroup(active_tab_data)
        # About
        if id == self.ID_MENU_ABOUT:
            newAboutDialog = AboutDialog()
            newAboutDialog.Open(dlgtype=c4d.DLG_TYPE_MODAL, defaultw=450, defaulth=200)

        return True

    def SavePickerData(self, active_tab_data, save_path):
        # 저장할 데이터를 구성
        data_to_save = {
            "tabname": active_tab_data['tabname'],  # 활성화된 탭의 이름만 저장
            "parentobjname_enable": active_tab_data['parentobjname_enable'],
            "parentobjname": active_tab_data['parentobjname'],
            "namespace_enable": active_tab_data['namespace_enable'],
            "namespace": active_tab_data['namespace'],
            # subdialog
            # path
            "pickerimage_path": active_tab_data['subdialog'].user_area.pickerimage_path,
            "pickerimage_x": active_tab_data['subdialog'].user_area.pickerimage_x,
            "pickerimage_y": active_tab_data['subdialog'].user_area.pickerimage_y,
            "pickerimage_scale": active_tab_data['subdialog'].user_area.pickerimage_scale,
            "pickerimage_opacity": active_tab_data['subdialog'].user_area.pickerimage_opacity,
            "buttons": self.CollectButtonsData(active_tab_data['subdialog'])
        }

        # JSON으로 파일에 쓰기 (여러 줄로 저장되도록 indent 옵션 추가)
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            print("Picker saved successfully to", save_path)
            active_tab_data['path'] = save_path  # 경로 업데이트
            active_tab_data['saved'] = True  # 저장 상태 업데이트
        except Exception as e:
            gui.MessageDialog("Failed to save picker:", e)
        self.DrawTabGroup(active_tab_data)

    def CollectButtonsData(self, subDialog):
        """ 지정된 SubDialog의 UserArea에서 버튼 상태를 수집하여 저장 가능한 데이터로 반환합니다. """
        buttons_data = []
        # subDialog의 user_area 안에 있는 버튼 데이터를 순회
        if hasattr(subDialog, 'user_area') and hasattr(subDialog.user_area, 'buttons'):
            for btn in subDialog.user_area.buttons:
                if btn:  # 유효한 버튼인지 확인
                    buttons_data.append({
                        'objname': btn['objname'],
                        'x': btn['x'],
                        'y': btn['y'],
                        'size_x': btn['size_x'],
                        'size_y_enable': btn['size_y_enable'],
                        'size_y': btn['size_y'],
                        'color': [btn['color'].x, btn['color'].y, btn['color'].z],
                        'text': btn['text']
                    })
        return buttons_data

    def SaveScenePickerData(self, doc=None):
        # 현재 활성화된 문서 가져오기
        if doc is None: doc = c4d.documents.GetActiveDocument()
        doc_bc = doc.GetDataInstance()
        doc_bc.RemoveData(PATH_ID)

        doc.SetData(doc_bc)
        # 새로운 BaseContainer 생성
        sub_bc = c4d.BaseContainer()

        for i, tab in enumerate(self._tabList):
            if tab['path'] == "":
                gui.MessageDialog("Please save the all pickers before saving the pickers to the project file.")
                return False

        for i, tab in enumerate(self._tabList):
            if tab['path']:
                sub_bc[1000+i] = tab['path']
        
        # 문서의 BaseContainer에 저장
        doc_bc.SetContainer(PATH_ID, sub_bc)
        doc.SetData(doc_bc)
        return True
    
    def LoadScenePickerData(self, open_path):
        try:
            with open(open_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print("Picker loaded successfully from", open_path)
        except Exception as e:
            print("Failed to load picker:", e)
            return True

        # 만약 _tablist에 있는 탭이 하나이고, tabname이 untitled이고, path가 없다면 해당 탭리스트 요소를 지워줘.
        if len(self._tabList) == 1 and self._tabList[0]['tabname'] == 'Untitled' \
            and self._tabList[0]['path'] is None:
            self._tabList.pop(0)

        new_tab_name = data.get("tabname", "Untitled")
        new_tab_buttons = data.get("buttons", [])
        for btn in new_tab_buttons:
            btn['color'] = c4d.Vector(*btn['color'])
        new_tab_parentobjname_enable = data.get("parentobjname_enable", False)
        new_tab_parentobjname = data.get("parentobjname", "")
        new_tab_namespace_enable = data.get("namespace_enable", False)
        new_tab_namespace = data.get("namespace", "")
        new_tab_pickerimage_path = data.get("pickerimage_path", "")
        new_tab_pickerimage_x = data.get("pickerimage_x", 0)
        new_tab_pickerimage_y = data.get("pickerimage_y", 0)
        new_tab_pickerimage_scale = data.get("pickerimage_scale", 1.0)
        new_tab_pickerimage_opacity = data.get("pickerimage_opacity", 0.5)

        new_tab = MWSubDialog(self)
        new_tab.user_area.buttons = new_tab_buttons
        new_tab.user_area.parentobjname_enable = new_tab_parentobjname_enable
        new_tab.user_area.parentobjname = new_tab_parentobjname
        new_tab.user_area.namespace_enable = new_tab_namespace_enable
        new_tab.user_area.namespace = new_tab_namespace

        new_tab.user_area.pickerimage_path = new_tab_pickerimage_path
        new_tab.user_area.pickerimage_x = new_tab_pickerimage_x
        new_tab.user_area.pickerimage_y = new_tab_pickerimage_y
        new_tab.user_area.pickerimage_scale = new_tab_pickerimage_scale
        new_tab.user_area.pickerimage_opacity = new_tab_pickerimage_opacity

        new_tab.user_area.ChangeButtonObjectNameSpace()
        new_tab.user_area.SetPickerImage()

        self.AppendTab(
                    new_tab_name,
                    new_tab,
                    active=True,
                    path=open_path,
                    saved=True,
                    parentobjname_enable=new_tab_parentobjname_enable,
                    parentobjname=new_tab_parentobjname,
                    namespace_enable=new_tab_namespace_enable,
                    namespace=new_tab_namespace,
                    pickerimage_path=new_tab_pickerimage_path,
                    pickerimage_x=new_tab_pickerimage_x,
                    pickerimage_y=new_tab_pickerimage_y,
                    pickerimage_scale=new_tab_pickerimage_scale,
                    pickerimage_opacity=new_tab_pickerimage_opacity
                    )
        return True

    def CoreMessage(self, id, msg):
        if id == c4d.EVMSG_CHANGE:
            activeDoc = c4d.documents.GetActiveDocument()

            if activeDoc is None: return

            if activeDoc != self.activeDoc: # 문서가 변경되었을 때
                oldDoc = self.activeDoc
                self.activeDoc = activeDoc
                for tab in self._tabList:
                    if tab['saved'] == False:
                        if tab['subdialog'].user_area.buttons == []: # 버튼이 없는 탭은 저장하지 않음
                            continue
                        if tab['path'] == "":
                            result = c4d.gui.MessageDialog(f"Do you want to save the changes to your\n" +
                                    f"picker \"{tab['tabname']}\"\n" +
                                    f"before closing?", c4d.GEMB_YESNO)
                            if result == c4d.GEMB_R_V_YES:
                                self.SavePickerAs()
                        else:
                            result = c4d.gui.MessageDialog(f"Do you want to save the changes to your\n" +
                                    f"picker \"{tab['tabname']}\"\n" +
                                    f"before closing?", c4d.GEMB_YESNO)
                            if result == 0:
                                self.SavePickerData(tab, tab['path'])
                
                #compare olddoc's path data with current tab's path data
                if oldDoc is not None:
                    if oldDoc.GetDataInstance().GetContainerInstance(PATH_ID) is None:
                        oldDoc_path = []
                    else:
                        oldDoc_path = [path for cid, path in oldDoc.GetDataInstance().GetContainerInstance(PATH_ID)]
                    current_path = [tab['path'] for tab in self._tabList]
                    current_path = [path for path in current_path if path != '']
                    # print('olddoc_path:', oldDoc_path)
                    # print('current_path:', [tab['path'] for tab in self._tabList])
                    if oldDoc_path != current_path:
                        result = c4d.gui.MessageDialog(f"Do you want to save picker to your\n" +
                                f"project \"{oldDoc.GetDocumentName()}\"\n" +
                                f"before closing?", c4d.GEMB_YESNO)
                        if result == c4d.GEMB_R_V_YES:
                            self.SaveScenePickerData(doc = oldDoc)

                self._tabList = []
                if self.activeDoc.GetDataInstance().GetContainerInstance(PATH_ID) is not None:
                    for cid, path in self.activeDoc.GetDataInstance().GetContainerInstance(PATH_ID):
                        if path is not None: self.LoadScenePickerData(path)

                # 기본적으로 'Untitled' 탭 추가
                if self._tabList == []:
                    cg1 = MWSubDialog(self)
                    self.AppendTab('Untitled', cg1, active=True, saved=False)
                return True
        return super().CoreMessage(id, msg)

class MWCharacterPickerCommand(plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = MWCharacterPickerDialog()
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID,
                                 xpos= -1, ypos= -1, defaultw=600, defaulth=600)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = MWCharacterPickerDialog()
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

# Main function
if __name__ == "__main__":
    # Registers the plugin
    iconFile=bitmaps.BaseBitmap()
    path, fn = os.path.split(__file__)
    iconFile.InitWith(os.path.join(path,"res","MW Character Picker.tif"))

    plugins.RegisterCommandPlugin(
        id=PLUGIN_ID,
        str="MW Character Picker",
        info=0,
        help="Displays a basic character picker GUI",
        dat=MWCharacterPickerCommand(),
        icon=iconFile
    )

"""
Track Document Change
https://developers.maxon.net/forum/topic/14555/how-to-track-if-the-document-has-changed/2?_=1731375039942

Detect Event Happened
https://developers.maxon.net/forum/topic/14124/how-to-detect-a-new-light-and-pram-change?_=1663922428911

Add Menu Icon
https://developers.maxon.net/forum/topic/12984/adding-an-icon-to-a-gedialog-menu-group/10?_=1731643435864

Add Menu Undocking
https://developers.maxon.net/forum/topic/4079/3610_submenues-dont-show-up-on-undocking/2?_=1731643435878

Cappucino Behavior
https://developers.maxon.net/forum/topic/15625/how-to-simulate-cappucino-behavior?_=1731656238928

QuickTab Radio Buttons
https://developers.maxon.net/forum/topic/12166/quick-tab-radio-for-gedialog/2?_=1731699127885

Enable / Disable Button
https://developers.maxon.net/forum/topic/9878/13303_enable--disable-button/2?_=1731643435926

Open Internet Browser
https://developers.maxon.net/forum/topic/7781/9984_just-a-link-to-a-help-page/5?_=1732184976882
"""
