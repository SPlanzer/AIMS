###### EDIT ##################### 
#Directory with ui and resource files
RESOURCE_DIR = ElectoralAddressPlugin
 
#Directory for compiled resources
COMPILED_DIR = ElectoralAddressPlugin
 
#UI files to compile
UI_FILES = \
	ElectoralAddress/Gui/Ui_JobManagerWidget.ui \
	Ui_DelAddressDialog.ui
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