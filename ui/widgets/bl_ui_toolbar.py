import bpy
import gpu
import os

from .bl_ui_widget import BL_UI_Widget
from .bl_ui_image import BL_UI_Image
from .Icons.Texture import Textures
from ...declarations import Operators

class BL_UI_Toolbar(BL_UI_Image):
    STATE_NORMAL = 0
    STATE_PRESSED = 1
    STATE_HOVER = 2

    def __init__(self, *args , **kwargs):
        """
        Initialisation du bouton avec position, dimensions et texte.
        """
        super().__init__( *args , **kwargs)
        self.className = "Toolbar"
        self._text_color = (1.0, 1.0, 1.0, 1.0)  # Couleur du texte
        self._hover_bg_color = (0.5, 0.5, 0.5, 1.0)  # Couleur arrière-plan au survol
        self._select_bg_color = (0.7, 0.7, 0.7, 1.0)  # Couleur arrière-plan à la sélection
        self._setState(self.STATE_NORMAL)
        
        self.__opClass = None  # Classe d'opérateur pour l'appel dynamique
        self.index = None  # Paramètre d'index pour l'opérateur
        self.type = None  # Paramètre de type pour l'opérateur

        self.nbDeBouton = 0
        self._clicFunct = []  # Fonction callback pour clic
        self._FunctData = []  # Données pour la fonction callback        
        self._imageNames = []
        self.textures = []
        self.buttonWidth = kwargs.get("buttonWidth", self.height)
        self.buttonHeight = kwargs.get("buttonHeight", self.height)
        self.maintexture = None

    def _setState(self,state):
        self.__state = state
      
    @property
    def hover_bg_color(self):
        """Retourne la couleur d'arrière-plan au survol."""
        return self._hover_bg_color

    @hover_bg_color.setter
    def hover_bg_color(self, value):
        """Définit la couleur d'arrière-plan au survol et redessine si nécessaire."""
        if value != self._hover_bg_color:
            bpy.context.region.tag_redraw()  # Redessiner la région
        self._hover_bg_color = value

    @property
    def select_bg_color(self):
        """Retourne la couleur d'arrière-plan à la sélection."""
        return self._select_bg_color

    @select_bg_color.setter
    def select_bg_color(self, value):
        """Définit la couleur d'arrière-plan à la sélection et redessine si nécessaire."""
        if value != self._select_bg_color:
            bpy.context.region.tag_redraw()  # Redessiner la région
        self._select_bg_color = value

    def setOpClass(self, opClass, index, type):
        """
        Définit la classe d'opérateur à appeler lors du clic.
        Définit l'index à passer à l'opérateur lors du clic.
        Définit le type à passer à l'opérateur lors du clic.
        :param opClass: String sous la forme "module.operateur".
        """
        self.__opClass = opClass
        self.index = index
        self.type = type

    def addButton(self,imageName,funct,data):
        self._imageNames.append(imageName)
        self._clicFunct.append(funct)
        self._FunctData.append(data)
        self.textures.append(Textures(self.buttonWidth - 2, self.buttonHeight - 2))
        self.nbDeBouton = self.nbDeBouton + 1
        svg_filepath = os.path.join(BL_UI_Image.svg_path, imageName + '.svg')
        self.textures[self.nbDeBouton - 1].load_SVG(svg_filepath)
        if self.maintexture is None:
            self.maintexture = Textures(self.buttonWidth, self.buttonHeight)
        else:
            self.maintexture.resize(self.buttonWidth * self.nbDeBouton + 1, self.buttonHeight)
        self.maintexture.bitblt(self.textures[self.nbDeBouton - 1], ((self.nbDeBouton - 1) * self.buttonWidth) + 1, 1, self.buttonWidth - 2, self.buttonHeight - 2)
        self.maintexture.update_texture()
        self.set_image_size((self.buttonWidth * self.nbDeBouton,self.buttonHeight))
        self.width = self.nbDeBouton * self.buttonWidth
        self.height = self.buttonHeight        

    def setMouseClicCallBack(self,buttonNo, funct, data):
        """
        Définit une fonction callback pour l'événement de clic.
        :param funct: Fonction callback à appeler.
        :param data: Données à passer à la fonction callback.
        """
        self._clicFunct[buttonNo] = funct
        self._FunctData[buttonNo] = data

    def set_colors(self):
        """
        Définit la couleur d'arrière-plan en fonction de l'état actuel (survol, sélection, normal).
        """
        if self.__state == self.STATE_PRESSED:
            color = self._select_bg_color
        elif self.__state == self.STATE_HOVER:
            color = self._hover_bg_color
        else:
            color = self._bg_color
        self.shader.uniform_float("color", color)

    def is_in_rect(self, x, y):
        return BL_UI_Widget.is_in_rect(self,x, y)

    def onButtonNo(self, x, y):
        buttonNo = None
        if self.is_in_rect(x, y):
            buttonNo = (x - self._x) // self.buttonWidth
        return buttonNo

    def draw(self,context):
        if not self._is_visible:
            return
        if (self.nbDeBouton > 0):
            if self.textures[self.nbDeBouton - 1] is not None:
                # draw image
                gpu.state.blend_set("ALPHA")
                self.drawStartShader(self.shader_img,context)
                self.maintexture.draw_texture(self.shader_img)
                self.batch_image.draw(self.shader_img) 
                self.drawEndShader(self.shader_img,context) 
                gpu.state.blend_set("NONE")
            
    def mouse_down(self, x, y, context):
        """
        Gère l'événement de clic de souris.
        :param x: Position x de la souris.
        :param y: Position y de la souris.
        """

        if self.is_in_rect(x, y):
            buttonNo = self.onButtonNo(x,y)
            self._setState(self.STATE_PRESSED)
            return {"RUNNING_MODAL"}, True
#        return {"RUNNING_MODAL"}, False
        return {"PASS_THROUGH"},False

    def mouse_move(self, x, y, context):
        """
        Gère l'événement de mouvement de souris.
        :param x: Position x de la souris.
        :param y: Position y de la souris.
        """
        buttonNo = self.onButtonNo(x,y)
        if self.is_in_rect(x, y):
            if self.__state != self.STATE_PRESSED:
                self._setState(self.STATE_HOVER)
        else:
            self._setState(self.STATE_NORMAL)
        return {"RUNNING_MODAL"}, False

    def mouse_up(self, x, y, context):
        """
        Gère l'événement de relâchement de la souris.
        :param x: Position x de la souris.
        :param y: Position y de la souris.
        """
        result = ({"RUNNING_MODAL"},False)
        buttonNo = self.onButtonNo(x,y)
        if self.is_in_rect(x, y) and self.__state == self.STATE_PRESSED:
            if self.__opClass is not None:
                family, operator = self.__opClass.split(".")
                try:
                    # Appeler l'opérateur en utilisant `bpy.ops` dynamiquement
                    if self.type is not None:
                        resDelete = getattr(bpy.ops, family).__getattr__(operator)(type = self.type,index= self.index)
                    else:
                        resDelete = getattr(bpy.ops, family).__getattr__(operator)(index= self.index)
                    result = (resDelete,True)
                except AttributeError as e:
                    print(f"Erreur d'appel d'opérateur: {e}")                    
            else:
                if len(self._clicFunct) > 0 and buttonNo is not None:
                    if self._clicFunct[buttonNo] is not None:
                        family, operator = self._clicFunct[buttonNo].split(".")
                        data = self._FunctData[buttonNo]
                        invoke_type = data[0]  # Argument positionnel
                        named_args = dict(data[1:])  # Arguments nommés en dictionnaire
                        resDelete = getattr(bpy.ops, family).__getattr__(operator)(invoke_type, **named_args)
                        result = (resDelete,True)
            self._setState(self.STATE_HOVER)
        else:
            self._setState(self.STATE_NORMAL)
            return {"PASS_THROUGH"},False

        return result