import bpy
from bpy.props import StringProperty
from bpy.props import BoolProperty
import os
from bpy_extras.io_utils import ExportHelper
from .properties import MeshNameItem
from .utils import validate_prefix

class ExportSettings(bpy.types.PropertyGroup):
    use_prefix: bpy.props.BoolProperty(
        name="Add Prefix",
        description="Add prefix to file names",
        default=True
    )
    prefix: bpy.props.StringProperty(
        name="Prefix",
        description="Prefix to add to file names",
        default="SM_",
        update=lambda self, context: validate_prefix(self, context)
    )


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

# Operator to remove all prefixes
class MESH_OT_remove_prefixes(bpy.types.Operator):
    bl_idname = "mesh.remove_prefixes"
    bl_label = "Remove All Prefixes"
    
    def execute(self, context):
        for item in context.scene.mesh_names:
            # Find the first underscore and remove everything before it
            underscore_pos = item.name.find('_')
            if underscore_pos != -1:
                item.name = item.name[underscore_pos + 1:]
        return {'FINISHED'}

# Operator to update names with prefix
class MESH_OT_update_names(bpy.types.Operator):
    bl_idname = "mesh.update_names"
    bl_label = "Update Names with Prefix"
    
    def execute(self, context):
        settings = context.scene.export_settings
        
        # Validate prefix format before updating names
        if settings.use_prefix and not settings.prefix.endswith('_'):
            settings.prefix += '_'
            self.report({'INFO'}, f"Added missing underscore to prefix: {settings.prefix}")
        
        for item in context.scene.mesh_names:
            if settings.use_prefix and not item.name.startswith(settings.prefix):
                item.name = settings.prefix + item.name.replace(settings.prefix, "")
            elif not settings.use_prefix:
                item.name = item.name.replace(settings.prefix, "")
        return {'FINISHED'}

# Main export operator
class ExportMeshesToFBX(bpy.types.Operator, ExportHelper):
    bl_idname = "export_meshes.fbx"
    bl_label = "Export Selected Meshes to FBX"
    
    filename_ext = ".fbx"
    
    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
    )
    
    def execute(self, context):
        directory = os.path.dirname(self.filepath)
        iteration = 0
        selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        
        # Create a mapping of original objects to their new names
        name_mapping = {obj: item.name for obj, item in zip(selected_objects, context.scene.mesh_names)}
        
        for obj in selected_objects:
            #Select this iteration object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
            #Store current location
            storedLocation = obj.location.copy()
            
            #Move to world origin and apply transforms
            bpy.context.object.location = (0, 0, 0)
            bpy.ops.object.transform_apply()
            
            #Export using the custom name
            export_name = name_mapping[obj]
            fbx_filepath = os.path.join(directory, f"{export_name}.fbx")
            bpy.ops.export_scene.fbx(filepath=fbx_filepath, use_selection=True, embed_textures=True, path_mode='COPY')
            
            #Return it to the original location
            obj.location = storedLocation
            
            iteration += 1
        
        self.report({'INFO'}, f'Successfully exported {iteration} objects.')
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(ExportSettings)
    bpy.utils.register_class(MESH_OT_name_editor)
    bpy.utils.register_class(MESH_OT_update_names)
    bpy.utils.register_class(MESH_OT_remove_prefixes)
    bpy.utils.register_class(ExportMeshesToFBX)
    bpy.types.Scene.export_settings = bpy.props.PointerProperty(type=ExportSettings)

def unregister():
    del bpy.types.Scene.export_settings
    bpy.utils.unregister_class(ExportMeshesToFBX)
    bpy.utils.unregister_class(MESH_OT_remove_prefixes)
    bpy.utils.unregister_class(MESH_OT_update_names)
    bpy.utils.unregister_class(MESH_OT_name_editor)
    bpy.utils.unregister_class(ExportSettings)