FROM python:3.6

LABEL maintainer "nat@karmios.com"

WORKDIR /root/


ADD ./aryas ./aryas
ADD ./bin ./bin
ADD ./README.md ./
ADD ./requirements.txt ./
ADD ./setup.py ./

RUN python3 setup.py install

RUN rm ./*


VOLUME ./.aryas/

CMD python3 aryas
