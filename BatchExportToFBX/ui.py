import bpy
from .properties import MeshNameItem

# UI List for showing mesh names
class MESH_UL_name_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)


class MESH_OT_name_editor(bpy.types.Operator):
    bl_idname = "mesh.name_editor"
    bl_label = "Edit Export Names"
    
    def execute(self, context):
        bpy.ops.export_meshes.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Clear previous name list
        context.scene.mesh_names.clear()
        
        # Validate prefix format before adding names
        settings = context.scene.export_settings
        if settings.use_prefix and not settings.prefix.endswith('_'):
            settings.prefix += '_'
            self.report({'INFO'}, f"Added missing underscore to prefix: {settings.prefix}")
        
        # Add selected meshes to the list
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                item = context.scene.mesh_names.add()
                if settings.use_prefix and not obj.name.startswith(settings.prefix):
                    item.name = settings.prefix + obj.name
                else:
                    item.name = obj.name
        
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        
        # Export settings
        box = layout.box()
        settings = context.scene.export_settings
        box.prop(settings, "use_prefix")
        if settings.use_prefix:
            box.prop(settings, "prefix")
        
        # Buttons for name operations
        row = box.row()
        if settings.use_prefix:
            row.operator("mesh.update_names", text="Update Names with Prefix")
        row.operator("mesh.remove_prefixes", text="Remove All Prefixes")
        
        # Name list
        layout.template_list("MESH_UL_name_list", "", context.scene, "mesh_names", context.scene, "active_mesh_index")

def menu_func_export(self, context):
    self.layout.operator(MESH_OT_name_editor.bl_idname, text="Export Selected Meshes to FBX")

def register():
    bpy.utils.register_class(MESH_UL_name_list)
    bpy.utils.register_class(MESH_OT_name_editor)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(MESH_OT_name_editor)
    bpy.utils.unregister_class(MESH_UL_name_list)