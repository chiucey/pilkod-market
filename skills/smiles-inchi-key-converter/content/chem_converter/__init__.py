"""
Chem-Converter: 本地化学标识符转换器
支持 SMILES ↔ InChI ↔ InChIKey 互相转换
"""

from .converter import (
    smiles_to_inchi,
    smiles_to_inchikey,
    inchi_to_smiles,
    inchi_to_inchikey,
    inchikey_to_inchi,
    validate_inchikey,
    batch_convert,
    interactive_mode,
    check_openbabel,
)

__version__ = "1.0.0"
__all__ = [
    'smiles_to_inchi',
    'smiles_to_inchikey',
    'inchi_to_smiles',
    'inchi_to_inchikey',
    'inchikey_to_inchi',
    'validate_inchikey',
    'batch_convert',
    'interactive_mode',
    'check_openbabel',
]
