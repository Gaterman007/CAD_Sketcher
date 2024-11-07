import bpy
import xml.etree.ElementTree as ET
import math
import json
import gpu
import bpy.utils
import copy

from .Matrices import Matrices
from .ImageCls import Image
from .SVG_Element import *

svg_Icons = {}

def get_SVG_Icon(name: str):
    if name not in svg_Icons.keys():
        svg_Icons[name] = SVG_Icon(filename = name)
    return svg_Icons[name]

class Base_Icon:
    def __init__(self, imageName = None, width = 300, height = 150, color = (0.0,0.0,0.0,0.0)):
        self.imageName = imageName
        self.width = width
        self.height = height
        self.color = color
        self.imageIcon = None # Image de l icon

    def __del__(self):
        if self.imageIcon is not None:
            self.imageIcon = None

    def create_ImageIcon(self,width,height,color):
        self.imageIcon = Image(name = self.imageName,width = width,height = height,color = color) # Image de l icon

    def updateData():
        self.imageIcon.updateData()

    def setSize(self,width = 300, height = 150):
        self.width = width
        self.height = height


class Base_SVG_Icon(Base_Icon):
    def __init__(self, filename = None, width = 300, height = 150):
        super().__init__(width = width, height = height)
        self.svgElement = []  # Liste pour stocker les éléments dans une hiérarchie
        self.load_XMLFile(filename)
        
    def __str__(self):
        return self.svgElement.__str__()

    def load_XMLFile(self,filename):
        self.filename = filename
        if (self.filename != None):
            with open(self.filename, 'r') as svg_file:
                self.load_FromXML(svg_file.read())

    def load_FromXML(self,svg_data):
        self.root = ET.fromstring(svg_data)
        # Extraire les dimensions du SVG
        self.svgElement = self.parse_tag_element(self.root)
    
    def parse_tag_element(self,element,level = 0,group_elements = None):
        local_name = element.tag.split('}', 1)[-1]
        
        if group_elements is None:
            group_elements = {}  # Dictionnaire pour stocker les instances de chaque nivea

        # Génération d'une clé unique pour chaque niveau
        level_key = f"level_{level}"
        
        if element.tag.endswith("svg"):  # Si l'élément est un <g> (groupe)
            group_elements[level_key] = SVG_Element()
            attributes_unused = group_elements[level_key].from_json(element)
            if attributes_unused is not None:
                print(group_elements[level_key].type,attributes_unused)
            
            for child in element:
                child_element = self.parse_tag_element(child, level + 1, group_elements)
                if child_element:
                    group_elements[level_key].addChild(child_element)
            return group_elements[level_key]
        elif element.tag.endswith("g"):  # Si l'élément est un <g> (groupe)
            group_elements[level_key] = Group_Element()
            attributes_unused = group_elements[level_key].from_json(element)
            if attributes_unused is not None:
                print(group_elements[level_key].type,attributes_unused)

            for child in element:
                child_element = self.parse_tag_element(child, level + 1, group_elements)
                if child_element:
                    group_elements[level_key].addChild(child_element)
            return group_elements[level_key]
        elif element.tag.endswith("path"):  # Si l'élément est un <path>
            path_Element = Path_Element()
            attributes_unused = path_Element.from_json(element)

            if attributes_unused is not None:
                print(path_Element.type,attributes_unused)


            return path_Element
        elif element.tag.endswith("namedview"):
            group_elements[level_key] = NameView_Element()
            attributes_unused = group_elements[level_key].from_json(element)
            if attributes_unused is not None:
                print(group_elements[level_key].type,attributes_unused)

            for child in element:
                child_element = self.parse_tag_element(child, level + 1, group_elements)
                if child_element:
                    group_elements[level_key].addChild(child_element)
            return group_elements[level_key]
        elif element.tag.endswith("grid"):
            grid_Element = Grid_Element()
            attributes_unused = grid_Element.from_json(element)
            if attributes_unused is not None:
                print(grid_Element.type,attributes_unused)
            return grid_Element
        elif element.tag.endswith("defs"):
            defs_Element = Defs_Element()
            attributes_unused = defs_Element.from_json(element)
            if attributes_unused is not None:
                print(defs_Element.type,attributes_unused)
            return defs_Element
        elif element.tag.endswith("radialGradient"):
            group_elements[level_key] = RadialGradient_Element()
            attributes_unused = group_elements[level_key].from_json(element)
            if attributes_unused is not None:
                print(group_elements[level_key].type,attributes_unused)
            for child in element:
                child_element = self.parse_tag_element(child, level + 1, group_elements)
                if child_element:
                    group_elements[level_key].addChild(child_element)
            return group_elements[level_key]
        elif element.tag.endswith("stop"):
            group_elements[level_key] = Stop_Element()
            attributes_unused = group_elements[level_key].from_json(element)
            if attributes_unused is not None:
                print(group_elements[level_key].type,attributes_unused)
            return group_elements[level_key]
        elif element.tag.endswith("rect"):
            group_elements[level_key] = Rect_Element()
            attributes_unused = group_elements[level_key].from_json(element)
            if attributes_unused is not None:
                print(group_elements[level_key].type,attributes_unused)
            return group_elements[level_key]
        elif element.tag.endswith("circle"):
            group_elements[level_key] = Circle_Element()
            attributes_unused = group_elements[level_key].from_json(element)
            if attributes_unused is not None:
                print(group_elements[level_key].type,attributes_unused)
            return group_elements[level_key]
        else:
            print(f"tag not supported {element.tag}")
            return None

class SVG_Icon(Base_SVG_Icon):
    def __init__(self, filename = None, width = 300, height = 150, keepRatio = True):
        super().__init__(filename = filename,width = width, height = height)
        self.keepRatio = keepRatio
        self.initData()
        
    def initData(self):
        self.drawColor = (1.0,1.0,1.0,1.0)   # (0.63,0.63,0.63,1.0)
        self.fillColor = (1.0,1.0,1.0,1.0)
        self.fillrule = 'nonzero'
        self.fill = None
        self.opacity = 1.0
        self.deltaX = 1
        self.deltaY = 1
        self.matrices = None
 
        self.vertices = []

        self.loopNo = -1        # nombre de boucle
        self.loopListe = []     # listes de boucle 
        self.loop = None        # current loop
        
    def __str__(self):
        return self.svgElement.__str__()

    def addBoucle(self,element):
        self.loopNo += 1
        self.loopListe.append(PathLoop()) 
        self.loop = self.loopListe[self.loopNo]
        element.loops.append(self.loop)
        self.loop.drawColor = self.drawColor
        self.loop.fillColor = self.fillColor
        self.loop.fillrule = self.fillrule
        self.loop.vertices = self.vertices
        self.loop.fill = self.fill
        self.loop.opacity = self.opacity
        return self.loop

    def addVertice(self,x,y):
        self.vertices.append((x / self.deltaX, y / self.deltaY))
    
    def addLineTo(self,x1,y1,element,fixPoint = True):
        # Ajouter le premier points 0,0 à vertices si aucun definie
        if (len(self.vertices) == 0):
            self.addVertice(0, 0)
            self.addBoucle(element) # on commence une boucle
        elif self.loopNo >= 0:   # on commence une nouvelle boucle si la boucle est fermé
            if self.loop.loopClosed:            
                self.addBoucle(element) # on commence une boucle
        if fixPoint:
            actual_x,actual_y = self.matrices.fixPoint(x1,y1)
        else:
            actual_x,actual_y = x1,y1
        # Ajouter les points à vertices
        self.addVertice(actual_x, actual_y)
        # Ajouter une ligne pour formé l arc
        lineToAdd = (len(self.vertices) - 2,len(self.vertices) - 1)
        self.loop.addLoopIndex(lineToAdd)


    def Cubic_Bezier_Curve(self,element, lastPosX, lastPosY, x1, y1, x2, y2, x, y):
        """
        Trace une courbe de Bézier cubique en utilisant des segments de ligne.
        
        Paramètres :
        lastPosX, lastPosY -- Point de départ de la courbe
        x1, y1 -- Premier point de contrôle
        x2, y2 -- Second point de contrôle
        x, y -- Point d'arrivée de la courbe
        """
        # Définir le nombre de segments pour approximer la courbe
        num_segments = 5
        lastX, lastY = lastPosX, lastPosY  # Initialiser au point de départ
        lastX, lastY = self.matrices.fixPoint(lastPosX, lastPosY) # Initialiser au point de départ
        x1,y1 = self.matrices.fixPoint(x1,y1)
        x2,y2 = self.matrices.fixPoint(x2,y2)
        x,y = self.matrices.fixPoint(x,y)
        if self.loopNo >= 0:
            if self.loop.loopClosed:
                self.addBoucle(element)
        else:
            self.addBoucle(element)
        # Boucle pour calculer chaque point de la courbe
        for i in range(1, num_segments + 1):
            t = i / num_segments  # Paramètre d'interpolation entre 0 et 1
            # Formule de Bézier cubique
            xt = (1 - t)**3 * lastX + 3 * (1 - t)**2 * t * x1 + 3 * (1 - t) * t**2 * x2 + t**3 * x
            yt = (1 - t)**3 * lastY + 3 * (1 - t)**2 * t * y1 + 3 * (1 - t) * t**2 * y2 + t**3 * y
            # Ajouter le segment de ligne entre le dernier point et le point actuel
            self.addLineTo(xt,yt,element,False)
            # Mettre à jour les coordonnées du dernier point
            lastX, lastY = xt, yt
        self.addLineTo(x,y,element,False)

    def Quadratic_Bezier_Curve(self,element, x0, y0, x1, y1, x2, y2):
        """
        Trace une courbe de Bézier quadratique en utilisant une série de segments de ligne.
        
        Paramètres :
        x0, y0 -- Point de départ de la courbe
        x1, y1 -- Point de contrôle de la courbe
        x2, y2 -- Point d'arrivée de la courbe
        """
        # Nombre de segments à utiliser pour approximer la courbe
        num_segments = 5
        lastX, lastY = x0, y0  # Initialiser au point de départ
        # Ajouter les points à vertices
        self.addVertice(lastX, lastY)
        # Calculer chaque point intermédiaire de la courbe
        for i in range(1, num_segments + 1):
            t = i / num_segments  # Paramètre d'interpolation entre 0 et 1
            # Formule de Bézier quadratique
            xt = (1 - t)**2 * x0 + 2 * (1 - t) * t * x1 + t**2 * x2
            yt = (1 - t)**2 * y0 + 2 * (1 - t) * t * y1 + t**2 * y2
            # Ajouter le segment de ligne entre le dernier point et le point actuel
            self.addLineTo(xt, yt, element)
            # Mettre à jour les coordonnées du dernier point
            lastX, lastY = xt, yt
        # Ajouter la ligne finale au point d'arrivée (si nécessaire)
        self.addLineTo(x2, y2, element)
        
    def draw_arc(self, element, lastPosX, lastPosY, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y, num_segments=6):
        # Étape 1 : Calculer le milieu entre les points (lastPosX, lastPosY) et (x, y)
        dx = (lastPosX - x) / 2.0
        dy = (lastPosY - y) / 2.0
        # Étape 2 : Appliquer la rotation de l'axe x à (dx, dy)
        radians = math.radians(x_axis_rotation)
        dx_prime = math.cos(radians) * dx + math.sin(radians) * dy
        dy_prime = -math.sin(radians) * dx + math.cos(radians) * dy
        # Étape 3 : Calculer le centre de l'arc (cx_prime, cy_prime) dans le système de coordonnées transformé
        radii_check = (dx_prime**2) / (rx**2) + (dy_prime**2) / (ry**2)
        if radii_check > 1:  # Si les rayons sont trop petits pour contenir l'arc
            rx *= math.sqrt(radii_check)
            ry *= math.sqrt(radii_check)
        denominator = rx**2 * dy_prime**2 + ry**2 * dx_prime**2
        if denominator != 0:
            factor = math.sqrt(max(0, (rx**2 * ry**2 - rx**2 * dy_prime**2 - ry**2 * dx_prime**2) / (denominator)))
        else:
            factor = 1
        if large_arc_flag == sweep_flag:
            factor = -factor
        cx_prime = factor * (rx * dy_prime / ry)
        cy_prime = factor * -(ry * dx_prime / rx)
        # Étape 4 : Calculer le centre (cx, cy) dans le système de coordonnées d'origine
        cx = math.cos(radians) * cx_prime - math.sin(radians) * cy_prime + (lastPosX + x) / 2
        cy = math.sin(radians) * cx_prime + math.cos(radians) * cy_prime + (lastPosY + y) / 2
        # Étape 5 : Calculer les angles de début et de fin
        start_angle = math.atan2((dy_prime - cy_prime) / ry, (dx_prime - cx_prime) / rx)
        end_angle = math.atan2((-dy_prime - cy_prime) / ry, (-dx_prime - cx_prime) / rx)

        # Vérifier le sweep_flag pour la direction correcte
        delta_angle = end_angle - start_angle
        if sweep_flag == 1.0:
            if delta_angle < 0:
                delta_angle += 2 * math.pi  # Assurez-vous que l'arc va dans le sens horaire
        else:
            if delta_angle > 0:
                delta_angle -= 2 * math.pi  # Assurez-vous que l'arc va dans le sens antihoraire
        
        # Étape 6 : Générer les points de l'arc
        for i in range(1,num_segments + 1):
            angle = start_angle + i * delta_angle / num_segments
            px = cx + rx * math.cos(angle) * math.cos(radians) - ry * math.sin(angle) * math.sin(radians)
            py = cy + rx * math.cos(angle) * math.sin(radians) + ry * math.sin(angle) * math.cos(radians)
            self.addLineTo(px, py, element)
            lastPosX, lastPosY = px, py
        return lastPosX, lastPosY

    def hex_to_rgba(self,hex_color):
        # Vérifie si la chaîne commence par '#'
        if not hex_color.startswith('#'):
            raise ValueError("La couleur doit commencer par '#'." , hex_color)
        # Supprime le '#' pour faciliter le traitement
        hex_color = hex_color[1:]
        # Détermine si la couleur est abrégée ou non
        if len(hex_color) == 3:  # Cas abrégé (ex: #fff)
            r = int(hex_color[0] * 2, 16)  # Multiplie le caractère par 2
            g = int(hex_color[1] * 2, 16)
            b = int(hex_color[2] * 2, 16)
            a = 1.0  # Alpha par défaut à 1.0
        elif len(hex_color) == 6:  # Cas complet (ex: #ffffff)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = 1.0  # Alpha par défaut à 1.0
        elif len(hex_color) == 8:  # Cas avec alpha (ex: #ffffff00)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = int(hex_color[6:8], 16) / 255.0  # Normaliser entre 0 et 1
        else:
            raise ValueError("Format de couleur hexadécimal invalide.")

        # Retourne un tuple RGBA normalisé entre 0 et 1
        return (r / 255.0, g / 255.0, b / 255.0, a)
    
    def token_vertice(self, element, level):
        level_key = f"level_{level}"
        dictionaire = self.element_dict[level_key]
        lastPosX = 0.0
        lastPosY = 0.0
        self.matrices = self.matrice[level_key] # Liste pour stocker les matrices créées

        self.fill = dictionaire.get('fill', '#000000')
        if self.fill[0] == '#':
            self.drawColor = self.hex_to_rgba(self.fill)
        else:
            if self.fill != 'none':
                print("fill not supported",self.fill)
        self.opacity = dictionaire.get('opacity', 1.0)
        self.drawColor = self.drawColor[:3] + (dictionaire.get('opacity', self.drawColor[3]),)
        self.fillColor = self.fillColor[:3] + (dictionaire.get('fill-opacity', self.fillColor[3]),)
        self.fillrule = dictionaire.get('fill-rule', self.fillrule)

        def setRelativeCoord(x,y,lastPosX,lastPosY):
            if self.coordRelative:
                x += lastPosX
                y += lastPosY
            return (x,y)

        # Variables pour les points de contrôle précédents (pour courbes "smooth")
        prevCtrlX, prevCtrlY = None, None
        prevCtrlX2, prevCtrlY2 = None, None
        prevCtrlTX, prevCtrlTY = None, None

        # Variables pour le point de départ d'un chemin
        startX, startY = None, None
        for token in element.tokens:
            self.coordRelative = token[0].islower()
            command  = token[0].lower()
            
            if command  == 'a':  # Arc (rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y)
                for i in range(1, len(token), 7):
                    if len(token[i:]) >= 7:
                        rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y = token[i:i+7]
                        x,y = setRelativeCoord(x,y,lastPosX,lastPosY)
                        lastPosX, lastPosY = self.draw_arc(element, lastPosX, lastPosY, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y)
                lastPosX, lastPosY = x, y
                prevCtrlX2 = None
                prevCtrlTX = None
            elif command == 'm':  # Move to (x, y)
                # Récupération des coordonnées x, y après 'm'
                x, y = token[1], token[2]
                x,y = setRelativeCoord(x,y,lastPosX,lastPosY)
                startX, startY = x, y
                lastPosX, lastPosY = x, y
                actual_x,actual_y = self.matrices.fixPoint(x,y)
                self.addVertice(actual_x,actual_y)
                self.addBoucle(element)
                if len(token) > 3:
                    for i in range(3, len(token), 2):
                        if len(token[i:]) >= 2:
                            x,y = setRelativeCoord(token[i],token[i + 1],lastPosX,lastPosY)
                            self.addLineTo(x, y, element)
                            lastPosX, lastPosY = x, y
                prevCtrlX2 = None
                prevCtrlTX = None
            elif command == 'l':  # Line to (x, y)
                for i in range(1, len(token), 2):
                    if len(token[i:]) >= 2:
                        x, y = setRelativeCoord(token[i],token[i + 1],lastPosX,lastPosY)
                        self.addLineTo(x, y, element)
                        lastPosX, lastPosY = x, y
                prevCtrlX2 = None
            elif command == 'h':  # Horizontal Line to (x)
                for i in range(1, len(token), 1):
                    lastPosX = token[i] + lastPosX if self.coordRelative else token[i]
                    self.addLineTo(lastPosX, lastPosY, element)
                prevCtrlX2 = None
                prevCtrlTX = None
            elif command == 'v':  # Vertical Line to (y)
                for i in range(1, len(token), 1):
                    lastPosY = token[i] + lastPosY if self.coordRelative else token[i]
                    self.addLineTo(lastPosX, lastPosY,element)
                prevCtrlX2 = None
                prevCtrlTX = None
            elif command == 's':  # Smooth Cubic Bézier Curve (x2, y2, x, y)
                for i in range(1, len(token), 4):
                    if len(token[i:]) >= 4:
                        x2, y2, x, y = token[i:i+4]
                        x,y = setRelativeCoord(x,y,lastPosX,lastPosY)
                        x2,y2 = setRelativeCoord(x2,y2,lastPosX,lastPosY)
                        # Calculer le premier point de contrôle (symétrie par rapport à lastPosX, lastPosY)
                        if prevCtrlX2 is not None:
                            x1 = 2 * lastPosX - prevCtrlX2
                            y1 = 2 * lastPosY - prevCtrlY2
                        else:
                            x1, y1 = lastPosX, lastPosY
                        self.Cubic_Bezier_Curve(element,lastPosX, lastPosY, x1, y1, x2, y2, x, y)
                        prevCtrlX2, prevCtrlY2 = x2, y2
                        lastPosX, lastPosY = x, y
            elif command == 'c':  # Cubic Bézier Curve (x1, y1, x2, y2, x, y)
                for i in range(1, len(token), 6):
                    if len(token[i:]) >= 6:
                        x1, y1, x2, y2, x, y = token[i:i+6]
                        x,y = setRelativeCoord(x,y,lastPosX,lastPosY)
                        x1,y1 = setRelativeCoord(x1,y1,lastPosX,lastPosY)
                        x2,y2 = setRelativeCoord(x2,y2,lastPosX,lastPosY)
                        self.Cubic_Bezier_Curve(element,lastPosX, lastPosY, x1, y1, x2, y2, x, y)
                        prevCtrlX2, prevCtrlY2 = x2, y2
                        lastPosX, lastPosY = x, y
                prevCtrlTX = None
            elif command in {'q', 't'}:  # Quadratic Bézier Curve (x1, y1, x, y) ou (x, y)
                nbOfparam = 4
                if command == 't':
                    nbOfparam = 2
                for i in range(1, len(token), nbOfparam):
                    if len(token[i:]) >= nbOfparam:
                        if command == 't':
                            x, y = token[i:i+2]
                            x,y = setRelativeCoord(x,y,lastPosX,lastPosY)
                            if prevCtrlTX is not None:
                                x1 = 2 * lastPosX - prevCtrlTX
                                y1 = 2 * lastPosY - prevCtrlTY
                            else:
                                x1, y1 = lastPosX, lastPosY
                        else:
                            x1, y1, x, y = token[i:i+4]
                            x,y = setRelativeCoord(x,y,lastPosX,lastPosY)
                            x1,y1 = setRelativeCoord(x1,y1,lastPosX,lastPosY)
                        self.Quadratic_Bezier_Curve(element,lastPosX, lastPosY, x1, y1, x, y)
                        prevCtrlTX, prevCtrlTY = x1, y1
                        lastPosX, lastPosY = x, y
                prevCtrlX2 = None
            elif command == 'z':  # Close path
                if startX is not None and startY is not None:
                    x, y = startX, startY
                    self.addLineTo(x, y,element)
                    lastPosX, lastPosY = x, y
                    self.loop.loopClosed = True
                    self.loop.determine_orientation()
                prevCtrlX2 = None
                prevCtrlTX = None
            else:
                print("Token inconnu :", token)
            
                
            
    def recursif_Vertices(self,element,level = 0):
        # Génération d'une clé unique pour chaque niveau
        level_key = f"level_{level}"
        level_key_moinsun = f"level_{level-1}"
        self.element_dict[level_key] = element.to_dict()
            
        if 'children' in self.element_dict[level_key]:
            children = self.element_dict[level_key].pop('children', None)

        self.matrice[level_key] = copy.deepcopy(element.matrice)
        if level > 0:
            self.element_dict[level_key] = {**self.element_dict[level_key_moinsun], **self.element_dict[level_key]}
            if self.matrice[level_key_moinsun] is not None:
                if self.matrice[level_key] is not None:
                    self.matrice[level_key].matrices += self.matrice[level_key_moinsun].matrices
                else:
                    self.matrice[level_key] = copy.deepcopy(self.matrice[level_key_moinsun])
                    
        retStr = self.element_dict[level_key].__str__().replace("\\n", "\n")
        if element.type != "path" and element.type != "svg":
            for subelement in element.elementChilds:
                self.recursif_Vertices(subelement,level+1)
        elif element.type == "svg":
            if self.keepRatio:
                ratio = float(element.width) / float(element.height)
                self.height = int(self.width / ratio)
            self.deltaX = element.width / self.width
            self.deltaY = element.height / self.height
            
            for subelement in element.elementChilds:
                self.recursif_Vertices(subelement,level+1)
        elif element.type == "path":
            self.token_vertice(element,level)

    def point_in_paths(self, x, y, loopList):
        crossings = 0  # Pour la règle evenodd ou nonzero
        winding_number = 0  # Pour la règle nonzero
        for loop in loopList:
            crossings,winding_number = loop.point_in_path(x,y, crossings,winding_number)

        # Appliquer la règle de remplissage sur toutes les boucles
        if self.fillrule == "evenodd":
            return crossings % 2 == 1
        elif self.fillrule == "nonzero":
            return winding_number != 0

        return False

    def draw_Image(self,element,image,level = 0):
        level_key = f"level_{level}"
        level_key_moinsun = f"level_{level-1}"
        self.element_dict[level_key] = element.to_dict()


        if level > 0:
            self.element_dict[level_key] = {**self.element_dict[level_key_moinsun], **self.element_dict[level_key]}

        if element.type == 'svg':
            if image is None:
                self.create_ImageIcon(self.width,self.height,(0.0, 0.0, 0.0, 0.0))

        for subelement in element.elementChilds:
            self.draw_Image(subelement,image,level+1)

        if element.type != 'grid' and element.type != 'nameview':
            if element.type == 'path':
                if self.imageIcon is not None or image is not None:
                    for loop in element.loops:
                        loop.get_bounding_box()
                    self.draw_paths(element.loops,image)

    def draw_paths(self, path_list,image):
        if self.imageIcon is not None or image is not None:
            for loop in path_list:
                loop.get_bounding_box()
                fixedRangeMinX = max(int(loop.bBox[0]), 0)
                fixedRangeMaxX = min(int(loop.bBox[2]), self.width)
                fixedRangeMinY = max(int(loop.bBox[1]), 0)
                fixedRangeMaxY = min(int(loop.bBox[3]), self.height)
                # draw fill loops
                if loop.fill != 'none':
                    directionOk = True
                    if directionOk:
                        for fillPosX in range(fixedRangeMinX,fixedRangeMaxX):
                            for fillPosY in range(fixedRangeMinY,fixedRangeMaxY):
                                if loop.point_in_loop(fillPosX, fillPosY):
                                    if self.point_in_paths(fillPosX, fillPosY, path_list):
                                        if image is not None:
                                            oldColor = image.getPixel(fillPosX, fillPosY)
                                        else:
                                            oldColor = self.imageIcon.getPixel(fillPosX, fillPosY)
                                        if oldColor is not None:
                                            couleur_finale = oldColor
                                            for idx in range(len(couleur_finale)):
                                                couleur_finale[idx] = (loop.drawColor[idx] * loop.opacity) + (oldColor[idx] * (1 - loop.opacity))
                                            if image is not None:
                                                image.setPixel(fillPosX, fillPosY,couleur_finale)
                                            else:
                                                self.imageIcon.setPixel(fillPosX, fillPosY,couleur_finale)


                # draw lines
                n = len(loop.loopIndex)
                for i in range(0,n,2):
                    # Obtenir les index des sommets
                    i1 = loop.loopIndex[i]
                    i2 = loop.loopIndex[i+1]
                    # Coordonées des sommets correspondants
                    x1, y1 = self.vertices[i1]
                    x2, y2 = self.vertices[i2]
                    if image is not None:
                        image.draw_line(int(x1), int(y1), int(x2), int(y2), loop.drawColor)
                    else:
                        self.imageIcon.draw_line(int(x1), int(y1), int(x2), int(y2), loop.drawColor)
            if image is not None:
                image.update_texture()
            else:
                self.imageIcon.updateData()

            
    def create_Image(self,image = None):
        if self.svgElement is not None:
            if self.imageIcon is not None:
                self.imageIcon = None
            self.element_dict = {}
            self.matrice = {}
            self.initData()
            self.recursif_Vertices(self.svgElement)
            for loop in self.loopListe:
                loop.get_bounding_box()
            self.draw_Image(self.svgElement,image)

    def create_Texture(self, texture):
        if self.svgElement is not None:
            self.element_dict = {}
            self.matrice = {}
            self.initData()
            self.recursif_Vertices(self.svgElement)
            for loop in self.loopListe:
                loop.get_bounding_box()
            self.draw_Image(self.svgElement)
