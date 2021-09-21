FROM python:3.8

WORKDIR /src
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY requirements.txt /src
RUN pip install -r requirements.txt
COPY . /src
