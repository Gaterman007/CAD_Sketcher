import bpy
import os

from bpy.utils import register_classes_factory
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.types import Operator, Context, Event, PropertyGroup

from .. import global_data
from ..utilities.highlighting import HighlightElement
from ..declarations import Operators
from ..ui.widgets.bl_ui_drag_panel import BL_UI_Drag_Panel
from ..ui.widgets.bl_ui_label import BL_UI_Label
from ..ui.widgets.bl_ui_textbox import BL_UI_Textbox
from ..ui.widgets.bl_ui_checkbox import BL_UI_Checkbox
from ..ui.widgets.bl_ui_button import BL_UI_Button
from ..ui.widgets.bl_ui_image import BL_UI_Image
from ..ui.widgets.bl_ui_dropdown import BL_UI_DropDown
from ..ui.widgets.bl_ui_seperator import BL_UI_Seperator
from ..ui.widgets.bl_ui_toolbar import BL_UI_Toolbar

from ..ui.widgets.Icons.SVG_Icon import SVG_Icon

class View3D_OT_slvs_context_dialog(Operator, HighlightElement):
    """Show element's settings"""

    bl_idname = Operators.ContextDialog
    bl_label = "Dialog"

    type: StringProperty(name="Type", options={"SKIP_SAVE"})
    index: IntProperty(name="Index", default=-1, options={"SKIP_SAVE"})
    delayed: BoolProperty(default=False)

    bl_options = {'UNDO'}
    
    @classmethod
    def description(cls, context: Context, properties: PropertyGroup):
        cls.handle_highlight_hover(context, properties)
        if properties.type:
            return properties.type.capitalize()
        return cls.__doc__
        
    def invoke(self, context: Context, event: Event):
        self.getElement(context)
        self.toolbar = False
        self.modal = False
        self.dialog = False
        if not self.element:
            self.loadToolbar(context)
            self.startModal(context)
            return {"RUNNING_MODAL"}
#            bpy.ops.wm.call_menu(name="VIEW3D_MT_selected_menu")
#            return {"FINISHED"}
        if not self.delayed:
            self.loadDialog(context)
        self.startModal(context)
        return {"RUNNING_MODAL"}

    def loadToolbar(self,context):
        if not self.toolbar:
            if not ('Toolbar' in global_data.created_dialog.keys()):
                self.panelWidth = 300
                self.panelHeight = 38
                self.panelX = (context.region.width // 2) - (self.panelWidth // 2)
                self.panelY = (context.region.height // 2) - (self.panelHeight // 2) + 400       
                toolbarpanel = BL_UI_Drag_Panel(self.panelX, self.panelY, self.panelWidth, self.panelHeight)
                toolbarpanel.bg_color = (0.0, 0.0, 0.0, 0.2)
                newtoolbar = BL_UI_Toolbar(3,3,38,38,buttonWidth = 32, buttonHeight = 32)
                newtoolbar.addButton("Distance",Operators.AddDistance,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("Diametre",Operators.AddDiameter,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("Angle",Operators.AddAngle,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("Coincident",Operators.AddCoincident,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("equal",Operators.AddEqual,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("vertical",Operators.AddVertical,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("horizontal",Operators.AddHorizontal,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("parallel",Operators.AddParallel,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("Perpendicular",Operators.AddPerpendicular,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("tangent",Operators.AddTangent,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("midpoint",Operators.AddMidPoint,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                newtoolbar.addButton("ratio",Operators.AddRatio,[('INVOKE_DEFAULT'),("wait_for_input",True)])
                toolbarpanel.add_widget(newtoolbar)
                toolbarpanel.width = newtoolbar.width + 6
                global_data.created_dialog['Toolbar'] = toolbarpanel
            global_data.dialog['Toolbar'] = global_data.created_dialog['Toolbar']
            self.toolbar = True

    def removeToolbar(self):
        if self.toolbar:
            if 'Toolbar' in global_data.dialog.keys():
                del global_data.dialog['Toolbar']
            bpy.context.region.tag_redraw()
            self.toolbar = False

    def loadDialog(self,context):
        if not self.dialog:
            self.layoutDialog(context)
            self.dialog = True

    def removeDialog(self):
        if self.dialog:
            del global_data.dialog['Menu1']
            self.panel.eraseChilds()
            del self.panel
            bpy.context.region.tag_redraw()

    def startModal(self,context):
        if not self.modal:
            context.window_manager.modal_handler_add(self)
            self.modal = True
            self.rightMouseDown = False
        
    def modal(self, context: Context, event: Event):
        retValue = {'RUNNING_MODAL'}

        if not self.dialog and not self.toolbar:
            if not self.element:
                self.loadToolbar(context)
            else:
                self.loadDialog(context)
            return retValue
        
        if event.type in {'ESC'}:  # Permet de quitter avec ESC
            self.removeDialog()
            self.removeToolbar()
            return {'CANCELLED'}

        if event.type == 'RIGHTMOUSE':
            if event.value == 'PRESS':
                self.rightMouseDown = True
            elif self.rightMouseDown and event.value == 'RELEASE':
                self.removeDialog()
                self.removeToolbar()
                return {'FINISHED'}
        
        retValue = {'PASS_THROUGH'}
            
        for widget in global_data.dialog.values():
            retValue, handled = widget.handle_event(context,event)
            if handled:
                break
        if retValue != {'RUNNING_MODAL'} and retValue != {'PASS_THROUGH'}:
            self.removeDialog()
            self.removeToolbar()
            
        return retValue

    def getElement(self,context):
        # create from element
        entity_index = None
        constraint_index = None
        self.element = None

        # Constraints
        if self.properties.is_property_set("type"):
            constraint_index = self.index
            constraints = context.scene.sketcher.constraints
            self.element = constraints.get_from_type_index(self.type, self.index)
        else:
            # Entities
            entity_index = (
                self.index
                if self.properties.is_property_set("index")
                else global_data.hover
            )

            if entity_index != -1:
                self.element = context.scene.sketcher.entities.get(entity_index)

    def getLayoutDef(self,propname):
        # Parcourt les annotations (propriétés) de la classe et de ses superclasses
        for base_cls in type(self.element).__mro__:  # __mro__ retourne la chaîne d'héritage
            if hasattr(base_cls, '__annotations__'):
                for prop_name, prop_info in base_cls.__annotations__.items():
                    if prop_name == propname:
                        if hasattr(prop_info,"function"):
                            return prop_info
        return None
        
    def findLayoutData(self,propname):
        # Parcourt les annotations (propriétés) de la classe et de ses superclasses
        for base_cls in type(self.element).__mro__:  # __mro__ retourne la chaîne d'héritage
            if hasattr(base_cls, '__annotations__'):
#                print(f"Properties in {base_cls.__name__}:")    
                for prop_name, prop_info in base_cls.__annotations__.items():
                    if prop_name == propname:
#                        print(f"  Type: {prop_info}")
                        if hasattr(prop_info,"function"):
#                                print(f"Function: {prop_info.function}")
                            print(f"  Property: {prop_name}")
                            print(f"Function: {prop_info.function.__name__}")
                            if hasattr(prop_info,"keywords"):
                                if 'attr' in prop_info.keywords:
                                    print(f"attr: {prop_info.keywords['attr']}")
                                if 'name' in prop_info.keywords:
                                    print(f"name: {prop_info.keywords['name']}")
                                if 'description' in prop_info.keywords:
                                    print(f"description: {prop_info.keywords['description']}")
                                if 'subtype' in prop_info.keywords:
                                    print(f"subType: {prop_info.keywords['subtype']}")
                                if 'unit' in prop_info.keywords:
                                    print(f"unit: {prop_info.keywords['unit']}")
                                if 'get' in prop_info.keywords:
                                    print(f"getter: {prop_info.keywords['get']}")
                                if 'set' in prop_info.keywords:
                                    print(f"setter: {prop_info.keywords['set']}")
                                if 'update' in prop_info.keywords:
                                    print(f"updatter: {prop_info.keywords['update']}")
                                if 'default' in prop_info.keywords:
                                    print(f"default: {prop_info.keywords['default']}")
                                if 'maxlen' in prop_info.keywords:
                                    print(f"maxlen: {prop_info.keywords['maxlen']}")
                                if 'translation_context' in prop_info.keywords:
                                    print(f"Translation Context: {prop_info.keywords['translation_context']}")
                                if 'options' in prop_info.keywords:
                                    print(f"options: {prop_info.keywords['options']}")
                                if 'override' in prop_info.keywords:
                                    print(f"overide: {prop_info.keywords['override']}")
                                if 'tags' in prop_info.keywords:
                                    print(f"tags: {prop_info.keywords['tags']}")
                                if 'size' in prop_info.keywords:
                                    print(f"size: {prop_info.keywords['size']}")
                                if 'items' in prop_info.keywords:
                                    print(f"items: {prop_info.keywords['items']}")
                                if 'min' in prop_info.keywords:
                                    print(f"min: {prop_info.keywords['min']}")
                                if 'max' in prop_info.keywords:
                                    print(f"max: {prop_info.keywords['max']}")
                                if 'soft_min' in prop_info.keywords:
                                    print(f"soft min: {prop_info.keywords['soft_min']}")
                                if 'soft_max' in prop_info.keywords:
                                    print(f"soft max: {prop_info.keywords['soft_max']}")
                                if 'step' in prop_info.keywords:
                                    print(f"step: {prop_info.keywords['step']}")
                                if 'precision' in prop_info.keywords:
                                    print(f"precision: {prop_info.keywords['precision']}")
                                if 'poll' in prop_info.keywords:
                                    print(f"poll: {prop_info.keywords['poll']}")
                                if 'search' in prop_info.keywords:
                                    print(f"search: {prop_info.keywords['search']}")
                                if 'search_options' in prop_info.keywords:
                                    print(f"search options: {prop_info.keywords['search_options']}")
#                            if hasattr(prop_info,"keywords"):
#                                print(f"All Keywords: {prop_info.keywords}")
                            print()
                            
    def get_operator_class_by_idname(self,idname):
        # Parcourir toutes les sous-classes de bpy.types.Operator
        for cls in bpy.types.Operator.__subclasses__():
            # Vérifier si le bl_idname de la classe correspond à celui recherché
            if hasattr(cls, "bl_idname") and cls.bl_idname == idname:
                return cls
        return None                           

    def layoutWidgets(self,y_pos,dialogList,panel):
        if dialogList is not None:
            for propname in dialogList:
                if isinstance(propname, list):
                    y_pos = self.layoutWidgets(y_pos,propname,panel)
                else:
                    for key, value in propname.items():
                        if key == "property":
                            y_pos = self.addPropToDialog(value,y_pos,panel)
                        elif key == "label":
                            newwidget = BL_UI_Label(8,y_pos,280,20,value)
                            if newwidget is not None:
                                panel.add_widget(newwidget)
                                y_pos += 26
                        elif key == "seperator":
                            newwidget = BL_UI_Seperator(8,y_pos,280,20)
                            if newwidget is not None:
                                panel.add_widget(newwidget)
                                y_pos += 26
                        elif key == "button":
                            ops = value["ops"]
                            ops_class = self.get_operator_class_by_idname(ops)
                            iconName = value["icon"]
                            newiconwidget = BL_UI_Image(8,y_pos,24,24)
                            newiconwidget.set_image(iconName)
                            newwidget = BL_UI_Button(8 + 26,y_pos,280 - 26,24,ops_class.bl_label)
                            newwidget.setOpClass(ops,value["index"],value["type"])
                            newwidget.setPropetyElement(self.element)
                            if newwidget is not None:
                                if newiconwidget is not None:
                                    panel.add_widget(newiconwidget)
                                panel.add_widget(newwidget)
                                y_pos += 26
                                
                        elif key == "image":
                            iconName = value["icon"]
                            newwidget = BL_UI_Image(8,y_pos,22,22)
                            newwidget.set_image(iconName)
                            if newwidget is not None:
                                panel.add_widget(newwidget)
                                y_pos += 26
        return y_pos

    def layoutDialog(self,context):
        self.panelX = 200
        self.panelY = 200
        self.panelWidth = 300
        self.panelHeight = 400
        self.panelX = (context.region.width // 2) - (self.panelWidth // 2)
        self.panelY = (context.region.height // 2) - (self.panelHeight // 2)        
        if self.element is not None:
            dialogList = self.element.getDialog(None)
            self.panel = BL_UI_Drag_Panel(self.panelX, self.panelY, self.panelWidth, self.panelHeight)
            y_pos = 8
            y_pos = self.layoutWidgets(y_pos,dialogList,self.panel)
            self.panel.height = y_pos + 8
            global_data.dialog['Menu1'] = self.panel
        return True

    def addPropToDialog(self,propname,ypos,panel):
        prop_info = self.getLayoutDef(propname)
        # create widget
        name_widget = None
        if hasattr(prop_info,"function"):
            if prop_info.function.__name__ == "StringProperty":
                name_widget = BL_UI_Textbox(8,ypos,280,20)
                name_widget.propName = prop_info.keywords['name']
                name_widget.setProperty(self.element,prop_info)
                panel.add_widget(name_widget)
                ypos += 26
            elif prop_info.function.__name__ == "BoolProperty":
                name_widget = BL_UI_Checkbox(8,ypos,280,20)
                name_widget.propName = prop_info.keywords['name']
                name_widget.setProperty(self.element,prop_info)
                panel.add_widget(name_widget)
                ypos += 26
            elif prop_info.function.__name__ == "FloatProperty":
                name_widget = BL_UI_Textbox(8,ypos,280,20,"test",propInfo = (prop_info.keywords['name'],self.element,prop_info))
                panel.add_widget(name_widget)
                ypos += 26
            elif prop_info.function.__name__ == "EnumProperty":
                name_widget = BL_UI_DropDown(8,ypos,280,20)
                name_widget.propName = prop_info.keywords['name']
                name_widget.setProperty(self.element,prop_info)
                panel.add_widget(name_widget)
                ypos += 26
            elif prop_info.function.__name__ == "FloatVectorProperty":
                name_widget = BL_UI_Label(8,ypos,280,20,prop_info.keywords['name'])
                name_widget.propName = prop_info.keywords['name']
                panel.add_widget(name_widget)
                ypos += 26
                newiconwidget = BL_UI_Label(8,ypos,24,24,"X")
                panel.add_widget(newiconwidget)
                name_widget = BL_UI_Textbox(8 + 24,ypos,280 - 24,20)
                name_widget.propName = prop_info.keywords['name']
                name_widget.setProperty(self.element,prop_info,0)
                panel.add_widget(name_widget)
                ypos += 26
                newiconwidget = BL_UI_Label(8,ypos,24,24,"Y")
                panel.add_widget(newiconwidget)
                name_widget = BL_UI_Textbox(8 + 24,ypos,280 - 24,20)
                name_widget.propName = prop_info.keywords['name']
                name_widget.setProperty(self.element,prop_info,1)
                panel.add_widget(name_widget)
                ypos += 26
                if prop_info.keywords['size'] > 2:
                    newiconwidget = BL_UI_Label(8,ypos,24,24,"Z")
                    panel.add_widget(newiconwidget)
                    name_widget = BL_UI_Textbox(8 + 24,ypos,280 - 24,20)
                    name_widget.propName = prop_info.keywords['name']
                    name_widget.setProperty(self.element,prop_info,2)
                    panel.add_widget(name_widget)
                    ypos += 26
            else:
                name_widget = BL_UI_Textbox(5,ypos,280,20)
                name_widget.propName = prop_info.keywords['name']
                print(prop_info.function.__name__)
                name_widget.setProperty(self.element,prop_info)
                panel.add_widget(name_widget)
                ypos += 26
        return ypos
            
    def execute(self, context: Context):
        self.dialog = False
        self.modal = False
        self.toolbar = False

        self.getElement(context)
        if not self.element:
            self.loadToolbar(context)
            self.startModal(context)
            return {"RUNNING_MODAL"}
        else:
            self.loadDialog(context)
            self.startModal(context)
            return {"RUNNING_MODAL"}

register, unregister = register_classes_factory((View3D_OT_slvs_context_dialog,))
