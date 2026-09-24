# AI Document Intelligence Platform

An AI-powered document processing and retrieval platform built with **FastAPI, PostgreSQL, pgvector, SQLAlchemy, Alembic, JWT authentication, Sentence Transformers, and Ollama**.

The platform allows authenticated users to upload PDF documents, process them asynchronously, extract text and structured metadata, generate vector embeddings, perform semantic search, ask questions using Retrieval-Augmented Generation (RAG), and generate document summaries.

---

## 1. Project Overview

### Problem

Traditional document systems usually store files but provide limited understanding of their contents. Finding a specific value inside a document can require manually opening and searching multiple files.

### Solution

The platform converts uploaded documents into searchable and AI-accessible information.

```text
User
 │
 ▼
JWT Authentication
 │
 ▼
Document Upload
 │
 ▼
PostgreSQL
 │
 ▼
Background Processing
 │
 ├── OCR / Text Extraction
 ├── Document Classification
 ├── Metadata Extraction
 ├── Text Chunking
 └── Embedding Generation
          │
          ▼
       pgvector
          │
          ▼
   Semantic Search
          │
          ▼
          RAG
          │
          ▼
       Ollama
          │
          ▼
      LLM Response
```

Document summarization uses the document processing data and sends the required LLM request to Ollama.

---

# 2. Key Features

## Authentication

- User registration
- User login
- JWT access tokens
- Current-user endpoint
- Password hashing
- Authenticated document access
- User-level document isolation

## Document Management

- PDF upload
- Unique server-side filenames
- Original filename preservation
- File type validation
- File-size validation
- Document listing
- Pagination
- Status filtering
- File-type filtering
- Document details
- File download
- Document deletion

## AI Document Processing

- PDF text extraction using PyMuPDF
- Rule-based document classification
- Document-type-specific extraction
- Metadata extraction
- Metadata persistence
- Text chunking
- Sentence Transformer embeddings
- pgvector storage
- Semantic similarity search

## Generative AI

- Retrieval-Augmented Generation
- Ollama integration
- Local LLM execution
- Document question answering
- Document summarization

## Processing Infrastructure

- Background document processing
- Processing stages
- Processing status
- Processing history
- Processing failure tracking
- Centralized application logging
- Custom document-processing exception handling

## Infrastructure

- Docker
- Docker Compose
- PostgreSQL
- pgvector
- Ollama
- Alembic migrations
- GitHub Actions CI

---

# 3. Technology Stack

| Area | Technology |
|---|---|
| API | FastAPI |
| Language | Python 3.12 |
| Database | PostgreSQL |
| Vector Extension | pgvector |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT |
| PDF Processing | PyMuPDF |
| Embeddings | Sentence Transformers |
| Embedding Model | `all-MiniLM-L6-v2` |
| Embedding Dimension | 384 |
| LLM Runtime | Ollama |
| LLM | Gemma 3 4B |
| API Server | Uvicorn |
| Containerization | Docker |
| Orchestration | Docker Compose |
| Testing | pytest |
| CI | GitHub Actions |
| Configuration | Pydantic Settings |
| Database Driver | psycopg2 |

---

# 4. System Architecture

```text
                         ┌─────────────────────┐
                         │       Client        │
                         │ Swagger / API Client│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │       API Layer     │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
              Authentication   Document APIs     AI APIs
                    │               │                │
                    └───────────────┼────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Service Layer     │
                         └──────────┬──────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               │                    │                    │
               ▼                    ▼                    ▼
        PostgreSQL/ORM         AI Processing         Background Tasks
                                    │
                         ┌──────────┼──────────┐
                         │          │          │
                        OCR   Classifier   Extractors
                                    │
                                    ▼
                               Chunking
                                    │
                                    ▼
                              Embeddings
                                    │
                                    ▼
                                pgvector
                                    │
                                    ▼
                             Semantic Search
                                    │
                                    ▼
                                   RAG
                                    │
                                    ▼
                                 Ollama
```

---

# 5. Complete Request Flow

```text
1. Register user
        ↓
2. Login
        ↓
3. Receive JWT token
        ↓
4. Upload PDF
        ↓
5. Document stored
        ↓
6. Start processing
        ↓
7. Background task begins
        ↓
8. OCR / text extraction
        ↓
9. Classification
        ↓
10. Metadata extraction
        ↓
11. Save metadata
        ↓
12. Chunk document
        ↓
13. Generate embeddings
        ↓
14. Store vectors in pgvector
        ↓
15. Mark document completed
        ↓
16. Semantic search
        ↓
17. Retrieve relevant chunks
        ↓
18. Send context to LLM
        ↓
19. Generate RAG answer
```

---

# 6. Authentication

The API uses JWT-based authentication.

## Registration

Users register with:

- Full name
- Email
- Password

Passwords are stored as hashes rather than plain text.

## Login

The login endpoint validates credentials and returns a JWT access token.

Protected endpoints use:

```text
Authorization: Bearer <token>
```

## Current User

The authenticated user's identity is resolved from the JWT.

Document queries use the authenticated user ID to prevent users from accessing documents belonging to other users.

---

# 7. Document Upload

The upload flow is:

```text
Client
  │
  ▼
Validate content type
  │
  ▼
Read file
  │
  ▼
Validate file size
  │
  ▼
Generate unique filename
  │
  ▼
Save under uploads/
  │
  ▼
Create Document record
```

The original filename is preserved separately from the generated storage filename.

---

# 8. Document Lifecycle

Typical processing state:

```text
uploaded
    │
    ▼
processing
    │
    ├── OCR
    ├── classification
    ├── metadata
    └── embedding
    │
    ▼
completed
```

If processing fails:

```text
processing
    │
    ▼
failed
```

The document also tracks a detailed `processing_stage`.

---

# 9. OCR / Text Extraction

PDF text is extracted using **PyMuPDF**.

The processing service:

1. Opens the PDF.
2. Iterates through pages.
3. Extracts available text.
4. Combines extracted content.
5. Passes the text to subsequent processing stages.

The current implementation primarily performs PDF text extraction; it should not be described as a dedicated image-OCR engine unless one is added.

---

# 10. Document Classification

After text extraction, the document is classified.

The current classifier is rule-based.

Classification determines which extraction strategy should be used.

Document-oriented processing includes extractors for areas such as:

- Insurance
- Invoice
- Resume

The architecture allows additional document types to be added independently.

---

# 11. Document Extractors

The platform uses an extractor-manager pattern.

```text
Extracted Text
      │
      ▼
ExtractorManager
      │
      ├── Insurance Extractor
      ├── Invoice Extractor
      ├── Resume Extractor
      └── Additional Extractors
```

Each extractor is responsible for identifying structured information relevant to its document type.

---

# 12. Metadata Extraction

After classification, structured metadata is extracted and persisted separately from the main document record.

Conceptually:

```text
Document
   │
   └── DocumentMetadata
          ├── key
          └── value
```

The API exposes stored metadata for a document.

---

# 13. Text Chunking

Long documents are divided into smaller chunks before embedding.

Chunking helps:

- Keep embedding input manageable.
- Improve semantic retrieval.
- Retrieve relevant portions of documents.
- Provide focused context to the LLM.

Each chunk stores:

- Document ID
- Chunk index
- Chunk text
- Embedding vector

---

# 14. Embeddings

The platform uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model produces:

```text
384-dimensional embeddings
```

Embeddings are normalized before storage.

```text
Text Chunk
    │
    ▼
Sentence Transformer
    │
    ▼
384-dimensional vector
    │
    ▼
PostgreSQL + pgvector
```

The embedding model is loaded lazily by the application.

---

# 15. PostgreSQL + pgvector

PostgreSQL stores application and document data.

The `pgvector` extension stores embeddings.

The document chunk structure contains:

```text
document_chunks
├── id
├── document_id
├── chunk_index
├── chunk_text
└── embedding VECTOR(384)
```

The vector dimension matches `all-MiniLM-L6-v2`.

---

# 16. Semantic Search

Semantic search converts the user's query into an embedding and compares it with stored document chunk embeddings.

```text
User Query
    │
    ▼
Embedding Model
    │
    ▼
Query Vector
    │
    ▼
pgvector
    │
    ▼
Cosine Distance
    │
    ▼
Relevant Chunks
```

The repository uses cosine-distance ordering.

Search results are filtered by the authenticated user.

A document ID can optionally restrict the search to one document.

The service also limits the requested result count to a controlled range.

---

# 17. Retrieval-Augmented Generation (RAG)

RAG combines semantic retrieval with an LLM.

Flow:

```text
Question
   │
   ▼
Embedding
   │
   ▼
Semantic Search
   │
   ▼
Relevant Chunks
   │
   ▼
Context + Question
   │
   ▼
Ollama / LLM
   │
   ▼
Answer
```

The application retrieves relevant document context instead of relying only on general LLM knowledge.

---

# 18. Ollama Integration

Ollama runs as a separate Docker service.

The application communicates with it through the Docker network:

```text
http://ollama:11434
```

Current architecture:

```text
FastAPI Container
       │
       │ HTTP
       ▼
Ollama Container
       │
       ▼
Gemma 3 4B
```

This separates the LLM runtime from the API process.

---

# 19. Document Summarization

The platform provides document summarization.

```text
Document
   │
   ▼
Processed Document Data
   │
   ▼
Summary Service
   │
   ▼
Ollama
   │
   ▼
Generated Summary
```

The current Docker logs verify successful communication with Ollama and successful summary responses.

---

# 20. Background Processing

Document processing uses FastAPI background tasks.

Example:

```text
POST /documents/{id}/process
            │
            ▼
        202 Accepted
            │
            ▼
    Background Task
            │
            ├── OCR
            ├── Classification
            ├── Metadata
            ├── Embeddings
            └── Completed
```

This prevents long-running processing from unnecessarily blocking the initial API request.

---

# 21. Processing Stages

The application tracks processing stages such as:

```text
uploaded
ocr
classification
metadata
embedding
completed
failed
```

The stage provides more detail than the general document status.

---

# 22. Processing History

Processing events are stored in:

```text
document_processing_logs
```

Each record contains:

- Log ID
- Document ID
- Processing stage
- Status
- Message
- Timestamp

This provides an audit trail of document processing.

The API exposes processing history for individual documents.

---

# 23. Error Handling

The application handles:

- Invalid file type
- File too large
- Document not found
- Unauthorized document access
- Empty semantic-search query
- OCR failure
- Metadata extraction failure
- Embedding failure
- LLM service failure
- Document processing failure

A custom:

```text
DocumentProcessingError
```

is used for document-processing-specific failures.

---

# 24. HTTP Error Handling

The implementation uses HTTP status codes appropriate to the request condition.

Examples:

```text
400  Invalid request
401  Authentication failure
404  Resource not found
422  Invalid/unprocessable input
500  Internal application error
503  Dependent service unavailable
202  Background processing accepted
```

The exact response depends on the endpoint and failure condition.

---

# 25. Logging

Centralized logging is configured using Python's logging framework.

Format:

```text
timestamp | level | logger | message
```

Logs are used for:

- Application startup
- Background processing
- External service communication
- API requests
- Processing completion
- Errors

---

# 26. Health Check

Endpoint:

```text
GET /health
```

The health endpoint checks database connectivity using:

```sql
SELECT 1
```

Healthy response:

```json
{
  "status": "healthy",
  "database": "healthy"
}
```

Database failure returns HTTP 503 with an unhealthy response.

---

# 27. Database Models

## User

```text
id
full_name
email
hashed_password
```

The email is unique.

## Document

```text
id
filename
original_filename
file_type
file_size
storage_path
status
processing_stage
uploaded_by
created_at
```

## DocumentMetadata

Stores extracted document key-value metadata.

## DocumentChunk

```text
id
document_id
chunk_index
chunk_text
embedding
```

## DocumentProcessingLog

```text
id
document_id
stage
status
message
created_at
```

---

# 28. Database Relationships

```text
User
 │
 └───────────────< Document
                     │
                     ├────────< DocumentMetadata
                     │
                     ├────────< DocumentChunk
                     │
                     └────────< DocumentProcessingLog
```

Document child records use cascading deletion where configured.

---

# 29. SQLAlchemy

SQLAlchemy is used for:

- Model definitions
- Database sessions
- Queries
- Relationships
- Transactions
- Persistence

FastAPI receives database sessions through the application's session dependency.

---

# 30. Repository Layer

Repositories isolate database access from business logic.

Examples include repositories for:

- Documents
- Document chunks
- Metadata

This keeps database operations separate from service-level processing logic.

---

# 31. Service Layer

Business logic is separated into services.

Examples include:

```text
DocumentService
DocumentMetadataService
DocumentChunkService
SemanticSearchService
Summarization Service
Embedding Service
```

This keeps API route handlers focused on request/response responsibilities.

---

# 32. AI Layer

AI-related functionality is separated into dedicated modules.

Conceptually:

```text
app/ai/
├── embeddings.py
├── ocr.py
├── classifier.py
├── extractor_manager.py
└── extractors/
    ├── insurance.py
    ├── invoice.py
    └── resume.py
```

The exact module tree may evolve as additional extractors are introduced.

---

# 33. API Layer

The API layer exposes endpoints for:

- Authentication
- User information
- Document management
- Processing
- Metadata
- Processing history
- Semantic search
- RAG
- Summarization
- Health

FastAPI provides OpenAPI documentation.

Swagger UI:

```text
http://localhost:8000/docs
```

OpenAPI specification:

```text
http://localhost:8000/openapi.json
```

---

# 34. API Endpoint Reference

## Authentication

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

## Documents

```text
POST   /documents/upload
GET    /documents
GET    /documents/{document_id}
GET    /documents/{document_id}/download
DELETE /documents/{document_id}
```

## Processing

```text
POST /documents/{document_id}/process
GET  /documents/{document_id}/processing-history
```

## Metadata

```text
GET /documents/{document_id}/metadata
```

## Semantic Search

```text
POST /documents/semantic-search
```

## Summarization

```text
GET /documents/{document_id}/summary
```

## RAG

The RAG endpoint uses semantic retrieval and the configured Ollama model. The generated OpenAPI schema at `/docs` is the authoritative request/response reference.

## Health

```text
GET /health
```

---

# 35. Pagination and Filtering

Document listing supports pagination and filtering.

Supported filters include:

```text
page
page_size
status
file_type
```

The response provides pagination information and document items.

---

# 36. User-Level Data Isolation

Documents are associated with the user who uploaded them.

Document and semantic-search queries are scoped using the authenticated user ID.

```text
Authenticated User
       │
       ▼
User ID
       │
       ▼
Document query filtered by uploaded_by
```

This is an important authorization boundary.

---

# 37. Alembic Database Migrations

Alembic manages database schema changes.

The migration history includes changes for:

```text
users
documents
document_metadata
document_chunks
processing_stage
document_processing_logs
```

Current migration head:

```text
4775ab64574e
```

Docker startup runs:

```bash
alembic upgrade head
```

before starting Uvicorn.

---

# 38. Docker Architecture

Docker Compose runs three services:

```text
┌─────────────────────────────┐
│           Docker            │
│                             │
│  ┌─────────┐                │
│  │ FastAPI │ :8000          │
│  └────┬────┘                │
│       │                     │
│       ├───────────┐         │
│       ▼           ▼         │
│  PostgreSQL     Ollama      │
│  :5432          :11434      │
│                             │
└─────────────────────────────┘
```

Services:

```text
app
db
ollama
```

---

# 39. FastAPI Container

The application container:

- Uses Python 3.12
- Installs dependencies
- Runs Alembic migrations
- Starts Uvicorn
- Exposes port 8000
- Mounts the uploads directory

Startup:

```text
alembic upgrade head
        ↓
uvicorn app.main:app
```

---

# 40. PostgreSQL Container

The database uses:

```text
pgvector/pgvector:pg18
```

It provides:

- PostgreSQL
- pgvector
- Persistent database storage
- Docker health checks

Local port:

```text
localhost:5432
```

---

# 41. Ollama Container

Ollama uses:

```text
ollama/ollama:latest
```

Local port:

```text
localhost:11434
```

The application uses:

```text
http://ollama:11434
```

The Ollama data directory uses a persistent Docker volume.

---

# 42. Docker Volumes

Configured persistence includes:

```text
postgres_data
ollama_data
```

Uploaded documents are mounted using:

```text
./uploads:/app/uploads
```

---

# 43. Docker Startup

```text
Container starts
      ↓
PostgreSQL becomes healthy
      ↓
Alembic migrations run
      ↓
Uvicorn starts
      ↓
API becomes available
```

Docker Compose uses the database health check for startup coordination.

---

# 44. Environment Configuration

Configuration is managed through environment variables and Pydantic Settings.

Example `.env.example` structure:

```env
APP_NAME=AI Document Intelligence Platform
APP_VERSION=1.0.0
DEBUG=False

DATABASE_URL=postgresql://username:password@localhost:5432/document_ai

SECRET_KEY=replace_with_a_secure_secret_key

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Never commit real secrets to source control.

---

# 45. Local Development

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies using the project's dependency configuration.

Configure `.env`.

Run migrations:

```powershell
alembic upgrade head
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

---

# 46. Docker Development

Build and start:

```powershell
docker compose up -d --build
```

Check services:

```powershell
docker compose ps
```

Check logs:

```powershell
docker compose logs app --tail=30
```

Check health:

```powershell
curl.exe http://localhost:8000/health
```

Expected:

```json
{
  "status": "healthy",
  "database": "healthy"
}
```

Swagger:

```text
http://localhost:8000/docs
```

Stop:

```powershell
docker compose down
```

---

# 47. Database Migration Commands

```powershell
docker compose exec app alembic current
docker compose exec app alembic heads
docker compose exec app alembic history
```

Apply migrations:

```powershell
docker compose exec app alembic upgrade head
```

---

# 48. Testing

Run:

```powershell
pytest -q
```

The current repository test suite has reached:

```text
16 passed
```

Tests cover areas including:

- Authentication
- Document APIs
- Database connectivity
- Health
- OCR
- Classification
- Insurance extraction
- Chunking
- Embeddings
- Semantic search
- Summarization
- LLM functionality
- Security

The exact test count can change as more tests are added.

---

# 49. CI

GitHub Actions runs tests on pushes and pull requests to `main`.

The workflow:

```text
Checkout
   ↓
Python 3.12
   ↓
Install dependencies
   ↓
Start PostgreSQL + pgvector
   ↓
Enable pgvector
   ↓
Run Alembic migrations
   ↓
Run pytest
```

CI uses test credentials and must not contain production secrets.

---

# 50. Security

Security-related implementation includes:

- Password hashing
- JWT authentication
- User-scoped document access
- Environment-based secrets
- No real secrets in `.env.example`
- Secret-key rotation
- Removal of an exposed historical database credential from Git history
- File validation
- Database access through configuration

Real secrets must remain outside source control.

---

# 51. Git Security Cleanup

During development, a database credential was identified in Git history.

The repository history was rewritten using `git-filter-repo`, the credential was removed from reachable history, the active database credential was rotated, and the cleaned history was force-pushed.

History rewriting should not be performed casually on shared branches.

---

# 52. Runtime Verification

The current Docker deployment has been verified with:

```text
FastAPI container      Running
PostgreSQL container   Running + healthy
Ollama container       Running
```

Verified operations include:

```text
GET  /health                         → 200
POST /documents/semantic-search      → 200
POST /documents/{id}/process         → 202
Background processing                → completed
GET  /documents/{id}/processing-history → 200
GET  /documents/{id}/metadata       → 200
Ollama /api/chat                      → 200
GET  /documents/{id}/summary         → 200
```

The logs also confirm background processing completion and successful Ollama communication.

---

# 53. Current Project Status

Implemented:

- [x] FastAPI application
- [x] PostgreSQL
- [x] pgvector
- [x] SQLAlchemy
- [x] Alembic
- [x] JWT authentication
- [x] User registration
- [x] User login
- [x] Current-user API
- [x] Document upload
- [x] Document listing
- [x] Pagination
- [x] Filtering
- [x] Document retrieval
- [x] Document download
- [x] Document deletion
- [x] PDF text extraction
- [x] Document classification
- [x] Metadata extraction
- [x] Metadata persistence
- [x] Chunking
- [x] Embeddings
- [x] pgvector semantic search
- [x] RAG
- [x] Ollama integration
- [x] Document summarization
- [x] Background processing
- [x] Processing stages
- [x] Processing history
- [x] Health endpoint
- [x] Centralized logging
- [x] Custom processing exception
- [x] Docker Compose
- [x] PostgreSQL Docker service
- [x] Ollama Docker service
- [x] Docker startup migrations
- [x] Automated tests
- [x] GitHub Actions CI
- [x] Secret cleanup

---

# 54. Current Limitations

- PDF is the primary supported document format.
- Current text extraction is primarily PDF text extraction rather than a dedicated image OCR engine.
- Background processing uses FastAPI `BackgroundTasks`; a distributed worker system such as Celery/RQ is not currently used.
- Vector retrieval uses the current pgvector similarity-search implementation and configured threshold.
- LLM generation depends on Ollama and available local resources.
- Production deployment requires additional infrastructure hardening.

---

# 55. Future Enhancements

## Document Support

- DOCX
- XLSX
- PPTX
- Images
- Scanned PDFs
- Dedicated OCR engine

## AI

- Additional embedding models
- Hybrid keyword + vector search
- Reranking
- Source citations
- Streaming LLM responses
- More document-specific extractors
- Multimodal document understanding

## Processing

- Celery/RQ
- Redis/RabbitMQ
- Retry policies
- Dead-letter handling
- Scheduled reprocessing

## Infrastructure

- Kubernetes
- Cloud deployment
- Object storage such as S3
- Managed PostgreSQL
- Secrets manager
- Reverse proxy
- TLS
- Monitoring
- Metrics
- Distributed tracing

## Security

- Refresh tokens
- Role-based access control
- Rate limiting
- File malware scanning
- Stronger upload validation
- Expanded audit logging

---

# 56. Production Considerations

Before production deployment, review:

- Secret management
- Database credentials
- JWT secret rotation
- HTTPS/TLS
- Reverse proxy configuration
- Database backups
- File storage strategy
- Container resource limits
- LLM resource requirements
- Rate limiting
- Authentication policies
- Authorization policies
- Monitoring and alerting
- Log retention
- Error tracking
- Data retention
- Disaster recovery

The Docker Compose setup is a development/deployment foundation and should not automatically be treated as a complete production architecture.

---

# 57. Project Structure

High-level structure:

```text
ai-document-intelligence-platform/
│
├── app/
│   ├── ai/
│   │   ├── embeddings.py
│   │   ├── ocr.py
│   │   ├── classifier.py
│   │   ├── extractor_manager.py
│   │   └── extractors/
│   │
│   ├── api/
│   │   └── v1/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   └── logging_config.py
│   │
│   ├── database/
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── document_metadata.py
│   │   ├── document_chunk.py
│   │   └── document_processing_log.py
│   │
│   ├── repositories/
│   │
│   ├── services/
│   │
│   ├── tasks/
│   │   └── document_tasks.py
│   │
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── tests/
├── uploads/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
└── README.md
```

---

# 58. Example AI Capabilities

Development testing demonstrated document question answering and retrieval for values such as:

```text
Invoice Number
INV-3337

Total Due
$93.50

Due Date
January 31, 2016

Insurance Policy Number
EXD20260001234
```

Actual answers depend on the uploaded document and retrieved context.

---

# 59. Design Principles

### Separation of Concerns

API, service, repository, AI, model, and task layers have separate responsibilities.

### User Isolation

Document and semantic-search queries are scoped to the authenticated user.

### Asynchronous Processing

Long-running document processing is executed as a background task.

### Persistent Processing State

Document status, processing stage, and processing history are persisted.

### Vector Retrieval

Embeddings are stored in PostgreSQL using pgvector.

### Local LLM Runtime

Ollama provides the local LLM runtime.

### Migration-Based Schema Management

Alembic manages repeatable database schema changes.

### Automated Validation

pytest and GitHub Actions provide automated testing.

---

# 60. Interview Explanation

> The AI Document Intelligence Platform is a FastAPI-based backend that allows authenticated users to upload PDF documents and automatically process them through text extraction, classification, metadata extraction, chunking, and embedding generation. Embeddings are stored in PostgreSQL using pgvector for semantic search. Relevant document chunks are retrieved for RAG-based question answering, while Ollama provides local LLM inference for question answering and document summarization. Long-running processing is handled using FastAPI background tasks, with persistent processing stages and history. The complete application is containerized using Docker Compose and includes PostgreSQL, pgvector, and Ollama services, with Alembic migrations and GitHub Actions CI.

---

# 61. Resume-Level Project Highlights

### AI Document Intelligence Platform

- Built a FastAPI-based document intelligence backend with JWT authentication, PostgreSQL, SQLAlchemy, and Alembic.
- Implemented asynchronous document processing including PDF text extraction, classification, metadata extraction, chunking, and embeddings.
- Integrated Sentence Transformers and pgvector for 384-dimensional semantic document search.
- Implemented RAG-based document question answering using retrieved document context.
- Integrated Ollama for local LLM-powered document summarization and question answering.
- Added processing-stage tracking, processing history, structured logging, exception handling, and health monitoring.
- Containerized FastAPI, PostgreSQL/pgvector, and Ollama using Docker Compose.
- Added automated pytest coverage and GitHub Actions CI with PostgreSQL/pgvector.

---

# 62. Complete System Commands

Start:

```powershell
docker compose up -d --build
```

Check services:

```powershell
docker compose ps
```

Health:

```powershell
curl.exe http://localhost:8000/health
```

Swagger:

```text
http://localhost:8000/docs
```

Logs:

```powershell
docker compose logs app --tail=50
```

Resource usage:

```powershell
docker stats --no-stream
```

Stop:

```powershell
docker compose down
```

---

# 63. Summary

The project combines:

```text
Backend Engineering
        +
Database Engineering
        +
Vector Search
        +
Document Processing
        +
Generative AI
        +
RAG
        +
Docker
        +
Automated Testing
        +
CI
```

The platform provides an end-to-end workflow from document upload to structured extraction, vector retrieval, contextual question answering, and LLM-powered summarization.

---

## Project Status

**Core implementation complete and Docker end-to-end workflow verified.**

The next phase is production hardening, additional document formats, stronger observability, and infrastructure scaling as required.
