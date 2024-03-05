# Imports
import os 
from qgis.PyQt.QtWidgets import QToolBar, QToolButton, QAction, QMenu, QGroupBox, QLabel, QComboBox, QHBoxLayout, QVBoxLayout
from qgis.PyQt.QtGui import QIcon
from qgis.core import Qgis, QgsFeatureRequest, QgsRectangle
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapToolEmitPoint, QgsMapTool, QgsMapToolPan

# TODO: Add the functionality to the plugin which syncs the added or removed fields to be reflected on the select field combobox.
# TODO: Reflect the added or removed feature to the layer in the field combo box.
# TODO: When the action button 1 or 1 is checked, if the curser is clicked on somewhere other than the feature, there is an error is raised.
# The error is message is as follows:
            #       File "C:\Users/salar/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\BinaryLabelingPlugin\binary_labeling_plugin.py", line 289, in handle_canvas_click
            #   print(f"list_features = {list_features[0].attributes()}")
            #  IndexError: list index out of ranges                 >>> the error might because of the list_features is empty since the cursor is clicked on somewhere other than a feature.

# TODO: Create shortcuts for the action buttons. For example, the action button 1 can be assigned to the key "Y" and the action button 2 can be assigned to the key "N".
# TODO: Check if the shortcuts are working properly with other shortcuts in QGIS. For example, if the action button 1 is assigned to the key "Y", then the "Y" key should not be used for other shortcuts in QGIS.

# Plugin:
class BinaryLabelingPlugin:
    
    def __init__(self, iface):
        self.iface = iface
        self.active_button = None
        self.map_canvas = self.iface.mapCanvas()  # Get a reference to the map canvas
        self.tool = QgsMapToolEmitPoint(self.map_canvas)
        self.tool.canvasClicked.connect(self.handle_canvas_click)
        self.default_tool = QgsMapToolPan(self.map_canvas)

    def initGui(self):
        # Set the map tool when the plugin is loaded
        self.map_canvas.setMapTool(self.tool)

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
        # (1) Create the action buttons objects
        self.action_button1 = QAction(QIcon(self.label_1_icon_path), "Assign 1 (Key: Y)", self.iface.mainWindow())
        self.action_button2 = QAction(QIcon(self.label_0_icon_path), "Assign 0 (Key: N)", self.iface.mainWindow())
        # TODO: Add shortcuts to the action buttons   <<<<<<< Attention >>>>>>      <<<<<<< Attention >>>>>>      <<<<<<< Attention >>>>>>     <<<<<<< Attention >>>>>>   <<<<<<< Attention >>>>>>     <<<<<<< Attention >>>>>>    <<<<<<< Attention >>>>>>     <<<<<<< Attention >>>>>>

        # (2) Make the action buttons checkable
        self.action_button1.setCheckable(True)
        self.action_button2.setCheckable(True)

        # (3) Connect the action buttons to their respective methods
        self.action_button1.triggered.connect(self.on_action_button1_triggered)
        self.action_button2.triggered.connect(self.on_action_button2_triggered)
    
    def on_action_button1_triggered(self):
        if self.action_button2.isChecked():
            self.action_button2.setChecked(False)
        
        # Set the cursor to cross cursor if one of the action buttons is checked, otherwise set it to arrow cursor
        if self.action_button1.isChecked() or self.action_button2.isChecked():
            self.map_canvas.setCursor(Qt.CrossCursor)
            self.tool.canvasClicked.connect(self.handle_canvas_click)
            self.map_canvas.setMapTool(self.tool)

        if not self.action_button1.isChecked() and not self.action_button2.isChecked():
            self.map_canvas.setCursor(Qt.ArrowCursor)
            self.map_canvas.setMapTool(self.default_tool)
            self.iface.actionPan().setChecked(True)
        

    def on_action_button2_triggered(self):
        if self.action_button1.isChecked():
            self.action_button1.setChecked(False)

        # Set the cursor to cross cursor if one of the action buttons is checked, otherwise set it to arrow cursor
        if self.action_button1.isChecked() or self.action_button2.isChecked():
            self.map_canvas.setCursor(Qt.CrossCursor)
            self.tool.canvasClicked.connect(self.handle_canvas_click)
            self.map_canvas.setMapTool(self.tool)

        if not self.action_button1.isChecked() and not self.action_button2.isChecked():
            self.map_canvas.setCursor(Qt.ArrowCursor)
            self.map_canvas.setMapTool(self.default_tool)
            self.iface.actionPan().setChecked(True)
     
    
    def deactivate_other_toolbar_buttons(self):
        # List of action object names to exclude
        exclude_actions = ['mActionToggleEditing', 'toolboxAction', 'mActionShowPythonDialog']

        for toolbar in self.iface.mainWindow().findChildren(QToolBar):
            if toolbar != self.toolbar:  # Skip your own toolbar
                for action in toolbar.actions():
                    # Only deactivate the action if it's not in the exclude list
                    if action.isCheckable() and action.isChecked():
                        if action.objectName() not in exclude_actions:
                            action.setChecked(False)
                            
    
    def deactivate_action_buttons(self):
        self.action_button1.setChecked(False)
        self.action_button2.setChecked(False)


    def on_other_toolbar_buttons_clicked(self):
        # Create a new map tool
        new_map_tool = QgsMapToolPan(self.iface.map_canvas)
                
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
                        
    def handle_canvas_click(self, point, button):

        if self.action_button1.isChecked() and button == Qt.LeftButton:                              # if the action_button1 is checked and the left mouse button is clicked
            label = 1
            # Get the layer and field names from the comboboxes
            selected_layer, selected_field = self.get_layer_and_field()                              # Get layer and field
            print(f"Selected layer: {selected_layer.name()}")
            print(f"Selected field: {selected_field}")

            if selected_layer and selected_field:                                                    # Validate the layer and field names not to be None
                
                if selected_layer.fields().field(selected_field).type() == 4:                        # Check if the field is of type integer
                    
                    if selected_layer.isEditable():                                                  # Check if the layer is in editing mode
                        tolerance = 0.01
                        rect = QgsRectangle(point.x() - tolerance, point.y() - tolerance, point.x() + tolerance, point.y() + tolerance)
                        request = QgsFeatureRequest().setFilterRect(rect)
                        features = selected_layer.getFeatures(request)
                        list_features = list(features)
                        print(f"lenght of features = {len(list_features)}")
                        print(f"list_features = {list_features[0].attributes()}")
                        # Check if any features were identified
                        if list_features:
                            # Get the first identified feature
                            selected_layer.startEditing()          # Start editing the layer
                            for feature in list_features:
                                selected_layer.changeAttributeValue(feature.id(), selected_layer.fields().indexFromName(selected_field), label)
                            
                            
                            selected_layer.commitChanges()            # Commit the changes to the layer
                            selected_layer.startEditing()              # Stop editing the layer
                            self.iface.messageBar().pushMessage("Feature updated", f"Feature with id: {feature.attribute('id')} has been updated with the value: {label} in the field: {selected_field}.", level=Qgis.Success)
                            
                        else:
                            self.iface.messageBar().pushMessage("No feature found", "No feature was found at the clicked point.", level=Qgis.Warning)
                    elif not selected_layer.isEditable():
                        self.iface.messageBar().pushMessage("Editing mode is off", f"The selected layer is not in editing mode. Please enable the editing mode for the selected layer={selected_layer}.", level=Qgis.Warning)
                else:
                    self.iface.messageBar().pushMesage("Field type is not integer", f"The selected field: {selected_field} is not of type integer. Please select a field of type integer.", level=Qgis.Warning)
            else:
                self.iface.messageBar().pushMessage("No valid layer or field selected", "Please select a valid layer and field.", level=Qgis.Warning)


        elif self.action_button2.isChecked() and button == Qt.LeftButton:
            label = 0
            # Get the layer and field names from the comboboxes
            selected_layer, selected_field = self.get_layer_and_field()                              # Get layer and field

            if selected_layer and selected_field:                                                    # Validate the layer and field names not to be None

                if selected_layer.fields().field(selected_field).type() == 4:                        # Check if the field is of type integer

                    if selected_layer.isEditable():                                                  # Check if the layer is in editing mode
                        tolerance = 0.01
                        rect = QgsRectangle(point.x() - tolerance, point.y() - tolerance, point.x() + tolerance, point.y() + tolerance)
                        request = QgsFeatureRequest().setFilterRect(rect)
                        features = selected_layer.getFeatures(request)
                        list_features = list(features)
                        print(f"lenght of features = {len(list_features)}")
                        print(f"list_features = {list_features[0].attributes()}")
                        # Check if any features were identified
                        if list_features:
                            # Get the first identified feature
                            selected_layer.startEditing()          # Start editing the layer
                            for feature in list_features:
                                selected_layer.changeAttributeValue(feature.id(), selected_layer.fields().indexFromName(selected_field), label)
                            
                            
                            selected_layer.commitChanges()            # Commit the changes to the layer
                            selected_layer.startEditing()              # Stop editing the layer
                            self.iface.messageBar().pushMessage("Feature updated", f"Feature with id: {feature.attribute('id')} has been updated with the value: {label} in the field: {selected_field}.", level=Qgis.Success)
                        else:
                            self.iface.messageBar().pushMessage("No feature found", "No feature was found at the clicked point.", level=Qgis.Warning)
                    
                    elif not selected_layer.isEditable():
                        self.iface.messageBar().pushMessage("Editing mode is off", f"The selected layer is not in editing mode. Please enable the editing mode for the selected layer={selected_layer}.", level=Qgis.Warning)
                else:
                    self.iface.messageBar().pushMesage("Field type is not integer", f"The selected field: {selected_field} is not of type integer. Please select a field of type integer.", level=Qgis.Warning)
            else:
                self.iface.messageBar().pushMessage("No valid layer or field selected", "Please select a valid layer and field.", level=Qgis.Warning)

    def get_layer_and_field(self):
        selected_layer = None
        selected_field = None

        # Get the selected layer and the select field from the comboboxes. Also check if the selected layer and field are valid and selected.
        if self.layer_combo.currentIndex() < 0:
            self.iface.messageBar().pushMessage("No valid layer selected", "Please select a valid layer.", level=Qgis.Warning) 
        elif self.layer_combo.currentIndex() >= 0:
            selected_layer = self.iface.mapCanvas().layers()[self.layer_combo.currentIndex()]  
            
            if self.field_combo.currentIndex() < 0:
                self.iface.messageBar().pushMessage("No valid field selected", "Please select a valid field.", level=Qgis.Warning) 
            elif self.field_combo.currentIndex() >= 0:
                selected_field = self.field_combo.currentText()
                
        return selected_layer, selected_field

    def check_field_type(self, selected_layer, selected_field):
        # Check if the selected field from the selected layer is from a datatype as integer.
        if selected_layer.fields().field(selected_field).type() != 10:
            print("The selected field is not of type integer")
        
    def check_editing_mode(self, selected_layer):
        # Check if the Toggle Editing mode is enabled for the selected layer. Retrun a message if not.
        if not selected_layer.isEditable():
            print("The selected layer is not in editing mode. Please enable the editing mode for the selected layer.")
    

    def unload(self):
        self.iface.mainWindow().removeToolBar(self.toolbar)
        self.toolbar.clear()
        if self.toolbar is not None:
            self.toolbar.deleteLater()
        
        # Reset the map tool when the plugin is unloaded
        self.map_canvas.unsetMapTool(self.tool)





            