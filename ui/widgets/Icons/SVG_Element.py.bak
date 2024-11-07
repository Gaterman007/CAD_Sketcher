import bpy
import json
from .Matrices import Matrices

class base_Element:
    attributes_to_get = {
        "id": str,
        "opacity": float,
        "stroke": str,
        "stroke-linecap": str,
        "stroke-linejoin": str,
        "stroke-miterlimit": float,
        "stroke-width": float,
        "style": str,
        "clip-rule": str,
        "fill": str,
        "fill-rule": str,
        "fill-opacity": float,
        "units": str,
        "spacingx": float,
        "spacingy": float,
        "color": str,
        "visible": bool,
        "transform": str,
    }
    
    def __init__(self):
        super().__setattr__("_attributes", {})  # Initialise le dictionnaire des attributs
        self._attributes["type"] = "base"  # On garde le type initial
        self._attributes["fillrule"] = "nonzero"           # nonzero ou evenodd
        self.loops = []
                
        self.elementChilds = []   # Initialisation à une liste vide
        
    def __getattr__(self, name):
        # Vérifier si l'attribut est dans _attributes
        if name in self._attributes:
            return self._attributes[name]
        # Vérifier s'il est dans attributes_to_get
        if name in self.attributes_to_get:
            return None  # Retourne None s'il fait partie de attributes_to_get mais n'est pas défini
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        # Mettre à jour les attributs dans le dictionnaire interne, en ignorant les valeurs None
        if name == "_attributes" or name not in self._attributes:
            super().__setattr__(name, value)
        else:
            if value is not None:  # On ne met à jour que si la valeur n'est pas None
                self._attributes[name] = value
            else:
                self._attributes.pop(attr_name, None)

    def __getitem__(self, key):
        # Accès via la notation de dictionnaire, retourne None si la clé n'existe pas
        return self._attributes.get(key, None)

    def __setitem__(self, key, value):
        # Modification via la notation de dictionnaire, en ignorant les valeurs None
        if value is not None:
            self._attributes[key] = value
        else:
            self._attributes.pop(key, None)

    def set_attribute(self, element, name, attr_type=str):
        value = element.get(name, None)
        if value is not None:
            try:
                value = attr_type(value)
                self._attributes[name] = value
            except ValueError:
                pass  # Ignorer les erreurs de conversion
        else:
            # Si la valeur est None, on enlève cet attribut du dictionnaire
            self._attributes.pop(name, None)
        return value

    def __str__(self):
        element_dict = self.to_dict()
        retStr = json.dumps(element_dict, indent=2)
        if self.transform:
            retStr += self.matrices.__str__()

        retStr = retStr.replace("\\n", "\n")
        return retStr

    def to_dict(self):
        # Représente l'élément sous forme de dictionnaire

        element_dict = self._attributes

        if len(self.elementChilds) > 0:
            childs_element_list = [element.to_dict() for element in self.elementChilds if element is not None]
            if len(childs_element_list) > 0:
                element_dict["children"] = childs_element_list
        element_dict = {k: v for k, v in element_dict.items() if v is not None}

        return element_dict

    def from_json(self,element):

        # Récupérer les attributs en évitant les exclusions
        for attr_name, attr_type in self.attributes_to_get.items():
            self.set_attribute(element, attr_name, attr_type)

        # Attributs inconnus (non exclus)
        filtered_attributes = {key.split('}')[-1]: value for key, value in element.attrib.items() if key.split('}')[-1] not in self.attributes_to_get.keys()}
        filtered_attributes = filtered_attributes if len(filtered_attributes) > 0 else None
        if filtered_attributes is not None:
            self._attributes["unknown"] = filtered_attributes if len(filtered_attributes) > 0 else None

        #  'matrix': 'matrix', 'translate': 'translate', 'scale': 'scale'
        self.matrice = Matrices()
        if self.transform is not None:
            self.matrice.setTransform(self.transform)

        return filtered_attributes

    def addChild(self, child):
        self.elementChilds.append(child)  # Utilisation de append au lieu de += []

class SVG_Element(base_Element):
    # On ajoute de nouveaux attributs à ceux de base_Element
    attributes_to_get = {**base_Element.attributes_to_get, 
                         "width": float, 
                         "height": float, 
                         "viewBox": str, 
                         "version": str, 
                         "docname": str, 
                         "space": str}    

    def __init__(self):
        super().__init__()
        self._attributes["type"] = "svg"  # On garde le type initial
        self._attributes["width"] = 300 
        self._attributes["height"] = 150

    def from_json(self, element):
        # Appeler la méthode parente
        filtered_attributes = super().from_json(element)
        
        # Gestion de viewBox avec vérification de type et conversion en liste
        viewBox_str = element.get("viewBox", None)
        if viewBox_str:
            try:
                viewBox = list(map(float, viewBox_str.split()))
                if len(viewBox) != 4:  # viewBox doit contenir exactement 4 valeurs
                    viewBox = None
            except ValueError:
                viewBox = None
        if viewBox is not None:
            self._attributes["viewBox"] = viewBox
        else:
            self._attributes.pop("viewBox", None)
        return filtered_attributes
    
    
class Path_Element(base_Element):
    # On ajoute de nouveaux attributs à ceux de base_Element
    attributes_to_get = {**base_Element.attributes_to_get, 
                         "d": str,
                         "nodetypes":str}
    def __init__(self):
        super().__init__()
        self._attributes["type"] = "path"  # On garde le type initial
        self.tokens = None
        self.unknow = None

    def __str__(self):
        element_dict = self.to_dict()
        if hasattr(element_dict,"tokens"):
            del element_dict['tokens']
        retStr = json.dumps({k: v for k, v in element_dict.items() if v is not None}, indent=2)
        for token in self.tokens:
            retStr = retStr + "\n" + repr(token)
        return retStr

    def to_dict(self):
        old_element_dict = super().to_dict()
        # Représente l'élément sous forme de dictionnaire
        tokenStr = ""
        for token in self.tokens:
            tokenStr = tokenStr + "\n" + repr(token)
        element_dict = {
            "tokens":tokenStr
        }
        element_dict = {k: v for k, v in element_dict.items() if v is not None}
        return {**old_element_dict, **element_dict}

    def from_json(self,element):
        filtered_attributes = super().from_json(element)
        self.tokens = self.tokenizePath(element.attrib.get("d", ""))
        return filtered_attributes

    def tokenizePath(self,chaine):
        rettokens = []
        subToken = []
        token = ""
        for char in chaine:
            if char.isalpha() and char.lower() != 'e':  # Si c'est une lettre, commence un nouveau token
                if token:
                    subToken.append(float(token))
                    token = ""
                if subToken:
                    rettokens.append(subToken)
                    subToken = []
                subToken.append(char)
            elif char.lower() == 'e':
                token += char
            elif char in ['.', '-']:  # Continuer à accumuler des chiffres et signes dans le token actuel
                addToken = char in token
                if char == '-':
                    if len(token) > 0:
                        if token[-1].lower() == 'e':
                            addToken = False
                        else:
                            addToken = True
                if addToken:
                    if token:
                        subToken.append(float(token))
                    token = char
                else:
                    token += char
            elif char.isdigit():  # Continuer à accumuler des chiffres et signes dans le token actuel
                token += char
            else:
                if token:
                   subToken.append(float(token))
                   token = ""
        if token:  # Ajouter le dernier token
            subToken.append(float(token))
        if subToken:
            rettokens.append(subToken)
            subToken = []
        return rettokens        

class Group_Element(base_Element):

    # On ajoute de nouveaux attributs à ceux de base_Element
    attributes_to_get = {**base_Element.attributes_to_get, 
                         "enable-background": str,
                         "label":str}

    def __init__(self):
        super().__init__()
        self._attributes["type"] = "group"  # On garde le type initial

class NameView_Element(base_Element):

    # On ajoute de nouveaux attributs à ceux de base_Element
    attributes_to_get = {**base_Element.attributes_to_get, 
                         "pagecolor":str,
                         "showgrid":bool,
                         "bordercolor":str,
                         "borderopacity":float,
                         "showpageshadow":int,
                         "pageopacity":float,
                         "pagecheckerboard":int,
                         "deskcolor":str,
                         "zoom":float,
                         "cx":float,
                         "cy":float,
                         "window-width":int,
                         "window-height":int,
                         "window-x":int,
                         "window-y":int,
                         "window-maximized":int,
                         "current-layer":str,
                         "showguides":bool
                         }

    def __init__(self):
        super().__init__()
        self._attributes["type"] = "nameview"  # On garde le type initial

    def from_json(self,element):
        filtered_attributes = super().from_json(element)
        self.namespace = element.tag 
        return filtered_attributes
        
class Grid_Element(base_Element):
    # On ajoute de nouveaux attributs à ceux de base_Element
    attributes_to_get = {**base_Element.attributes_to_get, 
                         "originx":int,
                         "originy":int,
                         "empspacing":int
                         }
    
    def __init__(self):
        super().__init__()
        self._attributes["type"] = "grid"  # On garde le type initial

class Defs_Element(base_Element):
    def __init__(self):
        super().__init__()
        self._attributes["type"] = "defs"  # On garde le type initial

class RadialGradient_Element(base_Element):
    # On ajoute de nouveaux attributs à ceux de base_Element
    attributes_to_get = {**base_Element.attributes_to_get, 
                         "cx":float,
                         "cy":float,
                         "gradientTransform":str,
                         "gradientUnits":str,
                         "r":float
                         }
    def __init__(self):
        super().__init__()
        self._attributes["type"] = "radialGradient"  # On garde le type initial

class Stop_Element(base_Element):
    # On ajoute de nouveaux attributs à ceux de base_Element
    attributes_to_get = {**base_Element.attributes_to_get, 
                         "offset":int,
                         "stop-color":str
                         }
    def __init__(self):
        super().__init__()
        self._attributes["type"] = "stop"  # On garde le type initial

class Rect_Element(base_Element):
    # On ajoute de nouveaux attributs à ceux de base_Element
    attributes_to_get = {**base_Element.attributes_to_get, 
                         "height":int,
                         "rx":float,
                         "width":int,
                         "x":int,
                         "y":int
                         }

    def __init__(self):
        super().__init__()
        self._attributes["type"] = "rect"  # On garde le type initial


class Circle_Element(base_Element):
    # On ajoute de nouveaux attributs à ceux de base_Element
    attributes_to_get = {**base_Element.attributes_to_get, 
                         "cx":float,
                         "cy":float,
                         "r":float,
                         }
    def __init__(self):
        super().__init__()
        self._attributes["type"] = "circle"  # On garde le type initial

class PathLoop:
    def __init__(self,stroke = None,strokelinecap = None,strokelinejoin = None,strokemiterlimit = None,strokewidth = None,drawColor = None,fillColor = None,fillrule = None, fill = None):
        self.loop = []
        self.loopIndex = []
        self.loopClosed = False
        self.stroke = stroke
        self.strokelinecap = strokelinecap
        self.strokelinejoin = strokelinejoin
        self.strokemiterlimit = strokemiterlimit
        self.strokewidth = strokewidth
        self.drawColor = drawColor
        self.fillColor = fillColor
        self.fillrule = fillrule
        self.fill = fill
        self.opacity = 1.0
        self.loopDirection = "Horaire"  # "Anti-horaire"  "Horaire" "Dégénéré (colinéaire)"
        self.bBox = None
        self.vertices = None
        
    def __str__(self):
        retStr = self.loopIndex.__str__() + ", "
        retStr += self.loopClosed.__str__()  + ", "
        retStr += self.drawColor.__str__() + ", "
        retStr += self.fillrule.__str__() + ", "
        if self.bBox:
            retStr += self.bBox.__str__() + ", "
        retStr += self.loopDirection
        return retStr


    def determine_orientation(self):
        """ Détermine si une boucle est horaire ou anti-horaire. """
        loop_index = self.loopIndex
        # Calculer l'aire signée de la boucle
        signed_area = 0.0
        n = len(loop_index)
        for i in range(0,n,2): # Parcourir les paires de segments de ligne
            # Obtenir les index des sommets
            i1 = loop_index[i]
            i2 = loop_index[(i+1) % n]
            # Coordonées des sommets correspondants
            x1, y1 = self.vertices[i1]
            x2, y2 = self.vertices[i2]
            # Calculer le terme (x1 * y2 - x2 * y1) et l'ajouter à l'aire signée

            contribution = (x1 * y2 - x2 * y1)
            signed_area += contribution
            
        # L'aire signée est divisée par 2
        signed_area *= 0.5

        # Déterminer l'orientation
        if signed_area > 0:
            self.loopDirection = "Anti-horaire"
        elif signed_area < 0:
            self.loopDirection = "Horaire"
        else:
            self.loopDirection = "Dégénéré (colinéaire)"

    def get_bounding_box(self):
        min_x = min(self.vertices[i][0] for i in self.loopIndex)
        max_x = max(self.vertices[i][0] for i in self.loopIndex)
        min_y = min(self.vertices[i][1] for i in self.loopIndex)
        max_y = max(self.vertices[i][1] for i in self.loopIndex)
        self.bBox = (min_x, min_y, max_x, max_y) 
        return (min_x, min_y, max_x, max_y)

    def addLoopIndex(self,index):
        self.loopIndex += ((index[0],index[1],))


    def point_in_path(self,x, y,crossings, winding_number):
        loopIndex = self.loopIndex
        fill_rule = self.fillrule

        n = len(loopIndex)
        for i in range(0, n, 2):
            i1 = loopIndex[i]
            i2 = loopIndex[i + 1]
            # Obtenir les coordonnées des points du segment
            x1, y1 = self.vertices[i1]
            x2, y2 = self.vertices[i2]

            # Teste si la ligne horizontale partant du point (x, y) coupe le segment
            if ((y1 <= y < y2) or (y2 <= y < y1)):  # La ligne du point coupe le segment

                # Calcul de l'abscisse du point d'intersection
                intersect_x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                
                if intersect_x > x:
                    crossings += 1

                    # Pour la règle nonzero, déterminer si c'est gauche-droite ou droite-gauche
                    if fill_rule == "nonzero":
                        if y1 < y2:  # Gauche-droite
                            winding_number += 1
                        else:  # Droite-gauche
                            winding_number -= 1
        return (crossings,winding_number)

    def point_in_loop(self,x, y):
        crossings = 0  # Pour la règle evenodd ou nonzero
        winding_number = 0  # Pour la règle nonzero
        crossings,winding_number = self.point_in_path(x,y, crossings,winding_number)
        # Appliquer la règle de remplissage sur toutes les boucles
        if self.fillrule == "evenodd":
            return crossings % 2 == 1
        elif self.fillrule == "nonzero":
            return winding_number != 0

        return False
