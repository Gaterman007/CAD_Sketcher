import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from gpu.matrix import get_projection_matrix, get_model_view_matrix
import mathutils
import math

from bpy.types import Operator, Context, Event, PropertyGroup

class BL_UI_Widget:
    def __init__(self, *args , **kwargs):
        self.className = "Widget"
        self._parent = None
        self.childs = []
        self._is_visible = True
        self._is_active = True  # if the widget needs to be disabled
        x = kwargs.get("x", args[0] if len(args) > 0 else None)
        y = kwargs.get("y", args[1] if len(args) > 1 else None)
        self._width = kwargs.get("width", args[2] if len(args) > 2 else None)
        self._height = kwargs.get("height", args[3] if len(args) > 3 else None)
        
        # Traiter d'autres paramètres optionnels (si existants)
        self.other_params = args[4:]  # Restant des arguments positionnels
        self.other_named_params = {k: v for k, v in kwargs.items() if k not in {"x", "y", "width", "height"}}
        self.set_location(x, y) # parent needs to be defined
        self._bg_color = (0.0, 0.0, 0.0, 1.0)
        self.bg_transparent = False

        self._tag = None
        self.__inrect = False
        self._mouse_down = False
        self._mouse_down_right = False
        self.batch()            # can be called once no need to change onless we change de shape
        self.childWithFocus = None
        self.hasFocus = False
        self._input_keys = ["BACK_SPACE",'SPACE','RET','LEFT_ARROW','RIGHT_ARROW','UP_ARROW','DOWN_ARROW','DEL']



        self.element = None
        self.getter = None
        self.setter = None
        self.updater = None
        self.prop_info = None
        self.attr = None
        self._attribut = None
        self.attrIndex = None
        self._is_numeric = False

    def setProperty(self,*args):
        if len(args) == 2 or len(args) == 3:
            self.attrIndex = None
            if len(args) == 3:
                self.attrIndex = args[2]
            self.setPropetyElement(args[0])
            self.set_propinfo(args[1])

    def setPropetyElement(self,element):
        self.element = element
        
    def setSetter(self,setter):
        self.setter = setter
        
    def setGetter(self,getter):
        self.getter = getter
        if self.getter is not None and self.element is not None:
            resultat = self.getter(self.element)

    def setUpdater(self,updater):
        self.updater = updater

    def set_propinfo(self,prop_info):
        if hasattr(prop_info,"keywords"):
            self.prop_info = prop_info
            if 'attr' in prop_info.keywords:
                self.attr = prop_info.keywords['attr']
#                self.attribut = getattr(self.element,self.attr)
            if 'get' in prop_info.keywords:
                if callable(prop_info.keywords['get']):
                    # Récupérer la fonction getter
                    self.setGetter(prop_info.keywords['get'])
            if 'set' in prop_info.keywords:
                if callable(prop_info.keywords['set']):
                    # Récupérer la fonction setter
                    self.setSetter(prop_info.keywords['set'])
            if 'update' in prop_info.keywords:
                if callable(prop_info.keywords['update']):
                    # Récupérer la fonction updater
                    self.setUpdater(prop_info.keywords['update'])
        
    def setFocus(self, widgetFocus):
        parent = widgetFocus.getParent()
        # aller chercher le premier parent
        while parent.getParent() is not None:
            parent = parent.getParent()
        # enlever le focus si deja sur un autre
        if parent.childWithFocus is not None:
            parent.childWithFocus.lostFocus()
        parent.childWithFocus = widgetFocus
        self.hasFocus = True

    def lostFocus(self):
        self.hasFocus = False
        
    def set_location(self, x, y):
        self._x = x
        self._y = y

    def get_location(self):
        return [self._x,self._y]
    
    def getTranslationMatrix(self,inMatrix):
        new_x,new_y = self.get_location()
        new_x,new_y = self.offsetParent(new_x,new_y,True)
        outMatrix = inMatrix @ mathutils.Matrix.Translation((new_x, new_y, 0.0))
        return outMatrix
    
    def setParent(self, parent):
        self._parent = parent
        if self.bg_transparent:
            self.bg_color = parent.bg_color    

    def getParent(self):
        return self._parent

    def add_widget(self, widget):
        widget.setParent(self)
        self.childs.append(widget)
        
    def add_widgets(self, childs):
        for widget in childs:
            widget.setParent(self)
        self.childs = childs

    @property
    def attribut(self):
        if self.getter is not None:
            self._attribut = self.getter(self.element)
        elif self.attr is not None:
            self._attribut = getattr(self.element,self.attr)
        if self.attrIndex is not None:
            if self.unit == "ROTATION":
                self._attribut[self.attrIndex] = math.degrees(self._attribut[self.attrIndex]) 
            if type(self._attribut[self.attrIndex]) is float:
                self._is_numeric = True
            return self._attribut[self.attrIndex]
        else:
            if self.unit == "ROTATION":
                self._attribut = math.degrees(self._attribut)
            if type(self._attribut) is float:
                self._is_numeric = True
            return self._attribut
            
            
    @attribut.setter
    def attribut(self, value):
        valdiff = False
        if self.attrIndex is not None:
            valdiff = (value != self._attribut[self.attrIndex])
        else:
            valdiff = (value != self._attribut)
        if valdiff:
            if self.unit == "ROTATION":
                value = math.radians(value)
            if self.attrIndex is not None:
                self._attribut[self.attrIndex] = value
            else:
                self._attribut = value
            if self.setter is not None:
                self.setter(self.element,self._attribut)
            elif self.attr is not None:
                setattr(self.element,self.attr,self._attribut)

    @property
    def attributText(self):
        value = self.attribut
        if type(value) is float:
            return f"{value:.{self.presision}f}"
        elif type(value) is int:
            return f"{value}"
        elif type(value) is str:
            return value
        return value

    @attributText.setter
    def attributText(self, value):
        if type(self.attribut) is float:
            self.attribut = float(value)
        elif type(self.attribut) is int:
            self.attribut = int(value)
        elif type(self.attribut) is str:
            self.attribut = str(value)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value != self._width:
            self._width = value
            self.batch()
            bpy.context.region.tag_redraw()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value != self._height:
            self._height = value
            self.batch()
            bpy.context.region.tag_redraw()

    @property
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, value):
        if value != self._bg_color:
            bpy.context.region.tag_redraw()
        self._bg_color = value

    @property
    def visible(self):
        retValue = self._is_visible
        if retValue:
            parent = self._parent
            while parent is not None:
                if not parent.visible:
                    retValue = False
                    parent = None
                else:
                    parent = parent.getParent()
        return self._is_visible

    @visible.setter
    def visible(self, value):
        if value != self._is_visible:
            bpy.context.region.tag_redraw()
        self._is_visible = value

    @property
    def active(self):
        return self._is_active

    @visible.setter
    def active(self, value):
        if value != self._is_active:
            bpy.context.region.tag_redraw()
        self._is_active = value

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    def apply_flip_y(self,view_height):
        # Créer une matrice d'inversion pour l'axe Y
        flip_y_matrix = mathutils.Matrix.Identity(4)  # Matrice identitaire 4x4
        flip_y_matrix[1][1] = -1  # Inverser l'axe Y

        # Créer une matrice de translation pour décaler l'origine
        translate_matrix = mathutils.Matrix.Translation((0, -view_height, 0))

        # Combiner les deux matrices : d'abord translation, puis inversion
        return flip_y_matrix @ translate_matrix


    def drawStartShader(self, shader, context):
        shader.bind()
        view_matrix = get_model_view_matrix()
        new_matrix = self.getTranslationMatrix(view_matrix)
        inverted_y_matrix = self.apply_flip_y(context.region.height)

        # Appliquer l'inversion Y
        final_matrix = inverted_y_matrix @ new_matrix
        gpu.matrix.push()
        gpu.matrix.load_matrix(final_matrix)

    def drawEndShader(self,shader,context):
        gpu.matrix.pop()
    
    
    def drawBackground(self,context):
        self.drawStartShader(self._shaderBackground,context)
        self._shaderBackground.uniform_float("color", self._bg_color)
        self.batch_panel.draw(self._shaderBackground)
        self.drawEndShader(self._shaderBackground,context)
            
    def draw(self, context):
        if not self._is_visible:
            return
        self.drawBackground(context)
        for widget in self.childs:
            widget.draw(context)   

    def batch(self):
        indices = ((0, 1, 2), (0, 2, 3))

        # bottom left, top left, top right, bottom right
        vertices = (
            (0, 0),
            (0, self.height),
            (self.width, self.height),
            (self.width, 0),
        )

        if bpy.app.version < (4, 0, 0):
            self._shaderBackground = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
        else:
            self._shaderBackground = gpu.shader.from_builtin("UNIFORM_COLOR")

        self.batch_panel = batch_for_shader(
            self._shaderBackground, "TRIS", {"pos": vertices}, indices=indices
        )
        bpy.context.region.tag_redraw()


    def offsetParent(self, x, y, add = False):
        parent = self.getParent()
        retx = x
        rety = y
        while parent is not None:
            parentX,parentY = parent.get_location()
            if add:
                retx += parentX
                rety += parentY
            else:
                retx -= parentX
                rety -= parentY
            parent = parent.getParent()
        return [retx,rety]

    def handle_event(self,context: Context, event: Event):
        """
        returns True if the event was handled by the widget
        # 'handled_pass', if the event was handled but the event should be passed to other widgets
        False if the event was not handled by the widget
        """

        retValue = ({"RUNNING_MODAL"},False)

        if not self._is_visible:
            return retValue
        if not self._is_active:
            return retValue

        for widget in self.childs:
            result, handled = widget.handle_event(context,event)
            if handled:
                return (result, handled)


        x = event.mouse_region_x
        y = event.mouse_region_y
        
        inverted_y = context.region.height - y  
        
        # bring back mouse position to widget position
        x , y = self.offsetParent(x,inverted_y)

        if event.type == "LEFTMOUSE":
            bpy.context.region.tag_redraw()
            if event.value == "PRESS":
                self._mouse_down = True
                return self.mouse_down(x, y)
            else:
                self._mouse_down = False
                return self.mouse_up(x, y)

        elif event.type == "RIGHTMOUSE":
            bpy.context.region.tag_redraw()
            if event.value == "PRESS":
                self._mouse_down_right = True
                return self.mouse_down_right(x, y)
            else:
                self._mouse_down_right = False
                return self.mouse_up(x, y)

        elif event.type == "MOUSEMOVE":
            self.mouse_move(x, y)
            inrect = self.is_in_rect(x, y)

            # we enter the rect
            if not self.__inrect and inrect:
                self.__inrect = True
                self.mouse_enter(event, x, y)
                # we tag redraw since the hover colors are picked in the draw function
                bpy.context.region.tag_redraw()

            # we are leaving the rect
            elif self.__inrect and not inrect:
                self.__inrect = False
                self.mouse_exit(event, x, y)
                bpy.context.region.tag_redraw()

            # return always false to enable mouse exit events on other buttons.(would sometimes not hide the tooltip)
            return ({"RUNNING_MODAL"},False) # self.__inrect

        elif (
            event.value == "PRESS"
#            and self.__inrect
            and (event.ascii != "" or event.type in self.get_input_keys())
        ):
            return self.text_input(event)

        return ({"RUNNING_MODAL"},False)

    def get_input_keys(self):
        return self._input_keys

    def is_in_rect(self, x, y):
        if (self._x <= x <= (self._x + self.width)) and (
            self._y <= y <= (self._y + self.height)
        ):
            return True

        return False

    def text_input(self, event):
        return ({"RUNNING_MODAL"},False)

    def mouse_down(self, x, y):
        return ({"RUNNING_MODAL"},False)

    def mouse_down_right(self, x, y):
        return ({"RUNNING_MODAL"},False)

    def mouse_up(self, x, y):
        return ({"RUNNING_MODAL"},False)

    def mouse_enter_func(self, widget):
        pass

    def mouse_exit_func(self, widget):
        pass

    def set_mouse_enter(self, mouse_enter_func):
        self.mouse_enter_func = mouse_enter_func

    def call_mouse_enter(self):
        if self.mouse_enter_func:
            self.mouse_enter_func(self)

    def mouse_enter(self, event, x, y):
        self.call_mouse_enter()

    def set_mouse_exit(self, mouse_exit_func):
        self.mouse_exit_func = mouse_exit_func

    def call_mouse_exit(self):
        if self.mouse_exit_func:
            self.mouse_exit_func(self)

    def mouse_exit(self, event, x, y):
        self.call_mouse_exit()

    def mouse_move(self, x, y):
        return {"RUNNING_MODAL"}
