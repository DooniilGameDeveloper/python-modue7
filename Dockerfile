FROM brunneis/python:3.8.3-ubuntu-20.04
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r ./requirements.txt && apt update && apt install iputils-ping -y
CMD mkdir /app
WORKDIR /app
ADD main.py .

