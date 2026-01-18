# AI Internship Resume Structuring Agent - Complete Implementation Prompt for Cursor AI

## 🎯 Project Mission

You are building a **production-grade AI-powered resume structuring system** that transforms scattered, unstructured resume data and GitHub profiles into a clean, canonical resume optimized for internship applications. This system prioritizes **transparency, accuracy, and professional software engineering practices**.

---

## 🏛️ Core Principles

### 1. **No Data Fabrication**
- The LLM must ONLY structure and normalize existing data
- Never invent skills, experiences, dates, or achievements
- All output must be traceable to source data

### 2. **Explainability First**
- Every decision the system makes must be logged
- Users should understand why data was included or excluded
- Generate detailed decision logs alongside structured output

### 3. **Production Quality**
- Write clean, maintainable, well-documented code
- Use proper error handling and validation
- Follow SOLID principles and design patterns
- Include comprehensive logging

### 4. **Type Safety & Validation**
- Use Pydantic models for all data structures
- Validate inputs and outputs rigorously
- Leverage TypeScript on frontend for type safety

---

## 📚 Technology Stack Requirements

### Backend Stack
- **Framework**: FastAPI (latest stable version)
- **Python Version**: 3.11+
- **LLM API**: Groq API using `llama-3.1-70b-versatile` model
- **Validation**: Pydantic v2 with strict type checking
- **Database**: SQLAlchemy 2.0+ with SQLite (dev) / PostgreSQL (production)
- **PDF Parsing**: Use `pdfplumber` (primary) and `pypdf` (fallback)
- **GitHub Integration**: `PyGithub` library
- **Testing**: pytest with async support
- **Code Quality**: ruff (linting), black (formatting), mypy (type checking)
- **Logging**: structlog for structured JSON logging
- **Environment Management**: python-dotenv

### Frontend Stack
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite (fast, modern)
- **UI Components**: shadcn/ui (built on Radix UI primitives)
- **Styling**: Tailwind CSS with custom design tokens
- **Forms**: React Hook Form + Zod validation
- **State Management**: TanStack Query (React Query) for server state
- **HTTP Client**: Axios with interceptors
- **File Upload**: react-dropzone for drag-and-drop
- **Icons**: Lucide React
- **Toast Notifications**: sonner

### DevOps
- **Containerization**: Docker + Docker Compose
- **API Documentation**: Auto-generated with FastAPI (Swagger/ReDoc)
- **CORS**: Properly configured for local and production

---

## 🗂️ Project Structure

Create a monorepo structure with clear separation:

```
ai-resume-structuring-agent/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   ├── models/         # Database models and Pydantic schemas
│   │   ├── services/       # Business logic layer
│   │   ├── core/           # Core utilities (DB, logging, config)
│   │   └── utils/          # Helper functions
│   ├── tests/              # Comprehensive test suite
│   ├── alembic/            # Database migrations
│   └── prompts/            # LLM system prompts (externalized)
│
├── frontend/               # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page-level components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utilities and API clients
│   │   └── types/         # TypeScript type definitions
│
├── docker-compose.yml      # Multi-container orchestration
└── README.md              # Comprehensive documentation
```

---

## 🔨 Implementation Phases

### Phase 1: Backend Foundation (Priority: CRITICAL)

#### 1.1 Project Initialization
**What to do:**
- Set up Python project with Poetry or pip-tools for dependency management
- Create `pyproject.toml` with all dependencies and dev dependencies
- Configure ruff, black, and mypy with strict settings
- Set up `.env` file structure with clear documentation
- Initialize git with comprehensive `.gitignore`

**Key files to create:**
- `backend/pyproject.toml` - Dependency management
- `backend/.env.example` - Environment variable template
- `backend/.gitignore` - Exclude sensitive files, venv, cache
- `backend/README.md` - Backend-specific documentation

#### 1.2 Configuration Management
**What to do:**
- Create a `config.py` using Pydantic Settings
- Load all configuration from environment variables
- Include settings for: Groq API, GitHub API, database, CORS, file upload limits
- Use `@lru_cache` for singleton pattern
- Validate all required environment variables on startup

**Critical settings:**
- `GROQ_API_KEY` - Required, no default
- `GROQ_MODEL` - Default to `llama-3.1-70b-versatile`
- `DATABASE_URL` - SQLite for dev, PostgreSQL for prod
- `MAX_UPLOAD_SIZE` - 10MB limit
- `ALLOWED_ORIGINS` - CORS whitelist

#### 1.3 Database Layer
**What to do:**
- Set up SQLAlchemy with async support
- Create database models for:
  - `ResumeUpload` - Stores uploaded files and extracted text
  - `GitHubData` - Caches GitHub API responses
  - `StructuredResume` - Final canonical resume output
  - `DecisionLog` - Explainability and audit trail
- Use Alembic for migrations from day 1
- Include proper indexes for common queries
- Add `created_at` and `updated_at` timestamps to all tables

**Database design principles:**
- Use enums for status fields
- Store structured data as JSON columns (PostgreSQL JSONB in production)
- Add foreign keys for referential integrity
- Include soft delete capability (optional `deleted_at` column)

#### 1.4 Pydantic Schemas
**What to do:**
- Create a comprehensive `resume_schema.py` defining the canonical resume structure
- Build nested Pydantic models matching this exact structure:

```
CanonicalResume
├── ContactInfo (name, email, phone, location, github, linkedin)
├── Summary (professional summary string)
├── TechnicalSkills (languages, frameworks, tools, databases)
├── Projects[] (name, description, technologies, source, url, highlights)
├── Education[] (degree, institution, graduation_date, gpa, coursework)
├── Experience[] (role, organization, dates, description, technologies)
├── Certifications[] (name, issuer, date, url)
└── AdditionalInfo (optional freeform text)
```

- Add field validators for:
  - Email format validation
  - Phone number format (international support)
  - URL validation for GitHub/LinkedIn
  - Date format validation
  - GPA range (0.0-4.0)
- Include example data in schema documentation
- Use descriptive field names and add helpful descriptions

---

### Phase 2: Core Services (Priority: CRITICAL)

#### 2.1 File Parsing Services
**What to do:**
- Create an abstract `BaseParser` class defining the interface
- Implement three concrete parsers:

**PDF Parser:**
- Use `pdfplumber` for primary extraction (better layout preservation)
- Handle multi-column layouts gracefully
- Extract text page by page
- Preserve structure (headings, bullets)
- Fall back to `pypdf` if pdfplumber fails
- Handle corrupted or password-protected PDFs with clear error messages
- Log warnings for low-quality extractions

**Markdown Parser:**
- Simple UTF-8 file reading
- Validate encoding
- Preserve markdown structure for LLM processing
- Handle large files (set reasonable size limits)

**LaTeX Parser:**
- Extract text content while preserving structure
- Remove LaTeX commands that don't contribute to content
- Handle common resume templates
- Warn if complex LaTeX formatting may be lost

**Common requirements for all parsers:**
- Return extracted text as clean string
- Include metadata (page count, character count)
- Implement `validate_file()` method
- Use async/await for potential future optimizations
- Comprehensive error handling with specific error types

#### 2.2 GitHub Integration Service
**What to do:**
- Create a `GitHubService` class using PyGithub
- Implement smart repository filtering:
  - Exclude archived repositories
  - Exclude forks without original contributions
  - Prioritize recently updated repositories
  - Limit to top 10-15 most relevant repos
- Extract for each repository:
  - Name, description, URL
  - Primary language and all languages used
  - Stars, forks (relevance signals)
  - Topics/tags
  - Creation and last update dates
  - README content (first 2000 characters)
- Extract profile data:
  - Name, bio, location
  - Email (if public)
  - Company, blog/website
  - Hireable status
- Implement rate limiting awareness
- Cache responses to avoid repeated API calls
- Handle common errors:
  - User not found (404)
  - Rate limit exceeded (403)
  - Network timeouts
  - Invalid tokens

**Filtering logic:**
- Skip repos with no description and no README
- Prioritize repos with stars > 0
- Prioritize repos with recent activity (last 6 months)
- Sort by: recency, stars, commit activity

#### 2.3 Groq LLM Service
**What to do:**
- Create an `LLMService` class wrapping the Groq API client
- Implement a `structure_resume()` method that:
  - Takes resume text and GitHub data as input
  - Sends a carefully crafted prompt to Groq
  - Returns structured JSON matching the CanonicalResume schema
  - Returns a separate decision log explaining choices

**Prompt engineering guidelines:**
- Create a detailed system prompt stored in `backend/prompts/system_prompt.txt`
- System prompt must:
  - Define the agent's role and constraints
  - Provide the exact JSON schema expected
  - Include strict rules: no fabrication, no assumptions
  - Give examples of good vs bad structuring
  - Emphasize internship optimization (highlight projects, education, skills)

**User message construction:**
- Format input data clearly with section headers
- Include: "=== RESUME TEXT ===" section
- Include: "=== GITHUB DATA ===" section
- Provide clear instructions for output format
- Request both structured resume AND decision log

**LLM configuration:**
- Model: `llama-3.1-70b-versatile` (good balance of quality and speed)
- Temperature: 0.1 (low for consistency)
- Max tokens: 4096 (sufficient for detailed output)
- Enable JSON mode if available

**Error handling:**
- Retry logic for transient failures (max 3 retries)
- Validate LLM output against Pydantic schema
- If invalid JSON, attempt to repair common issues
- Log all LLM interactions for debugging
- Handle rate limits gracefully

#### 2.4 Data Normalization Service
**What to do:**
- Create a `NormalizationService` for pre-processing data before LLM
- Implement functions to:
  - Standardize technology names (e.g., "JS" → "JavaScript", "react.js" → "React")
  - Deduplicate skills across sources
  - Merge duplicate projects (same name from resume and GitHub)
  - Normalize date formats
  - Clean up whitespace and encoding issues
  - Remove sensitive information (SSN, passport numbers)
- Use configurable mappings for technology normalization
- Keep a mapping file like `technology_aliases.json`

**Example normalizations:**
- Programming languages: python → Python, c++ → C++
- Frameworks: reactjs, react.js, React.js → React
- Tools: github → GitHub, postgresql → PostgreSQL

#### 2.5 Decision Logger Service
**What to do:**
- Create a `DecisionLogger` class to format explainability data
- Parse the LLM's decision log
- Structure decisions by section:
  - Projects: which included, which excluded, why
  - Skills: how skills were categorized and merged
  - Dates: any date format conversions
  - Contact: how contact info was prioritized
- Format for human readability
- Store in database linked to the structured resume
- Include:
  - Action taken
  - Items affected
  - Reasoning
  - Source of information
  - Timestamp

---

### Phase 3: API Endpoints (Priority: HIGH)

#### 3.1 FastAPI Application Setup
**What to do:**
- Create `main.py` as application entry point
- Configure CORS with explicit allowed origins
- Add middleware for:
  - Request logging (with request ID)
  - Error handling (catch-all exception handler)
  - Request timing
- Enable auto-generated OpenAPI documentation
- Add startup/shutdown events for database connection
- Configure file upload with multipart/form-data support

#### 3.2 API Endpoints to Implement

**Health Check Endpoint:**
```
GET /api/v1/health
- Returns API status, version, timestamp
- Checks database connectivity
- No authentication required
```

**Resume Upload Endpoint:**
```
POST /api/v1/resume/upload
- Accept file upload (PDF, MD, or TEX)
- Validate file type and size
- Extract text using appropriate parser
- Store in database with status "parsing"
- Return upload ID and extracted text preview
- Handle errors: invalid format, file too large, parsing failure
```

**GitHub Data Fetch Endpoint:**
```
POST /api/v1/github/fetch
- Accept GitHub username in request body
- Fetch profile and repository data
- Cache results in database
- Return GitHub data summary
- Handle errors: user not found, rate limit, API down
```

**Resume Structuring Endpoint:**
```
POST /api/v1/resume/structure
- Accept resume upload ID and GitHub data ID (both optional)
- Validate at least one source is provided
- Call LLM service to structure data
- Store structured resume and decision log
- Return structured resume ID
- This is the main orchestration endpoint
```

**Get Structured Resume Endpoint:**
```
GET /api/v1/resume/{resume_id}
- Retrieve structured resume by ID
- Include decision log
- Support format query parameter: json, markdown
- Return 404 if not found
```

**List User Resumes Endpoint (Future):**
```
GET /api/v1/resumes
- List all structured resumes for user
- Include metadata (created date, sources used)
- Paginated response
```

**Export Resume Endpoint:**
```
GET /api/v1/resume/{resume_id}/export?format=markdown
- Export in requested format (markdown, json, pdf)
- Generate clean formatted output
- For markdown: use the canonical structure template
```

#### 3.3 Request/Response Schemas
**What to do:**
- Create Pydantic models for all API requests and responses
- Separate schemas from database models
- Include validation rules
- Use clear, descriptive field names
- Add OpenAPI examples for documentation

**Example schemas needed:**
- `ResumeUploadRequest` (multipart file)
- `ResumeUploadResponse` (upload_id, filename, status, preview)
- `GitHubFetchRequest` (username)
- `GitHubFetchResponse` (profile summary, repo count)
- `StructureRequest` (resume_upload_id, github_data_id)
- `StructureResponse` (structured_resume_id, status)
- `ResumeDetailResponse` (full canonical resume + decision log)

#### 3.4 Error Handling Strategy
**What to do:**
- Create custom exception classes:
  - `FileParsingError`
  - `GitHubAPIError`
  - `LLMServiceError`
  - `ValidationError`
- Implement global exception handler
- Return consistent error response format:
```json
{
  "error": {
    "code": "PARSING_FAILED",
    "message": "Unable to extract text from PDF",
    "details": "File may be corrupted or password-protected",
    "request_id": "uuid"
  }
}
```
- Log all errors with full context
- Don't expose internal errors to users

---

### Phase 4: Frontend Application (Priority: HIGH)

#### 4.1 Project Setup
**What to do:**
- Initialize React project with Vite and TypeScript template
- Install and configure Tailwind CSS
- Set up shadcn/ui component library
- Configure path aliases (@/ for src/)
- Set up ESLint and Prettier
- Create proper TypeScript config (strict mode)
- Set up environment variables (.env.local)

#### 4.2 Design System
**What to do:**
- Define color palette in Tailwind config:
  - Primary: Professional blue (#0066CC or similar)
  - Secondary: Complementary accent
  - Neutral grays for text and backgrounds
  - Success, warning, error colors
- Define typography scale (headings, body, captions)
- Create consistent spacing system
- Define border radius values
- Set up dark mode support (optional but recommended)

**Design principles:**
- Clean, minimal, professional aesthetic
- High contrast for readability
- Consistent spacing (use Tailwind spacing scale)
- Clear visual hierarchy
- Responsive design (mobile-first)
- Accessible (WCAG AA compliant)

#### 4.3 Component Architecture

**Create these UI components using shadcn/ui:**
- Button (variants: default, outline, ghost)
- Card (for content sections)
- Input (text, email, file)
- Textarea
- Badge (for tags, technologies)
- Tabs (for switching views)
- Dialog/Modal
- Toast notifications (using sonner)
- Progress indicator
- Loading spinner
- Alert/Banner for errors

**Create custom components:**

**Layout Components:**
- `Header` - Logo, navigation, settings
- `Footer` - Credits, links
- `Layout` - Wraps all pages with consistent structure

**Resume Upload Section:**
- `ResumeUpload` - Drag-and-drop zone using react-dropzone
  - Show file name after upload
  - Display file size and type
  - Show parsing status (loading, success, error)
  - Preview extracted text in expandable section
- `FileTypeSelector` - Visual selector for PDF/MD/TEX
- `UploadProgress` - Progress bar for parsing

**GitHub Connection Section:**
- `GitHubConnect` - Input for username
  - Validate username format
  - Show fetching status
  - Display error if user not found
  - Preview fetched data (repo count, profile info)
- `RepositoryList` - Show fetched repositories
  - Display repo name, description, languages
  - Show which repos will be used
  - Allow manual exclusion (future feature)

**Resume Preview Section:**
- `ResumePreview` - Display structured resume
  - Render each section beautifully
  - Use cards for projects, experience
  - Show technologies as badges
  - Copy-to-clipboard functionality
  - Toggle between formatted view and raw JSON
- `SectionCard` - Reusable component for each resume section
- `ProjectCard` - Display individual project
- `ExperienceCard` - Display work experience

**Decision Log Section:**
- `DecisionLog` - Expandable panel showing AI decisions
  - Organize by section
  - Show action, reasoning, source
  - Color-code actions (included=green, excluded=red)
  - Make it educational for users

**Export Section:**
- `ExportOptions` - Download buttons
  - Export as Markdown
  - Export as JSON
  - Export as PDF (stretch goal)
  - Copy to clipboard

#### 4.4 Page Structure

**Create these pages:**

**Home Page (`/`)**
- Hero section with clear value proposition
- "Upload your resume to get started" CTA
- Feature highlights (structured output, GitHub integration, explainable)
- Example before/after
- Link to documentation

**Upload Page (`/upload`)**
- Two-column layout:
  - Left: Resume upload
  - Right: GitHub connection
- Clear instructions
- Validation feedback
- "Process Resume" button (only enabled when data ready)

**Processing Page (`/processing`)**
- Show during LLM structuring
- Animated loading indicator
- Status updates ("Parsing resume...", "Fetching GitHub...", "Structuring data...")
- Estimated time
- Auto-redirect to results when complete

**Results Page (`/results`)**
- Tabbed interface:
  - Tab 1: Structured Resume (main view)
  - Tab 2: Decision Log (explainability)
  - Tab 3: Raw Data (for debugging)
- Export options at top
- Share/save functionality
- "Start Over" button

#### 4.5 State Management
**What to do:**
- Use TanStack Query (React Query) for server state
- Define these queries:
  - `useUploadResume` - Upload and parse file
  - `useFetchGitHub` - Fetch GitHub data
  - `useStructureResume` - Trigger structuring
  - `useGetResume` - Fetch structured resume
- Configure proper cache times
- Handle loading and error states
- Use Zustand for minimal client state:
  - Current upload ID
  - Current GitHub username
  - UI state (current step, modal open/closed)

#### 4.6 API Integration
**What to do:**
- Create an Axios instance with base URL
- Add request interceptor for adding headers
- Add response interceptor for error handling
- Create typed API functions in `src/lib/api.ts`:
  - `uploadResume(file: File): Promise<UploadResponse>`
  - `fetchGitHub(username: string): Promise<GitHubResponse>`
  - `structureResume(data: StructureRequest): Promise<StructureResponse>`
  - `getResume(id: string): Promise<ResumeDetailResponse>`
- Handle network errors gracefully
- Show user-friendly error messages

#### 4.7 TypeScript Types
**What to do:**
- Create interfaces matching backend schemas
- Define in `src/types/resume.ts`
- Use strict null checks
- Avoid `any` types
- Create utility types for common patterns

**Key types needed:**
```typescript
interface ContactInfo { ... }
interface TechnicalSkills { ... }
interface Project { ... }
interface Education { ... }
interface Experience { ... }
interface CanonicalResume { ... }
interface DecisionLogEntry { ... }
interface APIError { ... }
```

#### 4.8 User Experience Enhancements
**What to do:**
- Add loading skeletons during data fetching
- Implement optimistic updates where appropriate
- Add smooth transitions between steps
- Show progress indicators for multi-step processes
- Provide helpful tooltips and hints
- Add keyboard shortcuts (Ctrl+Enter to submit, etc.)
- Implement proper focus management
- Add success animations when operations complete
- Show clear error messages with recovery actions

---

### Phase 5: LLM Prompt Engineering (Priority: CRITICAL)

#### 5.1 System Prompt Design
**What to do:**
- Create a comprehensive system prompt in `backend/prompts/system_prompt.txt`
- Structure it in clear sections:

**Role Definition:**
- You are a resume structuring assistant
- Your job is to organize and normalize resume data
- You MUST NOT invent or fabricate information

**Constraints:**
- Only use information explicitly provided
- Do not make assumptions about dates, locations, or achievements
- If information is missing, leave fields empty
- Maintain factual accuracy at all costs

**Schema Definition:**
- Provide the complete JSON schema for CanonicalResume
- Include field descriptions and constraints
- Give examples of properly formatted entries

**Normalization Rules:**
- Technology name standardization (provide examples)
- Date format guidelines
- How to categorize skills
- Project selection criteria

**Decision Logging:**
- Explain that you must also return a decision log
- Format for decision log entries
- What to log (selections, exclusions, transformations)

**Tone and Style:**
- Professional and concise
- Use action-oriented language for descriptions
- Avoid marketing buzzwords

#### 5.2 User Prompt Construction
**What to do:**
- Create a template for user messages
- Clearly separate input sources:
  
```
=== RESUME TEXT ===
[Insert extracted resume text here]

=== GITHUB DATA ===
Profile: [username, bio, location]
Repositories:
1. [name] - [description] - [languages]
2. ...

=== INSTRUCTIONS ===
Structure the above information into the canonical resume format.
Return TWO JSON objects:
1. structured_resume: Following the CanonicalResume schema
2. decision_log: Array of decisions made

Rules:
- Prefer resume data for personal info
- Use GitHub data to enrich projects section
- Normalize all technology names
- Select top 5-8 most relevant projects
- Explain all decisions in the log
```

#### 5.3 Few-Shot Examples (Optional but Recommended)
**What to do:**
- Include 1-2 example input/output pairs in the system prompt
- Show good structuring behavior
- Demonstrate proper decision logging
- Keep examples realistic and relevant to internships

#### 5.4 Output Validation Strategy
**What to do:**
- Parse LLM JSON response
- Validate against Pydantic schema
- If validation fails:
  - Log the raw LLM output
  - Attempt automatic repairs (common JSON issues)
  - If repair fails, return clear error to user
  - Consider retry with clarified prompt
- Never show raw LLM errors to end users

---

### Phase 6: Testing & Quality Assurance (Priority: HIGH)

#### 6.1 Backend Testing
**What to do:**
- Set up pytest with async support
- Create test fixtures for:
  - Sample resume files (PDF, MD, TEX)
  - Mock GitHub API responses
  - Mock Groq API responses
  - Test database
- Write unit tests for:
  - Each parser (PDF, Markdown, LaTeX)
  - GitHub service (with mocked API)
  - LLM service (with mocked responses)
  - Normalization functions
  - Pydantic schema validation
- Write integration tests for:
  - Full upload → parse → store flow
  - Full GitHub → cache → retrieve flow
  - End-to-end structuring pipeline
- Write API tests for:
  - All endpoints (happy path and error cases)
  - File upload handling
  - Error response formats
- Aim for >80% code coverage

#### 6.2 Frontend Testing
**What to do:**
- Set up Vitest for unit tests
- Test utility functions
- Test custom hooks
- Consider React Testing Library for component tests
- Test form validation logic
- Test API integration with mocked responses

#### 6.3 Manual Testing Checklist
**What to do:**
- Test with various resume formats:
  - Single-column PDF
  - Multi-column PDF
  - Markdown with different structures
  - LaTeX resume
- Test with different GitHub profiles:
  - Users with many repos
  - Users with few repos
  - Users with no repos
  - Non-existent users
- Test error scenarios:
  - Invalid file uploads
  - Network failures
  - LLM API errors
  - Malformed responses
- Test edge cases:
  - Very long resumes
  - Resumes with special characters
  - Missing sections
  - Conflicting data between sources

---

### Phase 7: Deployment & Documentation (Priority: MEDIUM)

#### 7.1 Docker Configuration
**What to do:**
- Create `Dockerfile` for backend:
  - Use Python 3.11 slim base image
  - Install dependencies from requirements.txt
  - Copy application code
  - Set proper user (non-root)
  - Expose port 8000
  - Health check endpoint
- Create `Dockerfile` for frontend:
  - Use Node.js for build stage
  - Use nginx for serve stage
  - Copy built static files
  - Configure nginx for SPA routing
  - Expose port 80
- Create `docker-compose.yml`:
  - Backend service
  - Frontend service
  - PostgreSQL service (production)
  - Proper networking
  - Volume mounts for development
  - Environment variable management

#### 7.2 Environment Configuration
**What to do:**
- Create comprehensive `.env.example` files
- Document every environment variable
- Separate dev/staging/prod configurations
- Never commit real secrets
- Use proper secret management for production

#### 7.3 Documentation
**What to do:**
- Create comprehensive README.md:
  - Project overview and purpose
  - Features list
  - Architecture diagram
  - Setup instructions (local development)
  - Environment variables documentation
  - API documentation link
  - Contributing guidelines
  - License

- Create API documentation:
  - Use FastAPI's auto-generated docs
  - Add descriptions to all endpoints
  - Include request/response examples
  - Document error codes

- Create user guide:
  - How to upload a resume
  - How to connect GitHub
  - How to interpret the decision log
  - How to export results
  - FAQ section
  - Troubleshooting common issues

- Create developer documentation:
  - Architecture overview
  - How to add a new parser
  - How to modify the canonical schema
  - LLM prompt modification guide
  - Database schema
  - Testing guide

#### 7.4 Logging & Monitoring
**What to do:**
- Use structlog for JSON structured logging
- Log all important events:
  - API requests (with request ID)
  - File uploads and parsing
  - LLM API calls (prompt + response)
  - Errors and exceptions
  - Performance metrics (timing)
- Include context in logs:
  - User ID (future)
  - Resume ID
  - Request ID (for tracing)
- Configure log levels properly
- Consider adding:
  - Sentry for error tracking (production)
  - Application metrics (Prometheus)
  - Request tracing (OpenTelemetry)

---

## 🎨 Design Guidelines for Professional UI

### Visual Design Principles

**Color Scheme:**
- Primary color: Professional blue (#0066CC or similar) for CTAs and important elements
- Background: Light gray (#F9FAFB) or white for main areas
- Text: Dark gray (#1F2937) for primary text, medium gray (#6B7280) for secondary
- Success: Green (#10B981)
- Warning: Yellow (#F59E0B)
- Error: Red (#EF4444)
- Use color consistently and meaningfully

**Typography:**
- Use system font stack for performance: `font-family: system-ui, -apple-system, ...`
- Clear hierarchy:
  - H1: 2.5rem, bold (page titles)
  - H2: 2rem, semibold (section headers)
  - H3: 1.5rem, semibold (subsections)
  - Body: 1rem, normal (main content)
  - Small: 0.875rem (captions, metadata)
- Ample line-height for readability (1.6 for body text)

**Spacing:**
- Use consistent spacing scale (4px base unit)
- Generous whitespace between sections
- Comfortable padding inside cards (16-24px)
- Clear separation between interactive elements

**Components:**
- Rounded corners (4-8px) for modern feel
- Subtle shadows for depth (avoid heavy shadows)
- Smooth transitions (200-300ms) for interactions
- Clear hover and focus states
- Loading states for all async operations

**Layout:**
- Responsive grid system
- Maximum content width (1200px) for readability
- Consistent margins and padding
- Stack on mobile, side-by-side on desktop
- Sticky header for navigation

**Interaction Design:**
- Clear visual feedback for all actions
- Disabled states for unavailable actions
- Progress indicators for multi-step flows
- Confirmation for destructive actions
- Undo capability where appropriate
- Keyboard navigation support
- Focus indicators for accessibility

**Professional Polish:**
- Smooth page transitions
- Loading skeletons instead of spinners
- Empty states with helpful guidance
- Error states with recovery actions
- Success states with next steps
- Consistent iconography
- Professional copy and microcopy

---

## 🚨 Critical Requirements & Best Practices

### Code Quality Standards

**Python Backend:**
- Use type hints everywhere
- Docstrings for all public functions (Google style)
- Async/await for I/O operations
- Context managers for resource cleanup
- Use Pydantic for validation
- Follow PEP 8 (enforced by black and ruff)
- Maximum function length: 50 lines
- Maximum file length: 500 lines
- Single Responsibility Principle

**TypeScript Frontend:**
- Enable strict mode
- No implicit any
- Proper null checking
- Use const for immutable values
- Functional components with hooks
- Custom hooks for reusable logic
- Props interfaces for all components
- Avoid prop drilling (use context or state management)

### Security Considerations

**Backend:**
- Validate all file uploads (type, size, content)
- Sanitize user inputs
- Use parameterized database queries (SQLAlchemy ORM prevents SQL injection)
- Rate limiting on API endpoints (prevent abuse)
- CORS configuration (whitelist only trusted origins)
- Secure environment variable handling (never log secrets)
- Input validation at API boundary (Pydantic models)
- File type verification (don't trust file extensions alone)
- Path traversal prevention when handling file uploads
- Set proper HTTP security headers

**Frontend:**
- Sanitize any user-generated content before display
- Use HTTPS in production
- Implement CSRF protection
- Validate all form inputs client-side AND server-side
- Don't store sensitive data in localStorage
- Handle tokens securely (httpOnly cookies if using auth)

**API Keys:**
- Never commit API keys to git
- Use environment variables exclusively
- Rotate keys periodically
- Use separate keys for dev/staging/prod
- Monitor API usage for anomalies

### Performance Optimization

**Backend:**
- Use connection pooling for database
- Implement caching for GitHub API responses (cache for 24 hours)
- Async endpoints for I/O-bound operations
- Stream large responses instead of loading in memory
- Use database indexes on frequently queried columns
- Implement request timeout limits
- Consider background tasks for long-running operations (Celery/RQ)
- Lazy load data where possible
- Optimize database queries (use `select_related` in SQLAlchemy)

**Frontend:**
- Code splitting with React lazy loading
- Optimize images (use WebP, lazy loading)
- Minimize bundle size (tree shaking, analyze with vite-bundle-visualizer)
- Use React.memo for expensive components
- Debounce search/filter inputs
- Virtual scrolling for long lists
- Prefetch critical API calls
- Cache API responses with React Query
- Use loading skeletons instead of spinners

**LLM Optimization:**
- Keep prompts concise but clear
- Use lower temperature for consistency (0.1-0.2)
- Implement response caching for identical inputs
- Consider streaming responses for real-time feedback
- Monitor token usage and costs
- Implement retry logic with exponential backoff
- Set appropriate timeouts

### Error Handling Strategy

**Backend Error Categories:**

1. **Validation Errors (400)**
   - Invalid file format
   - Missing required fields
   - Invalid data format
   - Response: Clear message about what's wrong and how to fix

2. **Not Found Errors (404)**
   - Resume ID doesn't exist
   - GitHub user not found
   - Response: Specific message about what wasn't found

3. **External Service Errors (502/503)**
   - GitHub API down
   - Groq API errors
   - Response: "Service temporarily unavailable, please try again"

4. **Rate Limit Errors (429)**
   - Too many requests
   - GitHub rate limit exceeded
   - Response: Clear message with retry-after timing

5. **Server Errors (500)**
   - Unexpected exceptions
   - Database errors
   - Response: Generic message, detailed logs server-side

**Frontend Error Handling:**
- Display toast notifications for errors
- Show inline validation errors on forms
- Provide "Retry" buttons for failed operations
- Show friendly error messages (not technical jargon)
- Offer fallback options when possible
- Log errors to console for debugging
- Consider error boundary components

---

## 🔄 Development Workflow

### Local Development Setup

**Initial Setup:**
1. Clone repository
2. Set up Python virtual environment: `python -m venv venv`
3. Install backend dependencies: `pip install -r requirements.txt`
4. Install frontend dependencies: `npm install`
5. Copy `.env.example` to `.env` and fill in API keys
6. Run database migrations: `alembic upgrade head`
7. Start backend: `uvicorn app.main:app --reload`
8. Start frontend: `npm run dev`
9. Access application at `http://localhost:5173`

**Development Workflow:**
1. Create feature branch from main
2. Write code following style guide
3. Write tests for new functionality
4. Run linters: `ruff check .` and `black .`
5. Run type checker: `mypy .`
6. Run tests: `pytest` with coverage
7. Commit with descriptive messages
8. Create pull request for review

**Git Commit Message Convention:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

Examples:
- `feat(parser): add LaTeX parser support`
- `fix(api): handle GitHub rate limit errors`
- `docs(readme): update setup instructions`

### Code Review Checklist

**For Backend Code:**
- [ ] Type hints on all functions
- [ ] Docstrings with parameter descriptions
- [ ] Error handling with specific exceptions
- [ ] Input validation with Pydantic
- [ ] Tests written with >80% coverage
- [ ] No hardcoded values (use config)
- [ ] Logging for important operations
- [ ] No TODO comments without issues

**For Frontend Code:**
- [ ] TypeScript types defined
- [ ] PropTypes or interfaces for components
- [ ] Accessibility attributes (ARIA labels)
- [ ] Responsive design tested
- [ ] Loading and error states handled
- [ ] No console.logs in production code
- [ ] Reusable components extracted
- [ ] Performance optimized (memoization if needed)

---

## 📊 Database Schema Details

### Table: resume_uploads
```
id: Integer (PK, Auto-increment)
filename: String(255) - Original filename
file_type: String(10) - pdf, md, or tex
file_size: Integer - Size in bytes
raw_text: Text - Extracted text content
uploaded_at: DateTime - UTC timestamp
status: Enum - pending, parsing, structuring, completed, failed
error_message: Text (nullable) - Error details if failed

Indexes:
- id (primary key)
- status (for filtering by status)
- uploaded_at (for sorting)
```

### Table: github_data
```
id: Integer (PK, Auto-increment)
username: String(100, Unique) - GitHub username
profile_data: JSON - {name, bio, location, email, blog, company, hireable}
repositories: JSON - Array of repository objects
extracted_at: DateTime - UTC timestamp
cache_expires_at: DateTime - When to refresh (24 hours)

Indexes:
- id (primary key)
- username (unique)
- cache_expires_at (for cache invalidation)
```

### Table: structured_resumes
```
id: Integer (PK, Auto-increment)
resume_upload_id: Integer (FK, nullable) - Reference to resume_uploads
github_data_id: Integer (FK, nullable) - Reference to github_data

contact: JSON - ContactInfo object
summary: Text - Professional summary
technical_skills: JSON - TechnicalSkills object
projects: JSON - Array of Project objects
education: JSON - Array of Education objects
experience: JSON - Array of Experience objects (nullable)
certifications: JSON - Array of Certification objects (nullable)
additional_info: JSON - Free-form text (nullable)

created_at: DateTime - UTC timestamp
updated_at: DateTime - UTC timestamp (auto-update)
version: Integer - For versioning (default: 1)

Indexes:
- id (primary key)
- resume_upload_id (foreign key)
- github_data_id (foreign key)
- created_at (for sorting)
```

### Table: decision_logs
```
id: Integer (PK, Auto-increment)
structured_resume_id: Integer (FK) - Reference to structured_resumes
decisions: JSON - Array of decision objects
created_at: DateTime - UTC timestamp

Decision object format:
{
  "section": "projects",
  "action": "included" | "excluded" | "merged" | "normalized",
  "items": ["item1", "item2"],
  "reason": "Explanation of decision",
  "source": "resume" | "github" | "both",
  "confidence": "high" | "medium" | "low"
}

Indexes:
- id (primary key)
- structured_resume_id (foreign key)
```

---

## 🎯 Detailed LLM Integration Guide

### System Prompt Structure

**File: `backend/prompts/system_prompt.txt`**

Create a multi-section prompt:

**Section 1: Role & Purpose**
```
You are a professional resume structuring assistant specializing in internship applications.
Your role is to transform unstructured resume data and GitHub information into a clean,
well-organized canonical resume format.

CRITICAL RULES:
1. NEVER fabricate or invent information
2. ONLY use data explicitly provided in the input
3. If information is missing, leave fields empty or null
4. Maintain factual accuracy at all costs
5. Do not make assumptions about dates, locations, or achievements
```

**Section 2: Canonical Schema**
```
You must return a JSON object with this EXACT structure:

{
  "structured_resume": {
    "contact": {
      "full_name": "string (required)",
      "email": "string (required, valid email)",
      "phone": "string (optional, e.164 format preferred)",
      "location": "string (optional, City, State/Country format)",
      "github": "string (optional, full URL)",
      "linkedin": "string (optional, full URL)",
      "website": "string (optional, full URL)"
    },
    "summary": "string (2-4 sentences, highlight internship-relevant skills and goals)",
    "technical_skills": {
      "languages": ["array of programming languages"],
      "frameworks_libraries": ["array of frameworks"],
      "tools_platforms": ["array of tools and platforms"],
      "databases": ["array of databases (optional)"],
      "other": ["array of other relevant technical skills"]
    },
    "projects": [
      {
        "name": "string (required)",
        "description": "string (required, 1-2 sentences)",
        "technologies": ["array of technologies used (required)"],
        "source": "resume | github | both",
        "url": "string (optional, GitHub or live demo URL)",
        "highlights": ["array of 2-4 key achievements/features"],
        "start_date": "YYYY-MM-DD or null",
        "end_date": "YYYY-MM-DD or null"
      }
    ],
    "education": [
      {
        "degree": "string (e.g., Bachelor of Science in Computer Science)",
        "institution": "string (university/college name)",
        "location": "string (optional)",
        "graduation_date": "Month YYYY or YYYY",
        "gpa": "string (X.XX/4.0 format or null)",
        "relevant_coursework": ["array of relevant courses"],
        "honors": ["array of honors/awards"]
      }
    ],
    "experience": [
      {
        "role": "string",
        "organization": "string",
        "location": "string (optional)",
        "start_date": "Month YYYY",
        "end_date": "Month YYYY or Present",
        "description": ["array of 2-5 achievement statements"],
        "technologies": ["array of technologies used"]
      }
    ],
    "certifications": [
      {
        "name": "string",
        "issuer": "string (optional)",
        "date": "Month YYYY (optional)",
        "credential_id": "string (optional)",
        "url": "string (optional)"
      }
    ],
    "additional_info": "string (optional, clubs, languages, interests)"
  },
  "decision_log": [
    {
      "section": "string (which section this decision affects)",
      "action": "included | excluded | merged | normalized",
      "items": ["array of items affected"],
      "reason": "string (clear explanation of why this decision was made)",
      "source": "resume | github | both",
      "confidence": "high | medium | low"
    }
  ]
}
```

**Section 3: Normalization Guidelines**
```
Technology Name Standardization:
- Always use official capitalization: Python (not python), JavaScript (not javascript)
- Expand common abbreviations: JS → JavaScript, TS → TypeScript
- Use full framework names: React (not React.js), Vue (not Vue.js)
- Standardize tools: GitHub (not Github), PostgreSQL (not Postgres)

Common mappings:
- react, react.js, reactjs → React
- node, node.js, nodejs → Node.js
- python3, py → Python
- c++, cpp → C++
- postgres, postgresql → PostgreSQL
- mongo, mongodb → MongoDB
- k8s → Kubernetes
- docker-compose → Docker Compose

Skill Categorization:
- Languages: Python, JavaScript, Java, C++, etc.
- Frameworks: React, Django, Express, FastAPI, etc.
- Tools/Platforms: Git, Docker, AWS, VS Code, etc.
- Databases: PostgreSQL, MongoDB, Redis, etc.
```

**Section 4: Project Selection Criteria**
```
When selecting projects from multiple sources:

Priority Order:
1. Projects with detailed descriptions and clear impact
2. Recent projects (within last 12 months)
3. Projects demonstrating relevant skills for internships
4. Projects with evidence of completion (README, commits, stars)
5. Projects with multiple technologies/complexity

Selection Guidelines:
- Include 5-8 most impressive projects
- Prefer projects with actual users or deployments
- Include a mix of personal, academic, and collaborative projects
- Exclude: homework assignments, basic tutorials, abandoned projects
- For GitHub repos: prefer those with >10 commits, good README, recent activity

When merging duplicate projects:
- If same project appears in resume AND GitHub, merge information
- Use resume description if more detailed
- Add GitHub URL and activity metrics
- Combine technology lists (deduplicate)
```

**Section 5: Writing Style Guidelines**
```
Descriptions should be:
- Action-oriented (start with strong verbs: Built, Developed, Implemented, Designed)
- Specific and quantifiable when possible (e.g., "Achieved 95% accuracy" not "Good accuracy")
- Concise (1-2 sentences for project descriptions)
- Professional but not overly formal
- Free of marketing buzzwords ("revolutionary", "game-changing")

Strong verbs for achievements:
- Built, Developed, Engineered, Architected
- Implemented, Integrated, Deployed
- Optimized, Improved, Reduced, Increased
- Designed, Created, Established
- Collaborated, Led, Managed

Example transformations:
❌ "Made a cool app that does stuff with AI"
✅ "Built a sentiment analysis web application using BERT transformers, achieving 92% accuracy on product reviews"

❌ "Worked on the backend"
✅ "Developed RESTful API endpoints using FastAPI, reducing response time by 40%"
```

**Section 6: Decision Logging Requirements**
```
You must log decisions for:
1. Projects included (which ones and why)
2. Projects excluded (which ones and why)
3. Skills categorization (how you grouped them)
4. Technology name normalizations (what you changed)
5. Data merging decisions (when combining sources)
6. Missing information (what couldn't be filled)

Decision log format:
- Be specific about what items were affected
- Provide clear, educational reasoning
- Indicate confidence level
- Cite source of information

Good decision log entry:
{
  "section": "projects",
  "action": "included",
  "items": ["ML Price Predictor", "Task Manager API", "Portfolio Website"],
  "reason": "Selected based on technical complexity, recency, and relevance to software engineering internships. These projects demonstrate full-stack capabilities and ML knowledge.",
  "source": "both",
  "confidence": "high"
}

{
  "section": "projects",
  "action": "excluded",
  "items": ["CS101 Homework", "Hello World Tutorial"],
  "reason": "Excluded basic academic assignments and tutorials that don't demonstrate independent project development",
  "source": "github",
  "confidence": "high"
}
```

**Section 7: Edge Cases**
```
Handle these situations gracefully:

No GitHub data provided:
- Rely entirely on resume
- Note in decision log that GitHub enrichment was unavailable

No resume data provided:
- Build resume from GitHub alone
- Extract name/email from GitHub profile
- Use repo descriptions for projects
- Note limitations in decision log

Conflicting information:
- Prefer resume data for personal information (name, email, location)
- Prefer GitHub for technical details (languages, project activity)
- Note conflicts in decision log

Missing critical information:
- Leave fields as null/empty
- Do NOT make assumptions
- Note what's missing in decision log
- Suggest user review these sections

Ambiguous dates:
- If year only, use "YYYY" format
- If month unclear, use year only
- Never guess specific dates
```

### User Prompt Template

**File: `backend/services/llm_service.py` - Prompt construction**

```python
def _build_user_prompt(
    resume_text: Optional[str],
    github_data: Optional[dict]
) -> str:
    """Build user prompt from input sources."""
    
    parts = []
    
    # Resume section
    if resume_text:
        parts.append("=== RESUME TEXT ===")
        parts.append(resume_text.strip())
        parts.append("")
    
    # GitHub section
    if github_data:
        parts.append("=== GITHUB DATA ===")
        parts.append("")
        
        # Profile
        profile = github_data.get("profile", {})
        parts.append("PROFILE:")
        parts.append(f"  Username: {profile.get('username', 'N/A')}")
        parts.append(f"  Name: {profile.get('name', 'N/A')}")
        parts.append(f"  Bio: {profile.get('bio', 'N/A')}")
        parts.append(f"  Location: {profile.get('location', 'N/A')}")
        parts.append(f"  Email: {profile.get('email', 'N/A')}")
        parts.append("")
        
        # Repositories
        repos = github_data.get("repositories", [])
        parts.append(f"REPOSITORIES ({len(repos)} total):")
        for i, repo in enumerate(repos, 1):
            parts.append(f"{i}. {repo['name']}")
            parts.append(f"   Description: {repo['description'] or 'No description'}")
            parts.append(f"   Languages: {', '.join(repo['languages'])}")
            parts.append(f"   URL: {repo['url']}")
            parts.append(f"   Stars: {repo['stars']}, Last updated: {repo['updated_at']}")
            if repo.get('readme'):
                parts.append(f"   README preview: {repo['readme'][:200]}...")
            parts.append("")
    
    # Instructions
    parts.append("=== TASK ===")
    parts.append("Structure the above information into the canonical resume format.")
    parts.append("")
    parts.append("REQUIREMENTS:")
    parts.append("1. Return valid JSON with 'structured_resume' and 'decision_log' keys")
    parts.append("2. Follow the exact schema provided in your system prompt")
    parts.append("3. Normalize all technology names using the standardization rules")
    parts.append("4. Select 5-8 most relevant projects for internship applications")
    parts.append("5. Write professional, action-oriented descriptions")
    parts.append("6. Log all significant decisions in the decision_log")
    parts.append("7. Do NOT fabricate any information")
    parts.append("8. Leave fields empty/null if information is not provided")
    parts.append("")
    parts.append("Focus on creating an internship-optimized resume that highlights:")
    parts.append("- Technical skills and project experience")
    parts.append("- Educational background and relevant coursework")
    parts.append("- Demonstrated ability to build real applications")
    
    return "\n".join(parts)
```

### LLM Response Parsing & Validation

**Implementation approach:**

```python
async def structure_resume(...) -> tuple[CanonicalResume, dict]:
    """Call LLM and validate response."""
    
    # 1. Build prompts
    system_prompt = self._load_system_prompt()
    user_prompt = self._build_user_prompt(resume_text, github_data)
    
    # 2. Call Groq API
    try:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}  # Force JSON mode
        )
    except Exception as e:
        logger.error("groq_api_error", error=str(e))
        raise LLMServiceError(f"Failed to call Groq API: {str(e)}")
    
    # 3. Extract and parse response
    content = response.choices[0].message.content
    
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("json_parse_error", content=content[:500])
        # Attempt repair
        parsed = self._attempt_json_repair(content)
    
    # 4. Validate against schema
    try:
        structured_resume = CanonicalResume(**parsed["structured_resume"])
        decision_log = parsed.get("decision_log", [])
    except (KeyError, ValidationError) as e:
        logger.error("schema_validation_error", error=str(e))
        raise LLMServiceError(f"LLM response does not match expected schema: {str(e)}")
    
    # 5. Post-processing
    structured_resume = self._post_process_resume(structured_resume)
    
    return structured_resume, decision_log
```

---

## 🎨 Detailed Component Specifications

### ResumeUpload Component

**Purpose**: Handle file upload with drag-and-drop and validation

**Features**:
- Drag-and-drop zone with visual feedback
- File type restriction (PDF, MD, TEX only)
- File size limit (10MB)
- Show upload progress
- Display parsing status
- Preview extracted text in collapsible section

**UI States**:
1. **Idle**: "Drag and drop your resume here or click to browse"
2. **Hovering**: Highlight drop zone with border
3. **Uploading**: Show progress bar and percentage
4. **Parsing**: "Extracting text from your resume..."
5. **Success**: Show checkmark, filename, preview button
6. **Error**: Show error message, "Try Again" button

**Code structure**:
```typescript
interface ResumeUploadProps {
  onUploadComplete: (uploadId: string, text: string) => void;
}

const ResumeUpload: React.FC<ResumeUploadProps> = ({ onUploadComplete }) => {
  // State: file, uploading, parsing, error, extractedText
  // useDropzone hook for drag-and-drop
  // useMutation for API call
  // Handle file validation client-side
  // Show toast notifications for errors
  // Return upload ID and text to parent
}
```

### GitHubConnect Component

**Purpose**: Fetch GitHub profile and repositories

**Features**:
- Input field for username
- Real-time validation (alphanumeric, hyphens only)
- "Connect GitHub" button
- Loading state while fetching
- Display fetched data summary
- Show repository count and preview

**UI States**:
1. **Idle**: Input field + "Connect" button
2. **Fetching**: Loading spinner, "Fetching your GitHub data..."
3. **Success**: Show avatar, name, repo count, "Connected ✓"
4. **Error**: Show error message, "Retry" button

**Data display after success**:
- GitHub avatar
- Username and full name
- Bio (if available)
- Repository count: "15 repositories found"
- Button to view repository list (opens modal)

### ResumePreview Component

**Purpose**: Display structured resume in readable format

**Features**:
- Tabbed interface: "Preview" and "Raw JSON"
- Copy entire resume to clipboard
- Download as Markdown
- Print-friendly styling

**Layout**:
- Header section (name, contact info) - centered, prominent
- Summary section - brief paragraph
- Skills section - categorized badges
- Projects section - card grid
- Education section - timeline format
- Experience section (if present) - timeline format
- Certifications - list format

**Styling details**:
- Use cards with subtle shadows
- Technology badges with color coding
- Icons for contact methods (email, phone, GitHub, LinkedIn)
- Responsive grid (1 column mobile, 2+ columns desktop)
- Consistent spacing between sections

### DecisionLog Component

**Purpose**: Show explainability information

**Features**:
- Collapsible sections by category
- Color-coded actions (green=included, red=excluded, blue=normalized)
- Search/filter functionality
- Export log as JSON

**Display format**:
```
Projects ▼
  ✓ Included (3)
    • ML Price Predictor
    • Task Manager API  
    • Portfolio Website
    Reason: Selected based on technical complexity, recency...
    Source: Both resume and GitHub
    
  ✗ Excluded (2)
    • CS101 Homework
    • Hello World Tutorial
    Reason: Basic academic assignments...
    Source: GitHub
    
Skills ▼
  ↻ Normalized (8)
    • react, react.js → React
    • python3 → Python
    Reason: Standardized technology names...
```

---

## 📱 Responsive Design Breakpoints

**Mobile First Approach:**

```css
/* Mobile: 320px - 640px */
- Single column layout
- Stack all elements vertically
- Full-width cards
- Hamburger menu for navigation
- Touch-friendly button sizes (min 44x44px)

/* Tablet: 641px - 1024px */
- Two-column layout for projects/experience
- Side-by-side upload sections
- Larger text for readability

/* Desktop: 1025px+ */
- Multi-column layouts
- Sidebar navigation (optional)
- Wider content area (max 1200px)
- Hover effects enabled
```

**Key responsive considerations**:
- Test on actual devices, not just browser resize
- Ensure forms are easy to fill on mobile
- Make tap targets large enough
- Optimize images for different screen sizes
- Consider landscape mode on tablets

---

## 🧪 Testing Strategy Details

### Backend Testing Approach

**Unit Tests** (`tests/test_parsers.py`):
```python
class TestPDFParser:
    def test_parse_single_column_pdf(self):
        """Test parsing standard single-column PDF."""
        # Use sample PDF from fixtures
        # Assert extracted text contains expected content
        # Check character count is reasonable
    
    def test_parse_multi_column_pdf(self):
        """Test parsing complex multi-column layout."""
        # Verify columns are properly merged
    
    def test_parse_corrupted_pdf(self):
        """Test handling of corrupted PDF file."""
        # Should raise ValueError with descriptive message
    
    def test_validate_file_success(self):
        """Test file validation for valid PDF."""
        # Returns True for valid file
```

**Integration Tests** (`tests/test_integration.py`):
```python
class TestResumeStructuringFlow:
    async def test_full_pipeline_with_resume_only(self, client, sample_resume):
        """Test complete flow from upload to structured output."""
        # 1. Upload resume
        # 2. Trigger structuring
        # 3. Verify structured resume created
        # 4. Verify decision log generated
    
    async def test_full_pipeline_with_github_only(self, client, mock_github):
        """Test building resume from GitHub alone."""
        # Mock GitHub API responses
        # Verify resume can be created from repos
    
    async def test_pipeline_with_both_sources(self, client):
        """Test merging resume and GitHub data."""
        # Verify proper data merging
        # Check decision log shows both sources used
```

**API Tests** (`tests/test_api.py`):
```python
class TestResumeEndpoints:
    async def test_upload_valid_pdf(self, client):
        """Test uploading valid PDF file."""
        # POST /api/v1/resume/upload
        # Assert 200 status
        # Assert response contains upload_id
    
    async def test_upload_invalid_file_type(self, client):
        """Test rejection of invalid file type."""
        # Try uploading .docx
        # Assert 400 status
        # Assert error message explains issue
    
    async def test_upload_file_too_large(self, client):
        """Test file size limit enforcement."""
        # Create file > 10MB
        # Assert 413 status
```

### Frontend Testing Approach

**Component Tests**:
```typescript
describe('ResumeUpload', () => {
  it('renders upload zone', () => {
    // Render component
    // Assert "Drag and drop" text visible
  });
  
  it('handles file drop', async () => {
    // Simulate file drop
    // Assert API called with file
    // Assert success state shown
  });
  
  it('shows error for invalid file', () => {
    // Drop .docx file
    // Assert error message displayed
  });
});
```

---

## 🚀 Deployment Checklist

### Pre-Deployment

**Backend:**
- [ ] All tests passing (>80% coverage)
- [ ] No linting errors (ruff, mypy)
- [ ] Environment variables documented
- [ ] Database migrations tested
- [ ] API documentation updated
- [ ] Error logging configured
- [ ] Rate limiting implemented
- [ ] Security headers set

**Frontend:**
- [ ] Build succeeds without warnings
- [ ] All TypeScript errors resolved
- [ ] Environment variables set
- [ ] API endpoints configured for production
- [ ] Analytics integrated (optional)
- [ ] Error tracking configured
- [ ] Performance optimized (Lighthouse score >90)

### Production Environment Variables

**Backend (.env.production):**
```env
DEBUG=false
DATABASE_URL=postgresql://user:pass@host:5432/dbname
GROQ_API_KEY=prod_key_here
GITHUB_TOKEN=prod_token_here
ALLOWED_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn
```

**Frontend (.env.production):**
```env
VITE_API_URL=https://api.yourdomain.com
VITE_ENVIRONMENT=production
```

### Docker Deployment

**Recommended setup:**
- Use Docker Compose for orchestration
- Separate containers for: backend, frontend, database
- Use environment-specific compose files
- Implement health checks
- Set resource limits
- Use volumes for persistent data
- Configure restart policies

---

## 📖 Final Documentation Requirements

### README.md Structure

```markdown
# AI Internship Resume Structuring Agent

[Project logo/banner]

## Overview
Brief description of what the project does and why it's useful.

## Features
- ✨ Feature 1
- ✨ Feature 2
- ✨ Feature 3

## Tech Stack
### Backend
- FastAPI
- Groq API (Llama 3.1)
- SQLAlchemy
- ...

### Frontend  
- React + TypeScript
- Tailwind CSS
- shadcn/ui
- ...

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Groq API key

### Installation
[Step-by-step instructions]

### Running Locally
[Commands to start dev servers]

## Architecture
[Diagram or explanation of system design]

## API Documentation
Link to Swagger/ReDoc

## Contributing
Guidelines for contributors

## License
MIT License

## Contact
Your information
```

### API Documentation

Auto-generated with FastAPI but enhance with:
- Endpoint descriptions
- Request/response examples
- Error code explanations
- Rate limit information
- Authentication details (if applicable)

---

## 🎓 Learning Outcomes

By completing this project, you will demonstrate:

**Technical Skills:**
- Full-stack development (FastAPI + React)
- LLM integration and prompt engineering
- Database design and ORM usage
- API design and documentation
- File processing and text extraction
- Type-safe programming (Python + TypeScript)
- Testing and quality assurance
-