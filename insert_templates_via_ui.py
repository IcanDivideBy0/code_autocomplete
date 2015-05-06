import bpy
from bpy.props import *
from . name_utils import *
from . text_block import TextBlock

class InsertTemplateMenu(bpy.types.Menu):
    bl_idname = "text_editor.insert_template_menu"
    bl_label = "Insert Template"
    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("code_autocomplete.insert_panel", text = "Panel")
        layout.operator_menu_enum("code_autocomplete.insert_menu", "menu_type", text = "Menu")
        layout.operator_menu_enum("code_autocomplete.insert_operator", "operator_type", text = "Operator")
        layout.operator("code_autocomplete.insert_license", "License")

class InsertTemplateBase:
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return TextBlock.get_active()
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, 300, 200)
        
class InsertClassTemplateBase(InsertTemplateBase):
    class_name = StringProperty(name = "Class Name", default = "")     

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "class_name", text = "Name")
           
        
def insert_template(code, changes = {}):
    text_block = TextBlock.get_active()
    
    if text_block.current_line.strip() != "":
        text_block.insert("\n")
    text_block.current_character_index = 0
    
    for old, new in changes.items():
        code = code.replace(old, new)
    if text_block:
        text_block.insert(code)
 


# License
###########################

class InsertLicense(bpy.types.Operator, InsertClassTemplateBase):
    bl_idname = "code_autocomplete.insert_license"
    bl_label = "Insert License"
    bl_description = ""
    
    author_name = StringProperty(name = "Name", default = bpy.context.user_preferences.system.author)     
    author_mail = StringProperty(name = "eMail", default = "")     

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "author_name", text = "Name")
        layout.prop(self, "author_mail", text = "E-Mail")
    
    def execute(self, context):
        changes = {
            "YOUR_NAME" : self.author_name,
            "YOUR_MAIL" : self.author_mail }
        insert_template(license_template, changes)
        return {"FINISHED"} 

license_template = """'''
Copyright (C) 2015 YOUR_NAME
YOUR_MAIL

Created by YOUR_NAME

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
"""

        
# Panel
###########################

class InsertPanel(bpy.types.Operator, InsertClassTemplateBase):
    bl_idname = "code_autocomplete.insert_panel"
    bl_label = "Insert Panel"
    bl_description = ""
    
    def execute(self, context):
        changes = {
            "CLASS_NAME" : get_valid_variable_name(self.class_name),
            "ID_NAME" : get_lower_case_with_underscores(self.class_name),
            "LABEL" : get_separated_capitalized_words(self.class_name) }
        insert_template(panel_template, changes)
        return {"FINISHED"} 
        
panel_template = '''class CLASS_NAME(bpy.types.Panel):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "category"
    
    def draw(self, context):
        layout = self.layout
        '''         


# Menu
###########################   

menu_type_items = [
    ("NORMAL", "Normal", ""),
    ("PIE", "Pie", "") ]        
class InsertMenu(bpy.types.Operator, InsertClassTemplateBase):
    bl_idname = "code_autocomplete.insert_menu"
    bl_label = "Insert Menu"
    bl_description = ""
    
    menu_type = EnumProperty(items = menu_type_items, default = "NORMAL")
    
    def execute(self, context):
        if self.menu_type == "NORMAL": code = menu_template
        if self.menu_type == "PIE": code = pie_menu_template
        changes = {
            "CLASS_NAME" : get_valid_variable_name(self.class_name),
            "ID_NAME" : "view3d." + get_lower_case_with_underscores(self.class_name),
            "LABEL" : get_separated_capitalized_words(self.class_name) }
        insert_template(code, changes)
        return {"FINISHED"}     

menu_template = '''class CLASS_NAME(bpy.types.Menu):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    
    def draw(self, context):
        layout = self.layout
        '''   

pie_menu_template = '''class CLASS_NAME(bpy.types.Menu):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    
    def draw(self, context):
        pie = self.layout.menu_pie()
        '''       
 
 
# Operator
###########################

operator_type_items = [
    ("NORMAL", "Normal", ""),
    ("MODAL", "Modal", ""),
    ("MODAL_DRAW", "Modal Draw", "") ]        
class InsertOperator(bpy.types.Operator, InsertClassTemplateBase):
    bl_idname = "code_autocomplete.insert_operator"
    bl_label = "Insert Operator"
    bl_description = ""
    
    operator_type = EnumProperty(items = operator_type_items, default = "NORMAL")
    
    def execute(self, context):
        if self.operator_type == "NORMAL": code = operator_template
        if self.operator_type == "MODAL": code = modal_operator_template
        if self.operator_type == "MODAL_DRAW": code = modal_operator_draw_template
        changes = {
            "CLASS_NAME" : get_valid_variable_name(self.class_name),
            "ID_NAME" : "my_operator." + get_lower_case_with_underscores(self.class_name),
            "LABEL" : get_separated_capitalized_words(self.class_name) }
        insert_template(code, changes)
        return {"FINISHED"} 
        
operator_template = '''class CLASS_NAME(bpy.types.Operator):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        return {"FINISHED"}
        '''      

modal_operator_template = '''class CLASS_NAME(bpy.types.Operator):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def modal(self, context, event):
    
        if event.type == "LEFTMOUSE":
            return {"FINISHED"}
    
        if event.type in {"RIGHTMOUSE", "ESC"}:
            return {"CANCELLED"}
            
        return {"RUNNING_MODAL"}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
        '''    

modal_operator_draw_template = '''class CLASS_NAME(bpy.types.Operator):
    bl_idname = "ID_NAME"
    bl_label = "LABEL"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
        
    def invoke(self, context, event):
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
        
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == "LEFTMOUSE":
            self.cancel(context)
            return {"FINISHED"}
            
        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.cancel(context)
            return {"CANCELLED"}
            
        return {"RUNNING_MODAL"}
        
    def cancel(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
    
    def draw_callback_px(tmp, self, context):
        pass
    '''        