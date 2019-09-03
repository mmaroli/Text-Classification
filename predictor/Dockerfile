FROM ubuntu:16.04
WORKDIR /app
COPY . /app

# Install Python
RUN apt-get update && apt-get install -y software-properties-common git-core make g++
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.6 curl
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.6 get-pip.py
RUN ln -s /usr/bin/python3.6 /usr/bin/python

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir /app/logs
EXPOSE 5000
CMD ["gunicorn", "--access-logfile", "logs/gunicorn-access.log", "--error-logfile", "logs/gunicorn-error.log", "--bind", "0.0.0.0:5000", "wsgi"]
