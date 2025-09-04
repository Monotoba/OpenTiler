from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton
from PySide6.QtCore import Qt


class PrinterCalibrationDialog(QDialog):
    """Dialog to calibrate printer horizontal/vertical offsets per orientation."""

    def __init__(self, parent, config):
        super().__init__(parent)
        self.setWindowTitle("Printer Calibration")
        self.config = config
        self.setModal(True)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Adjust safety insets (mm) to avoid right/bottom clipping.\n"
                                "These values reduce the usable printable area.\n"
                                "Print the test page in both Portrait and Landscape."))

        # Portrait
        portrait_form = QFormLayout()
        self.p_h = QDoubleSpinBox(); self.p_h.setRange(0.0, 50.0); self.p_h.setSuffix(" mm"); self.p_h.setDecimals(1)
        self.p_v = QDoubleSpinBox(); self.p_v.setRange(0.0, 50.0); self.p_v.setSuffix(" mm"); self.p_v.setDecimals(1)
        ph, pv = self.config.get_print_calibration("portrait")
        self.p_h.setValue(ph); self.p_v.setValue(pv)
        portrait_form.addRow("Portrait horizontal (right):", self.p_h)
        portrait_form.addRow("Portrait vertical (bottom):", self.p_v)
        layout.addLayout(portrait_form)

        # Landscape
        landscape_form = QFormLayout()
        self.l_h = QDoubleSpinBox(); self.l_h.setRange(0.0, 50.0); self.l_h.setSuffix(" mm"); self.l_h.setDecimals(1)
        self.l_v = QDoubleSpinBox(); self.l_v.setRange(0.0, 50.0); self.l_v.setSuffix(" mm"); self.l_v.setDecimals(1)
        lh, lv = self.config.get_print_calibration("landscape")
        self.l_h.setValue(lh); self.l_v.setValue(lv)
        landscape_form.addRow("Landscape horizontal (right):", self.l_h)
        landscape_form.addRow("Landscape vertical (bottom):", self.l_v)
        layout.addLayout(landscape_form)

        # Buttons
        btns = QHBoxLayout()
        print_btn = QPushButton("Print Test Page...")
        save_btn = QPushButton("Save")
        close_btn = QPushButton("Close")
        btns.addWidget(print_btn)
        btns.addStretch()
        btns.addWidget(save_btn)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

        def on_print():
            # Save temp values and invoke main window print debug page
            self._apply_to_config()
            try:
                self.parent().print_tiles()
            except Exception:
                pass

        def on_save():
            self._apply_to_config()

        print_btn.clicked.connect(on_print)
        save_btn.clicked.connect(on_save)
        close_btn.clicked.connect(self.accept)

    def _apply_to_config(self):
        self.config.set_print_calibration("portrait", self.p_h.value(), self.p_v.value())
        self.config.set_print_calibration("landscape", self.l_h.value(), self.l_v.value())

