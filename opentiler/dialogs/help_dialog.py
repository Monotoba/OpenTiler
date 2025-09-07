"""
Help dialog that displays Markdown and HTML files from the opentiler/help folder.

This dialog uses a simple sidebar to list available help topics (Markdown or HTML)
and a viewer that renders Markdown via Qt's Markdown support and HTML via QTextBrowser.
Embedded images and relative links resolve using the help directory as the base URL.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional
import tempfile

from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QTextBrowser,
    QSplitter,
    QLineEdit,
    QLabel,
    QWidget,
    QToolBar,
)


def _find_help_dir(start_dir: Optional[Path] = None, max_depth: int = 6) -> Optional[Path]:
    """Find the help directory under the package tree.

    Walk up from the given start directory (or this file's parent) up to max_depth
    levels to locate an "opentiler/help" directory. Returns the absolute Path or None.
    """
    cur = Path(start_dir or Path(__file__).resolve().parent)
    root = cur.anchor
    depth = 0
    while True:
        candidate = cur / ".." / "help"
        candidate = candidate.resolve()
        if candidate.is_dir() and candidate.name == "help":
            return candidate
        if cur.as_posix() == root or depth >= max_depth:
            break
        cur = cur.parent
        depth += 1
    # As a last resort, if running from repo root, use ./opentiler/help
    repo_candidate = Path.cwd() / "opentiler" / "help"
    if repo_candidate.is_dir():
        return repo_candidate
    return None


class HelpDialog(QDialog):
    """A simple help viewer dialog supporting Markdown and HTML topics."""

    def __init__(self, parent=None, start_topic: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle("OpenTiler Help")
        self.resize(1000, 700)

        # Resolve help directory
        self.help_dir: Optional[Path] = _find_help_dir()

        # UI
        outer = QVBoxLayout(self)
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        outer.addWidget(toolbar)

        # Search bar
        search_box = QLineEdit()
        search_box.setPlaceholderText("Filter topics…")
        search_box.setClearButtonEnabled(True)
        toolbar.addWidget(QLabel(" Topics: "))
        toolbar.addWidget(search_box)

        # Split view: topics list on the left, content on the right
        splitter = QSplitter(Qt.Horizontal)
        outer.addWidget(splitter, 1)

        # Sidebar topics (recursive tree)
        self.topics_tree = QTreeWidget()
        self.topics_tree.setHeaderHidden(True)
        splitter.addWidget(self.topics_tree)

        # Content viewer
        self.viewer = QTextBrowser()
        self.viewer.setOpenExternalLinks(False)
        self.viewer.setOpenLinks(False)
        self.viewer.anchorClicked.connect(self._on_anchor_clicked)
        splitter.addWidget(self.viewer)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        # Actions
        back_action = QAction("Back", self)
        back_action.setShortcut("Alt+Left")
        back_action.triggered.connect(self.viewer.backward)
        toolbar.addAction(back_action)

        fwd_action = QAction("Forward", self)
        fwd_action.setShortcut("Alt+Right")
        fwd_action.triggered.connect(self.viewer.forward)
        toolbar.addAction(fwd_action)

        home_action = QAction("Home", self)
        home_action.setShortcut("Alt+Home")
        home_action.triggered.connect(self._open_default_topic)
        toolbar.addAction(home_action)

        open_ext_action = QAction("Open in Browser", self)
        open_ext_action.setToolTip("Open current topic in your default browser")
        open_ext_action.triggered.connect(self._open_current_in_browser)
        toolbar.addAction(open_ext_action)

        # Populate topics
        self._populate_topics_tree()

        # Filtering
        search_box.textChanged.connect(self._filter_topics)

        # Open initial topic
        # Track temp HTML files for external views
        self._temp_paths: List[str] = []

        if start_topic:
            self.open_topic(start_topic)
        else:
            self._open_default_topic()

    # --- Topic management -------------------------------------------------
    def _populate_topics_tree(self):
        self.topics_tree.clear()
        if not self.help_dir:
            # Show a basic message if help dir not available
            placeholder = QTreeWidgetItem(["No help directory found. Create opentiler/help/ …"]) 
            placeholder.setDisabled(True)
            self.topics_tree.addTopLevelItem(placeholder)
            self.viewer.setHtml(
                "<h2>OpenTiler Help</h2>"
                "<p>No help content found. Place .md or .html files under <code>opentiler/help/</code>."  # noqa: E501
                " Images referenced with relative paths will load from that folder.</p>"
            )
            return

        # Build recursive tree: direct files at root, subdirectories as nodes
        # Add top-level files
        for p in sorted(self.help_dir.iterdir(), key=lambda x: x.name.lower()):
            if p.is_file() and p.suffix.lower() in (".md", ".markdown", ".html", ".htm"):
                leaf = QTreeWidgetItem([p.name])
                leaf.setData(0, Qt.UserRole, str(p))
                self.topics_tree.addTopLevelItem(leaf)

        # Add directories recursively
        def add_dir(parent: QTreeWidgetItem, directory: Path):
            # Add files in this directory
            for f in sorted([x for x in directory.iterdir() if x.is_file() and x.suffix.lower() in (".md", ".markdown", ".html", ".htm")], key=lambda x: x.name.lower()):
                leaf = QTreeWidgetItem([f.name])
                leaf.setData(0, Qt.UserRole, str(f))
                parent.addChild(leaf)
            # Recurse into subdirectories
            for d in sorted([x for x in directory.iterdir() if x.is_dir()], key=lambda x: x.name.lower()):
                node = QTreeWidgetItem([d.name])
                parent.addChild(node)
                add_dir(node, d)

        for d in sorted([x for x in self.help_dir.iterdir() if x.is_dir()], key=lambda x: x.name.lower()):
            node = QTreeWidgetItem([d.name])
            self.topics_tree.addTopLevelItem(node)
            add_dir(node, d)

        self.topics_tree.currentItemChanged.connect(self._on_topic_selected)

    def _filter_topics(self, text: str):
        t = text.lower().strip()
        def filter_item(item: QTreeWidgetItem) -> bool:
            # Returns True if item or any child matches
            child_match = False
            for i in range(item.childCount()):
                if filter_item(item.child(i)):
                    child_match = True
            is_match = (t == "") or (t in item.text(0).lower())
            visible = is_match or child_match
            item.setHidden(not visible)
            return visible

        for i in range(self.topics_tree.topLevelItemCount()):
            filter_item(self.topics_tree.topLevelItem(i))

    def _on_topic_selected(self, current: Optional[QTreeWidgetItem]):
        if not current:
            return
        path = current.data(0, Qt.UserRole)
        if path:
            self._load_path(Path(path))

    def _open_default_topic(self):
        # Prefer index.md, then README.md, then first topic
        if not self.help_dir:
            return
        candidates = [
            self.help_dir / "index.md",
            self.help_dir / "README.md",
        ]
        for c in candidates:
            if c.exists():
                self._load_path(c)
                # also select it in the list if present
                self._select_list_item(c)
                return
        # Fallback: first entry in the list
        if self.topics_tree.topLevelItemCount() > 0:
            self.topics_tree.setCurrentItem(self.topics_tree.topLevelItem(0))
            self._on_topic_selected(self.topics_tree.currentItem())

    def open_topic(self, topic_name_or_path: str):
        """Open a topic by base name (e.g., 'calibration.md') or full path."""
        if not topic_name_or_path:
            self._open_default_topic()
            return
        p = Path(topic_name_or_path)
        if not p.is_absolute():
            if self.help_dir:
                p = (self.help_dir / topic_name_or_path).resolve()
        if p.exists():
            self._load_path(p)
            self._select_list_item(p)

    def _select_list_item(self, path: Path):
        base = path.name
        def walk(item: QTreeWidgetItem):
            if item.text(0) == base and (item.data(0, Qt.UserRole) is not None):
                return item
            for i in range(item.childCount()):
                res = walk(item.child(i))
                if res is not None:
                    return res
            return None
        for i in range(self.topics_tree.topLevelItemCount()):
            res = walk(self.topics_tree.topLevelItem(i))
            if res is not None:
                self.topics_tree.setCurrentItem(res)
                return

    # --- Rendering --------------------------------------------------------
    def _load_path(self, path: Path):
        suffix = path.suffix.lower()
        self._current_path = path
        # Ensure base URL is the help directory so relative images/links resolve
        if self.help_dir:
            self.viewer.document().setBaseUrl(QUrl.fromLocalFile(str(self.help_dir) + os.sep))

        try:
            if suffix in (".md", ".markdown"):
                text = path.read_text(encoding="utf-8")
                # Prefer Python-Markdown with common extensions if available (closer to GFM)
                html_rendered = None
                try:
                    import markdown  # type: ignore
                    exts = [
                        'extra',            # tables, fenced code, etc.
                        'admonition',
                        'sane_lists',
                        'toc',
                        'codehilite',
                    ]
                    # Optional: GitHub task lists if extension is present
                    try:
                        import pymdownx.tasklist  # noqa: F401
                        exts.append('pymdownx.tasklist')
                    except Exception:
                        pass
                    html_rendered = markdown.markdown(text, extensions=exts, output_format='html5')
                except Exception:
                    html_rendered = None

                if html_rendered is not None:
                    self.viewer.setHtml(html_rendered)
                else:
                    # Fallback to Qt Markdown (CommonMark subset)
                    self.viewer.setMarkdown(text)
            elif suffix in (".html", ".htm"):
                html = path.read_text(encoding="utf-8")
                # Use setHtml with baseUrl by setting document base above
                self.viewer.setHtml(html)
            else:
                # Fallback: try to navigate directly
                self.viewer.setSource(QUrl.fromLocalFile(str(path)))
        except Exception as e:
            self.viewer.setHtml(
                f"<h3>Failed to open help topic</h3><p>{path}</p><pre>{e!s}</pre>"
            )

    def _on_anchor_clicked(self, url: QUrl):
        # Handle relative links inside help content
        if url.isRelative():
            if self.help_dir:
                target = (self.help_dir / url.toString()).resolve()
                if target.exists():
                    self._load_path(target)
            return
        if url.isLocalFile():
            target = Path(url.toLocalFile())
            if target.exists():
                self._load_path(target)
                return
        # For any other scheme, let QTextBrowser try
        self.viewer.setSource(url)

    def _open_current_in_browser(self):
        path = getattr(self, "_current_path", None)
        if not path:
            return
        suffix = Path(path).suffix.lower()
        # Directly open HTML files
        if suffix in (".html", ".htm"):
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
            return
        # For Markdown, render to a temp HTML with base href so relative resources resolve
        if suffix in (".md", ".markdown"):
            try:
                text = Path(path).read_text(encoding="utf-8")
                html_rendered = None
                try:
                    import markdown  # type: ignore
                    exts = ['extra', 'admonition', 'sane_lists', 'toc', 'codehilite']
                    try:
                        import pymdownx.tasklist  # noqa: F401
                        exts.append('pymdownx.tasklist')
                    except Exception:
                        pass
                    html_rendered = markdown.markdown(text, extensions=exts, output_format='html5')
                except Exception:
                    html_rendered = None

                if html_rendered is None:
                    # Fallback: open the raw markdown file
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
                    return

                base_href = ''
                if self.help_dir:
                    base_href = QUrl.fromLocalFile(str(self.help_dir) + os.sep).toString()
                html_doc = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\">
  <base href=\"{base_href}\">
  <title>{Path(path).name}</title>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; }}
    pre code {{ white-space: pre-wrap; }}
    code {{ background: #f6f8fa; padding: 0.15rem 0.3rem; }}
    table {{ border-collapse: collapse; }}
    th, td {{ border: 1px solid #ddd; padding: 4px 8px; }}
  </style>
  </head>
<body>
{html_rendered}
</body>
</html>"""
                fd, tmp_path = tempfile.mkstemp(suffix=".html", prefix="opentiler-help-")
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(html_doc)
                self._temp_paths.append(tmp_path)
                QDesktopServices.openUrl(QUrl.fromLocalFile(tmp_path))
            except Exception:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def closeEvent(self, event):
        # Cleanup any temp files we created
        try:
            for p in getattr(self, "_temp_paths", []) or []:
                try:
                    os.remove(p)
                except Exception:
                    pass
        finally:
            super().closeEvent(event)
