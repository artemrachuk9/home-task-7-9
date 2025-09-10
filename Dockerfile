FROM python:3.10-slim
RUN pip install pipenv
WORKDIR /app
COPY . /app
RUN pipenv install --system --deploy
CMD ["python", "main.py"]