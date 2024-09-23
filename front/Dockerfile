FROM python:3.12-slim
COPY /app/ /opt/app/
WORKDIR /opt/app/
RUN pip install --upgrade -r requirements.txt
CMD ["streamlit", "run", "main.py" , "--server.port", "8000"]