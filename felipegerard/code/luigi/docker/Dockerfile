############################################################
# Dockerfile to install ITAM Text Miner (itm) package
# Based on Ubuntu
############################################################

FROM ubuntu
LABEL name="Image to run ITAM Text Miner (itm) package"
LABEL version="0.1"
MAINTAINER Felipe Gerard

# Environment
ENV TERM=xterm-256color

# Install linear algebra, pandoc, python and R
RUN apt-get update -y
#RUN apt-get upgrade -y
RUN sudo apt-get install -y \
	python2.7-dev \
	python-pip
#	libblas-dev \
#	liblapack-dev \
#	gfortran \
#	pandoc \
#	python-numpy \
#	python-scipy \
#	r-base \
#	r-base-dev

# Install R libraries
#RUN R -e 'install.packages(c("dplyr", "optparse", "networkD3"), repos="http://cran.us.r-project.org")'

# Install itm
ENV PACK=itm-0.1
COPY ${PACK}.tar.gz /tmp/
RUN echo ${PACK}.tar.gz
RUN tar xzf /tmp/${PACK}.tar.gz
#RUN python /tmp/${PACK}/setup.py install

# System structure
#RUN mkdir -p /home/ubuntu
#ENTRYPOINT /bin/bash
#RUN groupadd -r itam && useradd -r -g itam itam
RUN groupadd -r itam
#RUN useradd -m itam && echo "itam:itam" | chpasswd && adduser itam sudo
RUN adduser itam sudo
USER itam
WORKDIR /home/itam

# Ports
EXPOSE 8082

# Comodidad
RUN alias l='ls -lh'
RUN alias ll='ls -lah'
