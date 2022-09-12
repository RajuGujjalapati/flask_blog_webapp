FROM centos:latest
RUN apk add install net-tools
RUN apk add install httpd
RUN apk add install python3
COPY requirements.txt /home
RUN pip3 install -r /home/requirements.txt
COPY FLASK_BLOG_WEBAPP WEB_APP
WORKDIR /WEB_APP
ENTRYPOINT [ "python3", "run.py" ]
EXPOSE 3000 5000