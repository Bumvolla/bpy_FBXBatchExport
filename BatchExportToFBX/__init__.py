bl_info = {
    "name": "BatchFBXExport",
    "author": "SoraMas",
    "version": (1, 0),
    "blender": (4, 2, 1),
    "location": "File > Export",
    "description": "Batch export all selected FBX files",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

from . import operators, ui, properties, utils

def register():
    properties.register()
    ui.register()
    operators.register()

def unregister():
    operators.unregister()
    ui.unregister()
    properties.unregister()