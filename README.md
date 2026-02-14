# Construction Image Editor (수질관리시스템 기록 사진 자동화)

A Python-based desktop application for managing and annotating construction site photos. Built with PySide6 and Pillow, this tool allows you to easily view images, add project metadata, and merge data tables directly onto your photos for documentation.

## Windows Installer (설치 프로그램)

Windows용 최신 설치 프로그램을 아래 링크에서 다운로드할 수 있습니다:

[📥 Windows용 설치 프로그램 다운로드](https://github.com/nemo8202/water_quality_management_photo_logger/releases/latest)

![Demo Animation](demo.gif)

## Features

- **Drag & Drop Interface**: Easily load images by dragging them into the application window.
- **Thumbnail Viewer**: Quickly navigate through loaded images via the sidebar.
- **Interactive Image Viewer**: Zoom and pan to inspect photo details.
- **Metadata Editing**: Input project details including:
  - **Project Name** (공사명)
  - **Location** (위치)
  - **Date** (날짜)
  - **Type of Work** (공종)
  - **Content** (내용)
- **Table Merging**: Automatically overlay the metadata table onto the bottom of the image.
  - **High Quality Text**: Uses direct text drawing (PIL) for sharp text at any resolution.
  - **Font Support**: Automatically uses "Malgun Gothic" for Korean text support.
- **Export**: Save the annotated image with an automatically generated filename.
- **Custom UI**:
  - **Main Toolbar**: Quick access to "About" dialog.
  - **About Dialog**: Custom dialog with background image support (`favicon.png`).

## Prerequisites

- Python 3.x
- `PySide6`
- `Pillow` (PIL)

## Installation

1. Clone or download this repository.
2. Install the required dependencies:

```bash
pip install PySide6 Pillow
```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```
2. **Load Images**: Drag and drop image files (`.jpg`, `.png`, etc.) into the window.
3. **Select Image**: Click a thumbnail in the left sidebar to view it.
4. **Edit Data**: Fill in the table on the right with project details.
5. **Merge**: Click the **Done** button to merge the table onto the image.
6. **Save**: Click **Export** to save the final image.

## Building Executable (Nuitka)

To compile the application into a standalone `.exe` file:

1. Ensure you have C++ compiler installed (see [COMPILATION_GUIDE.md](COMPILATION_GUIDE.md)).
2. Install Nuitka:
   ```bash
   pip install nuitka zstandard
   ```
3. Run the build script:
   ```powershell
   .\build_exe.ps1
   ```
   This will generate `ConstructionPhotoLogger.exe` in the `dist` folder, including the icon.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- **Version**: 1.0.0
- **Author**: Saladin from DCriders
