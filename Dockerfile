FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./sql_app /app/sql_app

RUN python -m sql_app.init_db

EXPOSE 8000

CMD ["uvicorn", "sql_app.main:app", "--host", "0.0.0.0", "--port", "8000"]