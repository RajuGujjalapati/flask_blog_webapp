FROM centos:latest
RUN sudo apt install net-tools
RUN sudo apt install httpd
RUN sudo apt install python3
COPY requirements.txt /home
RUN pip3 install -r /home/requirements.txt
COPY FLASK_BLOG_WEBAPP WEB_APP
WORKDIR /WEB_APP
ENTRYPOINT [ "python3", "run.py" ]
EXPOSE 3000 5000