FROM ubuntu:jammy-20240227

ENV DEBIAN_FRONTEND=noninteractive

# CrÃ©er un utilisateur et un groupe non root

# RUN groupadd -r app && useradd -r -g app appuser

#Download python

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev python3.9 python3-pip python3-setuptools python3-dev

RUN apt-get install sudo -y && apt install curl -y

RUN pip3 install --upgrade pip

RUN apt -y install libpng-dev && apt install -y gnupg2

# Install odbc

RUN sudo su

#RUN mkdir -p /opt/images/ && chown -R appuser:app /opt/images/

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

RUN curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN exit

RUN sudo apt-get update && apt install -y apt-utils

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN sudo apt-get remove -y libodbc2 libodbcinst2 odbcinst unixodbc-common

RUN sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17

# openssl config copy

COPY openssl.cnf /etc/ssl/openssl.cnf

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Env var for pyodbc
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/:$LD_LIBRARY_PATH

COPY . .

# Uninstall sudo, curl et nano
RUN apt-get remove -y curl nano && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 5980

# Put env Vars
ENV MYSQL_HOST="" \
    MYSQL_USER="" \
    MYSQL_PASSWORD="" \
    MYSQL_DATABASE="" \
    LIENAPISMS="" \
    PORT_NUMBER=5980

CMD ["python3", "app.py"]

