# AI Travel Agent

An intelligent, AI-powered travel assistant that helps users explore destinations, plan trips, and manage travel-related documents seamlessly through conversational AI and interactive maps.

## Features

- **Conversational AI with Gemini API**  
  Engage with a real-time chat assistant that understands your travel preferences and provides personalized recommendations.

- **Interactive Maps with Plotly & Mapbox**  
  Explore and mark travel destinations visually. The AI suggests locations and marks them directly on the map for easy itinerary planning.

- **Parallel Function Calling**  
  Efficiently handles multiple user requests and map interactions simultaneously to improve responsiveness and user experience.

- **PDF & Receipt Uploads**  
  Analyze uploaded trip documents such as itineraries, receipts, or tickets. Automatically extract key information and perform calculations (e.g., budget tracking).

- **Reusable & Modular Components**  
  Built with clean, reusable classes and functions, allowing easy customization and scalability for future travel features.

## Tech Stack

- **Backend:** FastAPI, Python  
- **Frontend:** Streamlit
- **AI API:** Gemini API by Google for conversational intelligence  
- **Data Processing:** PDF parsing, NLP for document understanding  

## Getting Started

### Prerequisites

- Python 3.8+
- Access to Gemini API credentials
- Docker (optional for containerized setup)

### Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/yourusername/ai-travel-agent.git
   cd ai-travel-agent
