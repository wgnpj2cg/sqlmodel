FROM ubuntu
ADD src/ /workarea
WORKDIR /workarea

RUN apt-get update --fix-missing \
    && apt-get -y install wget \
    && mkdir \workarea \
    && apt install -y python3 python3-pip
RUN pip3 install -r requirements.txt \
    && chmod 777 /workarea/start.sh \
    && chmod +x /workarea/start.sh

CMD /workarea/start.sh
