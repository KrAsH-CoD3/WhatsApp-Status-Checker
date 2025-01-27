from typing import Literal
from pathlib import Path
import requests


class NotSameVersionException(Exception):...

def get_platform_architecture() ->  Literal['linux64', 'mac-arm64', 'mac-x64', 'win32', 'win64']:
    """Returns the platform architecture for the current system.

    Returns:
        str: The platform architecture for the current system.
    """

    import platform
    
    system = platform.system().lower()
    arch, _ = platform.architecture()
    
    if system == "linux":
        return "linux64"
    elif system == "darwin":
        # Check if it's an ARM Mac (M1/M2)
        if "arm" in platform.machine().lower():
            return "mac-arm64"
        else:
            return "mac-x64"
    elif system == "windows":
        if arch == "32bit":
            return "win32"
        else:
            return "win64"
    else:
        raise ValueError("Unsupported platform")

def get_chromedriver_link(platform: str) -> str:
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
    
    chromedriver_version = stable_section.find('p').text.strip().split(" ")[1]
    chrome_version = get_chromebrowser_version()

    if chromedriver_version.split(".")[0] != chrome_version.split(".")[0]:
        raise NotSameVersionException(f"""
Chromedriver version {chromedriver_version} is not compatible with Chrome version {chrome_version}.
Update your Chrome browser to the latest version."""
        )
    return f"https://storage.googleapis.com/chrome-for-testing-public/{chromedriver_version}/{platform}/chromedriver-{platform}.zip"

def download_chromedriver(platform_arch: str, zip_file_path: Path) -> None:
    """Downloads the ChromeDriver for the specified platform architecture.

    Args:
        download_url (str): The URL of the ChromeDriver ZIP file.
        platform_arch (str): The platform architecture to download.
    """
    
    download_url = get_chromedriver_link(platform_arch)

    output_dir.mkdir(exist_ok=True)
    
    print(f"Downloading ChromeDriver for {platform_arch} from {download_url}...")
    
    # Download the file
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        with open(zip_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Downloaded to {zip_file_path}")
    else:
        print(f"Failed to download. Status code: {response.status_code}")
    
def move_chromedriver() -> None:
    """Move the extracted chromedriver.exe to the program's intent directory.
    If the chromedriver.exe is not found, it will be downloaded.

    Args:
        output_dir (Path): The output directory to move the chromedriver.exe to.
        platform_arch (str): The platform architecture to move the chromedriver.exe for.
    """

    from shutil import move, rmtree
    from zipfile import ZipFile

    extracted_dir = output_dir / platform_arch
    zip_file_path = output_dir / f"chromedriver-{platform_arch}.zip"
    chromedriver_path = output_dir / f"chromedriver.exe"

    if chromedriver_path.exists(): return # If chromedriver.exe already exists, do nothing

    # If chromedriver zip does not exist
    if not zip_file_path.exists():
        download_chromedriver(platform_arch, zip_file_path)

    # Extract the ZIP file
    with ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extracted_dir)
        print(f"Extracted to {extracted_dir}")

    # Find the extracted chromedriver.exe
    extracted_chromedriver_path = extracted_dir / "chromedriver.exe"
    for path in extracted_dir.rglob("chromedriver.exe"):
        extracted_chromedriver_path = path
        break

    # Move chromedriver.exe to the output directory
    if extracted_chromedriver_path.exists():
        move(str(extracted_chromedriver_path), str(output_dir / "chromedriver.exe"))
        print(f"Moved chromedriver.exe to {output_dir}")
        
    # Clean up the extracted directory
    if extracted_dir.exists():
        rmtree(extracted_dir)

    # Clean up ZIP file
    zip_file_path.unlink()

platform_arch = get_platform_architecture()
output_dir = Path(__file__).parent.parent / 'driver'

if "__main__" in __name__:
    move_chromedriver()
