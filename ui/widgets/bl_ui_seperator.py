import bpy
import gpu
from .bl_ui_widget import BL_UI_Widget
from gpu_extras.batch import batch_for_shader


class BL_UI_Seperator(BL_UI_Widget):
    def __init__(self, *args , **kwargs):
        super().__init__( *args , **kwargs)
        self.className = "Seperator"
        self._line_color  = (0.33, 0.33, 0.33, 1.0)
        
    def is_in_rect(self, x, y):
        return False

    def batch(self):        
        super().batch()

        off_x = 2
        off_y = self.height / 2.0
        sx, sy = (self.width,self.height)

        self.shader_chb = gpu.shader.from_builtin('UNIFORM_COLOR')
        
        inset = 1

        # line top-left, bottom-right | top-right, bottom-left
        vertices_cross = (
            (off_x + inset,      off_y + inset),
            (off_x + sx - inset, off_y + inset),
            (off_x + inset,      off_y),
            (off_x + sx - inset, off_y),
            (off_x + inset,      off_y - inset),
            (off_x + sx - inset, off_y - inset))

        self.batch_cross = batch_for_shader(self.shader_chb, 'LINES', {"pos": vertices_cross})
        
    def draw(self,context):
        if not self.visible:
            return
        # draw background
        super().draw(context)
        # draw la ligne
        self.drawStartShader(self.shader_chb,context)
        self.shader_chb.uniform_float("color", self._line_color)
        self.batch_cross.draw(self.shader_chb)
        self.drawEndShader(self.shader_chb,context) 