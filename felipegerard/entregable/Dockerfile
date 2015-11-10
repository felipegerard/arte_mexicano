############################################################
# Dockerfile to install ITAM Text Miner (itm) package
# Based on Ubuntu
############################################################

FROM ubuntu
LABEL name="Image to run ITAM Text Miner (itm) package"
LABEL version="0.2"
MAINTAINER Felipe Gerard

# Environment
ENV TERM=xterm-256color

# Install linear algebra, pandoc, python and R

RUN echo "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list && \
	sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9 && \
	apt-get update

RUN apt-get install -y \
	python2.7-dev \
	python-pip

RUN apt-get install -y \
	r-base \
	r-base-dev && \
	R --version

RUN apt-get install -y \
	libblas-dev \
	liblapack-dev \
	gfortran \
	pandoc

# Install itm
ENV VERSION="0.2"
COPY itm/dist/itm-$VERSION.tar.gz /tmp/
RUN pip install /tmp/itm-$VERSION.tar.gz

# Install R libraries and download nltk stopwords
RUN R -e 'install.packages(c("dplyr", "optparse", "networkD3"), repos="http://cran.us.r-project.org")'
RUN python -c "import nltk; nltk.download('stopwords')"

# System structure
#RUN mkdir -p /home/ubuntu
#ENTRYPOINT /bin/bash
#RUN groupadd -r itam && useradd -r -g itam itam
##RUN useradd -m itam && echo "itam:itam" | chpasswd && adduser itam sudo
##RUN echo 'itam  ALL=(ALL:ALL) ALL' >> /etc/sudoers
#USER itam
WORKDIR /home/itam

# Ports
EXPOSE 8082

# Comodidad
RUN echo "alias l='ls -lh'" >> ~/.bashrc
RUN echo "alias ll='ls -lah'" >> ~/.bashrc
