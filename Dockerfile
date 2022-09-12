FROM ubuntu
RUN apt-get update
RUN apt-get install net-tools
RUN apt-get update
RUN apt-get install python3-pip -y
RUN apt-get install zlib1g-dev -y libjpeg-dev -y libpng-dev -y
COPY requirements.txt /home
RUN pip install -r /home/requirements.txt
COPY FLASK_BLOG_WEBAPP WEB_APP
WORKDIR /WEB_APP
ENTRYPOINT [ "python3", "run.py" ]
EXPOSE 3000 5000