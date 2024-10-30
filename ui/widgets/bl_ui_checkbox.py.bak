from . bl_ui_label import BL_UI_Label
from . bl_ui_widget import BL_UI_Widget

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

class BL_UI_Checkbox(BL_UI_Label):
    
    def __init__(self, *args , **kwargs):
        super().__init__( *args , **kwargs)
        self._text = kwargs.get("text", args[4] if len(args) > 4 else "Visible")
        self.className = "Checkbox"
        self._box_color         = (1.0, 1.0, 1.0, 1.0)
        self._cross_color       = (0.2, 0.9, 0.9, 1.0)
        self.__state = False
        self.bg_transparent = True
#        self.bg_color = (1.0, 0.0, 1.0, 1.0)
        self._leftMargin = 30
    
    def set_propinfo(self,prop_info):
        super().set_propinfo(prop_info)
        if self.prop_info is not None:
            if 'name' in prop_info.keywords:
                self.text = prop_info.keywords['name']
        if self.attr is not None:
            self.checked = getattr(self.element,self.attr)

    def setParent(self, parent):
        super().setParent(parent)

    @property
    def cross_color(self):
        return self._cross_color

    @cross_color.setter
    def cross_color(self, value):
        self._cross_color = value

    @property
    def checked(self):
        return self.__state

    @checked.setter
    def checked(self, value):
        if value != self.__state:
            self.__state = value
            if self.attr is not None:
                setattr(self.element,self.attr,self.checked) 
            bpy.context.region.tag_redraw()
 
    def batch(self):        
        super().batch()

        off_x = 2
        off_y = 2
        sx, sy = (16,16)

        self.shader_chb = gpu.shader.from_builtin('UNIFORM_COLOR')
        
        # top left, top right, ...
        vertices_box = (
                    (off_x,      off_y + sy), 
                    (off_x + sx, off_y + sy), 
                    (off_x + sx, off_y),
                    (off_x,      off_y))

        self.batch_box = batch_for_shader(self.shader_chb, 'LINE_LOOP', {"pos": vertices_box})

        inset = 4

        # cross top-left, bottom-right | top-right, bottom-left
        vertices_cross = (
            (off_x + inset,      off_y +  inset), 
            (off_x + sx - inset, off_y + sy - inset),
            (off_x + sx - inset, off_y + inset), 
            (off_x + inset,      off_y + sy - inset))

        self.batch_cross = batch_for_shader(self.shader_chb, 'LINES', {"pos": vertices_cross})

   
    def draw(self,context):
        if not self.visible:
            return
        if self.updater is not None:
            self.updater(self.element,context)
        # draw le text
        super().draw(context)
        # draw le checkbox
        self.drawStartShader(self.shader_chb,context)
        self.shader_chb.uniform_float("color", self._box_color)
        self.batch_box.draw(self.shader_chb) 
        if self.checked:
            self.shader_chb.uniform_float("color", self._cross_color)
            self.batch_cross.draw(self.shader_chb)
        self.drawEndShader(self.shader_chb,context)  
         
    def toggle_state(self):
        self.checked = not self.checked
        bpy.context.region.tag_redraw()

    def is_in_rect(self, x, y):
        return BL_UI_Widget.is_in_rect(self,x, y)

    def mouse_down(self, x, y):
        if self.is_in_rect(x,y):
            return ({"RUNNING_MODAL"},True)

        return ({"RUNNING_MODAL"},False)

    def mouse_up(self, x, y):
        if self.is_in_rect(x,y):
            self.toggle_state()
            return ({"RUNNING_MODAL"},True)

        return ({"RUNNING_MODAL"},False)