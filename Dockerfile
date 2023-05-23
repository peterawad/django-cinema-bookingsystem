FROM python:3.11.1

ENV PYTHONUNBUFFERED 1

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONPATH="/c/Users/MUHAMMAD SHAHZAD/AppData/Local/Programs/Python/Python311/Lib/site-packages:$PYTHONPATH"

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app/
