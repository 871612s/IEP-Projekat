FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiranje izvornog koda kao root
COPY . .

# Kreiranje korisnika i dodela prava nad radnim direktorijumom
RUN useradd --create-home appuser && chown -R appuser:appuser /app

# Prebacivanje na neprivilegovanog korisnika
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:application"]