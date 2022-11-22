FROM python:3.7

ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /holistic-backend

# Install netcat to check connection of the dependency services
RUN apt-get update && apt-get install -y netcat

# Add source code to the working directory
ADD . /holistic-backend

# Install all requirements 
RUN pip install -r requirements.txt

RUN chmod +x /holistic-backend/runserver.sh
CMD ["sh", "runserver.sh"]