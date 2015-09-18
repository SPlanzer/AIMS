

###### EDIT ##################### 
#Directory with ui and resource files
RESOURCE_DIR = ./
 
#Directory for compiled resources
COMPILED_DIR = ./
  
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

pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --reports=n --rcfile=pylintrc . || true
# Run pep8 style checking
#http://pypi.python.org/pypi/pep8

pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E101,E201,E202,E203,E211,E225,E227,E226,E228,E231,E251,E261,E262,E293,W293,E121,E122,E123,E124,E125,E126,E127,E128,E501,E301,E302,E701,E702,E711,W291  --exclude pydev,resources.py,conf.py . || true


clean : 
	$(RM) $(COMPILED_UI) $(COMPILED_RESOURCES) $(COMPILED_UI:.py=.pyc) $(COMPILED_RESOURCES:.py=.pyc)  


