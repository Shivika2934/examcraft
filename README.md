https://cdad7ef9-7626-4c49-a658-e9416bb6b830-00-1uq08hnlem0q7.picard.replit.dev/
<img width="1377" height="534" alt="question2" src="https://github.com/user-attachments/assets/1b4593aa-0990-451c-973d-9790fc262958" />

<img width="1199" height="639" alt="image" src="https://github.com/user-attachments/assets/66efc807-7468-444d-91a1-4a5e7c0c09e8" />
student dashboard:
<img width="1194" height="623" alt="image" src="https://github.com/user-attachments/assets/db236e14-68d7-4bd6-906b-8016e234938a" />
<img width="1152" height="490" alt="image" src="https://github.com/user-attachments/assets/ced565e2-75e4-43f9-86d1-030db6fd145f" />

admin dashboard:
<img width="1156" height="541" alt="image" src="https://github.com/user-attachments/assets/5d925ff4-2751-4001-91cf-ccfca5a91443" />
<img width="1144" height="283" alt="image" src="https://github.com/user-attachments/assets/ab8eae4b-b1e5-40ac-bedd-4189c718c84e" />

# AI-Powered Digital Examination System

A comprehensive digital examination platform built with Flask that leverages AI for question generation, automated evaluation, and intelligent exam management.

## 🌟 Features

### Core Functionality
- **Role-based Authentication**: Separate interfaces for administrators and students using Replit OAuth
- **AI Question Generation**: Automatically generate unique questions using OpenAI's GPT-4o model
- **Exam Management**: Create, publish, and manage exams with flexible settings
- **Timed Examinations**: Built-in countdown timer with automatic submission
- **Anti-Cheat Measures**: Tab switching detection, question randomization, and session monitoring
- **Automated Evaluation**: Instant grading for multiple-choice questions
- **Comprehensive Analytics**: Detailed performance statistics and reporting

### Admin Features
- Create exams with AI-generated questions
- Subject and difficulty level management
- Question approval and review workflow
- Real-time exam monitoring
- Performance analytics and reporting
- Student result management

### Student Features
- Responsive exam interface
- Real-time timer with visual warnings
- Progress tracking and navigation
- Auto-save functionality
- Detailed result viewing
- Mobile-friendly design

### AI Integration
- **Question Generation**: Create contextually relevant questions based on subject and difficulty
- **Question Variations**: Generate multiple versions to prevent cheating
- **Content Adaptation**: Adjust difficulty and complexity automatically
- **Future Enhancement**: Subjective answer evaluation (framework ready)

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Web Interface - HTML/CSS/JS]
        B[Admin Dashboard]
        C[Student Exam Interface]
        D[Mobile Responsive UI]
    end
    
    subgraph "Authentication"
        E[Replit OAuth]
        F[Role-Based Access Control]
    end
    
    subgraph "Backend Services"
        G[Flask Application Server]
        H[Exam Management Service]
        I[AI Question Generator]
        J[Evaluation Engine]
        K[Timer & Anti-Cheat Service]
    end
    
    subgraph "AI Integration"
        L[OpenAI API]
        M[Question Generation]
        N[Answer Evaluation]
        O[Question Variations]
    end
    
    subgraph "Data Layer"
        P[SQLite Database]
        Q[User Management]
        R[Exam Storage]
        S[Results Analytics]
    end
    
    subgraph "Security & Integrity"
        T[Session Management]
        U[Question Randomization]
        V[Tab Switch Detection]
        W[Time Validation]
    end
