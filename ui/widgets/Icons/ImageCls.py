import bpy

class Image:
    
    def __init__(self, name, width=512, height=512, color=(0.0, 0.0, 0.0, 1.0), _alpha=True):
        self.imageName = name if name is not None else "CustomImage"
        self.imageData = None
        self.width = int(width)
        self.height = int(height)
        self.backColor = color
        self.image = None  # Une seule variable pour stocker l'image
        self.texture = None
        
        # Créer une nouvelle image par défaut (si aucune image n'est chargée)
        self.create_image(width, height, color, _alpha)

    def create_image(self, width, height, color, _alpha=True):
        """Crée une nouvelle image avec une couleur donnée."""
        self.image = bpy.data.images.new(self.imageName, width=width, height=height, alpha=_alpha)
        self.imageData = [color[0], color[1], color[2], color[3]] * (width * height)
        self.image.pixels = self.imageData

    def get_image_copy(self,new_name):
        has_alpha = (self.image.channels == 4)
        new_image = bpy.data.images.new(
            name=new_name,
            width=self.image.size[0],
            height=self.image.size[1],
            alpha=has_alpha
        )
        # Copier les pixels
        new_image.pixels = self.image.pixels[:]
        return new_image

    def set_image(self, rel_filename):
        """Charge une image si elle n'est pas déjà chargée, ou la crée si elle n'existe pas."""
        # D'abord, essayer de charger l'image
        imgname = f".{os.path.basename(rel_filepath)}"

        try:
            # Vérifier si l'image existe déjà dans bpy.data.images
            img = bpy.data.images.get(imgname)
            if img is not None:
                self.image = img
            else:
                # Charger l'image si elle existe sur le disque
                if os.path.exists(rel_filepath):
                    self.image = bpy.data.images.load(rel_filepath, check_existing=True)
                    self.image.name = imgname
                else:
#                    print(f"Image file {rel_filepath} not found, using default image.")
                    self.create_image(self.width, self.height, self.backColor)

            # Charger l'image dans OpenGL si elle existe
            if self.image is not None:
                self.image.gl_load()
                self.texture = gpu.texture.from_image(self.image)
            else:
                print("Failed to load the image.")
        except Exception as e:
            print("Exception in set_image function:", e)
            self.image = None

    def __del__(self):
        """Libère les ressources de l'image."""
        if self.image is not None:
            bpy.data.images.remove(self.image)
            self.image = None

        if self.imageData is not None:
            self.imageData = None

    def updateData(self):
        if self.image is not None:
            self.image.pixels = self.imageData

    def setPixel(self,x,y,color):
        if self.image is not None:
            width = self.image.size[0]
            height = self.image.size[1]
            pixels = self.imageData
            if 0 <= x < width and 0 <= y < height:
                index = (y * width + x) * 4
                self.imageData[index:index+4] = color

    def getPixel(self,x,y):
        retValue = None
        if self.image is not None:
            width = self.image.size[0]
            height = self.image.size[1]
            pixels = self.imageData
            if 0 <= x < width and 0 <= y < height:
                index = (y * width + x) * 4
                retValue = self.imageData[index:index+4]
        return retValue

    # 3. Fonction pour dessiner une ligne
    def draw_line(self, x0, y0, x1, y1, color):
        if self.image is not None:
            width = self.image.size[0]
            height = self.image.size[1]
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
        
        
    # Fonction pour remplir une région contiguë avec une couleur
    def draw_fill(self, x, y, fill_color):
        if self.image is not None:
            width = self.image.size[0]
            height = self.image.size[1]
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
        self.updateData()

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
        self.updateData()
