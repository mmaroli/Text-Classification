FROM nvidia/cuda:9.1-devel-ubuntu16.04
WORKDIR /app
COPY . /app

ENV CUDNN_VERSION 7.1.2.21

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcudnn7=$CUDNN_VERSION-1+cuda9.1 \
&& \
    apt-mark hold libcudnn7 && \
    rm -rf /var/lib/apt/lists/*



# Install Python
RUN apt-get update && apt-get install -y software-properties-common git-core make g++
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.6 curl
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.6 get-pip.py
RUN ln -s /usr/bin/python3.6 /usr/bin/python

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# Install CMake
RUN curl -L https://github.com/Kitware/CMake/releases/download/v3.15.2/cmake-3.15.2-Linux-x86_64.sh -o /opt/cmake-3.15.2-Linux-x86_64.sh
RUN chmod +x /opt/cmake-3.15.2-Linux-x86_64.sh
