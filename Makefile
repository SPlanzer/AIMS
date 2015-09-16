###### EDIT ##################### 
#Directory with ui and resource files
RESOURCE_DIR = /ElectoralAddressPlugin
 
#Directory for compiled resources
COMPILED_DIR = /ElectoralAddressPlugin
 
#UI files to compile
UI_FILES = Ui_InfoWidget.ui Ui_DelAddressDialog.ui \
	ElectoralAddress/Gui/Ui_ReviewQueueWidget.ui \
	ElectoralAddress/Gui/Ui_AddressEditorWidget.ui \
	ElectoralAddress/Gui/Ui_AddressLinkingWidget.ui \
	ElectoralAddress/Gui/Ui_AdminDialog.ui \
	ElectoralAddress/Gui/Ui_ConfigureDatabase.ui \
	ElectoralAddress/Gui/Ui_CreateUploadWidget.ui \
	ElectoralAddress/Gui/Ui_JobEditorWidget.ui \
	ElectoralAddress/Gui/Ui_JobManagerWidget.ui \
	ElectoralAddress/Gui/Ui_JobSelectorDialog.ui \
	ElectoralAddress/Gui/Ui_ManageSourceTypes.ui \
	ElectoralAddress/Gui/Ui_ManageSuppliers.ui \
	ElectoralAddress/Gui/Ui_NewJobDialog.ui \
	ElectoralAddress/Gui/Ui_ReviewEditorWidget.ui \
	ElectoralAddress/Gui/Ui_ReviewQueueWidget.ui

#Qt resource files to compile
RESOURCES = Resources.qrc
 
#pyuic4 and pyrcc4 binaries
PYUIC = pyuic4
PYRCC = pyrcc4
 
#################################
# DO NOT EDIT FOLLOWING
 
COMPILED_UI = $(UI_FILES:%.ui=$(COMPILED_DIR)/%.py)
COMPILED_RESOURCES = $(RESOURCES:%.qrc=$(COMPILED_DIR)/%.py)
 
all : resources ui 
 
resources : $(COMPILED_RESOURCES) 
 
ui : $(COMPILED_UI)
 
$(COMPILED_DIR)/%.py : $(RESOURCE_DIR)/%.ui
	$(PYUIC) $< -o $@
 
$(COMPILED_DIR)/%.py : $(RESOURCE_DIR)/%.qrc
	-$(PYRCC) $< -o $@
 
clean : 
	$(RM) $(COMPILED_UI) $(COMPILED_RESOURCES) $(COMPILED_UI:.py=.pyc) $(COMPILED_RESOURCES:.py=.pyc)  