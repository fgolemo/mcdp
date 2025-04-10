# PyMCDP

A Python interpreter and solver for Monotone Co-Design Problems.

[![Build Status](https://travis-ci.org/your-username/mcdp.svg?branch=master)](https://travis-ci.org/your-username/mcdp)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

PyMCDP provides tools for defining, solving, and visualizing co-design problems through a specialized language and mathematical framework. The project includes:

- **MCDPL**: A domain-specific language for expressing co-design problems
- **Solver engine**: For computing solutions to monotone co-design problems
- **Visualization tools**: For representing problems and solutions graphically
- **Web interface**: For interactive development and analysis

Please see the [website](http://co-design.science) and in particular
[the manual](https://co-design.science/media/pymcdp-manual-jul16.html)
for detailed documentation.

## Installation

The code works with Python 3.8+. It has been tested on Ubuntu and macOS.

### Dependencies

Required system packages:
```bash
# Ubuntu
sudo apt-get install python3-dev python3-pip graphviz wkhtmltopdf git

# macOS (with Homebrew)
brew install graphviz wkhtmltopdf git
```

### Option 1: Install using pip

```bash
pip install PyMCDP
```

### Option 2: Installation from source (recommended for development)

```bash
# Clone the repository
git clone https://github.com/AndreaCensi/mcdp.git
cd mcdp

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## Getting Started

### Running the web interface

Start the web server:

```bash
mcdp-web
```

Then open your browser to [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

### Solving co-design problems

Use the solver command line tool:

```bash
mcdp-solve -d <library> <model_name> <functionality>
```

Example:

```bash
mcdp-solve -d src/mcdp_data/libraries/examples/example-battery.mcdplib battery "<1 hour, 0.1 kg, 1 W>"
```

### Visualization of co-design problems

Generate visual representations:

```bash
mcdp-plot -d <library> <model_name>
```

## Development

### Code Quality

This project uses the following tools to maintain code quality:

- **Black**: For code formatting
- **Flake8**: For code linting
- **Pytest**: For testing

Run the formatters and linters:

```bash
# Format code with Black
black .

# Run linter
flake8

# Run tests
pytest
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

## License

PyMCDP is licensed under [LICENSE INFORMATION].

## More Information

For more information, please visit [http://co-design.science](http://co-design.science).