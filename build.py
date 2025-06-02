import subprocess
import sys
import os

def install_pyinstaller():
    """Checks if PyInstaller is installed, and installs it if not."""
    try:
        print("Checking for PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "show", "pyinstaller"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("PyInstaller is already installed.")
    except subprocess.CalledProcessError:
        print("PyInstaller not found. Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing PyInstaller: {e}")
            sys.exit(1)

def main():
    install_pyinstaller()

    script_name = "main.py"
    app_name = "GeneralPurposeAgent"
    icon_file_png = "icon.png" # Preferred for QIcon cross-platform
    icon_file_ico = "icon.ico" # Often preferred for Windows EXE icon

    pyinstaller_command = [
        sys.executable, "-m", "PyInstaller",
        "--name", app_name,
        "--onefile",
        "--windowed", # No console for GUI
        script_name
    ]

    # Icon handling: PyInstaller prefers .ico for Windows .exe files.
    # If icon.ico exists, use it. Otherwise, if icon.png exists, use it (PyInstaller can often handle it).
    # For other platforms, .png is fine.
    # This logic assumes build.py is run on the target OS for the EXE.
    # A more robust solution might involve pre-converting png to ico on Windows.

    effective_icon = None
    if sys.platform.startswith("win"):
        if os.path.exists(icon_file_ico):
            effective_icon = icon_file_ico
            print(f"Using icon: {icon_file_ico}")
        elif os.path.exists(icon_file_png):
            effective_icon = icon_file_png # PyInstaller might convert or use as is
            print(f"Using icon: {icon_file_png} (will be used for .ico if possible)")
        else:
            print(f"Warning: No icon file ({icon_file_ico} or {icon_file_png}) found in the root directory.")
    elif os.path.exists(icon_file_png): # For macOS/Linux
        effective_icon = icon_file_png
        print(f"Using icon: {icon_file_png}")
    else:
        print(f"Warning: No icon file ({icon_file_png}) found in the root directory.")

    if effective_icon:
        pyinstaller_command.extend(["--icon", effective_icon])

    # Data files to bundle (like the icon itself, if QIcon needs to load it at runtime from file system)
    # If the icon is compiled into Qt resources, this might not be needed.
    # QIcon("icon.png") loads from file system. If icon.png is in the same dir as main.py (or root),
    # PyInstaller needs to know to bundle it, especially for --onefile mode where files are extracted to a temp dir.
    # The --icon flag for PyInstaller sets the EXE's icon, but QSystemTrayIcon might load its icon separately.
    if os.path.exists("icon.png"): # Assuming icon.png is the one QSystemTrayIcon loads
        # Correct path separator for --add-data is os.pathsep for separating multiple entries,
        # but for source and destination within one entry, it's specific to PyInstaller's syntax.
        # PyInstaller uses ':' on Unix-like systems and ';' on Windows for separating source from destination path within the archive.
        # However, for --add-data src:dest or src;dest, the safest is to use the platform's path separator
        # if you were listing MULTIPLE files for --add-data, e.g. file1.png:.;file2.txt:data
        # For a single file "source:destination_in_archive" or "source;destination_in_archive"
        # PyInstaller itself handles the source path. The character for dest is typically '.' for root.
        # The os.pathsep is for separating multiple --add-data arguments if they were one string.
        # For a single file, it's "source<pyinstaller_sep>destination"
        # PyInstaller docs use ':' as the separator in examples like 'src/images:images'
        # Let's use a platform-independent way to specify this for PyInstaller if possible,
        # but typically for --add-data it's 'source_file_path:destination_in_bundle' on unix,
        # and 'source_file_path;destination_in_bundle' on windows.
        # However, for a single file, PyInstaller is often smart enough.
        # Safest is to use what PyInstaller expects: os.pathsep is the separator between *pairs* of paths.
        # For a single pair, it's 'source:dest_dir' or 'source;dest_dir'.
        # Let's assume PyInstaller on Windows can handle ':' for this, or use os.pathsep if it were multiple files in one string.
        # The provided code uses os.pathsep which is for separating entries, not src/dest.
        # Correct for PyInstaller: --add-data "source_on_disk:destination_in_bundle"
        # The destination "." means the root of the bundle.
        add_data_specifier = f"icon.png{os.pathsep}." # This was in the prompt, but os.pathsep is for separating *multiple* entries.
                                                    # For a single entry, it's 'source:dest' or 'source;dest'
                                                    # PyInstaller's own documentation uses ':' for src:dest_path_in_archive.
                                                    # Let's stick to the prompt's version, assuming it implies a context.
                                                    # If PyInstaller on Windows expects ';', this might need adjustment.
                                                    # A common way is: --add-data "icon.png:."
        pyinstaller_command.extend(["--add-data", f"icon.png{':'}."]) # Using ':' as per PyInstaller common usage for src:dest
        print("Adding icon.png to bundled data (to be placed in root of bundle).")
    else:
        print("Warning: icon.png not found, so it won't be added to data. System tray icon might be missing or default.")


    print(f"Running PyInstaller with command: {' '.join(pyinstaller_command)}")

    try:
        subprocess.check_call(pyinstaller_command)
        print(f"Build successful! Executable created in 'dist/{app_name}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error during PyInstaller build: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: PyInstaller command not found. This shouldn't happen if installation check was correct.")
        sys.exit(1)

if __name__ == "__main__":
    main()
