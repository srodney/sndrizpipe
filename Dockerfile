FROM python:3.8

RUN pip install astropy stsci.tools

WORKDIR /packages
RUN git clone --recursive https://github.com/srodney/drizzlepac.git \
    && cd drizzlepac \
    && python setup.py install

COPY . sndrizpipe
WORKDIR /packages/sndrizpipe
RUN python setup.py install

ENV iref=/dev/null

WORKDIR /work
ENTRYPOINT ["/usr/local/bin/sndrizpipe"]
