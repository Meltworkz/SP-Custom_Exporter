import substance_painter as sp

res_requirement = {
    "Props": [1024, 1024],
    "Weapons": [2048, 2048],
    "Characters": [4096, 4096],
}


def get_required_res_from_asset_type(asset_type):
    required_res = res_requirement.get(asset_type)
    if required_res is None:
        strict_res_values = min(res_requirement.values(), key=sum)
        required_res_width, required_res_height = strict_res_values
        sp.logging.log(
            sp.logging.WARNING,
            "CUSTOM EXPORTER",
            f"There is no resolution budget for the asset type {asset_type}. \
            Fallback to the default {required_res_width} x {required_res_height}",
        )
    else:
        required_res_width, required_res_height = required_res

    return required_res_width, required_res_height


def validate_res(asset_type, current_texture_set_res):
    is_valitadion_passed = None
    validation_details = None

    required_res_width, required_res_height = get_required_res_from_asset_type(asset_type)
    if current_texture_set_res.width > required_res_width or current_texture_set_res.height > required_res_height:
        is_valitadion_passed = False
        validation_details = f"Current resolution for Texture Set is {current_texture_set_res.width} x {current_texture_set_res.height}, \
                                \nwhich is bigger than max allowed for current Asset Type ({asset_type}):\
                                \n{required_res_width} x {required_res_height}"

    else:
        is_valitadion_passed = True
        validation_details = "Validation is Passed"

    return is_valitadion_passed, validation_details
