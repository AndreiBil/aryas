FROM python:3.6

ARG DISCORD_TOKEN
ARG WEATHER_KEY

ADD ./requirements.txt ./
RUN pip3 install -r requirements.txt
RUN rm ./requirements.txt

RUN cd ~

ADD ./aryas.py ./
ADD ./src ./src

ADD ./setup.py ./

RUN python3 ./setup.py --discord_token=$DISCORD_TOKEN --OpenWeatherMap_api_key=$WEATHER_KEY

RUN rm ./setup.py

CMD python3 ./aryas.py
