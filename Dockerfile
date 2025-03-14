FROM python:3.12-slim AS builder
 
# Create the app directory
RUN mkdir /app
WORKDIR /app
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.1.1
 
# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir poetry==$POETRY_VERSION && poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction

 
# Stage 2: Production stage
FROM python:3.12-slim
 
RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app
 
# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
 
# Set the working directory
WORKDIR /app
 
# Copy application code
COPY --chown=appuser:appuser . .
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Switch to non-root user
USER appuser
 
# Expose the application port
EXPOSE 8000

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "GameRPSSL.wsgi:application"]
