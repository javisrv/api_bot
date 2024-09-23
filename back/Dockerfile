FROM python:3.12-slim
COPY /app /opt/app/
WORKDIR /opt/app/
RUN pip install --upgrade -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]