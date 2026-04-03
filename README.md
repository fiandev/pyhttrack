# 🕸️ PyHttrack — Mirror Your Favorite Web to Your Computer!

PyHttrack is a lightweight and powerful Python tool that allows you to download entire websites directly to your local computer for offline access, archive, or content analysis. Inspired by the legendary HTTrack, PyHttrack comes with a modern approach, is easily customizable, and can be integrated in various automated workflows.

![Image](https://github.com/user-attachments/assets/4eeb7a42-48b2-4c00-81bd-274abd7bbe75)

### 🔍 Top Features:

- 🌐 Download Full Website - HTML, CSS, JS, images and other media directly to local directory.
- ⚙️ Flexible Configuration - Specify crawl depth, file extensions, domain limits and more.
- 🖥️ Simple CLI Interface - Run and monitor processes with easy-to-understand commands.
- 📁 Organized Directory Structure - Keeps the original structure of the site for an identical offline experience.
- 🧩 Easy to Customize - Suitable for developers, researchers, and digital archivists.

### 🛠️ Use Case:

- Save important site documentation before going offline
- Perform local SEO crawling & analysis
- Learn to build a site from real examples
- Backup personal content or public blogs

## 🚀 Get Started

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/riodevnet/PyHttrack.git
cd PyHttrack
```

#### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

#### 3. Run PyHttrack

```bash
python pyhttrack.py
```

### CLI Options

PyHttrack can also be run with command-line arguments:

```bash
python pyhttrack.py --url "https://example.com"
```

Available options:
- `--url` - Single URL to download (overrides web.json)
- `--help` - Show help message

### Configuration

Edit the `web.json` file and add the url of the website you want to download, for example the following :

```json
["https://example.com/xxx/xxx"]
```

or download many websites

```json
[
  "https://example.com/xxx/xxx",
  "https://example.com/xxx/xxx",
  "https://example.com/xxx/xxx"
]
```

### Start Download

Run the following command to start the download :

```bash
python pyhttrack.py
```

## 🔨 Build from Source

### Using Makefile

```bash
# Install dependencies
make install

# Test locally
make test

# Clean build artifacts
make clean
```

### GitHub Actions (Automated Build)

The repository includes `.github/workflows/build.yml` that automatically builds for all platforms when you push a tag:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

This will trigger builds for:
- **Linux**: x64, x86, arm64, armv7, ppc64le, s390x
- **Windows**: x64, x86, arm64

## 📦 Installation as a System Command (Optional)

You can install PyHttrack as a global command on your system using symlinks:

### Linux / macOS

```bash
# Create a symlink to make pyhttrack available globally
sudo ln -sf "$(pwd)/pyhttrack.py" /usr/local/bin/pyhttrack

# Run from anywhere
pyhttrack
```

### Windows

```cmd
:: Open Command Prompt as Administrator
cd C:\path\to\PyHttrack
mklink C:\Windows\System32\pyhttrack.py pyhttrack.py

:: Run from anywhere
python C:\Windows\System32\pyhttrack.py
```

Or add the PyHttrack directory to your PATH:
```cmd
setx PATH "%PATH%;C:\path\to\PyHttrack"
```

## 📥 Latest Release

[Click here](https://github.com/riodevnet/PyHttrack/releases/latest) to get the latest version of PyHttrack.

## 🤝 Contribution

Contributions are very welcome!. Please feel free to fork this repo, create an issue, or submit a pull request for new features or performance improvements 🚀
