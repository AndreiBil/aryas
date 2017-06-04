FROM python:3.6

LABEL maintainer "nat@karmios.com"

ADD ./requirements.txt ./
RUN pip3 install -r requirements.txt
RUN rm ./requirements.txt

WORKDIR ~/

VOLUME ./.aryas/

ADD ./run.py ./
ADD ./src ./src

CMD python3 ./aryas.py
