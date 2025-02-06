import substance_painter as sp
from math import log2
from os import startfile


def get_export_preset_from_shader_type(shader_type):
    custom_export_preset = {
            "Basic": "custom_basic",
            "Armament": "custom_armament",
            "Morph": "custom_morph",
            }

    export_preset_name = custom_export_preset.get(shader_type)
    if export_preset_name is None:
        sp.logging.log(sp.logging.ERROR, "CUSTOM EXPORTER", f"there is no export preset for the specified shader type {shader_type}")
    return export_preset_name


def build_export_config(texture_set_name, shader_type, export_path):
    texture_set = sp.textureset.TextureSet.from_name(texture_set_name)
    texture_set_stack = texture_set.get_stack()

    export_preset_name = get_export_preset_from_shader_type(shader_type)

    export_preset_id = sp.resource.ResourceID("test_lib", export_preset_name)

    resolution = texture_set.get_resolution()
    resolution = [log2(resolution.width), log2(resolution.height)]

    export_config = {
            "exportShaderParams": False,
            "exportPath": export_path,
            "defaultExportPreset": export_preset_id.url(),
            "exportList": [
                {
                    "rootPath": str(texture_set_stack)
                }
                ],
            "exportParameters": [
                {
                    "parameters": {
                        "paddingAlgorithm": "infinite",
                        "sizeLog2": resolution,
                        }
                    },
                ]
            }
    return export_config


def open_exporter_at_given_path(path):
    startfile(path)


def export_textures(texture_set_name, shader_type, export_path):
    if not sp.project.is_open():
        return

    export_config = build_export_config(texture_set_name, shader_type, export_path)

    sp.logging.log(sp.logging.INFO, "CUSTOM EXPORTER", "going to perform Texture Exporting")
    export_result = sp.export.export_project_textures(export_config)

    # In case of error, display a human readable message:
    if export_result.status == sp.export.ExportStatus.Success:
        open_exporter_at_given_path(export_path)
    else:
        sp.logging.log(sp.logging.WARNING, "CUSTOM EXPORTER", export_result.message)

    # Display the details of what was exported:
    for k, v in export_result.textures.items():
        sp.logging.log(sp.logging.INFO, "CUSTOM EXPORTER", f"Stack {k}:")
        for exported in v:
            sp.logging.log(sp.logging.INFO, "CUSTOM EXPORTER", exported)
