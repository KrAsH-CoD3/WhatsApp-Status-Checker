import os
import requests
import subprocess
from pathlib import Path
from shutil import move, rmtree
from typing import Literal, Optional
from zipfile import ZipFile

BASE_DIR = Path(__file__).parent.parent
IS_WINDOWS = os.name == 'nt'
CHROMEDRIVER_NAME = "chromedriver.exe" if IS_WINDOWS else "chromedriver"

class NotSameVersionException(Exception):
    """Exception raised when the installed Chrome version is not compatible with the available ChromeDriver."""
    pass


def _get_platform_architecture() ->  Literal['linux64', 'mac-arm64', 'mac-x64', 'win32', 'win64']:
    """Returns the platform architecture for the current system.

    Returns:
        str: The platform architecture for the current system.
    """

    import platform
    
    system = platform.system().lower()
    arch, _ = platform.architecture()
    
    if system == "windows":
        if arch == "64bit":
            return "win64"
        else:
            return "win32"
    elif system == "darwin":
        # Check if it's an ARM Mac (M1/M2)
        if "arm" in platform.machine().lower():
            return "mac-arm64"
        else:
            return "mac-x64"
    elif system == "linux":
        return "linux64"
    else:
        raise ValueError("Unsupported platform")


def _get_chromedriver_link(platform_arch: str) -> str:
    """
    Fetches the ChromeDriver download link matching the installed Chrome version.

    Args:
        platform_arch (str): The platform (e.g., "linux64", "mac-arm64", "win64").

    Returns:
        str: The download link for the matching ChromeDriver.
    """
    from .get_chrome_version import get_chromebrowser_version

    chrome_version_full = get_chromebrowser_version()
    if not chrome_version_full:
        raise Exception("Unable to detect installed Chrome version.")
    
    milestone = chrome_version_full.split('.')[0]
    
    api_url = "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Chrome for Testing API. Status code: {response.status_code}")
    
    data = response.json()
    milestone_data = data.get("milestones", {}).get(milestone)
    
    if not milestone_data:
        raise Exception(f"No ChromeDriver found for Chrome milestone {milestone}")
    
    downloads = milestone_data.get("downloads", {}).get("chromedriver", [])
    for download in downloads:
        if download.get("platform") == platform_arch:
            return download.get("url")
            
    raise Exception(f"No ChromeDriver download found for platform {platform_arch} in milestone {milestone}")


def download_chromedriver(platform_arch: str, zip_file_path: Path) -> None:
    """Downloads the ChromeDriver for the specified platform architecture.

    Args:
        download_url (str): The URL of the ChromeDriver ZIP file.
        platform_arch (str): The platform architecture to download.
    """
    
    download_url = _get_chromedriver_link(platform_arch)

    output_dir = BASE_DIR / 'driver'
    output_dir.mkdir(exist_ok=True)
    chrome_driver_version = download_url.split("/")[-2]
    
    print(f"Downloading Chrome Driver {chrome_driver_version}...")
    
    # Download the chromedriver zip file
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        with open(zip_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Downloaded to {zip_file_path}")
    else:
        print(f"Failed to download. Status code: {response.status_code}")


def _get_chromedriver_version(chromedriver_path: Path) -> Optional[int]:
    """Return the major version of an existing chromedriver, or None if unavailable."""
    try:
        result = subprocess.run(
            [str(chromedriver_path), '--version'],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=True
        )
        # Expected output: 'ChromeDriver 126.0.6478.127 (....)'
        version_str = result.stdout.strip().split()[1]
        return int(version_str.split('.')[0])
        
    except Exception as e:
        print("Unable to get chromedriver version")
        print(e)
        return None


def ensure_chromedriver(output_dir: Optional[Path] = None, platform_arch: Optional[str] = None) -> None:
    """Ensure chromedriver exists and matches installed Chrome version."""
    from .get_chrome_version import get_chromebrowser_version
    
    if output_dir is None:
        output_dir = BASE_DIR / 'driver'
    
    chromedriver_path = output_dir / CHROMEDRIVER_NAME
    # Determine installed Chrome major version
    chrome_version_full = get_chromebrowser_version()
    if not chrome_version_full:
        raise Exception("Unable to detect installed Chrome version.")
    chrome_major = int(chrome_version_full.split('.')[0])

    # If a driver exists, verify compatibility
    if chromedriver_path.exists():
        if not IS_WINDOWS:
            os.chmod(chromedriver_path, 0o755)
        driver_major = _get_chromedriver_version(chromedriver_path)
        if driver_major is not None and (chrome_major - 1 <= driver_major <= chrome_major + 1):
            return  # Existing driver is compatible
        # Incompatible driver; remove it to allow fresh download
        chromedriver_path.unlink()

    if platform_arch is None:
        platform_arch = _get_platform_architecture()
    
    zip_file_path = _get_or_download_zip(output_dir, platform_arch)
    extracted_dir = _extract_zip(zip_file_path, output_dir / platform_arch)
    driver_path = _find_chromedriver(extracted_dir)

    if driver_path:
        _move_chromedriver(driver_path, chromedriver_path)

    _cleanup(extracted_dir, zip_file_path)


def _get_or_download_zip(output_dir: Path, platform_arch: str) -> Path:
    """Return path to chromedriver zip, downloading if needed."""
    zip_path = output_dir / f"chromedriver-{platform_arch}.zip"
    if not zip_path.exists():
        download_chromedriver(platform_arch, zip_path)
    return zip_path


def _extract_zip(zip_file: Path, target_dir: Path) -> Path:
    """Extract a zip archive into target_dir and return the directory path."""
    with ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(target_dir)
    return target_dir


def _find_chromedriver(extracted_dir: Path) -> Path | None:
    """Search for chromedriver executable inside extracted_dir."""
    for path in extracted_dir.rglob(CHROMEDRIVER_NAME):
        return path
    return None


def _move_chromedriver(src: Path, dest: Path) -> None:
    """Move chromedriver to destination directory and set permissions."""
    move(str(src), str(dest))
    if not IS_WINDOWS:
        os.chmod(dest, 0o755)


def _cleanup(extracted_dir: Path, zip_file: Path) -> None:
    """Safely remove temporary files after driver installation."""
    # Only remove temporary files, never the final driver
    if extracted_dir.exists():
        rmtree(extracted_dir)
    if zip_file.exists():
        zip_file.unlink()


if "__main__" in __name__:
    ensure_chromedriver()
