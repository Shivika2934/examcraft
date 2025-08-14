# Overview

The AI-Powered Digital Examination System is a comprehensive web-based platform built with Flask that leverages artificial intelligence for creating, managing, and evaluating digital exams. The system features role-based access control for administrators and students, AI-powered question generation using OpenAI's GPT-4o model, automated evaluation, real-time exam monitoring, and comprehensive analytics. The platform includes anti-cheat measures such as tab switching detection, question randomization per student, and session monitoring to ensure exam integrity.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
The application is built on Flask with SQLAlchemy for database operations using a declarative base model approach. The system follows a modular design with separate service layers for different functionalities:

- **Core Application**: Flask app with session management and database configuration
- **Authentication Service**: Replit OAuth integration with custom storage for user sessions and role-based access control
- **AI Service**: OpenAI GPT-4o integration for intelligent question generation with customizable parameters for subject, topic, difficulty, and question type
- **Exam Service**: Business logic for exam session management, question randomization, answer submission, and automated evaluation

## Database Architecture
The system uses SQLAlchemy ORM with the following core entities:
- **User Management**: User and OAuth tables (mandatory for Replit Auth) with role-based access (admin/student)
- **Content Management**: Subject, Exam, Question, ExamSession, and Answer tables with proper relationships
- **Session Tracking**: Exam sessions with timing, submission status, and scoring information

## Frontend Architecture  
The frontend uses Bootstrap with Replit's dark theme for consistent styling:
- **Responsive Design**: Mobile-friendly interface with Bootstrap grid system
- **Real-time Features**: JavaScript-based exam timer, progress tracking, and auto-save functionality
- **Template Structure**: Jinja2 templates with base template inheritance for consistent layout
- **Interactive Components**: Dynamic question navigation, timer warnings, and form validation

## Anti-Cheat and Security Measures
- **Session Security**: Browser session keys tied to OAuth tokens
- **Question Randomization**: Deterministic but unique question shuffling per student using seeded random generation
- **Client-side Monitoring**: Tab switching detection and session monitoring via JavaScript
- **Time Management**: Server-side time validation with automatic submission on timeout

## AI Integration Strategy
- **Question Generation**: OpenRouter API with GPT-4o model using structured prompts for creating multiple-choice questions
- **Content Customization**: Dynamic difficulty adjustment and topic-specific question creation
- **Quality Control**: Structured JSON response format with validation for consistency
- **Extensibility**: Framework ready for subjective answer evaluation and question variations
- **Provider Flexibility**: OpenRouter allows easy switching between different AI model providers

# External Dependencies

## Authentication Services
- **Replit OAuth**: Primary authentication provider with custom storage implementation
- **Flask-Login**: Session management and user authentication state handling

## AI and Machine Learning
- **OpenRouter API**: Unified access to multiple AI models including OpenAI's GPT-4o for intelligent question generation and content creation
- **Custom AI Service**: Wrapper service for OpenRouter integration with structured prompting and automatic model routing

## Database and Storage
- **SQLAlchemy**: ORM for database operations with declarative base model
- **Database**: Configurable via DATABASE_URL environment variable (supports PostgreSQL and other databases)

## Frontend Libraries
- **Bootstrap**: UI framework with Replit's dark theme for consistent styling
- **Feather Icons**: Icon library for modern, consistent iconography
- **Custom JavaScript**: Exam timer, navigation, and anti-cheat functionality

## Development and Deployment
- **Flask Framework**: Core web framework with WSGI application structure
- **Werkzeug ProxyFix**: For proper URL generation in deployed environments
- **Environment Configuration**: Uses environment variables for sensitive data and configuration

## Third-party Integrations
- **Mermaid**: For system architecture diagram rendering in documentation
- **jQuery/Vanilla JS**: For client-side interactivity and AJAX operations