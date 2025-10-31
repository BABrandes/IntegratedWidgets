from typing import Mapping, AbstractSet, Iterable

from united_system import Unit, Dimension
from nexpy.core import WritableHookProtocol

def complete_available_unit(available_units_dict_hook: WritableHookProtocol[Mapping[Dimension, AbstractSet[Unit]]], unit: Unit) -> None:
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
    complete_available_units(available_units_dict_hook, [unit])

def complete_available_units(available_units_dict_hook: WritableHookProtocol[Mapping[Dimension, AbstractSet[Unit]]], units: Iterable[Unit]) -> None:
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
            success, msg = available_units_dict_hook.change_value(available_units_dict)
            if not success:
                raise RuntimeError(f"Failed to submit available units dict: {msg}")