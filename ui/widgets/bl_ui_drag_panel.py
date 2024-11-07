from . bl_ui_widget import * 

class BL_UI_Drag_Panel(BL_UI_Widget):
    
    def __init__(self, *args , **kwargs):
        super().__init__( *args , **kwargs)
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.downPos = [0,0]
        self.is_drag = False
        self.className = "drag Panel"

    def get_location(self):
        return [self._x + self.drag_offset_x,self._y + self.drag_offset_y]

    def mouse_down(self, x, y, context):
        if self.is_in_rect(x,y):
            self.is_drag = True
            self.downPos = [x,y]
            return ({"RUNNING_MODAL"},True)
        
        return ({"PASS_THROUGH"},False)
        

    def mouse_move(self, x, y, context):
        if self.is_drag:
            self.drag_offset_x = x - self.downPos[0]
            self.drag_offset_y = y - self.downPos[1]
            bpy.context.region.tag_redraw()
        return ({"RUNNING_MODAL"},False)
        
    def mouse_up(self, x, y, context):
        if self.is_drag:
            self.is_drag = False
            self.set_location(self._x + self.drag_offset_x,self._y + self.drag_offset_y)
            self.drag_offset_x = 0
            self.drag_offset_y = 0
            bpy.context.region.tag_redraw()
        if self.is_in_rect(x,y):
            return ({"RUNNING_MODAL"},False)
        else:
            return ({"PASS_THROUGH"},False)
