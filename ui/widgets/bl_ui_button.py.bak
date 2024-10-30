import bpy
import gpu

from .bl_ui_widget import BL_UI_Widget
from .bl_ui_label import BL_UI_Label


class BL_UI_Button(BL_UI_Label):
    STATE_NORMAL = 0
    STATE_PRESSED = 1
    STATE_HOVER = 2

    def __init__(self, *args , **kwargs):
        """
        Initialisation du bouton avec position, dimensions et texte.
        """
        super().__init__( *args , **kwargs)
        self._text = kwargs.get("text", args[4] if len(args) > 4 else "button")
        self.className = "Button"
        self._text_color = (1.0, 1.0, 1.0, 1.0)  # Couleur du texte
        self._hover_bg_color = (0.5, 0.5, 0.5, 1.0)  # Couleur arrière-plan au survol
        self._select_bg_color = (0.7, 0.7, 0.7, 1.0)  # Couleur arrière-plan à la sélection
        self._setState(self.STATE_NORMAL)
        
        self.__opClass = None  # Classe d'opérateur pour l'appel dynamique
        self.index = None  # Paramètre d'index pour l'opérateur
        self.type = None  # Paramètre de type pour l'opérateur


        self._clicFunct = None  # Fonction callback pour clic
        self._FunctData = None  # Données pour la fonction callback        
      
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

    def setMouseClicCallBack(self, funct, data):
        """
        Définit une fonction callback pour l'événement de clic.
        :param funct: Fonction callback à appeler.
        :param data: Données à passer à la fonction callback.
        """
        self._clicFunct = funct
        self._FunctData = data

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

    def setMouseClicCallBack(self,funct,data):
        self._clicFunct = funct
        self._FunctData = data

    def is_in_rect(self, x, y):
        return BL_UI_Widget.is_in_rect(self,x, y)

    def mouse_down(self, x, y):
        """
        Gère l'événement de clic de souris.
        :param x: Position x de la souris.
        :param y: Position y de la souris.
        """
        if self.is_in_rect(x, y):
            self._setState(self.STATE_PRESSED)
            return {"RUNNING_MODAL"}, True
        return {"RUNNING_MODAL"}, False

    def mouse_move(self, x, y):
        """
        Gère l'événement de mouvement de souris.
        :param x: Position x de la souris.
        :param y: Position y de la souris.
        """
        if self.is_in_rect(x, y):
            if self.__state != self.STATE_PRESSED:
                self._setState(self.STATE_HOVER)
        else:
            self._setState(self.STATE_NORMAL)
        return {"RUNNING_MODAL"}, False

    def mouse_up(self, x, y):
        """
        Gère l'événement de relâchement de la souris.
        :param x: Position x de la souris.
        :param y: Position y de la souris.
        """
        result = ({"RUNNING_MODAL"},False)
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
                if self._clicFunct is not None:
                    result = self._clicFunct(self._FunctData)
            self._setState(self.STATE_HOVER)
        else:
            self._setState(self.STATE_NORMAL)
        return result