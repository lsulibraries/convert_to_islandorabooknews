# docker build -t ubuntu-14.04-python3.6 .

FROM ubuntu:14.04

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        wget \
        xz-utils \
        build-essential \
        libsqlite3-dev \
        libreadline-dev \
        libssl-dev \
        openssl \
        unzip \
        zip \
        software-properties-common \
        libopenjpeg2* \
        imagemagick \
        pdftk \
        libpoppler-cpp-dev \
        pkg-config \
        cython3 \
        libtiff4-dev \
        libjpeg8-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        tcl8.5-dev \
        tk8.5-dev \
        python-tk \
        python-dev \
        libxml2-dev \
        libxslt-dev \
        lib32z1-dev \
        tesseract-ocr \
        poppler-utils

WORKDIR /tmp

# removing a security feature that prevent pdf creation
RUN mv /etc/ImageMagick/policy.xml /etc/ImageMagick/policy.xmlold

RUN wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tar.xz \
    && tar -xf Python-3.6.9.tar.xz \
    && cd /tmp/Python-3.6.9 \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/Python-3.6.9.tar.xz /tmp/Python-3.6.9

RUN pip3 install -U pip \
    && pip3 install -U pdftotext jpylyzer Pillow lxml


RUN wget http://kakadusoftware.com/wp-content/uploads/2014/06/KDU7A2_Demo_Apps_for_Centos7-x86-64_170827.zip \
    && unzip KDU7A2_Demo_Apps_for_Centos7-x86-64_170827.zip \
    && rm KDU7A2_Demo_Apps_for_Centos7-x86-64_170827.zip \
    && mv KDU7A2_Demo_Apps_for_Centos7-x86-64_170827/libkdu_v7AR.so /usr/local/lib/ \
    && mv KDU7A2_Demo_Apps_for_Centos7-x86-64_170827/* /usr/local/bin/ \
    && rm -R KDU7A2_Demo_Apps_for_Centos7-x86-64_170827/
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib


WORKDIR /required_libraries

COPY ./required_libraries/jdk-7u80-linux-x64.tar.gz /required_libraries
COPY ./required_libraries/fits-0.8.5.zip /required_libraries
RUN unzip -u fits-0.8.5.zip && chmod +x /required_libraries/fits-0.8.5/fits.sh
RUN tar -xvf jdk-7u80-linux-x64.tar.gz \
  && mkdir -p /usr/lib/jvm \
  && mv ./jdk1.7.0_80 /usr/lib/jvm/ \
  && update-alternatives --install "/usr/bin/java" "java" "/usr/lib/jvm/jdk1.7.0_80/bin/java" 1 \
  && update-alternatives --install "/usr/bin/javac" "javac" "/usr/lib/jvm/jdk1.7.0_80/bin/javac" 1 \
    && update-alternatives --install "/usr/bin/javaws" "javaws" "/usr/lib/jvm/jdk1.7.0_80/bin/javaws" 1 \
    && chmod a+x /usr/bin/java \
    && chmod a+x /usr/bin/javac \
    && chmod a+x /usr/bin/javaws \
    && chown -R root:root /usr/lib/jvm/jdk1.7.0_80
