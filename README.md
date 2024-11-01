> **The app doesn't work on Brave browser due to its default privacy settings, try it out on a firefox based browser**

## Table of Contents
1. [Overview](#overview)
2. [Architecture Components](#architecture-components)
   - [Web Framework](#web-framework)
   - [Database](#database)
   - [File Handling](#file-handling)
   - [Session Management](#session-management)
   - [Logging](#logging)
3. [Main Components and their Interactions](#main-components-and-their-interactions)
   - [User Interface](#user-interface)
   - [PDF Upload Endpoint](#pdf-upload-endpoint)
   - [WebSocket Endpoint](#websocket-endpoint)
   - [Database Operations](#database-operations)
   - [Chat Model Initialization](#chat-model-initialization)
4. [Technologies Used](#technologies-used)
5. [Low-Level Design (LLD)](#low-level-design-lld)
   - [Database Model (Session)](#database-model-session)
   - [Key Functions](#key-functions)
     - [create_session](#create_session)
     - [get_session_data](#get_session_data)
     - [update_session_data](#update_session_data)
   - [File Handling](#file-handling)
     - [save_file](#save_file)
     - [read_pdf](#read_pdf)
   - [WebSocket Communication](#websocket-communication)
     - [websocket_endpoint](#websocket_endpoint)
   - [Initialization of Chat Model](#initialization-of-chat-model)

# Demo Video

[Demo Video](./assets/demo-video.mp4)

### High-Level Design (HLD)

### Overview
The application is a PDF chatbot that allows users to upload PDF documents, which are then processed to extract content for question-answering tasks. It maintains a session for each uploaded document, storing user queries and responses to facilitate an interactive chat experience.

### Architecture Components
1. **Web Framework**: The application is built using **FastAPI**, which provides endpoints for uploading PDF files and handling WebSocket connections for real-time interactions.

2. **Database**: Utilizes **SQLite** with SQLAlchemy as the ORM to manage the `sessions` table, where session data (document paths, queries, answers) is stored.

3. **File Handling**: Uploaded PDF files are saved to a specified public directory and processed to extract content using **Langchain** libraries.

4. **Session Management**: Each session is uniquely identified by a `session_id`. It stores the document path, the content of the document, and chat history for the session.

5. **Logging**: The application logs important events and errors to a log file, aiding in debugging and monitoring.

**Main Components and their Interactions:**
- **User Interface**: A web page (HTML template) for uploading PDFs and interacting with the chatbot.
- **PDF Upload Endpoint**: `/upload-pdf` accepts file uploads and initiates a session.
- **WebSocket Endpoint**: `/question` allows users to ask questions about the uploaded PDF and receive responses.
- **Database Operations**: CRUD operations on session data using SQLAlchemy.
- **Chat Model Initialization**: Loads the document and initializes the chat model for answering user queries.

**Technologies Used:**
- **FastAPI** for building the web application.
- **SQLAlchemy** for ORM and database management.
- **Langchain** libraries for document processing and question-answering.
- **SQLite** for lightweight database storage.

### Low-Level Design (LLD)

**1. Database Model (Session):**
```python
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False)
    document_path = Column(String, unique=True, nullable=False)
    date = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    context = Column(String, nullable=False)
    history = Column(String, nullable=True, default="")
```
- **Fields**:
  - `id`: Unique identifier for each session.
  - `session_id`: Unique session identifier for tracking.
  - `document_path`: Path to the uploaded PDF file.
  - `date`: Timestamp for session creation.
  - `updated_at`: Timestamp for the last update to the session.
  - `context`: JSON string storing the content of the PDF.
  - `history`: JSON string storing the conversation history.

**2. Key Functions:**
- `create_session`
  - Creates a new session and stores it in the database.
  - Generates a unique session ID.

- `get_session_data`
  - Retrieves session data from the database based on the `session_id`.

- `update_session_data`
  - Updates the session history with the latest question and answer.

**3. File Handling:**
- `save_file`:
  - Saves the uploaded PDF file to the public folder and returns the file path.

- `read_pdf`:
  - Loads the PDF file and returns its content as a list of documents.

**4. WebSocket Communication:**
- `websocket_endpoint`:
  - Handles incoming WebSocket connections for chat functionality.
  - Receives user questions, invokes the retrieval chain, and sends back answers.

**5. Initialization of Chat Model:**
- `init_chat_model`:
  - Reads the PDF content and initializes a question-answering model using Langchain.
