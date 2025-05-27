"""
Save-As dialog for OpenTiler.
Handles saving original documents in different CAD formats.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QFileDialog,
    QGroupBox, QMessageBox, QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from ..formats.dxf_handler import DXFHandler
from ..formats.freecad_handler import FreeCADHandler


class SaveAsWorker(QThread):
    """Worker thread for save-as operations."""

    finished = Signal(bool, str)

    def __init__(self, handler, source_pixmap, output_path, scale_factor, units):
        super().__init__()
        self.handler = handler
        self.source_pixmap = source_pixmap
        self.output_path = output_path
        self.scale_factor = scale_factor
        self.units = units

    def run(self):
        """Run save-as operation in background thread."""
        try:
            success = False
            error_details = ""

            if isinstance(self.handler, DXFHandler):
                success = self.handler.save_as_dxf(
                    self.source_pixmap, self.output_path,
                    self.scale_factor, self.units
                )
                format_name = "DXF"
            elif isinstance(self.handler, FreeCADHandler):
                success = self.handler.save_as_freecad(
                    self.source_pixmap, self.output_path,
                    self.scale_factor, self.units
                )
                format_name = "FreeCAD"
            else:
                success = False
                format_name = "Unknown"

            if success:
                message = f"Save completed successfully: {self.output_path}"
            else:
                message = f"{format_name} save failed - check file path and permissions"

            self.finished.emit(success, message)

        except Exception as e:
            self.finished.emit(False, f"Save error: {str(e)}")


class SaveAsDialog(QDialog):
    """Dialog for saving documents in different CAD formats."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_pixmap = None
        self.scale_factor = 1.0
        self.save_worker = None

        self.setWindowTitle("Save As CAD Format")
        self.setModal(True)
        self.resize(500, 350)

        self.init_ui()
        self.check_format_availability()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Format selection
        format_group = QGroupBox("CAD Format")
        format_layout = QFormLayout()

        self.format_combo = QComboBox()
        self.format_combo.addItems(["DXF (AutoCAD)", "FreeCAD (.FCStd)"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addRow("Format:", self.format_combo)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # Scale settings
        scale_group = QGroupBox("Scale Information")
        scale_layout = QFormLayout()

        self.scale_label = QLabel("Not set")
        scale_layout.addRow("Current Scale:", self.scale_label)

        self.units_combo = QComboBox()
        self.units_combo.addItems(["mm", "inches"])
        scale_layout.addRow("Units:", self.units_combo)

        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)

        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout()

        # Output path
        path_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_output_path)
        path_layout.addWidget(self.output_path_edit)
        path_layout.addWidget(self.browse_button)
        output_layout.addRow("Output File:", path_layout)

        # Include grid option
        self.include_grid_check = QCheckBox("Include reference grid")
        self.include_grid_check.setChecked(True)
        output_layout.addRow("", self.include_grid_check)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(80)
        self.status_text.setReadOnly(True)
        font = QFont("Consolas", 9)
        self.status_text.setFont(font)
        layout.addWidget(self.status_text)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save As")
        self.save_button.clicked.connect(self.start_save)
        self.save_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Initialize UI state
        self.on_format_changed()

    def check_format_availability(self):
        """Check which formats are available and update UI."""
        dxf_available = DXFHandler.is_available()
        freecad_available = FreeCADHandler.is_available()

        if dxf_available:
            self.status_text.append("✅ DXF support available")
        else:
            self.status_text.append("⚠️ DXF support not available - install 'ezdxf' and 'matplotlib'")

        if freecad_available:
            freecad_status = FreeCADHandler.get_availability_status()
            self.status_text.append(f"✅ FreeCAD support available - {freecad_status}")
        else:
            self.status_text.append("⚠️ FreeCAD support not available - install FreeCAD")

        # Disable unavailable formats
        for i in range(self.format_combo.count()):
            item_text = self.format_combo.itemText(i)
            if "DXF" in item_text and not dxf_available:
                # Can't disable individual items in QComboBox easily
                # Will handle in save logic instead
                pass
            elif "FreeCAD" in item_text and not freecad_available:
                pass

    def on_format_changed(self):
        """Handle format selection change."""
        format_text = self.format_combo.currentText()

        # Update default extension
        if "DXF" in format_text:
            self.update_output_extension(".dxf")
        elif "FreeCAD" in format_text:
            self.update_output_extension(".FCStd")

    def update_output_extension(self, new_ext):
        """Update output path extension."""
        current_path = self.output_path_edit.text()
        if current_path:
            base_path = os.path.splitext(current_path)[0]
            self.output_path_edit.setText(base_path + new_ext)

    def browse_output_path(self):
        """Browse for output path."""
        format_text = self.format_combo.currentText()

        if "DXF" in format_text:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save as DXF", "", "DXF Files (*.dxf)"
            )
        elif "FreeCAD" in format_text:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save as FreeCAD", "", "FreeCAD Files (*.FCStd)"
            )
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save As", "", "All Files (*.*)"
            )

        if file_path:
            self.output_path_edit.setText(file_path)

    def set_document_data(self, source_pixmap, scale_factor):
        """Set the document data to save."""
        self.source_pixmap = source_pixmap
        self.scale_factor = scale_factor

        # Update scale display
        if scale_factor != 1.0:
            self.scale_label.setText(f"{scale_factor:.6f} mm/pixel")
        else:
            self.scale_label.setText("Not set (1:1)")

        # Update status
        self.status_text.append(f"Document loaded: {source_pixmap.width()}x{source_pixmap.height()} pixels")
        if scale_factor != 1.0:
            real_width = source_pixmap.width() * scale_factor
            real_height = source_pixmap.height() * scale_factor
            self.status_text.append(f"Real-world size: {real_width:.2f}x{real_height:.2f} mm")

    def start_save(self):
        """Start the save process."""
        if not self.source_pixmap:
            QMessageBox.warning(self, "Error", "No document to save")
            return

        output_path = self.output_path_edit.text().strip()
        if not output_path:
            QMessageBox.warning(self, "Error", "Please specify output file")
            return

        format_text = self.format_combo.currentText()
        units = self.units_combo.currentText()

        # Add proper file extension if missing
        if "DXF" in format_text:
            if not output_path.lower().endswith('.dxf'):
                output_path += '.dxf'
                self.output_path_edit.setText(output_path)
                self.status_text.append(f"Added .dxf extension: {output_path}")
        elif "FreeCAD" in format_text:
            if not output_path.lower().endswith('.fcstd'):
                output_path += '.FCStd'
                self.output_path_edit.setText(output_path)
                self.status_text.append(f"Added .FCStd extension: {output_path}")

        # Check format availability
        if "DXF" in format_text:
            if not DXFHandler.is_available():
                QMessageBox.warning(self, "DXF Not Available",
                                  "DXF support requires 'ezdxf' and 'matplotlib' packages.\n"
                                  "Install with: pip install ezdxf matplotlib")
                return
            handler = DXFHandler()
        elif "FreeCAD" in format_text:
            if not FreeCADHandler.is_available():
                QMessageBox.warning(self, "FreeCAD Not Available",
                                  "FreeCAD support requires FreeCAD to be installed.\n"
                                  "Please install FreeCAD and ensure it's in your system PATH.")
                return
            handler = FreeCADHandler()
        else:
            QMessageBox.warning(self, "Error", "Unknown format selected")
            return

        # Start save in background thread
        self.save_worker = SaveAsWorker(
            handler, self.source_pixmap, output_path, self.scale_factor, units
        )
        self.save_worker.finished.connect(self.on_save_finished)

        # Update UI for save
        self.save_button.setEnabled(False)
        self.status_text.append("Starting save operation...")

        self.save_worker.start()

    def on_save_finished(self, success, message):
        """Handle save completion."""
        self.save_button.setEnabled(True)
        self.status_text.append(message)

        if success:
            QMessageBox.information(self, "Save Complete", "Document saved successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Save Failed", f"Save failed: {message}")

    def closeEvent(self, event):
        """Handle dialog close."""
        if self.save_worker and self.save_worker.isRunning():
            self.save_worker.terminate()
            self.save_worker.wait()
        event.accept()
