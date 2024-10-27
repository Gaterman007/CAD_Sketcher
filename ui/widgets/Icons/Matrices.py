import bpy
import numpy as np

class Matrices:

    def __init__(self):
        self.matrices = []
                
    # Fonction pour extraire toutes les transformations "matrix" d'une chaîne transform
    def extract_matrices(self,transform_string,matrice_type = "matrix"):
        # Liste pour stocker les matrices extraites
        matrices = []

        # Position de recherche initiale dans la chaîne
        current_pos = 0

        while current_pos < len(transform_string):
            # Cherche le début de la transformation "matrix"
            matrix_start = transform_string.find(matrice_type+"(", current_pos)

            if matrix_start == -1:  # Plus de matrices à trouver
                break

            # Cherche la fin de la transformation "matrix"
            matrix_end = transform_string.find(")", matrix_start)
            if matrix_end == -1:
                break

            # Extrait la sous-chaîne de la transformation "matrix(a, b, c, d, e, f)"
            matrix_content = transform_string[matrix_start + len(matrice_type+"("):matrix_end]


            if ',' in matrix_content:
                # Convertit la chaîne en liste de flottants
                matrix_values = list(map(float, matrix_content.split(",")))
            else:
                # Convertit la chaîne en liste de flottants
                matrix_values = list(map(float, matrix_content.split(" ")))

            # Ajoute la matrice à la liste des matrices
            matrices.append(matrix_values)

            # Met à jour la position de recherche après la fin de la matrice courante
            current_pos = matrix_end + 1

        return matrices

    def setTransform(self,transform):
        self.matrices = []
        transformTypes = self.extract_transformations(transform)
        for transformType in transformTypes:
            matrixTypeList = self.extract_matrices(transform,transformType) 
            for values in matrixTypeList:
                if transformType == 'translate':  # Créer une matrice selon le type de transformation
                    if len(values) == 1:  # Si une seule valeur est fournie
                        matrix = self.create_translation_matrix(values[0], 0)  # Assigner 0 pour l'axe y
                    elif len(values) == 2:  # Si deux valeurs sont fournies
                        matrix = self.create_translation_matrix(values[0], values[1])
                elif transformType == 'scale' and len(values) == 2:
                    matrix = self.create_scale_matrix(values[0], values[1])
                elif transformType == 'rotate' and len(values) == 1:
                    matrix = self.create_rotation_matrix(values[0])
                elif transformType == 'skewX' and len(values) == 1:
                    matrix = self.create_skew_x_matrix(values[0])
                elif transformType == 'skewY' and len(values) == 1:
                    matrix = self.create_skew_y_matrix(values[0])
                elif transformType == 'matrix' and len(values) == 6:
                    matrix = self.create_matrix(*values)
                else:
                    continue  # Ignorer les cas non pris en charge
                self.matrices.append(matrix)
        return self.matrices

    def extract_transformations(self,transform_string):
        current_name = ""
        in_parentheses = False
        name_List = []

        # Parcourir chaque caractère de la chaîne de transformation
        for char in transform_string:
            if char.isalpha():  # Si c'est une lettre, on construit le nom de la transformation
                if in_parentheses:  # Si on est encore dans les parenthèses, ignorer
                    continue
                current_name += char
            elif char == '(':  # Début d'une parenthèse, donc on enregistre la transformation actuelle
                if current_name:  # Vérifier qu'on a bien un nom de transformation
                    name_List.append(current_name)
                    current_name = ""
                in_parentheses = True
            elif char == ')':  # Fin de la parenthèse
                in_parentheses = False

        return name_List


    def create_translation_matrix(self,x, y):
        """ Crée une matrice de translation. """
        return np.array([
            [1, 0, x],
            [0, 1, y],
            [0, 0, 1]
        ])

    def create_scale_matrix(self,sx, sy):
        """ Crée une matrice de mise à l'échelle. """
        return np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ])

    def create_rotation_matrix(self,angle):
        """ Crée une matrice de rotation. """
        radians = np.radians(angle)
        cos_angle = np.cos(radians)
        sin_angle = np.sin(radians)
        return np.array([
            [cos_angle, -sin_angle, 0],
            [sin_angle, cos_angle, 0],
            [0, 0, 1]
        ])

    def create_skew_x_matrix(self,angle):
        """ Crée une matrice de cisaillement en X. """
        radians = np.radians(angle)
        return np.array([
            [1, np.tan(radians), 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

    def create_skew_y_matrix(self,angle):
        """ Crée une matrice de cisaillement en Y. """
        radians = np.radians(angle)
        return np.array([
            [1, 0, 0],
            [np.tan(radians), 1, 0],
            [0, 0, 1]
        ])

    def create_matrix(self,a, b, c, d, e, f):
        """ Crée une matrice de transformation. """
        return np.array([
            [a, c, e],
            [b, d, f],
            [0, 0, 1]
        ])

    # Fonction pour appliquer une matrice à un point 2D
    def apply_transformation(self,matrix, point):
        # Représenter le point en coordonnées homogènes
        point_homogeneous = np.array([point[0], point[1], 1])
        # Multiplier la matrice par le point
        transformed_point = matrix @ point_homogeneous
        return transformed_point[:2]  # Retourner les coordonnées 2D

    def fixPoint(self,x,y):
        point = (x, y)
        if self.matrices:
            for mat in self.matrices: # Appliquer chaque transformation à un point
                point = self.apply_transformation(mat, point)
        return point[0],point[1]