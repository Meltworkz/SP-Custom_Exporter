"""
    Module to validate Texture Set name. 
    
    Rules:
    Name should be splitted with _
    Name should consists of acronyms: AssetType_AssetDetail1_AssetDetail2_AssetID
    
    For Props, details are Prop Type and Size/Scale:
        Prop Type could be: "CHR" (Chair), "TBL" (Table), LMP (Lamp), or WIN (Window).
        Prop Size/Scale could be: "S" (Small), "M" (Medium), or "L" (Large).
        Valid Texture Set names for Props:
            Prop_CHR_S_01
            Prop_BKL_M_02
    
    For Weapons, details are Weapon Type and Rarity:
        Weapon Type could be: "SWD: (Sword), "BOW" (Bow), "RFL" (Rifle), or "EXP" (Explosive).
        Weapon Rarity could be: "COM" (Common),  "RAR" (Rare), or "EPC" (Epic).
        Valid Texture Set names for Weapons:
            WPN_BOW_COM_01
            WPN_RLF_EPC_04
    
    For Character, details are Character Type and Gender
        Character Type could be: "PLR" (Player), "ENM" (Enemy), or "CIV" (Civilian).
        Character Gender could be: Male (ML), or Female (FL).
        Valid Texture Set names for Characters:
            CHAR_PLR_ML_01
            CHAR_CIV_FM_05

    Content:
        - validate_name
        - validate_name_props
        - validate_name_characters
        - validate_name_weapon

    Contributors:
        - Viacheslav Makhynko, viacheslav.makhynko@gmail.com
"""

from typing import Tuple

props_asset_detail_1_list = ["CHR", "TBL", "LMP", "WIN"]
props_asset_detail_2_list = ["S", "M", "L"]

weapons_asset_detail_1_list = ["SWD", "BOW", "RFL", "EXP"]
weapons_asset_detail_2_list = ["COM", "RAR", "EPC"]

character_asset_detail_1_list = ["PLR", "ENM", "CIV"]
character_asset_detail_2_list = ["ML", "FL"]


def validate_name_props(asset_type_acronym: str, asset_type_detail_1: str, asset_type_detail_2: str) -> Tuple[bool, str]:
    """ Sub-validation fucntion used for specific rules check applied to Characters Texture sets. """
    is_validation_passed = None
    validation_details = None
    if asset_type_acronym != "PROP":
        is_validation_passed = False
        validation_details = f"First acronym is for Asset Type \
                            \nFor asset type 'Props' valid option is 'PROP'. \
                            \nCurrent acronyms is: {asset_type_acronym}"

    elif asset_type_detail_1 not in props_asset_detail_1_list:
        is_validation_passed = False
        validation_details = f"Second acronym is for Asset Detail #1 \
                            \nFor 'Props' valid option are {props_asset_detail_1_list}. \
                            \nCurrent acronyms is: {asset_type_detail_1}"

    elif asset_type_detail_2 not in props_asset_detail_2_list:
        is_validation_passed = False
        validation_details = f"Second acronym is for Asset Detail #2 \
                            \nFor 'Props' valid option are {props_asset_detail_2_list}. \
                            \nCurrent acronyms is: {asset_type_detail_2}"
    else:
        is_validation_passed = True
        validation_details = "Validation is passed!"

    return is_validation_passed, validation_details


def validate_name_weapons(asset_type_acronym: str, asset_type_detail_1: str, asset_type_detail_2: str) -> Tuple[bool, str]:
    """ Sub-validation fucntion used for specific rules check applied to Weapons Texture sets. """
    is_validation_passed = None
    validation_details = None
    if asset_type_acronym != "WPN":
        is_validation_passed = False
        validation_details = f"First acronym is for Asset Type \
                            \nFor asset type 'Weapons' valid option is 'WPN'. \
                            \nCurrent acronyms is: {asset_type_acronym}"

    elif asset_type_detail_1 not in weapons_asset_detail_1_list:
        is_validation_passed = False
        validation_details = f"Second acronym is for Asset Detail #1 \
                            \nFor 'Weapons' valid option are {weapons_asset_detail_1_list}. \
                            \nCurrent acronyms is: {asset_type_detail_1}"

    elif asset_type_detail_2 not in weapons_asset_detail_2_list:
        is_validation_passed = False
        validation_details = f"Second acronym is for Asset Detail #2 \
                            \nFor 'Weapons' valid option are {weapons_asset_detail_2_list}. \
                            \nCurrent acronyms is: {asset_type_detail_2}"

    else:
        is_validation_passed = True
        validation_details = "Validation is passed!"

    return is_validation_passed, validation_details


def validate_name_characters(asset_type_acronym: str, asset_type_detail_1: str, asset_type_detail_2: str) -> Tuple[bool, str]:
    """ Sub-validation fucntion used for specific rules check applied to Characters Texture sets. """
    is_validation_passed = None
    validation_details = None
    if asset_type_acronym != "CHAR":
        is_validation_passed = False
        validation_details = f"First acronym is for Asset Type \
                            \nFor asset type 'Characters' valid option is 'CHAR'. \
                            \nCurrent acronyms is: {asset_type_acronym}"

    elif asset_type_detail_1 not in character_asset_detail_1_list:
        is_validation_passed = False
        validation_details = f"Second acronym is for Asset Detail #1 \
                            \nFor 'Characters' valid option are {character_asset_detail_1_list}. \
                            \nCurrent acronyms is: {asset_type_detail_1}"

    elif asset_type_detail_2 not in character_asset_detail_2_list:
        is_validation_passed = False
        validation_details = f"Second acronym is for Asset Detail #2 \
                            \nFor 'Characters' valid option are {character_asset_detail_2_list}. \
                            \nCurrent acronyms is: {asset_type_detail_1}"

    else:
        is_validation_passed = True
        validation_details = "Validation is passed!"

    return is_validation_passed, validation_details


def validate_name(asset_type: str, texture_set_name: str) -> Tuple[bool, str]:
    """
    Core function to validate texture set name.
    Performs general rules validation and, if thy are passed,
    triggers sub-validation functions for specific asset type.
    """
    texture_set_name_acronyms = texture_set_name.split("_")

    # Template vallidation
    if len(texture_set_name_acronyms) != 4:
        return False, f"Texture Set name should consist of 4 acronyms separated by underscored _ \
                        \nValid structure: AssetType_AssetDetail1_AssetDetail2_AssetID\
                        \nCurrent number of acronyms: {len(texture_set_name_acronyms)}"

    asset_type_acronym, asset_type_detail_1, asset_type_detail_2, asset_id = texture_set_name_acronyms

    # Asset ID Validation
    if (len(asset_id) != 2) or (not asset_id.isdigit()):
        return False, f"last acronym is used to specify Asset ID \
                        \nValid options are any number from range 00 to 99. Example: 01, 55, 99\
                        \nCurrent acronyms is: {len(asset_id)}"

    if asset_type == "Props":
        return validate_name_props(asset_type_acronym, asset_type_detail_1, asset_type_detail_2)

    elif asset_type == "Weapons":
        return validate_name_weapons(asset_type_acronym, asset_type_detail_1, asset_type_detail_2)

    elif asset_type == "Characters":
        return validate_name_characters(asset_type_acronym, asset_type_detail_1, asset_type_detail_2)

    return False, "General validation error. Asset Type is not valid \
                    \nThere is a mismatch between Asset Type in the Dropdown list of the widget with the strings in alidate_name function \
                    \nPlease, contact a tool maintaner for the assistance"
