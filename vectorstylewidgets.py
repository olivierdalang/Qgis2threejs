# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qgis2threejs
                                 A QGIS plugin
 export terrain and map image into web browser
                             -------------------
        begin                : 2013-12-21
        copyright            : (C) 2013 by Minoru Akagi
        email                : akaginch@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QWidget, QColor, QColorDialog, QFileDialog, QMessageBox
from qgis.core import QGis
from ui_widgetComboEdit import Ui_ComboEditWidget

class StyleWidget(QWidget, Ui_ComboEditWidget):
  # function types
  FIELD_VALUE = 1
  COLOR = 2
  FILEPATH = 3
  HEIGHT = 4

  def __init__(self, funcType=None, parent=None):
    QWidget.__init__(self, parent)
    self.setupUi(self)
    self.comboBox.currentIndexChanged.connect(self.comboBoxSelectionChanged)
    self.toolButton.clicked.connect(self.toolButtonClicked)
    self.defaultValue = 0
    self.funcType = funcType
    self.func = None

  def setup(self, funcType=None, name=None, label=None, defaultValue=None, layer=None, fieldNames=None):
    if funcType is None:
      funcType = self.funcType

    if self.func is None or self.funcType != funcType:
      if funcType == StyleWidget.FIELD_VALUE:
        self.func = FieldValueWidgetFunc(self)
      elif funcType == StyleWidget.COLOR:
        self.func = ColorWidgetFunc(self)
      elif funcType == StyleWidget.FILEPATH:
        self.func = FilePathWidgetFunc(self)
      elif funcType == StyleWidget.HEIGHT:
        self.func = HeightWidgetFunc(self)
      else:
        self.func = None
        self.setVisible(False)
        return
    self.func.setup(name, label, defaultValue, layer, fieldNames)
    self.setVisible(True)

  def comboBoxSelectionChanged(self, index):
    if self.func:
      self.func.comboBoxSelectionChanged(index)

  def toolButtonClicked(self):
    if self.func:
      self.func.toolButtonClicked()

  def values(self):
    if self.func:
      return self.func.values()
    else:
      return []

  def setValues(self, vals):
    if self.func:
      self.func.setValues(vals)

  def addFieldNameItems(self, layer, fieldNames=None):
    fields = layer.pendingFields()
    if fieldNames is None:
      for i, field in enumerate(fields):
        if field.type() in [QVariant.Double, QVariant.Int, QVariant.LongLong, QVariant.UInt, QVariant.ULongLong]:
          self.comboBox.addItem(field.name(), WidgetFuncBase.FIRST_ATTRIBUTE + i)
    else:
      for fieldName in fieldNames:
        self.comboBox.addItem(fieldName, WidgetFuncBase.FIRST_ATTRIBUTE + fields.indexFromName(fieldName))

class WidgetFuncBase:
  FIRST_ATTRIBUTE = 100

  def __init__(self, widget):
    self.widget = widget

  def setup(self):
    # initialize widgets
    self.widget.lineEdit.setPlaceholderText("")
    self.widget.lineEdit.setVisible(True)

  def comboBoxSelectionChanged(self, index):
    pass

  def toolButtonClicked(self):
    pass

  def values(self):
    return [self.widget.comboBox.itemData(self.widget.comboBox.currentIndex()), self.widget.comboBox.currentText(), self.widget.lineEdit.text()]

  def setValues(self, vals):
    index = self.widget.comboBox.findData(vals[0])
    if index != -1:
      self.widget.comboBox.setCurrentIndex(index)
    self.widget.lineEdit.setText(vals[2])

class FieldValueWidgetFunc(WidgetFuncBase):
  ABSOLUTE = 1

  def setup(self, name, label, defaultValue, layer, fieldNames):
    WidgetFuncBase.setup(self)
    self.widget.label_1.setText(name)
    self.widget.label_2.setText(label)
    self.widget.toolButton.setVisible(False)
    self.defaultValue = defaultValue

    self.widget.comboBox.clear()
    self.widget.comboBox.addItem("Fixed value", FieldValueWidgetFunc.ABSOLUTE)
    if layer:
      self.widget.addFieldNameItems(layer, fieldNames)

  def comboBoxSelectionChanged(self, index):
    itemData = self.widget.comboBox.itemData(index)
    if itemData == FieldValueWidgetFunc.ABSOLUTE:
      label = "Value"
      defaultValue = self.defaultValue
    else:
      label = "Multiplier"
      defaultValue = 1
    self.widget.label_2.setText(label)
    self.widget.lineEdit.setText(str(defaultValue))

class ColorWidgetFunc(WidgetFuncBase):
  CURRENTSTYLE = 1
  RANDOM = 2
  RGB = 3

  def setup(self, name, label, defaultValue, layer, fieldNames):
    self.widget.label_1.setText("Color")
    self.widget.label_2.setText("Value")
    self.widget.lineEdit.setVisible(False)
    self.widget.lineEdit.setPlaceholderText("Format: 0xrrggbb")
    self.widget.toolButton.setVisible(False)

    self.widget.comboBox.clear()
    self.widget.comboBox.addItem("Current style", ColorWidgetFunc.CURRENTSTYLE)
    self.widget.comboBox.addItem("Random", ColorWidgetFunc.RANDOM)
    self.widget.comboBox.addItem("RGB value", ColorWidgetFunc.RGB)

  def comboBoxSelectionChanged(self, index):
    itemData = self.widget.comboBox.itemData(index)
    isRGB = itemData == ColorWidgetFunc.RGB
    self.widget.label_2.setVisible(isRGB)
    self.widget.lineEdit.setVisible(isRGB)
    self.widget.toolButton.setVisible(isRGB)

  def toolButtonClicked(self):
    color = QColorDialog.getColor(QColor(self.widget.lineEdit.text().replace("0x", "#")))
    if color.isValid():
      self.widget.lineEdit.setText(color.name().replace("#", "0x"))

  def setValues(self, vals):
    index = self.widget.comboBox.findData(vals[0])
    if index != -1:
      self.widget.comboBox.setCurrentIndex(index)
      self.widget.comboBoxSelectionChanged(index)  # make sure to update visibility
    self.widget.lineEdit.setText(vals[2])

class FilePathWidgetFunc(WidgetFuncBase):
  FILEPATH = 1

  def setup(self, name, label, defaultValue, layer, fieldNames):
    WidgetFuncBase.setup(self)
    self.widget.label_1.setText(name)
    self.widget.label_2.setText(label)
    self.widget.toolButton.setVisible(True)

    self.widget.comboBox.clear()
    self.widget.comboBox.addItem("File path", FilePathWidgetFunc.FILEPATH)

  def comboBoxSelectionChanged(self, index):
    pass

  def toolButtonClicked(self):
    filename = QFileDialog.getOpenFileName()
    if filename != "":
      self.widget.lineEdit.setText(filename)

class HeightWidgetFunc(WidgetFuncBase):
  ABSOLUTE = 1
  RELATIVE = 2
  RELATIVE_TO_Z = 3

  def setup(self, name, label, defaultValue, layer, fieldNames):
    WidgetFuncBase.setup(self)
    self.widget.label_1.setText("Height")
    self.widget.toolButton.setVisible(False)
    self.defaultValue = 0 if defaultValue is None else defaultValue

    self.widget.comboBox.clear()
    if layer.wkbType() in [QGis.WKBPoint25D, QGis.WKBLineString25D, QGis.WKBMultiPoint25D, QGis.WKBMultiLineString25D]:
      self.widget.comboBox.addItem("Z value", HeightWidgetFunc.RELATIVE_TO_Z)
    self.widget.comboBox.addItem("Height from surface", HeightWidgetFunc.RELATIVE)
    self.widget.comboBox.addItem("Fixed value", HeightWidgetFunc.ABSOLUTE)
    if layer:
      self.widget.addFieldNameItems(layer, fieldNames)

  def comboBoxSelectionChanged(self, index):
    itemData = self.widget.comboBox.itemData(index)
    if itemData in [HeightWidgetFunc.ABSOLUTE, HeightWidgetFunc.RELATIVE]:
      label = "Value"
      defaultValue = self.defaultValue
    else:
      label = "Addend"
      defaultValue = 0
    self.widget.label_2.setText(label)
    self.widget.lineEdit.setText(str(defaultValue))
