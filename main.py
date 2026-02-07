import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                               QScrollArea, QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMessageBox, QSizePolicy, QAbstractScrollArea)
from PySide6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent, QAction, QPainter
from PySide6.QtCore import Qt, QBuffer, QIODevice, QRect, QRectF
from PIL import Image, ImageDraw, ImageFont
import io

class AboutDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("About")
        self.setFixedSize(400, 300)
        
        # Set background image
        # Priority: favicon.png (as requested) -> others
        bg_path = None
        for ext in [".png", ".jpg", ".ico"]:
             path = os.path.join(os.path.dirname(__file__), f"favicon{ext}")
             if os.path.exists(path):
                 bg_path = path.replace("\\", "/")
                 break
        
        if bg_path:
            # Use style sheet for background
            self.setStyleSheet(f"""
                AboutDialog {{
                    background-image: url({bg_path});
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: 100% 100%; 
                }}
            """)
            
            # Semi-transparent overlay
            overlay = QWidget(self)
            overlay.setStyleSheet("background-color: rgba(255, 255, 255, 200); border-radius: 10px;")
            # Center the overlay
            overlay_w = 360
            overlay_h = 260
            overlay.setGeometry((400-overlay_w)//2, (300-overlay_h)//2, overlay_w, overlay_h)
            
            layout = QVBoxLayout(overlay)
        else:
            layout = QVBoxLayout(self)

        # Content
        title = QLabel("Construction Image Editor")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        
        version = QLabel("Version 1.0.0")
        version.setStyleSheet("font-size: 14px; color: #555;")
        version.setAlignment(Qt.AlignCenter)
        
        author = QLabel("made by Saladin from DCriders")
        author.setStyleSheet("font-size: 14px; color: #555; font-style: italic;")
        author.setAlignment(Qt.AlignCenter)

        copyright = QLabel("Copyright 2026. All rights reserved.")
        copyright.setStyleSheet("font-size: 12px; color: #777;")
        copyright.setAlignment(Qt.AlignCenter)
        
        desc = QLabel("A tool for managing and annotating\nconstruction site photos.")
        desc.setStyleSheet("font-size: 13px; color: #444;")
        desc.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(author)
        layout.addWidget(copyright)
        layout.addSpacing(10)
        layout.addWidget(desc)
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._pixmap_item = None
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    def set_image(self, pixmap):
        self._scene.clear()
        self._pixmap_item = self._scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))
        
        # Reset any existing transformations
        self.resetTransform()
        
        # Only scale down if image is larger than the view
        view_rect = self.viewport().rect()
        img_rect = pixmap.rect()
        
        if img_rect.width() > view_rect.width() or img_rect.height() > view_rect.height():
            self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
        else:
            # Center the image in the view
            self.centerOn(self._pixmap_item)

    def get_pixmap(self):
        if self._pixmap_item:
            return self._pixmap_item.pixmap()
        return None

    def wheelEvent(self, event):
        if self._pixmap_item:
            factor = 1.15
            if event.angleDelta().y() > 0:
                self.scale(factor, factor)
            else:
                self.scale(1.0 / factor, 1.0 / factor)

class EnterKeyTableWidget(QTableWidget):
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            current_row = self.currentRow()
            current_col = self.currentColumn()
            if current_row < self.rowCount() - 1:
                # Move to next row, same column
                next_row = current_row + 1
                self.setCurrentCell(next_row, current_col)
                # Optional: start editing the next cell automatically
                self.editItem(self.item(next_row, current_col))
            return
        super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Construction Image Editor")
        
        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(__file__), "favicon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QPixmap(icon_path))
            
        self.setFixedSize(1024, 768)
        self.setAcceptDrops(True)
        
        # Toolbar
        self.toolbar = self.addToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # About Action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        self.toolbar.addAction(about_action)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left Sidebar (Thumbnails)
        self.scroll_area = QScrollArea()
        self.scroll_area.setFixedWidth(150)
        self.scroll_area.setWidgetResizable(True)
        self.thumbnail_container = QWidget()
        self.thumbnail_layout = QVBoxLayout(self.thumbnail_container)
        self.thumbnail_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.thumbnail_container)
        self.main_layout.addWidget(self.scroll_area)

        # Right Area
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.main_layout.addWidget(self.right_widget)

        # Image Viewer
        self.image_viewer = ImageViewer()
        self.right_layout.addWidget(self.image_viewer, stretch=2)

        # Table
        self.table = EnterKeyTableWidget(5, 2)
        self.table.setHorizontalHeaderLabels(["Item", "Value"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setStyleSheet("background-color: white; color: black;")
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.table_items = ["공사명", "위치", "날짜", "공종", "내용"]
        for i, item in enumerate(self.table_items):
            self.table.setItem(i, 0, QTableWidgetItem(item))
            self.table.setItem(i, 1, QTableWidgetItem(""))
            # Make first column read-only
            self.table.item(i, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.right_layout.addWidget(self.table)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.done_btn = QPushButton("Done")
        self.done_btn.clicked.connect(self.merge_table)
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_image)
        self.button_layout.addWidget(self.done_btn)
        self.button_layout.addWidget(self.export_btn)
        self.right_layout.addLayout(self.button_layout)

        self.current_image_path = None
        self.original_pixmap = None
        
        # Load default logo if available
        # Priority: favicon.png -> favicon.jpg -> favicon.ico
        for ext in [".png", ".jpg", ".ico"]:
             logo_path = os.path.join(os.path.dirname(__file__), f"favicon{ext}")
             if os.path.exists(logo_path):
                 self.load_image(logo_path)
                 break
        
    def show_about(self):
        self.about_dialog = AboutDialog(self)
        self.about_dialog.show()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.add_thumbnail(file_path)

    def add_thumbnail(self, path):
        btn = QPushButton()
        pixmap = QPixmap(path)
        icon = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        btn.setIcon(icon)
        btn.setIconSize(icon.size())
        btn.clicked.connect(lambda: self.load_image(path))
        self.thumbnail_layout.addWidget(btn)
        
        # Load the first image dropped if none loaded
        if self.current_image_path is None:
            self.load_image(path)

    def load_image(self, path):
        self.current_image_path = path
        self.original_pixmap = QPixmap(path)
        self.image_viewer.set_image(self.original_pixmap)

    def merge_table(self):
        if self.original_pixmap is None:
            QMessageBox.warning(self, "Error", "No image loaded.")
            return

        # 1. Convert QPixmap to PIL Image
        input_buffer = QBuffer()
        input_buffer.open(QIODevice.ReadWrite)
        self.original_pixmap.save(input_buffer, "PNG")
        pil_image = Image.open(io.BytesIO(input_buffer.data())).convert("RGB") # Ensure RGB mode for drawing

        img_w, img_h = pil_image.size
        
        # 2. Setup Drawing
        draw = ImageDraw.Draw(pil_image)
        
        # Font settings (Dynamic sizing)
        try:
            # Use Malgun Gothic for Korean support on Windows
            font_path = "C:/Windows/Fonts/malgun.ttf"
            if not os.path.exists(font_path):
                 font_path = "arial.ttf" # Fallback
            
            # Font size relative to image width (e.g., 2.5% of width)
            font_size = int(img_w * 0.025)
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
            font_size = 20 # Approximation for default font

        padding = int(font_size * 0.6)
        row_height = font_size + (padding * 2)
        rows = 5
        cols = 2
        table_height = rows * row_height
        
        # Calculate max width for each column
        max_col1_width = 0
        max_col2_width = 0
        
        # Check column 1 (keys)
        for item in self.table_items:
             # Use getbbox for accurate width or getlength
             try:
                 w = font.getlength(item)
             except AttributeError:
                 w = font.getsize(item)[0] # Older pillow fallback
             max_col1_width = max(max_col1_width, w)
             
        # Check column 2 (values)
        for i in range(rows):
            val_text = ""
            if self.table.item(i, 1):
                val_text = self.table.item(i, 1).text()
            try:
                 w = font.getlength(val_text)
            except AttributeError:
                 w = font.getsize(val_text)[0]
            max_col2_width = max(max_col2_width, w)
            
        # Add padding to widths
        col1_width = int(max_col1_width + (padding * 3)) # Left + Right padding + extra
        col2_width = int(max_col2_width + (padding * 3))
        
        # Ensure minimum width to look decent (e.g. 30% of image width total)
        min_total_width = int(img_w * 0.3)
        
        table_width = col1_width + col2_width
        
        # If calculated width is less than minimum, expand col2
        if table_width < min_total_width:
             diff = min_total_width - table_width
             col2_width += diff
             table_width = min_total_width

        # Ensure it doesn't exceed image width
        if table_width > img_w:
             table_width = img_w
             # Recalculate cols proportionally or just clamp?
             # Simple clamp for now, text might clip but better than crash
             col2_width = table_width - col1_width
        
        # Position: Bottom-Right
        # start_x = img_w - table_width - padding
        start_x = img_w - table_width - padding
        start_y = img_h - table_height - padding 
        
        # Ensure it doesn't go off-screen (top/left)
        if start_x < 0: start_x = 0
        if start_y < 0: start_y = 0
        
        # Draw background for table
        # We'll make it semi-transparent white optionally, but solid white is safer for readability
        draw.rectangle([start_x, start_y, start_x + table_width, start_y + table_height], fill="white", outline="black")
        
        # Draw rows and text
        # col1_width is now absolute width of first column
        
        for i in range(rows):
            row_y = start_y + (i * row_height)
            
            # Draw Horizontal Line
            draw.line([(start_x, row_y), (start_x + table_width, row_y)], fill="black", width=2)
            
            # Get data
            key_item = self.table_items[i]
            val_item = ""
            if self.table.item(i, 1):
                val_item = self.table.item(i, 1).text()
                
            # Draw Vertical Line between columns
            draw.line([(start_x + col1_width, row_y), (start_x + col1_width, row_y + row_height)], fill="black", width=2)

            # Text positioning
            text_y = row_y + padding
            
            # Draw Key
            draw.text((start_x + padding, text_y), key_item, font=font, fill="black")
            
            # Draw Value
            draw.text((start_x + col1_width + padding, text_y), val_item, font=font, fill="black")
            
        # Draw bottom border
        draw.line([(start_x, start_y + table_height), (start_x + table_width, start_y + table_height)], fill="black", width=2)
        # Draw right border
        draw.line([(start_x + table_width -1, start_y), (start_x + table_width -1, start_y + table_height)], fill="black", width=2) # -1 to be visible
        # Draw left border
        draw.line([(start_x, start_y), (start_x, start_y + table_height)], fill="black", width=2)

        # 3. Update QPixmap
        output_buffer = io.BytesIO()
        pil_image.save(output_buffer, format="PNG")
        output_data = output_buffer.getvalue()
        
        updated_pixmap = QPixmap()
        updated_pixmap.loadFromData(output_data)
        
        self.image_viewer.set_image(updated_pixmap)
        QMessageBox.information(self, "Success", "Table merged successfully.")

    def export_image(self):
        pixmap = self.image_viewer.get_pixmap()
        if pixmap is None:
            QMessageBox.warning(self, "Error", "No image to export.")
            return

        # Get construct name and date
        name = ""
        date = ""
        for i in range(5):
             key_item = self.table.item(i, 0)
             val_item = self.table.item(i, 1)
             if key_item and val_item:
                 if key_item.text() == "공사명":
                     name = val_item.text()
                 elif key_item.text() == "날짜":
                     date = val_item.text()
        
        if not name or not date:
            QMessageBox.warning(self, "Error", "Please fill '공사명' and '날짜' to export.")
            return

        filename = f"{date}_{name}.jpg"
        # Sanitize filename
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Image", filename, "Images (*.jpg *.png)")
        
        if file_path:
            pixmap.save(file_path)
            QMessageBox.information(self, "Success", f"Saved to {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
