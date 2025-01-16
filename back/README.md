# Backend repository of Switcher software

## Run the proyect
For this we use a venv virtual environment which is self-configured using a Makefile target.
Before we start we must have venv installed on our computer and python 3.x.

If you don't have venv installed you can install it by running:
```apt install python3-venv```

After that we have to load the virtual environment in which our project will run:
**```make .venv```**

Now we can run the code locally with the makefile target:
**```make run```**

## Other functions
We added some more functionality in the makefile:
- **```make clean```**: delete all the pycache 
- **```make clean_db```**: delete all .sqlite files
- **```make test```**: Runs all tests
- **```make coverage```**: Shows the test coverage percentage