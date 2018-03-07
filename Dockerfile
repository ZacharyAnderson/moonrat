from python:3

#Add necessary files
ADD moonrat.py /
ADD config.ini /
ADD requirements.txt / 

#Install dependencies
RUN pip3 install -r requirements.txt

#Exposes port that needs to be mapped to container
EXPOSE 80

#Command to execute python code
CMD ["python3", "./moonrat.py"]