from shutil import move, rmtree
from typing import Literal
from zipfile import ZipFile
from pathlib import Path
import requests


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

def download_chromedriver(platform_arch: str, zip_file_path: Path) -> None:
    """Downloads the ChromeDriver for the specified platform architecture.

    Args:
        download_url (str): The URL of the ChromeDriver ZIP file.
        platform_arch (str): The platform architecture to download.
    """
    
    download_url = f"https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/{platform_arch}/chromedriver-{platform_arch}.zip"

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
    
def move_chromedriver():
    """Move the extracted chromedriver.exe to the program's intent directory.
    If the chromedriver.exe is not found, it will be downloaded.

    Args:
        output_dir (Path): The output directory to move the chromedriver.exe to.
        platform_arch (str): The platform architecture to move the chromedriver.exe for.
    """

    extracted_dir = output_dir / platform_arch
    zip_file_path = output_dir / f"chromedriver-{platform_arch}.zip"

    # If chromedriver zip does not exist
    if not zip_file_path.exists():
        download_chromedriver(platform_arch, zip_file_path)

    # Extract the ZIP file
    with ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extracted_dir)
        print(f"Extracted to {extracted_dir}")

    # Find the extracted chromedriver.exe
    chromedriver_path = extracted_dir / "chromedriver.exe"
    for path in extracted_dir.rglob("chromedriver.exe"):
        chromedriver_path = path
        break

    # Move chromedriver.exe to the output directory
    if chromedriver_path.exists():
        move(str(chromedriver_path), str(output_dir / "chromedriver.exe"))
        print(f"Moved chromedriver.exe to {output_dir}")
        
    # Clean up the extracted directory
    if extracted_dir.exists():
        rmtree(extracted_dir)

    # Clean up ZIP file
    zip_file_path.unlink()

platform_arch = get_platform_architecture()
output_dir = Path(__file__).parent.parent / 'driver'


if "__main__" in __name__:
    move_chromedriver(output_dir, platform_arch)
