# Rekhta Navees (ریختہ نویس)

## Introduction
Rekhta Navees is an effort to _kill two birds with one stone_,

1. Collect **voice clips**/**transcribed text** pairs for dataset creation for training an STT AI model,
2. Creating/Collecting **Urdu** language text data through transcribed audio to minimize manual text entry.

The application is geared to,
1. record audio, followed by,
2. user supervised audio segmentation,
3. transcription with existing working solutions (currently using _OpenAI Whisper_ STT model) and,
4. aggregation of individual transcriptions to usable text.

Standing on the shoulders of,
* [PySide6](https://pypi.org/project/PySide6/) (Qt6) based UI with Python,
* [librosa](https://pypi.org/project/librosa/)/[Numpy](https://pypi.org/project/numpy/) for audio processing,
* [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for audio transcription,
* [PyMuPDF](https://pypi.org/project/PyMuPDF/) for pdf rendering,
* [PyInstaller](https://pypi.org/project/pyinstaller/) for MS Windows standalone executable creation.

## Installation
### Binary Installer
For MS Windows a binary installation file is available.

Not tested on Linux/macOS.

### From Source
#### Prerequisites
* [Python](https://www.python.org/) 3.9 (Created and tested with 3.9, may work with Python 3 in general),
* [Poetry](https://pypi.org/project/poetry/) python package manager.

#### Getting the source code
The source is hosted on GitHub at [RoXimn/RekhtaNavees](https://github.com/roximn/rekhtanavees),

Get the source code.
```commandline
git clone
``` 

#### Installing dependencies
Activate the virtual environment and install dependencies with `Poetry`,
```commandline
cd rekhtanavees
python -m venv .venv
.venv\Scripts\activate.bat
poetry install
```
 
#### Compiling UI components
The QT user interface and resource files need to be compiled before they can be used by the application,
```commandline
python scripts\compileUI.py
```

#### Running the application
Run the application
```commandline
python rekhtanavees\main.py
```

#### Creating MS Windows standalone executable (optional)
The PyInstaller is run from the root directory of the project, where the specification file resides,
```commandline
pyinstaller rekthanavees.app.spec 
```
producing the executable in the `dist/rektanvees` folder.
