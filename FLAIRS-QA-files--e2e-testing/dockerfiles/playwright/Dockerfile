FROM mcr.microsoft.com/playwright:v1.34.0-jammy

USER root
ENV PATH=$PATH:/root/.local/bin

RUN apt update; apt upgrade -y; DEBIAN_FRONTEND=noninteractive apt install -y postgresql curl
RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python3 get-pip.py
RUN python3 -m pip install -U pip
RUN python3 -m pip install --user pipenv==2023.6.26
