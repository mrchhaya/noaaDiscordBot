FROM python:3
ADD noaaBot.py /
ADD numref.json /
ADD secrets.env /
RUN pip install python-dotenv
RUN pip install discord.py
RUN pip install selenium
RUN pip install python-dotenv
RUN apt-get install -y wget unzip
ENV DISPLAY=:99
RUN \
  wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
  echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
  apt-get update && \
  apt-get install -y google-chrome-stable && \
  rm -rf /var/lib/apt/lists/*

ENV CHROMEDRIVER_DIR /chromedriver
RUN mkdir $CHROMEDRIVER_DIR


RUN wget -q --continue -P $CHROMEDRIVER_DIR "https://chromedriver.storage.googleapis.com/87.0.4280.88/chromedriver_linux64.zip"
RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR
ENV PATH $CHROMEDRIVER_DIR:$PATH

CMD [ "python", "./noaaBot.py" ]
