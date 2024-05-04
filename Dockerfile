FROM brunneis/python:3.8.3-ubuntu-20.04
RUN pip install --upgrade pip
ENV HOST=192.168.140.129
RUN mkdir /app
ADD requirements.txt /app
ADD main.py /app
RUN pip install -r /app/requirements.txt
