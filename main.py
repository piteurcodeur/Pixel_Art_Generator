import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QStatusBar, QToolBar, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QGridLayout, QSlider, QMessageBox, QInputDialog
from PyQt5.QtCore import QCoreApplication, QSize, Qt
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QColor, QPalette
from PIL import ImageColor
import random
import os

class Pixel(QPushButton):
    def __init__(self, x, y):
        super().__init__()
        self.pos = (x, y)
        self.couleur = (255, 255, 255)

class CouleurPalette(QPushButton):
    def __init__(self, x, y):
        super().__init__()
        self.pos = (x, y)
        

class Fenetre(QMainWindow):

    'Juste un simple générateur de pixel-art'

    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 800)
        self.setWindowTitle('GENERATEUR DE PIXEL-ART')
        #####

        self.parametres = {
            'outil': 'Stylo',
            'filtre': None,
            'enregistre': False,
            'enregistre_sous': False,
            'current_color': (0, 0, 0),
            'colorBaguette' : (0, 0, 0),
            'couleurPot' : (0,0,0),
            'choixPersonnalColor' : False, 
            'grille' : False,
            'estVide': True,
        }

        self.myPalette = QPalette()

        self.toolbar = QToolBar("Barre d'outils")
        self.toolbar.setIconSize(QSize(30, 30))
        self.addToolBar(self.toolbar)
        liste_menu = [('Grille'), ('Filtre'), ('Effet'),
                      ('onSave'), ('onQuit')]
        liste_sous_menu = [[('reinitialiser', 'D'), ('reinitialiser palette', 'P')], [
            ('rouge', 'R'), ('vert', 'V'), ('bleu', 'B'), ('negatif', 'N'), ('gris', 'G')], [('Afficher grille', 'E')], [('onSave', 'S')], [('onQuit', 'Q')]]

        for menu in liste_menu:
            self.menuItems = self.menuBar().addMenu(f"{menu}")
            for sous_menu in liste_sous_menu[liste_menu.index(menu)]:
                self.action = QAction(
                    QIcon(f'icons/{sous_menu[0]}.png'), f"{sous_menu[0]}", self)
                self.action.setStatusTip(f"{sous_menu[0]}")
                #self.action.triggered.connect(self.onDitClick)
                self.options_toolbar(sous_menu[0], self.action)
                raccourci = sous_menu[1]
                self.action.setShortcut(QKeySequence(f'Ctrl+{raccourci}'))
                self.menuItems.addAction(self.action)

                self.bouton_toolbar = QAction(
                    QIcon(f"icons/{sous_menu[0]}.png"), '',   self)
                self.bouton_toolbar.setStatusTip(f"{sous_menu[0]}")
                #self.bouton_toolbar.triggered.connect(self.onReset)
                self.options_toolbar(sous_menu[0], self.bouton_toolbar)
                self.toolbar.addAction(self.bouton_toolbar)

        # barre du bas qui indique le statut
        self.setStatusBar(QStatusBar(self))

        # debut de la fenetre
        self.surface = QWidget()
        self.main_layout = QVBoxLayout()

        self.layout_top = QHBoxLayout()  # layout du top
        self.label_outil = QLabel('OUTILS')
        self.label_outil.setFont(QFont('Arial', 12))
        self.layout_top.addWidget(self.label_outil)
        self.combo1 = QComboBox()
        self.combo1.setFixedHeight(50)
        self.combo1.setFont(QFont('Arial', 12))
        for i in ['Stylo', 'Gomme', 'Baguette', 'Pot']:
            self.combo1.addItem(i)
        self.combo1.activated[str].connect(self.select_outils)
        self.layout_top.addWidget(self.combo1)

        self.label_couleur = QLabel('')
        self.label_couleur.setFixedSize(50, 50)
        self.label_couleur.setAutoFillBackground(True)
        self.myPalette.setColor(QPalette.Window, self.RGBToQColor((0, 0, 0)))
        self.label_couleur.setPalette(self.myPalette)
        self.layout_top.addWidget(self.label_couleur)

        self.combo2 = QComboBox()
        self.combo2.setFixedHeight(50)
        self.combo2.setFont(QFont('Arial', 12))
        try:
            self.combo2.addItem('Load project')
            for i in os.listdir('save'):
                self.combo2.addItem(i.strip('.txt'))
        except:
            self.combo2.addItem('Load project')
        self.combo2.activated[str].connect(self.afficher_last_project)
        self.layout_top.addWidget(self.combo2)

        self.layout_center = QHBoxLayout()

        self.layout_left = QVBoxLayout()
        self.label_palette = QLabel('COULEURS')
        self.label_palette.setFont(QFont('Arial', 12))
        self.layout_left.addWidget(self.label_palette)
        self.liste_couleurs_predef_palette = [(0, 0, 0), (205, 97, 152), (0, 36, 204), (204, 123, 0), (
            204, 0, 0), (194, 211, 0), (2, 175, 0), (255, 255, 255), (1, 102, 0), (101, 0, 102)]
        c = 0
        self.boardPalette = []
        for i in range(5):
            self.mini_lay = QHBoxLayout()
            for j in range(2):
                self.bouton_palette = CouleurPalette(i, j)
                self.boardPalette.append(self.bouton_palette)
                self.bouton_palette.setFixedSize(50, 50)
                self.bouton_palette.clicked.connect(
                    self.select_couleur_palette)
                self.give_color(self.bouton_palette,
                                self.liste_couleurs_predef_palette[c])
                self.mini_lay.addWidget(self.bouton_palette)
                c += 1
            self.layout_left.addLayout(self.mini_lay)
        self.layout_center.addLayout(self.layout_left)

        self.sliders_layout = QVBoxLayout()
        for _ in range(3):   
            slider_layout = QHBoxLayout()
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(255)
            slider.valueChanged.connect(self.slider_position)
            slider_layout.addWidget(slider)
            label = QLabel('0')
            label.setFont(QFont('Arial', 10))
            slider_layout.addWidget(label)
            self.sliders_layout.addLayout(slider_layout)

        self.label_valider_couleur = QLabel()
        self.label_valider_couleur.setFixedSize(200,40)
        self.button_valider_couleur = QPushButton('Ajouter la couleur à la palette')
        self.button_valider_couleur.clicked.connect(self.get_personnal_color)
        self.layout_left.addLayout(self.sliders_layout)
        self.layout_left.addWidget(self.label_valider_couleur)
        self.layout_left.addWidget(self.button_valider_couleur)


        self.layout_grille_label = QVBoxLayout()
        self.layout_grille = QGridLayout()
        self.label_grille = QLabel('GRILLE')
        self.label_grille.setFont(QFont('Arial', 12))
        self.label_grille.setAlignment(Qt.AlignCenter)
        self.layout_grille_label.addWidget(self.label_grille)
        self.grille_size = 20
        self.board = []
        for i in range(self.grille_size):
            for j in range(self.grille_size):
                self.bouton_grille = Pixel(i, j)
                self.bouton_grille.setFixedSize(50, 50)
                self.bouton_grille.setAutoFillBackground(True)
                self.myPalette.setColor(QPalette.Button, QColor(255,255,255))
                self.myPalette.setColor(QPalette.Base, QColor(255,255,255))
                self.bouton_grille.setPalette(self.myPalette)
                self.bouton_grille.setFlat(True)
                self.bouton_grille.clicked.connect(self.bouton_grille_clicked)
                self.board.append(self.bouton_grille)
                self.layout_grille.addWidget(self.bouton_grille, i, j)
        self.layout_grille_label.addLayout(self.layout_grille)

        self.layout_center.addLayout(self.layout_grille_label)

        self.main_layout.addLayout(self.layout_top)
        self.main_layout.addLayout(self.layout_center)
        self.surface.setLayout(self.main_layout)
        self.setCentralWidget(self.surface)


    def get_personnal_color(self):
        self.popup = QMessageBox(QMessageBox.Information, 'Info' , 'vous devez choisir un emplacement dans la palette, puis sélectionner une couleur dans la palette' )
        self.parametres['choixPersonnalColor'] = True
        self.popup.show()

    def slider_position(self): #pour la position des sliders 
        for i in range(self.sliders_layout.count()):
            slider_layout = self.sliders_layout.itemAt(i).layout()
            slider = slider_layout.itemAt(0).widget()
            label = slider_layout.itemAt(1).widget()
            label.setText(str(slider.value()))
        self.get_color()

    def get_color(self):
        couleur = QColor(
            int(self.sliders_layout.itemAt(0).layout().itemAt(1).widget().text()),
            int(self.sliders_layout.itemAt(1).layout().itemAt(1).widget().text()),
            int(self.sliders_layout.itemAt(2).layout().itemAt(1).widget().text()))
        self.label_valider_couleur.setAutoFillBackground(True)
        self.myPalette.setColor(QPalette.Window, couleur)
        self.label_valider_couleur.setPalette(self.myPalette)

    def give_color(self, button, rgb):
        couleur = self.RGBToQColor(rgb)
        button.setAutoFillBackground(True)
        self.myPalette.setColor(QPalette.Button, couleur)
        button.setPalette(self.myPalette)

    def select_outils(self, text):
        self.parametres['outil'] = text

    def bouton_grille_clicked(self):
        self.parametres['enregistre'] = False
        self.parametres['estVide'] = False
        outil = self.parametres['outil']
        if outil == 'Stylo':
            couleur = self.parametres['current_color']
            self.give_color(self.sender(), couleur)
        if outil == 'Gomme':
            self.give_color(self.sender(), (255, 255, 255))
        if outil == 'Baguette' :
            couleur = self.parametres['current_color']          #couleur dans les paramètres a effacer
            couleur_bouton = self.sender().palette().button().color().name() #couleur du bouton actuel
            couleur_bouton = self.couleurToRGB(couleur_bouton)
            if couleur_bouton == couleur :
                self.give_color(self.sender(), (255, 255, 255))
        if outil == 'Pot' :
            x, y = self.sender().pos
            self.colorAround(x, y)
    
    def colorAround(self, posx, posy):
        current_bouton = self.layout_grille.itemAtPosition(posx, posy).widget()
        current_couleur = current_bouton.palette().button().color()
        self.parametres['couleurPot'] = current_couleur
        couleur_target = self.parametres['current_color']
        queue = [(posx, posy)]
        visited = [(posx, posy)]
        while len(queue)  > 0 : 
            row, col = queue.pop()
            if row < 0 or col < 0 or row >= self.grille_size or col >= self.grille_size:
                continue
            else :
                current_bouton = self.layout_grille.itemAtPosition(row, col).widget()
                current_couleur = current_bouton.palette().button().color()  
            if current_couleur != self.parametres['couleurPot'] :
                continue
            self.give_color(current_bouton, couleur_target)
            if not(row - 1, col) in visited :
                queue.append((row - 1, col))  # Pixel sup
                visited.append((row - 1, col))
            if not(row + 1, col) in visited :
                queue.append((row + 1, col)) 
                visited.append((row + 1, col)) # Pixel inf  
            if not(row, col - 1) in visited:
                queue.append((row, col - 1))
                visited.append((row, col - 1))  # Pixel gauche
            if not(row, col + 1) in visited :
                queue.append((row, col + 1))
                visited.append((row, col + 1))  #pixel droit

    def select_couleur_palette(self):
        if self.parametres['choixPersonnalColor'] == False :
            couleur = self.sender().palette().button().color().name()
            couleur = self.couleurToRGB(couleur)
            self.parametres['current_color'] = couleur
            couleur = self.RGBToQColor(couleur)
            self.myPalette.setColor(QPalette.Window, couleur)
            self.label_couleur.setPalette(self.myPalette)
        else :
            color = self.label_valider_couleur.palette().color(QPalette.Window).name()
            self.give_color(self.sender(), self.couleurToRGB(color))
            self.parametres['choixPersonnalColor'] = False 

       

    def couleurToRGB(self, couleur):
        return ImageColor.getcolor(str(couleur), "RGB")

    def RGBToQColor(self, rgb):
        return QColor(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    
    def options_toolbar(self, option, bouton): #donne la fonction correspondante au bouton cliqué
        if option == 'reinitialiser':
            bouton.triggered.connect(self.onReset)
        if option == 'reinitialiser palette':
            bouton.triggered.connect(self.onResetPalette)
        if option == 'rouge' :
            bouton.triggered.connect(self.filtre_rouge)
        if option ==  'vert':
            bouton.triggered.connect(self.filtre_vert)
        if option == 'bleu':
            bouton.triggered.connect(self.filtre_bleu)
        if option == 'negatif':
            bouton.triggered.connect(self.filtre_negatif)
        if option == 'gris':
            bouton.triggered.connect(self.filtre_gris)
        if option == 'Afficher grille':
            bouton.triggered.connect(self.effet)
        if option == 'onSave':
            bouton.triggered.connect(self.onSave)
        if option == 'onQuit':
            bouton.triggered.connect(self.onQuit)
        

    def onReset(self):
        for i in self.board :
            self.give_color(i, (255,255,255))

    def onResetPalette(self):
        for i in range(len(self.boardPalette)) :
            self.give_color(self.boardPalette[i], self.liste_couleurs_predef_palette[i])
        return
    def filtre_rouge(self):
        self.create_filtre(r=True)
        return
    def filtre_bleu(self):
        self.create_filtre(b=True)
        return
    def filtre_vert(self):
        self.create_filtre(g=True)
        return
    def filtre_negatif(self):
        for i in self.board :
            self.give_color(i, self.negatif_couleur_rgb(self.couleurToRGB(i.palette().button().color().name())))
        return
    def filtre_gris(self):
        self.create_filtre(gr=True)
        return
    def effet(self):
        for i in self.board:
            if self.parametres['grille'] == False:
                i.setFlat(False)
                
                
            elif self.parametres['grille'] == True:
                i.setFlat(True)
        self.parametres['grille'] = False if self.parametres['grille'] == True else True   
        return
    
    def onSave(self):
        if self.parametres['estVide'] == False :
            matrice_image = []
            for i in self.board :
                matrice_image.append(self.couleurToRGB(i.palette().button().color().name()))
            if self.parametres['enregistre_sous'] == False :
                text, ok = QInputDialog.getText(self, 'Enregistrer','Sauvegarder votre travail')
                if ok:
                    fichier = open(f"save/{text}.txt", "w")
                    fichier.write(str(matrice_image))
                    fichier.close()
                    self.combo2.addItem(text)
                    self.parametres['enregistre_sous'] = text
                    return True
            elif self.parametres['enregistre'] == False:
                fichier = open(f"save/{self.parametres['enregistre_sous']}.txt", "w")
                fichier.write(str(matrice_image))
                fichier.close()
                self.parametres['enregistre'] = True
                return True
            return False
        return
    

    def onQuit(self):
        if (self.parametres['enregistre_sous'] == False or self.parametres['enregistre'] == False ) and self.parametres['estVide'] == False:
            self.onSave()
        
        QApplication.quit()
        return
    
    def create_filtre(self, r=False, g=False, b=False, gr=False):
        palette = []
        for k in range(10):
            if not gr:
                red = 255 if r == True else random.randint(0, 150)
                green = 255 if g == True else random.randint(0,150)
                blue = 255 if b == True else random.randint(0, 150)
            else :
                red, blue, green = (k+1)*25,  (k+1)*25,  (k+1)*25
            palette.append((red, green, blue))
        for i in range(len(self.boardPalette)) :
            self.give_color(self.boardPalette[i], palette[i])
    
    def negatif_couleur_rgb(self, couleur):
        red_neg= 255 - couleur[0]
        green_neg = 255 - couleur[1]
        blue_neg = 255 - couleur[2]
        return (red_neg, green_neg, blue_neg)

    def afficher_last_project(self, text):
        if self.parametres['enregistre'] == self.parametres['enregistre_sous'] == True :
            if text != 'Load project' :
                with open(f'save/{text}.txt', 'r') as file :
                    contenu = eval(file.readlines()[0])
                    for i in range(len(self.board)) :
                        self.give_color(self.board[i], contenu[i])
        else :
            saved = self.onSave()
            if text != 'Load project' :
                with open(f'save/{text}.txt', 'r') as file :
                    contenu = eval(file.readlines()[0])
                    for i in range(len(self.board)) :
                        self.give_color(self.board[i], contenu[i])
            

        


app = QCoreApplication.instance()
if app is None:
    app = QApplication(sys.argv)
# utiliser fusion sinon c'est juste la bordure qui se colore
app.setStyle('Fusion')
window = Fenetre()
window.show()

app.exec_()
