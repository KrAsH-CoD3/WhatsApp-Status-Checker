import platform
import subprocess
import os
import shutil

def get_chrome_version_windows():
    """Get the installed version of Google Chrome on Windows."""
    paths_to_check = [
        r'HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon',
        r'HKEY_LOCAL_MACHINE\Software\Google\Chrome\BLBeacon',
    ]
    for path in paths_to_check:
        try:
            # Query the registry for Chrome's version
            result = subprocess.run(
                ['reg', 'query', path, '/v', 'version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            for line in result.stdout.splitlines():
                if "version" in line.lower():
                    return line.split()[-1]
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Continue to the next path if the current one fails
            continue
    return None  # Return None if no version is found

def get_chrome_version_linux():
    """Get the installed version of Google Chrome on Linux."""
    commands = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
    for cmd in commands:
        if shutil.which(cmd):
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                # Output usually looks like: "Google Chrome 124.0.6367.60"
                return result.stdout.strip().split()[-1]
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
    return None # Return None if Chrome is not found

def get_chrome_version_mac():
    """Get the installed version of Google Chrome on macOS."""
    # Check common application paths
    paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chrome.app/Contents/MacOS/Google Chrome",
        os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    ]
    
    for path in paths:
        if os.path.exists(path):
            try:
                result = subprocess.run(
                    [path, '--version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                return result.stdout.strip().split()[-1] # Extract version number
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
    
    # Fallback to mdfind (Spotlight)
    try:
        app_path = subprocess.check_output(["mdfind", "kMDItemCFBundleIdentifier == 'com.google.Chrome'"], text=True).strip().split('\n')[0]
        if app_path:
            version_path = os.path.join(app_path, "Contents", "Info.plist")
            if os.path.exists(version_path):
                version = subprocess.check_output(["defaults", "read", version_path, "CFBundleShortVersionString"], text=True).strip()
                return version
    except Exception:
        pass
        
    return None # Return None if Chrome is not found

def get_chromebrowser_version():
    """Get the installed version of Google Chrome for the current platform."""
    current_os = platform.system()
    if current_os == "Windows":
        return get_chrome_version_windows()
    elif current_os == "Linux":
        return get_chrome_version_linux()
    elif current_os == "Darwin":  # macOS
        return get_chrome_version_mac()
    else:
        return None  # Unsupported OS

def main():
    chrome_version = get_chromebrowser_version()
    if chrome_version:
        print(f"Detected Chrome version: {chrome_version}")
    else:
        print("Unable to detect Chrome version. Ensure Google Chrome is installed and accessible.")

if __name__ == "__main__":
    main()
