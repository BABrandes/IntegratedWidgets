from typing import Mapping, AbstractSet, Iterable, Optional

from united_system import Unit, Dimension
from nexpy.core import WritableHookProtocol

def get_updated_available_units_dict(available_units_dict_hook: WritableHookProtocol[Mapping[Dimension, AbstractSet[Unit]]], units: Iterable[Unit], *, raise_submission_error_flag: bool = True) -> Optional[Mapping[Dimension, AbstractSet[Unit]]]:
    """
    Get the updated allowed dimensions by adding the dimension of the unit to the allowed dimensions if it is not in the allowed dimensions.

    Args:
    -----
    available_units_dict_hook : (WritableHookProtocol[Mapping[Dimension, AbstractSet[Unit]]])
        The hook for the available units dict
    units : (Iterable[Unit])
        The units to complete the available units dict with

    Returns:
    --------
    Optional[Mapping[Dimension, AbstractSet[Unit]]]: The updated available units dict if the units were added, otherwise None.

    Raises:
    -------
    RuntimeError : If the available units dict cannot be updated
    """
    
    available_units_dict = dict[Dimension, AbstractSet[Unit]](available_units_dict_hook.value)

    for unit in units:
        dimension = unit.dimension
        
        # Step 1: Check if we need to add this unit
        needs_update = False
        if dimension not in available_units_dict:
            needs_update = True
        elif unit not in available_units_dict[dimension]:
            needs_update = True
        
        # Step 2: If we need to add this unit, add it to the dict
        if needs_update:
            # Use setdefault to ensure we don't overwrite existing dimension entries
            if dimension not in available_units_dict:
                available_units_dict[dimension] = set[Unit]()
            else:
                _units: set[Unit] = set(available_units_dict[dimension])
                _units.add(unit)
                available_units_dict[dimension] = _units
            return available_units_dict
    return None

def complete_available_unit(available_units_dict_hook: WritableHookProtocol[Mapping[Dimension, AbstractSet[Unit]]], unit: Unit, *, raise_submission_error_flag: bool = True) -> tuple[bool, str]:
    """
    Complete the available units dict by adding a single missing unit to the dict if it is not in the dict.
    If the unit is already in the dict, do nothing.
    If the unit is not in the dict, add it to the dict - and even create a new dimension entry if necessary.

    Args:
    -----
    available_units_dict_hook : (WritableHookProtocol[Mapping[Dimension, AbstractSet[Unit]]])
    unit : (Unit)
        The unit to add to the available units dict
    """
    success, msg = complete_available_units(available_units_dict_hook, [unit], raise_submission_error_flag=False)
    if not success and raise_submission_error_flag:
        raise RuntimeError(f"Failed to complete available units: {msg}")
    return success, msg

def complete_available_units(available_units_dict_hook: WritableHookProtocol[Mapping[Dimension, AbstractSet[Unit]]], units: Iterable[Unit], *, raise_submission_error_flag: bool = True) -> tuple[bool, str]:
    """
    Complete the available units dict by adding missing units to the dict.
    If the unit is already in the dict, do nothing.
    If the units are not in the dict, add them to the dict - and even create new dimension entries if necessary.

    Args:
    -----
    available_units_dict_hook : (WritableHookProtocol[Mapping[Dimension, AbstractSet[Unit]]])
        The hook for the available units dict
    units : (Iterable[Unit])
        The units to complete the available units dict with

    Raises:
    -------
    RuntimeError : If the available units dict cannot be updated
    """
    
    available_units_dict = get_updated_available_units_dict(available_units_dict_hook, units, raise_submission_error_flag=False)
    if available_units_dict is not None:
        success, msg = available_units_dict_hook.change_value(available_units_dict)
        if not success and raise_submission_error_flag:
            raise RuntimeError(f"Failed to submit available units dict: {msg}")
        return success, "Available units dict updated successfully"
    else:
        return True, "No units needed to be added to the available units dict"