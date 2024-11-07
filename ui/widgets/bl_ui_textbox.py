import blf
import bpy
import functools
from gpu_extras.batch import batch_for_shader

from .bl_ui_widget import BL_UI_Widget
from .bl_ui_label import BL_UI_Label
from mathutils import Vector

def in_5_seconds(textbox):
    # force redraw of the view to display or hide caret
    if not textbox.timerOn:
        textbox.caret_visible = False
        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return None
    else:
        textbox.caret_visible = not textbox.caret_visible
        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    return BL_UI_Textbox.blinkTime

        
class BL_UI_Textbox(BL_UI_Label):

    blinkTime = 0.3
    def __init__(self, *args , **kwargs):
        super().__init__( *args , **kwargs)
        self._text = kwargs.get("text", args[4] if len(args) > 4 else "TextBox")
        self.className = "TextBox"
        self._carret_color = (0.0, 0.2, 1.0, 1.0)
        self._offset_letters = 0
        self._carret_pos = 0
        self.max_input_chars = 200
        self.update_carret()
#        self._input_keys = ['ESC', 'RET', 'BACK_SPACE', 'HOME', 'END', 'LEFT_ARROW', 'RIGHT_ARROW', 'DEL']
        self.caret_visible = False
        self.timerOn = False
        self.drag = False
        self.mousePressed = False
        self.step = 3
        self.increment = 100.0
        self.variable = None
        
    def set_propinfo(self,prop_info):
        super().set_propinfo(prop_info)
        if 'step' in prop_info.keywords:
            self.setStep(getattr(self.element,"step"))
        self._text = self.attributText
        
    def setStep(self,value):
        self.step = value
        self.increment = 1.0
        for i in range(self.step - 1):
            self.increment *= 10.0
        
    def lostFocus(self):
        super().lostFocus()
        self.endCaretTime()

    def setParent(self, parent):
        super().setParent(parent)
        self.update_carret()

    def get_carret_pos_px(self):
        size_all = blf.dimensions(self.font_id, self.text)
        size_to_carret = blf.dimensions(self.font_id, self.text[:self._carret_pos])
        return self._x + (self.width / 2.0) - (size_all[0] / 2.0) + size_to_carret[0]

    def update_carret(self):

        x = self.get_carret_pos_px()

        size_to_carret = blf.dimensions(self.font_id, self.text[:self._carret_pos])
        textsize = blf.dimensions(self.font_id, "WWWW")

        x = self._x + size_to_carret[0] + self._leftMargin
        
        x, y = self.offsetParent(x,self._y,True)
        y = bpy.context.region.height - y
        # bottom left, top left, top right, bottom right
        vertices = (
            (x, y),
            (x, y - self.height),
            (x+1, y),
            (x+1, y - self.height)
        )

        self.batch_carret = batch_for_shader(
            self._shaderBackground, 'LINES', {"pos": vertices})

    def draw(self,context):

        if not self.visible:
            return
        # update la valeur du text au cas qu il a changer
        if self.hasProp:
            self._text = self.attributText

        super().draw(context)
    
        if self.caret_visible:
            self.update_carret()
            self._shaderBackground.bind()
            self._shaderBackground.uniform_float("color", self._carret_color)
            self.batch_carret.draw(self._shaderBackground)
            

    def text_input(self, event, context):

        if self.hasFocus:
            text_Changed = False
            index = self._carret_pos
            # Vérifie les combinaisons de copier/couper/coller
            if (event.ctrl or event.oskey) and event.type == 'C':  # Copier
                bpy.context.window_manager.clipboard = self.text
                return ({"RUNNING_MODAL"}, False)
            elif (event.ctrl or event.oskey) and event.type == 'X':  # Couper
                bpy.context.window_manager.clipboard = self.text
                self.text = ""
                self._carret_pos = 0
                text_Changed = True
            elif (event.ctrl or event.oskey) and event.type == 'V':  # Coller
                paste_text = bpy.context.window_manager.clipboard
                self.text = paste_text
                self._carret_pos = 0
                text_Changed = True
            elif event.ascii != '' and len(self.text) < self.max_input_chars:
                textvalue = self.text[:index] + event.ascii + self.text[index:]
                if self._is_numeric and not (event.ascii.isnumeric() or event.ascii in ['.', ',', '-']):
                    return ({"RUNNING_MODAL"},False)
                self.text = textvalue
                self._carret_pos += 1
                text_Changed = True
            elif event.type == 'BACK_SPACE':
                if event.ctrl:
                    self.text = ""
                    self._carret_pos = 0
                elif self._carret_pos > 0:
                    self.text = self.text[:index-1] + self.text[index:]
                    self._carret_pos -= 1
                text_Changed = True
            elif event.type == 'DEL':
                if self._carret_pos < len(self.text):
                    self.text = self.text[:index] + self.text[index+1:]
                    text_Changed = True

            elif event.type == 'LEFT_ARROW':
                if self._carret_pos > 0:
                    self._carret_pos -= 1

            elif event.type == 'RIGHT_ARROW':
                if self._carret_pos < len(self.text):
                    self._carret_pos += 1

            elif event.type == 'HOME':
                self._carret_pos = 0

            elif event.type == 'END':
                self._carret_pos = len(self.text)
            if text_Changed and self.element is not None:
                if self.hasProp:
                    self.attributText = self.text              
                    self.text = self.attributText
            self.update_carret()
                
            bpy.context.region.tag_redraw()
            return ({"RUNNING_MODAL"},True)
        return ({"RUNNING_MODAL"},False)

    def is_in_rect(self, x, y):
        return BL_UI_Widget.is_in_rect(self,x, y)

    def mouse_down(self, x, y, context):
        if self.is_in_rect(x, y):
            self.downPos = [x,y]
            self.mousePressed = True
            self.drag = False
            return ({"RUNNING_MODAL"},True)
        else:
            return ({"RUNNING_MODAL"},False)

    def mouse_move(self, x, y, context):
        if self.mousePressed:
            if self.drag:
#                if self.attrName is not None:
                if self.hasProp:
                    print(self.saveData)
                    value = self.saveData - (float(self.downPos[0] - x) / self.increment)
                    print(value)
                    print()
                    self.attribut = value
                    self.text = self.attributText
                return ({"RUNNING_MODAL"},True)
            else:
                if self._is_numeric:
                    if self.hasProp:
                        if abs(self.downPos[0] - x) > 5 or abs(self.downPos[1] - y) > 5:
                            self.saveData = self.attribut
                            self.drag = True
                return ({"RUNNING_MODAL"},True)
        return ({"RUNNING_MODAL"},False)

    def mouse_up(self, x, y, context):
        if self.drag:
            self.drag = False
            self.mousePressed = False
            bpy.context.region.tag_redraw()
            return ({"RUNNING_MODAL"},True)
        elif self.mousePressed:
            self.mousePressed = False
            if self.is_in_rect(x, y):
                if not self.hasFocus:
                    self.setFocus(self)
                    self.startCaretTime()
                self.setCaretPos(x,y)
                return ({"RUNNING_MODAL"},True)
        return ({"RUNNING_MODAL"},False)

    def setCaretPos(self,x,y):
        new_carretPos = 0
        xMousePos = (x - self._leftMargin)
        if xMousePos < 0:
            xMousePos = 0
        size_to_carret = blf.dimensions(self.font_id, self.text[:new_carretPos])
        while size_to_carret[0] <= xMousePos and new_carretPos < len(self.text) + 1:
            new_carretPos += 1
            size_to_carret = blf.dimensions(self.font_id, self.text[:new_carretPos])
        self._carret_pos = new_carretPos - 1

    def startCaretTime(self):
        if not self.timerOn:
            self.timerOn = True
            if not bpy.app.timers.is_registered(in_5_seconds):
                bpy.app.timers.register(functools.partial(in_5_seconds, self), first_interval=BL_UI_Textbox.blinkTime, persistent=True)

    def endCaretTime(self):
        if self.timerOn:
            self.timerOn = False
