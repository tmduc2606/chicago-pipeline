# ---------- build ----------
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- runtime ----------
FROM python:3.11-slim
RUN groupadd -r app && useradd -r -g app -d /opt/app -s /sbin/nologin app
WORKDIR /opt/app
COPY --from=builder /install /usr/local
COPY . .
RUN chown -R app:app /opt/app
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
