from typing import Literal, Optional
from shutil import move, rmtree
from zipfile import ZipFile
from pathlib import Path
import requests

BASE_DIR = Path(__file__).parent.parent

class NotSameVersionException(Exception):...


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


def _get_chromedriver_link(platform: str) -> str:
    """
    Fetches the ChromeDriver download link from the 'Stable' section for a given platform.

    Args:
        platform (str): The platform (e.g., "linux64", "mac-arm64", "win64").

    Returns:
        str: The download link for the specified ChromeDriver.
    """
    from bs4 import BeautifulSoup
    from .get_chrome_version import get_chromebrowser_version

    url = "https://googlechromelabs.github.io/chrome-for-testing/"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the webpage. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    stable_section = soup.find('section', {'id': 'stable'})
    if not stable_section:
        raise Exception("Could not find the 'Stable' section on the webpage.")
    
    chromedriver_full_version = stable_section.find('p').text.strip().split(" ")[1]
    chromedriver_version = int(chromedriver_full_version.split('.')[0])
    
    chrome_version_full_version = get_chromebrowser_version()
    chrome_version: int = int(chrome_version_full_version.split('.')[0])

    if (chrome_version < chromedriver_version):
        raise NotSameVersionException(f"""
Chromedriver version {chromedriver_full_version} is not compatible with Chrome version {chrome_version_full_version}.
Update your Chrome browser to the latest version."""
        )
    
    return f"https://storage.googleapis.com/chrome-for-testing-public/{chromedriver_full_version}/{platform}/chromedriver-{platform}.zip"


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
    
    print(f"Downloading Chrome Driver {chrome_driver_version} for {platform_arch}...")
    
    # Download the chromedriver zip file
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        with open(zip_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Downloaded to {zip_file_path}")
    else:
        print(f"Failed to download. Status code: {response.status_code}")


def ensure_chromedriver(output_dir: Optional[Path] = None, platform_arch: Optional[str] = None) -> None:
    """Ensure chromedriver.exe exists in output_dir for the given platform_arch."""
    if output_dir is None:
        output_dir = BASE_DIR / 'driver'
     
    chromedriver_path = output_dir / "chromedriver.exe"
    if chromedriver_path.exists():
        return
    
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
    """Search for chromedriver.exe inside extracted_dir."""
    for path in extracted_dir.rglob("chromedriver.exe"):
        return path
    return None


def _move_chromedriver(src: Path, dest: Path) -> None:
    """Move chromedriver.exe to destination directory."""
    move(str(src), str(dest))


def _cleanup(extracted_dir: Path, zip_file: Path) -> None:
    """Remove extracted directory and zip file."""
    if extracted_dir.exists():
        rmtree(extracted_dir)
    if zip_file.exists():
        zip_file.unlink()


if "__main__" in __name__:
    ensure_chromedriver()
