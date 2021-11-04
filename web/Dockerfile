FROM python:slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && \ 
    pip install -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python", "app.py"]
