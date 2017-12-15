FROM heroku/miniconda

# Grab requirements.txt.
ADD ./requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip install -qr /tmp/requirements.txt

# Add our code
ADD . ./chrome-extension
WORKDIR ./chrome-extension

RUN sudo apt-get install swig

RUN conda install scipy=1.0.0
RUN conda install sklearn=0.0
RUN conda install numpy==1.13.3
RUN conda install gensim==3.1.0
RUN conda install gunicorn==19.7.1

# CMD gunicorn --bind 0.0.0.0:$PORT wsgi

CMD pwd && gunicorn app:app --log-level=DEBUG
