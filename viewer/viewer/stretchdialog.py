
"""
Module that contains the StretchLayout, RuleLayout
and StretchDefaultsDialog classes
"""

from PyQt4.QtGui import QDialog, QFormLayout, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox
from PyQt4.QtGui import QLabel, QPushButton, QGroupBox, QTabWidget, QWidget, QSpinBox
from PyQt4.QtCore import QVariant, QSettings, SIGNAL
import json

from . import viewerstretch

# strings for the combo boxes and their values
MODE_DATA = (("Color Table", viewerstretch.VIEWER_MODE_COLORTABLE),
                ("Greyscale", viewerstretch.VIEWER_MODE_GREYSCALE),
                ("RGB", viewerstretch.VIEWER_MODE_RGB))

STRETCH_DATA = (("None", viewerstretch.VIEWER_STRETCHMODE_NONE),
                ("Linear", viewerstretch.VIEWER_STRETCHMODE_LINEAR),
                ("Standard Deviation", viewerstretch.VIEWER_STRETCHMODE_STDDEV),
                ("Histogram", viewerstretch.VIEWER_STRETCHMODE_HIST))

DEFAULT_STRETCH_KEY = 'DefaultStretch'

class StretchLayout(QFormLayout):
    """
    Layout that contains the actual stretch information
    """
    def __init__(self, parent, stretch):
        QFormLayout.__init__(self)

        # the mode
        self.modeCombo = QComboBox(parent)
        index = 0
        for text, code in MODE_DATA:
            self.modeCombo.addItem(text, QVariant(code))
            if code == stretch.mode:
                self.modeCombo.setCurrentIndex(index)
            index += 1

        # callback so we can set the state of other items when changed
        self.connect(self.modeCombo, SIGNAL("currentIndexChanged(int)"), self.modeChanged)

        self.addRow("Mode", self.modeCombo)

        # create the 3 band spin boxes
        self.bandLayout = QHBoxLayout()
        self.redSpinBox = QSpinBox(parent)
        self.redSpinBox.setRange(1, 100)
        self.bandLayout.addWidget(self.redSpinBox)

        self.greenSpinBox = QSpinBox(parent)
        self.greenSpinBox.setRange(1, 100)
        self.bandLayout.addWidget(self.greenSpinBox)

        self.blueSpinBox = QSpinBox(parent)
        self.blueSpinBox.setRange(1, 100)
        self.bandLayout.addWidget(self.blueSpinBox)

        # set them depending on if we are RGB or not
        if stretch.mode == viewerstretch.VIEWER_MODE_RGB:
            (r, g, b) = stretch.bands
            self.redSpinBox.setValue(r)
            self.greenSpinBox.setValue(g)
            self.blueSpinBox.setValue(b - 1)
        else:
            self.redSpinBox.setValue(stretch.bands[0])
            self.greenSpinBox.setEnabled(False)
            self.blueSpinBox.setEnabled(False)

        self.addRow("Bands", self.bandLayout)

        # create the combo for the type of stretch
        self.stretchCombo = QComboBox(parent)
        index = 0
        for text, code in STRETCH_DATA:
            self.stretchCombo.addItem(text, QVariant(code))
            if code == stretch.stretchmode:
                self.stretchCombo.setCurrentIndex(index)
            index += 1

        self.addRow("Stretch", self.stretchCombo)
        self.stretchCombo.setEnabled(stretch.mode != viewerstretch.VIEWER_MODE_COLORTABLE)


    def getStretch(self):
        """
        Return a ViewerStretch object that reflects
        the current state of the GUI
        """
        obj = viewerstretch.ViewerStretch()
        index = self.modeCombo.currentIndex()
        obj.mode = self.modeCombo.itemData(index).toInt()[0]

        bands = []
        value = self.redSpinBox.value()
        bands.append(value)
        if obj.mode == viewerstretch.VIEWER_MODE_RGB:
            value = self.greenSpinBox.value()
            bands.append(value)
            value = self.blueSpinBox.value()
            bands.append(value)
        obj.setBands(tuple(bands))

        index = self.stretchCombo.currentIndex()
        obj.stretchmode = self.stretchCombo.itemData(index).toInt()[0]
        return obj

    def modeChanged(self, index):
        """
        Called when user changed the mode. 
        Updates other GUI elements as needed
        """
        mode = self.modeCombo.itemData(index).toInt()[0]
        greenredEnabled = (mode == viewerstretch.VIEWER_MODE_RGB)
        self.greenSpinBox.setEnabled(greenredEnabled)
        self.blueSpinBox.setEnabled(greenredEnabled)

        if mode == viewerstretch.VIEWER_MODE_COLORTABLE:
            # need to set stretch to none
            self.stretchCombo.setCurrentIndex(0)
        self.stretchCombo.setEnabled(mode != viewerstretch.VIEWER_MODE_COLORTABLE)

RULE_DATA = (("Number of Bands Less than", viewerstretch.VIEWER_COMP_LT),
                ("Number of Bands Greater than", viewerstretch.VIEWER_COMP_GT),
                ("Number of Bands Equal to", viewerstretch.VIEWER_COMP_EQ))

class RuleLayout(QGridLayout):
    """
    Layout that contains the 'rules'. These are 
    the number of bands, the comparison with the
    number of bands and the check for a color table
    """
    def __init__(self, parent, rule):
        QGridLayout.__init__(self)            

        # the comaprison combo
        self.compCombo = QComboBox(parent)
        index = 0
        for text, code in RULE_DATA:
            variant = QVariant(code)
            self.compCombo.addItem(text, variant)
            if code == rule.comp:
                self.compCombo.setCurrentIndex(index)
            index += 1
        self.addWidget(self.compCombo, 0, 0)

        # the number of bands spinbox
        self.numberBox = QSpinBox(parent)
        self.numberBox.setRange(1, 100)
        self.numberBox.setValue(rule.value)
        self.addWidget(self.numberBox, 0, 1)

        # the label for the color table rule
        self.colorTableLabel = QLabel(parent)
        self.colorTableLabel.setText("Color Table in Band")
        self.addWidget(self.colorTableLabel, 1, 0)

        # color table band spinbox
        self.colorTableBox = QSpinBox(parent)
        self.colorTableBox.setRange(0, 100)
        self.colorTableBox.setSpecialValueText('No color table required')
        if rule.ctband is None:
            self.colorTableBox.setValue(0)
        else:
            self.colorTableBox.setValue(rule.ctband)
        self.addWidget(self.colorTableBox, 1, 1)

    def getRule(self):
        """
        Return a StretchRule instance for the current GUI
        settings
        Note: the stretch field will be None
        """
        index = self.compCombo.currentIndex()
        comp = self.compCombo.itemData(index).toInt()[0]
        value = self.numberBox.value()
        ctband = self.colorTableBox.value()
        if ctband == 0:
            ctband = None # no color table required

        obj = viewerstretch.StretchRule(comp, value, ctband, None)
        return obj

class StretchDefaultsDialog(QDialog):
    """
    Dialog that contains a Tabs, each one describing a rule
    and is a combination of RuleLayout and StretchLayout
    """
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        # create a tab widget with its tabs on the left
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setTabPosition(QTabWidget.West)

        # grab the rules from the setting
        # this supplies some default rules if none
        ruleList = self.fromSettings()
        self.widgetList = []
        count = 1
        # go through each rule
        for rule in ruleList:

            # create a widget that contains the rule/stretch
            widget = QWidget()
    
            # create the rule layout and put it into a group box
            widget.ruleLayout = RuleLayout(widget, rule)
            widget.ruleGroup = QGroupBox('Rule')
            widget.ruleGroup.setLayout(widget.ruleLayout)

            # create the stretch layout and put it into a group box
            widget.stretchLayout = StretchLayout(widget, rule.stretch)
            widget.stretchGroup = QGroupBox("Stretch")
            widget.stretchGroup.setLayout(widget.stretchLayout)

            # create a layout for the group boxes
            widget.mainLayout = QVBoxLayout(widget)
            widget.mainLayout.addWidget(widget.ruleGroup)
            widget.mainLayout.addWidget(widget.stretchGroup)

            # set the layout
            widget.setLayout(widget.mainLayout)

            # add the widget as a new tab
            name = "Rule %d" % count
            self.tabWidget.addTab(widget, name)
            self.widgetList.append(widget)
            count += 1

        # now sort out the rest of the dialog
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.tabWidget)

        # ok and cancel buttons
        self.okButton = QPushButton(self)
        self.okButton.setText("OK")
        self.okButton.setDefault(True)
        self.connect(self.okButton, SIGNAL("clicked()"), self.onOK)

        self.cancelButton = QPushButton(self)
        self.cancelButton.setText("Cancel")
        self.connect(self.cancelButton, SIGNAL("clicked()"), self.reject)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.mainLayout.addLayout(self.buttonLayout)

        self.setWindowTitle("Default Stretch")
        self.setSizeGripEnabled(True)
        self.resize(600,400)

    @staticmethod
    def fromSettings():
        """
        Read the default stretch rules from the 
        settings and return a list of StretchRules.
        Supplies a default set of rules if none found.
        """
        settings = QSettings()
        settings.beginGroup('Stretch')

        ruleList = []

        defaultRulesJSON = settings.value(DEFAULT_STRETCH_KEY)
        if defaultRulesJSON.isNull():
            # there isn't one, construct some defaults
            stretch = viewerstretch.ViewerStretch()

            # single band with color table
            stretch.setColorTable()
            stretch.setBands((1,))
            # must be one band and band one must have a color table
            rule = viewerstretch.StretchRule(
                        viewerstretch.VIEWER_COMP_EQ, 1, 1, stretch)
            ruleList.append(rule)

            # single band without color table
            stretch.setGreyScale()
            rule = viewerstretch.StretchRule( 
                        viewerstretch.VIEWER_COMP_EQ, 1, None, stretch)
            ruleList.append(rule)

            # 2 bands
            rule = viewerstretch.StretchRule( 
                        viewerstretch.VIEWER_COMP_EQ, 2, None, stretch)
            ruleList.append(rule)
            
            # 3 bands
            stretch.setRGB()
            stretch.setNoStretch()
            stretch.setBands((1,2,3))
            rule = viewerstretch.StretchRule(
                        viewerstretch.VIEWER_COMP_EQ, 3, None, stretch)
            ruleList.append(rule)

            # < 6 bands
            stretch.setStdDevStretch()
            stretch.setBands((4,3,2))
            rule = viewerstretch.StretchRule(
                        viewerstretch.VIEWER_COMP_LT, 6, None, stretch)
            ruleList.append(rule)

            # > 5 bands
            stretch.setBands((5,4,2))
            rule = viewerstretch.StretchRule(
                        viewerstretch.VIEWER_COMP_GT, 5, None, stretch)
            ruleList.append(rule)

        else:
            # is a list of json strings
            defaultRulesJSON = str(defaultRulesJSON.toString())
            for string in json.loads(defaultRulesJSON):
                # go through each one (which is itself a json string)
                # and decode into a StretchRule
                rule = viewerstretch.StretchRule.fromString(string)
                ruleList.append(rule)

        settings.endGroup()
        return ruleList

    def toSettings(self):
        """
        Write the contents of the dialog as the
        default rules to be remembered for next time. 
        """
        settings = QSettings()
        settings.beginGroup('Stretch')

        # go through each tab and turn
        # rules into JSON string and append to list
        defaultRulesList = []
        for widget in self.widgetList:
            stretch = widget.stretchLayout.getStretch()
            rule = widget.ruleLayout.getRule()
            rule.stretch = stretch
            
            string = rule.toString()
            defaultRulesList.append(string)

        # turn list into a json string and write to settings
        JSONstring = json.dumps(defaultRulesList)
        settings.setValue(DEFAULT_STRETCH_KEY, JSONstring)

        settings.endGroup()
        

    def onOK(self):
        """
        OK button pressed. Save settings
        """
        self.toSettings()
        QDialog.accept(self)

