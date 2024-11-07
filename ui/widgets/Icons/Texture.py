import gpu
from gpu.types import Buffer, GPUTexture
from .SVG_Icon import SVG_Icon, get_SVG_Icon


class Textures:
    def __init__(self, width, height,initial_color = (0.0,0.0,0.0,0.0)):
        self.width = width
        self.height = height
        # Initialise la texture avec la couleur initial
        self.imageData = [*initial_color] * (width * height)
        if len(self.imageData) != self.width * self.height * 4:
            raise ValueError("Les pixels doivent correspondre à la taille de la texture (width * height * 4).")
        self.texture = None
        self.isDirty = True

    def __del__(self):
        self.delete_texture()

    def set_textureData(self,width,height,data):
        self.width = width
        self.height = height
        self.imageData = data
        self.isDirty = True
        
    def update_texture(self):
        # Supprime l'ancienne texture si elle existe
        if self.texture is not None:
            del self.texture
        # Crée un buffer pour les nouveaux pixels
#        print(len(self.imageData)," ",self.width," ", self.height," ",self.width*self.height*4)
        buffer = Buffer('FLOAT', len(self.imageData), self.imageData)
        # Crée une nouvelle texture avec les données mises à jour
        self.texture = GPUTexture((self.width, self.height), data=buffer)

    def clear_texture(self, value=(0.0, 0.0, 0.0, 0.0)):
        """Remplit la texture d'une couleur spécifique."""
        if self.texture is not None:
            self.texture.clear(value=value)

    def delete_texture(self):
        """Supprime explicitement la texture."""
        if self.texture is not None:
            del self.texture
            self.texture = None

    def read_pixels(self):
        """Lit les pixels actuels de la texture et les retourne."""
        if self.texture is not None:
            return self.texture.read()
        return None

    def resize(self, new_width, new_height, fill_value=(0.0, 0.0, 0.0, 1.0)):
        """Redimensionne la texture, recréant une nouvelle avec les nouvelles dimensions."""
        # Supprime l'ancienne texture et recrée une nouvelle texture avec les nouvelles dimensions
        
        newImageData = [*fill_value] * (new_width * new_height)
        rangeHeight = min(self.height,new_height)
        rangeWidth = min(self.width,new_width)
        for y in range(rangeHeight):
            for x in range(rangeWidth):
                # Calcul des index pour la texture source et destination
                src_index = (y * self.width + x) * 4
                dest_index = (y * new_width + x) * 4        
                newImageData[dest_index:dest_index + 4] = self.imageData[src_index:src_index + 4]
        self.width = new_width
        self.height = new_height
        self.imageData = newImageData
        self.isDirty = True

    def draw_texture(self,shader):
        if self.isDirty:
            self.update_texture()
        if self.texture is not None:
            shader.uniform_sampler("image", self.texture)
        
    def setPixel(self,x,y,color):
        width = self.width
        height = self.height
        pixels = self.imageData
        if 0 <= x < width and 0 <= y < height:
            index = (y * width + x) * 4
            self.imageData[index:index+4] = color
            self.isDirty = True
                
    def getPixel(self,x,y):
        retValue = None
        width = self.width
        height = self.height
        pixels = self.imageData
        if 0 <= x < width and 0 <= y < height:
            index = (y * width + x) * 4
            retValue = self.imageData[index:index+4]
        return retValue
        
    # 3. Fonction pour dessiner une ligne
    def draw_line(self, x0, y0, x1, y1, color):
        width = self.width
        height = self.height
        pixels = self.imageData
        # Convertir les coordonnées en index dans la liste des pixels
        def set_pixel(x, y, color):
            if 0 <= x < width and 0 <= y < height:
                index = (y * width + x) * 4
                pixels[index:index+4] = color
        
        # Algorithme de Bresenham pour tracer une ligne
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
    
        while True:
            set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        self.isDirty = True
        
    # Fonction pour remplir une région contiguë avec une couleur
    def draw_fill(self, x, y, fill_color):
        width = self.width
        height = self.height
        pixels = self.imageData

        # Convertit une position (x, y) en un index dans la liste des pixels
        def get_pixel_index(x, y):
            return (y * width + x) * 4

        # Récupère la couleur d'un pixel aux coordonnées (x, y)
        def get_pixel_color(x, y):
            index = get_pixel_index(x, y)
            return pixels[index:index+4]

        # Définit la couleur d'un pixel aux coordonnées (x, y)
        def set_pixel(x, y, color):
            if 0 <= x < width and 0 <= y < height:
                index = get_pixel_index(x, y)
                pixels[index:index+4] = color

        # Récupère la couleur de départ (à partir de laquelle on va remplir)
        start_color = get_pixel_color(x, y)

        # Si la couleur de départ est déjà égale à la couleur de remplissage, rien à faire
        if start_color == fill_color:
            return

        # Stack pour l'algorithme de Flood Fill
        pixel_stack = [(x, y)]

        # Tant qu'il reste des pixels à traiter
        while pixel_stack:
            current_x, current_y = pixel_stack.pop()
            current_color = get_pixel_color(current_x, current_y)

            # Vérifie si le pixel est de la couleur de départ (donc doit être rempli)
            if current_color == start_color:
                # Remplit le pixel avec la couleur désirée
                set_pixel(current_x, current_y, fill_color)

                # Ajoute les voisins à la pile (4-connecté : haut, bas, gauche, droite)
                if current_x > 0:  # Pixel de gauche
                    pixel_stack.append((current_x - 1, current_y))
                if current_x < width - 1:  # Pixel de droite
                    pixel_stack.append((current_x + 1, current_y))
                if current_y > 0:  # Pixel du bas
                    pixel_stack.append((current_x, current_y - 1))
                if current_y < height - 1:  # Pixel du haut
                    pixel_stack.append((current_x, current_y + 1))
        self.isDirty = True
        
    def flip_horizontal(self):
        """Effectue un miroir horizontal de l'image (inverser de gauche à droite)."""
        width = self.width
        height = self.height
        pixels = self.imageData[:]

        for y in range(height):
            for x in range(width // 2):
                index1 = (y * width + x) * 4
                index2 = (y * width + (width - 1 - x)) * 4

                # Échange les pixels
                pixels[index1:index1+4], pixels[index2:index2+4] = pixels[index2:index2+4], pixels[index1:index1+4]

        self.imageData = pixels
        self.isDirty = True

    def flip_vertical(self):
        """Effectue un miroir vertical de l'image (inverser de haut en bas)."""
        width = self.width
        height = self.height
        pixels = self.imageData[:]

        for y in range(height // 2):
            for x in range(width):
                index1 = (y * width + x) * 4
                index2 = ((height - 1 - y) * width + x) * 4

                # Échange les pixels
                pixels[index1:index1+4], pixels[index2:index2+4] = pixels[index2:index2+4], pixels[index1:index1+4]

        self.imageData = pixels
        self.isDirty = True
        
    def load_SVG(self,filename):
        svg_Icon = get_SVG_Icon(filename)
        svg_Icon.setSize(width = self.width, height = self.height)
        svg_Icon.create_Image(self)
        self.isDirty = True

    def load_PNG(self,filename):
        self.__image = bpy.data.images.load(
            filename, check_existing=True
        )
        self.width = self.__image.size[0]
        self.height = self.__image.size[1]
        self.imageData = self.__image.pixels[:]
        self.update_texture()
        bpy.data.images.remove(self.__image)
        self.__image = None
        
    def bitblt(self, src_texture, dest_x, dest_y, width, height):
        """
        Copie une région de la texture source `src_texture` dans `self.imageData`
        aux coordonnées (dest_x, dest_y) avec une largeur `width` et une hauteur `height`,
        sans dépasser les limites de la texture de destination.
        
        :param src_texture: instance de `Textures` représentant la source.
        :param dest_x: position x de départ dans la texture de destination.
        :param dest_y: position y de départ dans la texture de destination.
        :param width: largeur de la région à copier.
        :param height: hauteur de la région à copier.
        """
        # Ajuster la largeur et la hauteur pour rester dans les limites des textures
        width = min(width, src_texture.width, self.width - dest_x)
        height = min(height, src_texture.height, self.height - dest_y)

        # Vérification pour s'assurer que width et height sont positifs
        if width > 0 and height > 0:
            for y in range(height):
                for x in range(width):
                    # Calcul des index pour la texture source et destination
                    src_index = (y * src_texture.width + x) * 4
                    dest_index = ((dest_y + y) * self.width + (dest_x + x)) * 4

                    # Copie des pixels RGBA de la source vers la destination
                    self.imageData[dest_index:dest_index + 4] = src_texture.imageData[src_index:src_index + 4]
        self.isDirty = True