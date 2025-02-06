# Painter API Module
import substance_painter as sp
import substance_painter_plugins as spp

# 3rd party ui lib
from PySide2 import QtWidgets, QtCore, QtGui

# custom exporter modules
import module_export
import module_validation_name
import module_validation_resolution

# default utils
import importlib
import os

is_user_dev = True
if is_user_dev:
    importlib.reload(module_export)
    importlib.reload(module_validation_name)

CUSTOM_EXPORTER = None


class CustomExporter():
    def __init__(self):
        self.initialization()

    def initialization(self):
        self.init_widget_window()
        self.show_ui_widget()
        self.connect_widget_events()
        self.connect_painter_events()

    def init_widget_window(self):
        self.asset_types = ["Props", "Weapons", "Characters"]
        self.shader_types = ["Basic", "Armament", "Morph"]
        self.texsets_with_overbudget_res = []
        self.widget = QtWidgets.QWidget()
        self.widget.setObjectName("Custom Exporter")
        self.widget.setWindowTitle("CUSTOM EXPORTER")

        self.file_dir = os.path.dirname(__file__)

        self.icon_path = os.path.join(self.file_dir, "Icons")

        self.icon_main_window = QtGui.QIcon(os.path.join(self.icon_path, "main_window_icon.png"))
        self.icon_validation_ok = QtGui.QIcon(os.path.join(self.icon_path, "validation_ok.png"))
        self.icon_validation_fail = QtGui.QIcon(os.path.join(self.icon_path, "validation_fail.png"))
        self.pixmap_help= QtGui.QPixmap(os.path.join(self.icon_path, "help.png"))
        self.widget.setWindowIcon(self.icon_main_window)
        self.layout = QtWidgets.QVBoxLayout(self.widget)

        # help icon
        help_layout = QtWidgets.QHBoxLayout()
        help_layout.setAlignment(QtCore.Qt.AlignRight)
        help_label = QtWidgets.QLabel()
        scaled_pixmap = self.pixmap_help.scaled(32, 32)
        help_label.setPixmap(scaled_pixmap)
        help_label.setFixedSize(scaled_pixmap.size())
        help_label.mousePressEvent = self.show_help
        help_label.setToolTip("Click for help documentation. \nHotkey: Alt + F1")
        help_layout.addWidget(help_label)
        self.layout.addLayout(help_layout)

        # help action
        self.help_action = QtWidgets.QAction("Show Help", self.widget)
        self.help_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.ALT + QtCore.Qt.Key_F1))
        self.widget.addAction(self.help_action)

        # personal export checkbox
        self.personal_export_cb = QtWidgets.QCheckBox("Personal Export")
        self.personal_export_cb.setToolTip("Specify desired project root export path: Personal or Official")
        self.layout.addWidget(self.personal_export_cb)

        # label
        self.label = QtWidgets.QLabel("Asset Type:")
        self.layout.addWidget(self.label)

        # asset type combo box
        self.asset_type_cmb = QtWidgets.QComboBox()
        self.asset_type_cmb.addItems(self.asset_types)
        self.asset_type_cmb.setToolTip("Specify type of the asset. It will affect Export path generation and Texture Set validations")
        self.layout.addWidget(self.asset_type_cmb)

        self.refresh_table_button = QtWidgets.QPushButton("Refresh")
        self.refresh_table_button.setToolTip("Refresh data in the Table below. \nHotkey: Alt + R")
        self.refresh_table_button.setShortcut(QtGui.QKeySequence(QtCore.Qt.ALT + QtCore.Qt.Key_R))
        self.layout.addWidget(self.refresh_table_button)

        # table
        self.texset_table = QtWidgets.QTableWidget()
        self.texset_table.setMinimumSize(730, 250)
        self.init_texset_table()
        self.layout.addWidget(self.texset_table)

        # export push button
        self.export_button = QtWidgets.QPushButton("Export")
        self.export_button.setToolTip("Trigger export of the selected textuyre sets. \nHotkey: Alt + E")
        self.export_button.setShortcut(QtGui.QKeySequence(QtCore.Qt.ALT + QtCore.Qt.Key_E))
        self.layout.addWidget(self.export_button)

        if sp.project.is_open():
            self.fill_texset_table()
            settings = QtCore.QSettings()
            settings.setValue("dialog_window_checkbox_state", QtCore.Qt.Unchecked)

    def connect_widget_events(self):
        self.export_button.clicked.connect(self.on_export_request)
        self.refresh_table_button.clicked.connect(self.on_refresh_texset_table)
        self.personal_export_cb.stateChanged.connect(self.on_refresh_texset_table)
        self.asset_type_cmb.currentIndexChanged.connect(self.on_refresh_texset_table)
        self.help_action.triggered.connect(self.show_help)

    def connect_painter_events(self):
        painter_connections = {
                sp.event.ProjectOpened: self.on_project_opened,
                sp.event.ProjectCreated: self.on_project_created,
                sp.event.ProjectAboutToClose: self.on_project_close,
                }

        for event, callback in painter_connections.items():
            sp.event.DISPATCHER.connect(event, callback)

    def show_ui_widget(self):
        plugin = spp.plugins.get("Custom Exporter", None)
        if plugin is not None:
            # Refresh of the widget
            self.delete_widget()
            self.init_widget_window()

        sp.ui.add_dock_widget(self.widget)
        self.widget.show()

    def show_help(self, event):
        help_doc_path = os.path.join(self.file_dir, "Custom_Exporter_Help.pdf")
        help_url = QtCore.QUrl.fromLocalFile(help_doc_path)
        QtGui.QDesktopServices.openUrl(help_url)

    def init_texset_table(self):
        column_headers = ["Export", "Texture Set Name", "Shader Type", "Resolution", "Export Path", "Validation"]
        num_coloumn = len(column_headers)
        num_row = 0

        self.texset_table.setColumnCount(num_coloumn)
        self.texset_table.setRowCount(num_row)

        self.texset_table.setHorizontalHeaderLabels(column_headers)

        self.texset_table.verticalHeader().setVisible(False)

        self.texset_table.setColumnWidth(0, 40)
        self.texset_table.setColumnWidth(3, 70)
        self.texset_table.setColumnWidth(4, 350)
        self.texset_table.setColumnWidth(5, 70)

    def fill_texset_table(self):
        self.all_texture_sets = sp.textureset.all_texture_sets()
        self.texset_table.setRowCount(len(self.all_texture_sets))

        for i, texture_set in enumerate(self.all_texture_sets):
            # Use QCheckbox for the "Export" column
            check_box = QtWidgets.QCheckBox()
            check_box.setChecked(True)
            check_box.stateChanged.connect(self.gray_out_unchecked_rows)
            self.texset_table.setCellWidget(i, 0, check_box)

            # Texture set name Column
            self.texset_table.setItem(i, 1, QtWidgets.QTableWidgetItem(texture_set.name()))

            # use QComboBox for "Shader Type" column
            combo_box = QtWidgets.QComboBox()
            combo_box.addItems(self.shader_types)
            combo_box.currentIndexChanged.connect(self.on_refresh_texset_table)
            combo_box.setToolTip("Specify Type of the export preset to be used during the export")
            self.texset_table.setCellWidget(i, 2, combo_box)

            # Resolution Column
            resolution = texture_set.get_resolution()
            width = resolution.width
            height = resolution.height
            self.texset_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{width} x {height}"))

        self.on_refresh_texset_table()

    def validate_texture_sets(self):
        asset_type = self.asset_type_cmb.currentText()
        self.texsets_with_overbudget_res = []
        for i, texture_set in enumerate(self.all_texture_sets):
            res_is_valid, res_validation_details = module_validation_resolution.validate_res(asset_type, texture_set.get_resolution())
            validation_item = QtWidgets.QTableWidgetItem()
            export_checkbox = self.texset_table.cellWidget(i, 0)
            if res_is_valid:
                name_is_valid, name_validation_details = module_validation_name.validate_name(asset_type, texture_set.name())
                if name_is_valid:
                    validation_item.setIcon(self.icon_validation_ok)
                    validation_item.setToolTip(f"Texture set validation are OK for texture set {i+1} \
                                                \n{texture_set.name()}")
                    export_checkbox.setToolTip(f"Texture set validation are OK for texture set {i+1} \
                            \n{texture_set.name()}")
                else:
                    validation_item.setIcon(self.icon_validation_fail)
                    validation_item.setToolTip(f"Texture set name validation is FAILED for texture set {i+1} \
                                                \n{texture_set.name()} \
                                                \nReason: {name_validation_details} \
                                                \nExport of this texture set is disabled until validation is OK")
                    export_checkbox.setToolTip(f"Texture set name validation is FAILED for texture set {i+1} \
                                                \n{texture_set.name()} \
                                                \nReason: {name_validation_details} \
                                                \nExport of this texture set is disabled until validation is OK")

            else:
                validation_item.setIcon(self.icon_validation_fail)
                validation_item.setToolTip(f"Texture set Resolution validation is FAILED for texture set {i+1} \
                                            \n{texture_set.name()} \
                                            \nReason: {res_validation_details} \
                                            \nExport of this texture set is disabled until validation is OK")
                export_checkbox.setToolTip(f"Texture set Resolution validation is FAILED for texture set {i+1} \
                                            \n{texture_set.name()} \
                                            \nReason: {res_validation_details} \
                                            \nExport of this texture set is disabled until validation is OK")
                self.texsets_with_overbudget_res.append(texture_set)

            export_checkbox.setChecked(res_is_valid and name_is_valid)
            export_checkbox.setEnabled(res_is_valid and name_is_valid)
            self.texset_table.setItem(i, 5, validation_item)

        if len(self.texsets_with_overbudget_res) > 0:
            self.open_dialog_res_confirmation()

    def open_dialog_res_confirmation(self):
        settings = QtCore.QSettings()
        if settings.value("dialog_window_checkbox_state", QtCore.Qt.Unchecked) == QtCore.Qt.Unchecked:
            dialog = DialogWindow(self.icon_main_window)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                self.apply_required_res()
                self.on_refresh_texset_table()
            else:
                sp.logging.log(
                        sp.logging.WARNING,
                        "CUSTOM EXPORTER",
                        "Remember to manually fix the resolution in the texture set settings. Validation error would present from export"
                        )
        else:
            sp.logging.log(
                    sp.logging.INFO,
                    "CUSTOM EXPORTER",
                    "dialog for Resolution validation autofix was not triggered as per user settings"
                    )

    def apply_required_res(self):
        required_widht, required_height = module_validation_resolution.get_required_res_from_asset_type(self.asset_type_cmb.currentText())
        required_res = sp.textureset.Resolution(required_widht, required_height)
        for texture_set in self.texsets_with_overbudget_res:
            original_resolution = texture_set.get_resolution()
            texture_set.set_resolution(required_res)
            sp.logging.log(sp.logging.INFO,
                           "CUSTOM EXPORTER",
                           f"Applied required resolution for texture sets {texture_set.name()} \
                            \nWas: {original_resolution}; Now: {required_res}"
                           )

    def gray_out_unchecked_rows(self):
        for i in range(self.texset_table.rowCount()):
            check_box_item = self.texset_table.cellWidget(i, 0)
            if check_box_item.isChecked():
                for j in range(1, self.texset_table.columnCount() -1):
                    item = self.texset_table.item(i, j)
                    if item is not None:
                        item.setFlags(item.flags() | QtCore.Qt.ItemIsEnabled)
                    else:
                        cell_widget = self.texset_table.cellWidget(i, j)
                        if cell_widget is not None:
                            cell_widget.setEnabled(True)
            else:
                for j in range(1, self.texset_table.columnCount() -1):
                    item = self.texset_table.item(i, j)
                    if item is not None:
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
                    else:
                        cell_widget = self.texset_table.cellWidget(i, j)
                        if cell_widget is not None:
                            cell_widget.setDisabled(True)

    def on_refresh_texset_table(self):
        if sp.project.is_open():
            export_path_root = self.build_root_export_path()
            if self.all_texture_sets is not None:
                for i, texture_set in enumerate(self.all_texture_sets):
                    # Texture set name Column
                    self.texset_table.setItem(i, 1, QtWidgets.QTableWidgetItem(texture_set.name()))

                    # Resolution Column
                    resolution = texture_set.get_resolution()
                    width = resolution.width
                    height = resolution.height
                    self.texset_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{width} x {height}"))

                    # export path
                    self.texset_table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{export_path_root}/{self.asset_type_cmb.currentText()}/{texture_set.name()}/{self.texset_table.cellWidget(i, 2).currentText()}"))

                self.validate_texture_sets()
                self.gray_out_unchecked_rows()

                self.set_column_read_only(1)  # set read-only to name column
                self.set_column_read_only(3)  # set read-only to resolution column
                self.set_column_read_only(4)  # set read-only to export path column
                self.set_column_read_only(5)  # set read-only to validation column

    def set_column_read_only(self, column_index):
        for row in range(self.texset_table.rowCount()):
            item = self.texset_table.item(row, column_index)
            if item is not None:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)

    def build_root_export_path(self):
        if self.personal_export_cb.isChecked():
            root = "C:/Test"
        else:
            root = "D:/Test"
        return root

    def delete_widget(self):
        while self.widget is not None:
            sp.ui.delete_ui_element(self.widget)

    def on_export_request(self):
        if self.all_texture_sets is not None:
            for i in range(len(self.all_texture_sets)):
                should_export = self.texset_table.cellWidget(i, 0).isChecked()
                if not should_export:
                    continue

                texture_set_name = self.texset_table.item(i, 1).text()
                shader_type = self.texset_table.cellWidget(i, 2).currentText()
                export_path = self.texset_table.item(i, 4).text()
                module_export.export_textures(texture_set_name, shader_type, export_path)

    def on_project_opened(self, e):
        settings = QtCore.QSettings()
        settings.setValue("dialog_window_checkbox_state", QtCore.Qt.Unchecked)
        self.fill_texset_table()

    def on_project_created(self, e):
        self.fill_texset_table()

    def on_project_close(self,e):
        self.init_texset_table()

class DialogWindow(QtWidgets.QDialog):
    def __init__(self, icon):
        super().__init__()
        self.setWindowTitle("Texture set Resolution is over Budget")
        self.setWindowIcon(icon)
        self.setFixedSize(600, 160)

        layout = QtWidgets.QVBoxLayout(self)

        text_label = QtWidgets.QLabel("There is a validation error in the resolution check step. \nBut, no worries, the tool can automatically adjust the resolution of all texture sets that do not meet the requirment. \nDo you want to proceed?")

        layout.addWidget(text_label)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.No)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QtWidgets.QDialogButtonBox.Yes).setText("Yes, apply the required resolution for all texture asets.")
        buttons.button(QtWidgets.QDialogButtonBox.No).setText("No, i'll modify the resolution manually")
        layout.addWidget(buttons)

        checkbox = QtWidgets.QCheckBox("Do not show this window again")
        checkbox.setChecked(False)
        checkbox.stateChanged.connect(self.save_checkbox_state)
        layout.addWidget(checkbox)

    def save_checkbox_state(self, state):
        settings = QtCore.QSettings()
        settings.setValue("dialog_window_checkbox_state", state)


def start_plugin():
    global CUSTOM_EXPORTER
    CUSTOM_EXPORTER = CustomExporter()


def close_plugin():
    global CUSTOM_EXPORTER
    CUSTOM_EXPORTER.delete_widget()


if __name__ == "__main__":
    start_plugin()
