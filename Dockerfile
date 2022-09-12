FROM ubuntu
RUN apt-get update
RUN apt-get install net-tools
RUN apt-get update
RUN apt-get install python3-pip -y
COPY requirements.txt /home
RUN pip3 install -r /home/requirements.txt
COPY FLASK_BLOG_WEBAPP WEB_APP
WORKDIR /WEB_APP
ENTRYPOINT [ "python3", "run.py" ]
EXPOSE 3000 5000