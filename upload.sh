#!/bin/bash
rm -rf ./build/*
rm -rf ./dist/*
python3 setup.py sdist bdist_wheel
twine upload dist/*
echo "Upload done"

git push && git push github
