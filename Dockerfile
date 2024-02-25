FROM python:3.11 

# Create a directory in the container 
WORKDIR /usr/src/application 

COPY . /usr/src/application

RUN python3 run_unit_tests.py

CMD ["python3", "app.py"]

