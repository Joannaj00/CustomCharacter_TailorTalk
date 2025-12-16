# TailorTalk – Character Chat Module

This repository contains a minimal, self-contained version of the character conversation system I built for TailorTalk. The app allows writers to create detailed character profiles and have real-time conversations with those characters, powered by GPT-3.5 Turbo. Character information is saved per session, and the system maintains consistent behavior across dialogue turns.

## Demo Video


https://github.com/user-attachments/assets/b355bfdd-e285-42cf-a195-02125540ded9



## ✨ Features

### 1. Character Profile Builder
Users define:
- Name, job, age, location  
- Family and relationship details  
- Personality sliders (extroversion, tech-savviness, loyalty, etc.)  
- Additional custom traits  

All fields are integrated into the LLM prompt to create a rich, personalized character.

### 2. LLM-Driven Conversation
- Conversations use **GPT-3.5 Turbo**  
- The system uses a structured system prompt built from the character profile  
- Each message updates session history  
- The model responds *as the character*, maintaining consistent voice and personality

### 3. Session-Based Dialogue Memory
Conversations persist across turns using:
- A `session_id`
- SQLAlchemy conversation table  
- Stored user messages + assistant responses  
- Automatic reload of previous turns to preserve context

## 🏗️ Tech Stack

- **Flask** for backend routes  
- **SQLAlchemy + SQLite** for persistent conversation history  
- **HTML, CSS, JavaScript** for frontend UI  
- **OpenAI GPT-3.5 Turbo** for character dialogue  
- **Python** for application logic  
