# Imports
import os 
from qgis.PyQt.QtWidgets import QToolBar, QToolButton, QAction, QActionGroup, QMenu, QGroupBox, QLabel, QComboBox, QHBoxLayout, QVBoxLayout
from qgis.PyQt.QtGui import QIcon



# Plugin:
class BinaryLabelingPlugin:
    
    def __init__(self, iface):
        self.iface = iface
        self.active_button = None
        self.map_canvas = self.iface.mapCanvas()  # Get a reference to the map canvas

    def initGui(self):
        # Create toolbar
        self.toolbar = QToolBar("Binary Labeling Toolbar")
        self.toolbar.setObjectName("Binary Labeling Toolbar")
        self.iface.addToolBar(self.toolbar)

        # Get toolbar's icons file paths
        self.settings_icon_path = os.path.join(os.path.dirname(__file__), "media/settings.png")
        self.label_1_icon_path = os.path.join(os.path.dirname(__file__), "media/label_1.png")
        self.label_0_icon_path = os.path.join(os.path.dirname(__file__), "media/label_0.png")

        # create Settings Menu:
        self.create_settings_menu()

        # Create a ToolButton and add a Settings Menu to it.
        self.tool_button = QToolButton(self.iface.mainWindow())     # Create a QToolButton and set it as a child of the main window
        self.tool_button.setIcon(QIcon(self.settings_icon_path))    # Set the icon of the tool button to the image located at self.settings_icon_path
        self.tool_button.setPopupMode(QToolButton.InstantPopup)     # Set the popup mode of the tool button to InstantPopup, which shows the menu when clicked
        self.tool_button.setMenu(self.settings_menu)                # Set the menu of the tool button to the settings_menu created earlier, So when the tool button is clicked, the settings_menu will be shown.

        # Add the tool button to the toolbar
        self.toolbar.addWidget(self.tool_button)

        # Create two action buttons. One for assigning 1 and the other for assigning 0. However, for making them synced together (i.e. only one of them can be checked at a time), we need to create a QActionGroup object and add the action buttons to it.
        # For doing that we need to create a method called create_action_buttons() that creates the action buttons and adds them to the action group.
        self.create_action_buttons()

        # Add the action buttons to the toolbar
        self.toolbar.addAction(self.action_button1)
        self.toolbar.addAction(self.action_button2)

        # Connect to signals for dynamically added or removed layers
        self.map_canvas.layersChanged.connect(self.layer_combo_update)
        
        # TODO: Check if the connection is correct between the layer_combo and the field_combo_populate method.
        # Connect the currentIndexChanged signal of the layer_combo combobox to the field_combo_populate slot
        self.layer_combo.currentIndexChanged.connect(self.field_combo_populate)

        # Add the toolbar to the main window
        self.iface.addToolBar(self.toolbar)

    def create_action_buttons(self):
        # (1) Create an action group object
        self.action_group = QActionGroup(self.iface.mainWindow())
        self.action_group.setExclusive(True)    # Make the action group exclusive, so only one of the action buttons can be checked at a time.

        # (2) Create the action buttons objects
        self.action_button1 = QAction(QIcon(self.label_1_icon_path), "Assign 1 (Key: Y)", self.iface.mainWindow())
        self.action_button2 = QAction(QIcon(self.label_0_icon_path), "Assign 0 (Key: N)", self.iface.mainWindow())
        # TODO: Add shortcuts to the action buttons   <<<<<<< Attention >>>>>>      <<<<<<< Attention >>>>>>      <<<<<<< Attention >>>>>>     <<<<<<< Attention >>>>>>   <<<<<<< Attention >>>>>>     <<<<<<< Attention >>>>>>    <<<<<<< Attention >>>>>>     <<<<<<< Attention >>>>>>

        # (3) Make the action buttons checkable
        self.action_button1.setCheckable(True)
        self.action_button2.setCheckable(True)

        # (4) Add the action buttons to the action group
        self.action_group.addAction(self.action_button1)
        self.action_group.addAction(self.action_button2)

        # (5) Connect the action buttons to their respective methods
        self.action_button1.triggered.connect(self.toggle_action_button)
        self.action_button2.triggered.connect(self.toggle_action_button)
    
    def toggle_action_button(self):
        # Get the action button that triggered the signal
        action_button = self.sender()

        # Check if the action button is currently checked
        if action_button.isChecked():
            # If it is, uncheck it
            action_button.setChecked(False)

    def layer_combo_update(self):
        # Clear the layer combo box
        self.layer_combo.clear()

        # Add the names of the vector layers to the layer_combo
        self.layer_combo.addItems([layer.name() for layer in self.iface.mapCanvas().layers() if layer.type() == 0])

        # Call the field_combo_populate method to populate the field combo box with the field names of the selected layer
        self.field_combo_populate()
        
    def create_settings_menu(self):
        # Create a new menu
        self.settings_menu = QMenu(self.iface.mainWindow())

        # Create a group box with the title "Binary Labeling Settings"
        self.group_box = QGroupBox("Binary Labeling Settings")

        # (1) Vector layer selection (layer & combo box)
        # Create a label and a comboxo to select a desired vector layer
        self.layer_label = QLabel("Select a layer:", self.group_box)
        self.layer_combo = QComboBox(self.group_box)
        self.layer_combo.setMinimumWidth(400)
        self.layer_combo.addItems([layer.name() for layer in self.iface.mapCanvas().layers() if layer.type() == 0])
        self.layer_combo.setCurrentIndex(-1)
        
        # Creat QHBox Layout for the layer label & layer combobox.
        self.box1_layout = QHBoxLayout()
        self.box1_layout.addWidget(self.layer_label)
        self.box1_layout.addWidget(self.layer_combo)

        # (2) Field selection (layer & combo box)
        # Create a label and a combobox to select a desired field
        self.field_label = QLabel("Select a field:", self.group_box)
        self.field_combo = QComboBox(self.group_box)
        self.field_combo.setMinimumWidth(400)
        self.field_combo.setCurrentIndex(-1)

        # Create QHBox Layout for the field label & field combobox.
        self.box2_layout = QHBoxLayout()
        self.box2_layout.addWidget(self.field_label)
        self.box2_layout.addWidget(self.field_combo)

        # Create a layout for the group box
        self.group_box_layout = QVBoxLayout()
        self.group_box_layout.addLayout(self.box1_layout) 
        self.group_box_layout.addLayout(self.box2_layout)
        self.group_box.setLayout(self.group_box_layout)   # Set the layout of the group box to the group_box_layout

        # Add the group box to the settings menu
        self.menu_layout = QVBoxLayout(self.settings_menu)
        self.menu_layout.addWidget(self.group_box)
        self.settings_menu.setLayout(self.menu_layout)
    
    def field_combo_populate(self):
        # Clear the field combo box
        self.field_combo.clear()

        # Check if there is a valid selection in the layer_combo
        if self.layer_combo.currentIndex() >= 0:
            # Get the selected layer
            selected_layer = self.iface.mapCanvas().layers()[self.layer_combo.currentIndex()]

            # Add the field names to the field combo box (self.field_combo)
            self.field_combo.addItems([field.name() for field in selected_layer.fields()])

    def unload(self):
        self.iface.mainWindow().removeToolBar(self.toolbar)
        self.toolbar.clear()
        if self.toolbar is not None:
            self.toolbar.deleteLater()





            