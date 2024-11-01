# Use an official Python image as a base
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file
COPY poetry.lock pyproject.toml ./

RUN pip install poetry && poetry install --no-root

# Copy the application code
COPY . .
RUN poetry install

# Expose the port for the web server
EXPOSE 8000

# Run the command to start the development server
CMD ["poetry", "run", "uvicorn", "pdf_chatbot.app:app", "--host", "0.0.0.0", "--port", "8000"]
