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
