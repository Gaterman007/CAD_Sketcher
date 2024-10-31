import blf
import bpy
import gpu
from .bl_ui_widget import BL_UI_Widget
from gpu.state import scissor_set,scissor_get
from mathutils import Vector

class BL_UI_Label(BL_UI_Widget):
    def __init__(self, *args , **kwargs):
        super().__init__( *args , **kwargs)
        self.className = "Label"
        self._text_color = (1.0, 1.0, 1.0, 1.0)

        self._text = kwargs.get("text", args[4] if len(args) > 4 else "Label")
        self._text_size = 16
        self._halign = "LEFT"
        self._valign = "CENTER"
        
        # margin for text label
        self._leftMargin = 0
        self._topMargin = 0
        self._rightMargin = 0
        self._bottomMargin = 0
        
        self.font_id = 1
        self.bg_transparent = False
        self.subtype = None

        
#
# Number
# PIXEL:              Pixel.
# UNSIGNED:           Unsigned.
# PERCENTAGE:         Percentage.
# FACTOR:             Factor.
# ANGLE:              Angle.
# TIME:               Time (Scene Relative).          Time specified in frames, converted to seconds based on scene frame rate.
# TIME_ABSOLUTE:      Time (Absolute).                Time specified in seconds, independent of the scene.
# DISTANCE:           Distance.
# DISTANCE_CAMERA:    Camera Distance.
# POWER:              Power.
# TEMPERATURE:        Temperature.
# WAVELENGTH:         Wavelength.
# NONE:               None.


# String
# FILE_PATH:          File Path.
# DIR_PATH:           Directory Path.
# FILE_NAME:          File Name.
# BYTE_STRING:        Byte String.
# PASSWORD:           Password.           A string that is displayed hidden (********).
# NONE:               None.


# Number Array
# COLOR:              Color.
# TRANSLATION:        Translation.
# DIRECTION:          Direction.
# VELOCITY:           Velocity.
# ACCELERATION:       Acceleration.
# MATRIX:             Matrix.
# EULER:              Euler Angles.
# QUATERNION:         Quaternion.
# AXISANGLE:          Axis-Angle.
# XYZ:                XYZ.
# XYZ_LENGTH:         XYZ Length.
# COLOR_GAMMA:        Color.
# COORDINATES:        Coordinates.
# LAYER:              Layer.
# LAYER_MEMBER:       Layer Member.
# NONE:               None.


#


    def get_length_unit_text(self):
        scene = bpy.context.scene
        unit_system = scene.unit_settings.system  # 'NONE', 'METRIC', 'IMPERIAL'
        scale_length = round(scene.unit_settings.scale_length, 6)  # Échelle des longueurs

        if unit_system == 'METRIC':
            if scale_length == 1.0:
                return " m"  # Mètres
            elif scale_length == 0.01:
                return " cm"  # Centimètres
            elif scale_length == 0.001:
                return " mm"  # Millimètres
        elif unit_system == 'IMPERIAL':
            if scale_length == 0.0254:
                return " inch"  # Pouces
            elif scale_length == 0.3048:
                return " ft"  # Pieds
        return ""

    def set_propinfo(self,prop_info):
        super().set_propinfo(prop_info)
        if self.prop_info is not None:
            if 'precision' in prop_info.keywords:
                self.setPrecision(prop_info.keywords['precision'])
            if 'subtype' in prop_info.keywords:
                self.subtype = prop_info.keywords['subtype']


    def setPrecision(self,presision):
        self.presision = presision
        
    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        if value != self._text_color:
            bpy.context.region.tag_redraw()
        self._text_color = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if value != self._text:
            self._text = value

    @property
    def text_size(self):
        return self._text_size

    @text_size.setter
    def text_size(self, value):
        if value != self._text_size:
            bpy.context.region.tag_redraw()
        self._text_size = value

    @property
    def h_align(self):
        return self._halign

    @h_align.setter
    def h_align(self, value):
        self._halign = value

    @property
    def v_align(self):
        return self._valign

    @v_align.setter
    def v_align(self, value):
        self._valign = value


    def is_in_rect(self, x, y):
        return False
        
    def draw(self,context):
        if not self.visible:
            return
        # draw background
        super().draw(context)

#        if type(self._text) is not str:
#            print("label", self.propName,self._text)

        # draw the text
        if bpy.app.version < (4, 0, 0):
            blf.size(self.font_id, self._text_size, 72)
        else:
            blf.size(self.font_id, self._text_size)

        r, g, b, a = self._text_color
        
        # set left, baseLine offset au parent
        left, baseLine = self.offsetParent(self._x + self._leftMargin,self._y + self._topMargin,True)

        width_text, height_text = blf.dimensions(self.font_id, self._text)

        # set baseLine to bottom
        baseLine += self.height
        
        if self._halign != "LEFT":
            if self._halign == "RIGHT":
                left -= self.width
            elif self._halign == "CENTER":
                left -= self.width // 2
        if self._valign != "BOTTOM":
            if self._valign == "CENTER":
                baseLine -= (self.height - height_text) // 2
            elif self._valign == "TOP":
                # set baseLine back to top + height of text
                baseLine = (baseLine - self.height) + height_text 
           
        # invert for 0 is now top bottom is +
        inverted_y = context.region.height - baseLine

        boxleft, boxtop = self.offsetParent(self._x + self._leftMargin,self._y + self._topMargin,True)
        boxright, boxbottom = self.offsetParent((self._x + self._leftMargin) + (self.width - self._rightMargin) ,(self._y + self._topMargin) + (self.height - self._bottomMargin),True)
        boxtop = context.region.height - boxtop
        
        boxsaved = scissor_get()
       # Définir la zone de clipping
        scissor_set(boxleft, boxtop, self.width, self.height)

        blf.position(self.font_id, left, inverted_y, 0)

        blf.color(self.font_id, r, g, b, a)

        if self.unit is None:
            blf.draw(self.font_id, self._text)
        else:
            if self.unit == "LENGTH":
                blf.draw(self.font_id, self._text + self.get_length_unit_text())
            elif self.unit == "ROTATION":
                blf.draw(self.font_id, self._text + "\u00B0 Degré")
            else:
                blf.draw(self.font_id, self._text)

        # Désactiver le scissoring
        scissor_set(boxsaved[0],boxsaved[1],boxsaved[2],boxsaved[3])