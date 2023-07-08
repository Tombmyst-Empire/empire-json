@echo off
echo "Formatting using black"
black -t py310 .
echo "Formating using isort"
isort src
echo "################################### PYLINT ########################"
pylint src
echo "################################### PYTEST ########################"
pytest
cd docs
make html
cd..