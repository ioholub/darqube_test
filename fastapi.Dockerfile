FROM python:3.9
WORKDIR /darqube_test
COPY requirements.txt /darqube_test/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /darqube_test/requirements.txt
COPY app /darqube_test/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
