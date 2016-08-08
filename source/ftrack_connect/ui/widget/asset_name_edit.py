# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from Qt import QtWidgets


class AssetNameValidator(QtWidgets.QValidator):
    '''Asset Name Validator.

    Validates the input's uniqueness using *assetSelector* and
    *assetTypeSelector*.
    '''

    def __init__(self, assetSelector, assetTypeSelector, **kwargs):
        self.assetSelector = assetSelector
        self.assetTypeSelector = assetTypeSelector
        super(AssetNameValidator, self).__init__(**kwargs)

    def fixup(self, value):
        return value

    def validate(self, value, position):
        assetType = self.assetTypeSelector.currentItem()
        assetTypeId = assetType and assetType.getId()

        isValid = True
        for asset in self.assetSelector.items():
            if (
                asset.get('typeid') == assetTypeId
                and asset.get('name').lower() == value.lower()
            ):
                isValid = False
                break

        if not value or not isValid:
            return QtWidgets.QValidator.Intermediate
        else:
            return QtWidgets.QValidator.Acceptable


class AssetNameEdit(QtWidgets.QLineEdit):
    '''Asset Name line edit

    ..note ::

        Validates the input's uniqueness using *assetSelector* and
        *assetTypeSelector*.
    '''

    def __init__(self, assetSelector, assetTypeSelector, **kwargs):
        super(AssetNameEdit, self).__init__(**kwargs)
        self.setValidator(
            AssetNameValidator(assetSelector, assetTypeSelector)
        )
