FROM ubuntu:latest
MAINTAINER k_kanou

RUN apt-get update \
  && apt-get install python3 python3-pip curl git sudo cron -y \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install mecab
WORKDIR /opt
RUN git clone https://github.com/taku910/mecab.git
WORKDIR /opt/mecab/mecab
RUN ./configure  --enable-utf8-only \
  && make \
  && make check \
  && make install \
  && ldconfig

WORKDIR /opt/mecab/mecab-ipadic
RUN ./configure --with-charset=utf8 \
  && make \
  && make install


# Install mecab-ipadic-neologd
WORKDIR /opt
RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
WORKDIR /opt/mecab-ipadic-neologd
RUN ./bin/install-mecab-ipadic-neologd -n -y


# Install build tools
RUN apt-get update && \
    apt-get install -y wget git build-essential unzip

WORKDIR /usr/local/src/


# Install Open JTalk
RUN wget http://downloads.sourceforge.net/hts-engine/hts_engine_API-1.10.tar.gz && \
    tar zxvf hts_engine_API-1.10.tar.gz && \
    cd hts_engine_API-1.10/ && \
    ./configure && \
    make && \
    make install

RUN wget http://downloads.sourceforge.net/open-jtalk/open_jtalk-1.09.tar.gz && \
    tar zxvf open_jtalk-1.09.tar.gz && \
    cd open_jtalk-1.09/ && \
    ./configure --with-hts-engine-header-path=/usr/local/include --with-hts-engine-library-path=/usr/local/lib --with-charset=UTF-8 && \
    make && \
    make install

RUN wget http://downloads.sourceforge.net/open-jtalk/hts_voice_nitech_jp_atr503_m001-1.05.tar.gz && \
    tar zxvf hts_voice_nitech_jp_atr503_m001-1.05.tar.gz && \
    cp -r hts_voice_nitech_jp_atr503_m001-1.05 /usr/local/lib/hts_voice_nitech_jp_atr503_m001-1.05

RUN wget http://downloads.sourceforge.net/open-jtalk/open_jtalk_dic_utf_8-1.09.tar.gz && \
    tar zxvf open_jtalk_dic_utf_8-1.09.tar.gz && \
    cp -r open_jtalk_dic_utf_8-1.09 /usr/local/lib/open_jtalk_dic_utf_8-1.09

RUN wget https://sourceforge.net/projects/mmdagent/files/MMDAgent_Example/MMDAgent_Example-1.7/MMDAgent_Example-1.7.zip/download -O MMDAgent_Example-1.7.zip && \
    unzip MMDAgent_Example-1.7.zip MMDAgent_Example-1.7/Voice/* && \
    cp -r MMDAgent_Example-1.7/Voice/mei/ /usr/local/src


# Install julius
RUN wget https://osdn.net/projects/julius/downloads/66547/julius-4.4.2.tar.gz && \
    tar -xvzf julius-4.4.2.tar.gz && \
    cd julius-4.4.2 && \
    ./configure && \
    make && \
    make install

RUN wget https://osdn.net/projects/julius/downloads/66544/dictation-kit-v4.4.zip && \
    unzip dictation-kit-v4.4.zip

# Install sox
RUN apt-get install -y sox


# Add our code
ADD ./webapp /opt/webapp/
WORKDIR /opt/webapp


# Install dependencies
ADD ./webapp/requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -qr /tmp/requirements.txt


# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku			
CMD gunicorn --bind 0.0.0.0:$PORT wsgi
