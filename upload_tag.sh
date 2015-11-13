#!/bin/bash
set -e
set -x
python setup.py sdist upload
version=`python -c "import mocdp; print mocdp.__version__"`
git commit -a -m "tagging version ${version}"
git tag "v${version}"
git push --tags