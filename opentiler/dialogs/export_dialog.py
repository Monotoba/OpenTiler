"""
Export dialog for OpenTiler.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QCheckBox,
    QLineEdit, QFileDialog, QGroupBox, QMessageBox,
    QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from ..exporter.pdf_exporter import PDFExporter
from ..exporter.image_exporter import ImageExporter


class ExportWorker(QThread):
    """Worker thread for export operations."""

    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self, exporter, source_pixmap, page_grid, output_path, **kwargs):
        super().__init__()
        self.exporter = exporter
        self.source_pixmap = source_pixmap
        self.page_grid = page_grid
        self.output_path = output_path
        self.kwargs = kwargs

    def run(self):
        """Run export in background thread."""
        try:
            success = self.exporter.export(
                self.source_pixmap,
                self.page_grid,
                self.output_path,
                **self.kwargs
            )
            self.finished.emit(success, "Export completed successfully" if success else "Export failed")
        except Exception as e:
            self.finished.emit(False, f"Export error: {str(e)}")


class ExportDialog(QDialog):
    """Dialog for exporting tiled documents."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_pixmap = None
        self.page_grid = None
        self.export_worker = None

        self.setWindowTitle("Export Tiles")
        self.setModal(True)
        self.resize(500, 400)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Export format selection
        format_group = QGroupBox("Export Format")
        format_layout = QFormLayout()

        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF (Multi-page)", "PNG Images", "JPEG Images", "TIFF Images"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addRow("Format:", self.format_combo)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

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
        output_layout.addRow("Output Path:", path_layout)

        # Quality setting (for images)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(95)
        self.quality_spin.setSuffix("%")
        output_layout.addRow("Image Quality:", self.quality_spin)

        # Page size (for PDF)
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["A4", "Letter", "A3", "Legal", "Tabloid"])
        output_layout.addRow("Page Size:", self.page_size_combo)

        # Composite option (for images)
        self.composite_check = QCheckBox("Export as single composite image")
        output_layout.addRow("", self.composite_check)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        font = QFont("Consolas", 9)
        self.status_text.setFont(font)
        layout.addWidget(self.status_text)

        # Buttons
        button_layout = QHBoxLayout()

        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.start_export)
        self.export_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Initialize UI state
        self.on_format_changed()

    def on_format_changed(self):
        """Handle format selection change."""
        format_text = self.format_combo.currentText()

        # Show/hide relevant options
        is_pdf = "PDF" in format_text
        is_image = not is_pdf

        self.quality_spin.setVisible(is_image)
        self.page_size_combo.setVisible(is_pdf)
        self.composite_check.setVisible(is_image)

        # Update default extension
        if is_pdf:
            self.update_output_extension(".pdf")
        elif "PNG" in format_text:
            self.update_output_extension(".png")
        elif "JPEG" in format_text:
            self.update_output_extension(".jpg")
        elif "TIFF" in format_text:
            self.update_output_extension(".tiff")

    def update_output_extension(self, new_ext):
        """Update output path extension."""
        current_path = self.output_path_edit.text()
        if current_path:
            base_path = os.path.splitext(current_path)[0]
            self.output_path_edit.setText(base_path + new_ext)

    def browse_output_path(self):
        """Browse for output path."""
        format_text = self.format_combo.currentText()

        if "PDF" in format_text:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export PDF", "", "PDF Files (*.pdf)"
            )
            if file_path:
                self.output_path_edit.setText(file_path)
        else:
            if self.composite_check.isChecked():
                # Single file
                if "PNG" in format_text:
                    filter_str = "PNG Files (*.png)"
                elif "JPEG" in format_text:
                    filter_str = "JPEG Files (*.jpg)"
                elif "TIFF" in format_text:
                    filter_str = "TIFF Files (*.tiff)"
                else:
                    filter_str = "Image Files (*.png *.jpg *.tiff)"

                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Export Image", "", filter_str
                )
                if file_path:
                    self.output_path_edit.setText(file_path)
            else:
                # Directory for multiple files
                dir_path = QFileDialog.getExistingDirectory(
                    self, "Select Output Directory"
                )
                if dir_path:
                    self.output_path_edit.setText(dir_path)

    def set_export_data(self, source_pixmap, page_grid):
        """Set the data to export."""
        self.source_pixmap = source_pixmap
        self.page_grid = page_grid

        # Update status
        self.status_text.append(f"Ready to export {len(page_grid)} pages")

    def start_export(self):
        """Start the export process."""
        if not self.source_pixmap or not self.page_grid:
            QMessageBox.warning(self, "Error", "No data to export")
            return

        output_path = self.output_path_edit.text().strip()
        if not output_path:
            QMessageBox.warning(self, "Error", "Please specify output path")
            return

        # Prepare export parameters
        format_text = self.format_combo.currentText()

        if "PDF" in format_text:
            exporter = PDFExporter()
            kwargs = {
                'page_size': self.page_size_combo.currentText()
            }
        else:
            exporter = ImageExporter()
            if "PNG" in format_text:
                image_format = "PNG"
            elif "JPEG" in format_text:
                image_format = "JPEG"
            elif "TIFF" in format_text:
                image_format = "TIFF"
            else:
                image_format = "PNG"

            kwargs = {
                'image_format': image_format,
                'quality': self.quality_spin.value()
            }

            # Use composite export if requested
            if self.composite_check.isChecked():
                exporter.export_composite = True

        # Start export in background thread
        self.export_worker = ExportWorker(
            exporter, self.source_pixmap, self.page_grid, output_path, **kwargs
        )
        self.export_worker.finished.connect(self.on_export_finished)

        # Update UI for export
        self.export_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_text.append("Starting export...")

        self.export_worker.start()

    def on_export_finished(self, success, message):
        """Handle export completion."""
        self.progress_bar.setVisible(False)
        self.export_button.setEnabled(True)

        self.status_text.append(message)

        if success:
            QMessageBox.information(self, "Export Complete", "Export completed successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Export Failed", f"Export failed: {message}")

    def closeEvent(self, event):
        """Handle dialog close."""
        if self.export_worker and self.export_worker.isRunning():
            self.export_worker.terminate()
            self.export_worker.wait()
        event.accept()
