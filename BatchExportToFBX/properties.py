import bpy

# Property group for each mesh name
class MeshNameItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Export Name",
        description="Name that will be used for the exported file",
        default=""
    )

def register():
    bpy.utils.register_class(MeshNameItem)
    bpy.types.Scene.mesh_names = bpy.props.CollectionProperty(type=MeshNameItem)
    bpy.types.Scene.active_mesh_index = bpy.props.IntProperty()

def unregister():
    del bpy.types.Scene.active_mesh_index
    del bpy.types.Scene.mesh_names
    bpy.utils.unregister_class(MeshNameItem)