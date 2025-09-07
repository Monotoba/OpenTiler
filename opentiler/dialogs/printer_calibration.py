from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QDoubleSpinBox, QFormLayout, QGroupBox,
                               QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                               QSpacerItem, QVBoxLayout)


class PrinterCalibrationDialog(QDialog):
    """Dialog to calibrate printer horizontal/vertical offsets per orientation."""

    def __init__(self, parent, config):
        super().__init__(parent)
        self.setWindowTitle("Printer Calibration")
        self.config = config
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Header row with help button (top-right)
        header_row = QHBoxLayout()
        header_label = QLabel(
            "Adjust safety insets (mm) to avoid right/bottom clipping.\n"
            "These values reduce the usable printable area. Print calibration sheets\n"
            "and enter measurements per orientation."
        )
        header_row.addWidget(header_label)
        header_row.addItem(
            QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        help_btn = QPushButton("Help")
        help_btn.setToolTip("Open calibration help")
        try:
            help_btn.clicked.connect(
                lambda: getattr(self.parent(), "show_help", lambda *a, **k: None)(
                    "printer_calibration.md"
                )
            )
        except Exception:
            pass
        header_row.addWidget(help_btn)
        layout.addLayout(header_row)

        # Portrait
        # Portrait section
        portrait_group = QGroupBox("Portrait Calibration")
        portrait_form = QFormLayout(portrait_group)
        self.p_h = QDoubleSpinBox()
        self.p_h.setRange(0.0, 50.0)
        self.p_h.setSuffix(" mm")
        self.p_h.setDecimals(1)
        self.p_v = QDoubleSpinBox()
        self.p_v.setRange(0.0, 50.0)
        self.p_v.setSuffix(" mm")
        self.p_v.setDecimals(1)
        ph, pv = self.config.get_print_calibration("portrait")
        self.p_h.setValue(ph)
        self.p_v.setValue(pv)
        self.p_h.setToolTip(
            "Portrait: Horizontal (right) calibration in millimeters.\nShrinks usable width from the right edge by this amount."
        )
        self.p_v.setToolTip(
            "Portrait: Vertical (bottom) calibration in millimeters.\nShrinks usable height from the bottom edge by this amount."
        )
        portrait_form.addRow("Horizontal (right):", self.p_h)
        portrait_form.addRow("Vertical (bottom):", self.p_v)
        layout.addWidget(portrait_group)

        # Landscape
        # Landscape section
        landscape_group = QGroupBox("Landscape Calibration")
        landscape_form = QFormLayout(landscape_group)
        self.l_h = QDoubleSpinBox()
        self.l_h.setRange(0.0, 50.0)
        self.l_h.setSuffix(" mm")
        self.l_h.setDecimals(1)
        self.l_v = QDoubleSpinBox()
        self.l_v.setRange(0.0, 50.0)
        self.l_v.setSuffix(" mm")
        self.l_v.setDecimals(1)
        lh, lv = self.config.get_print_calibration("landscape")
        self.l_h.setValue(lh)
        self.l_v.setValue(lv)
        self.l_h.setToolTip(
            "Landscape: Horizontal (right) calibration in millimeters.\nShrinks usable width from the right edge by this amount."
        )
        self.l_v.setToolTip(
            "Landscape: Vertical (bottom) calibration in millimeters.\nShrinks usable height from the bottom edge by this amount."
        )
        landscape_form.addRow("Horizontal (right):", self.l_h)
        landscape_form.addRow("Vertical (bottom):", self.l_v)
        layout.addWidget(landscape_group)

        # Ladder measured inputs (Portrait)
        ladder_p_group = QGroupBox("Portrait Ladder Measurements")
        ladder_p_form = QFormLayout(ladder_p_group)
        self.p_meas_h = QDoubleSpinBox()
        self.p_meas_h.setRange(0.0, 50.0)
        self.p_meas_h.setSuffix(" mm")
        self.p_meas_h.setDecimals(1)
        self.p_meas_v = QDoubleSpinBox()
        self.p_meas_v.setRange(0.0, 50.0)
        self.p_meas_v.setSuffix(" mm")
        self.p_meas_v.setDecimals(1)
        self.p_meas_h.setToolTip(
            "From the Portrait ladder sheet: largest visible RIGHT tick in millimeters."
        )
        self.p_meas_v.setToolTip(
            "From the Portrait ladder sheet: largest visible BOTTOM tick in millimeters."
        )
        ladder_p_form.addRow("Measured right (mm):", self.p_meas_h)
        ladder_p_form.addRow("Measured bottom (mm):", self.p_meas_v)
        layout.addWidget(ladder_p_group)

        # Ladder measured inputs (Landscape)
        ladder_l_group = QGroupBox("Landscape Ladder Measurements")
        ladder_l_form = QFormLayout(ladder_l_group)
        self.l_meas_h = QDoubleSpinBox()
        self.l_meas_h.setRange(0.0, 50.0)
        self.l_meas_h.setSuffix(" mm")
        self.l_meas_h.setDecimals(1)
        self.l_meas_v = QDoubleSpinBox()
        self.l_meas_v.setRange(0.0, 50.0)
        self.l_meas_v.setSuffix(" mm")
        self.l_meas_v.setDecimals(1)
        self.l_meas_h.setToolTip(
            "From the Landscape ladder sheet: largest visible RIGHT tick in millimeters."
        )
        self.l_meas_v.setToolTip(
            "From the Landscape ladder sheet: largest visible BOTTOM tick in millimeters."
        )
        ladder_l_form.addRow("Measured right (mm):", self.l_meas_h)
        ladder_l_form.addRow("Measured bottom (mm):", self.l_meas_v)
        layout.addWidget(ladder_l_group)

        # Buttons
        btns = QHBoxLayout()
        print_btn = QPushButton("Print Debug Page...")
        print_l_p = QPushButton("Print Ladder (Portrait)")
        print_l_l = QPushButton("Print Ladder (Landscape)")
        save_btn = QPushButton("Save")
        close_btn = QPushButton("Close")
        btns.addWidget(print_btn)
        btns.addWidget(print_l_p)
        btns.addWidget(print_l_l)
        btns.addStretch()
        btns.addWidget(save_btn)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

        def on_print():
            # Save temp values and print a single debug page (not all tiles)
            self._apply_to_config()
            try:
                self.parent().print_debug_page()
            except Exception:
                pass

        def on_save():
            self._apply_to_config()

        def on_print_l_p():
            self._apply_to_config()
            try:
                self.parent().print_ladder_test("portrait")
            except Exception:
                pass

        def on_print_l_l():
            self._apply_to_config()
            try:
                self.parent().print_ladder_test("landscape")
            except Exception:
                pass

        def on_apply_from_ladder():
            # Populate H/V from measured values so user can add tiny extra if desired
            self.p_h.setValue(self.p_meas_h.value())
            self.p_v.setValue(self.p_meas_v.value())
            self.l_h.setValue(self.l_meas_h.value())
            self.l_v.setValue(self.l_meas_v.value())

        # Secondary row for ladder apply
        apply_row = QHBoxLayout()
        apply_btn = QPushButton("Set From Ladder Measurements")
        apply_btn.setToolTip(
            "Copy measured values into calibration fields; you can then add a small extra if desired."
        )
        apply_row.addWidget(apply_btn)
        layout.addLayout(apply_row)

        print_btn.clicked.connect(on_print)
        print_l_p.clicked.connect(on_print_l_p)
        print_l_l.clicked.connect(on_print_l_l)
        apply_btn.clicked.connect(on_apply_from_ladder)
        save_btn.clicked.connect(on_save)
        close_btn.clicked.connect(self.accept)

    def _apply_to_config(self):
        self.config.set_print_calibration(
            "portrait", self.p_h.value(), self.p_v.value()
        )
        self.config.set_print_calibration(
            "landscape", self.l_h.value(), self.l_v.value()
        )
