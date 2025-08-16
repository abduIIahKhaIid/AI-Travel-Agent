# 🌍 AI Travel Assistant

An intelligent travel assistant powered by Google's Gemini API with advanced function calling capabilities for interactive map display.

## ✨ Features

### 🤖 AI-Powered Travel Assistance
- **Gemini API Integration**: Powered by Google's latest Gemini 1.5 Flash model
- **Function Calling**: Automatically displays maps when discussing travel destinations
- **Context-Aware**: Remembers conversation history and uploaded documents
- **Travel-Focused**: Specialized in travel-related queries only

### 🗺️ Interactive Map Display
- **Automatic Map Generation**: Gemini automatically calls the `show_map` function when locations are mentioned
- **Real-time Geocoding**: Converts location names to coordinates using OpenStreetMap
- **Interactive Markers**: Clickable markers with location information and descriptions
- **Sidebar Integration**: Maps are displayed in the sidebar for better space utilization
- **Customizable Zoom**: Adjustable map zoom levels for optimal viewing

### 📄 Document Analysis
- **PDF Expense Reports**: Upload and analyze travel expense documents
- **Smart Context**: AI uses uploaded documents to provide personalized travel advice
- **Budget Insights**: Get travel budgeting recommendations based on your expenses
- **File Icons**: Uploaded files are displayed with icons and file size information

### 🔍 Enhanced User Experience
- **Clean Sidebar Layout**: Organized sidebar with file uploads, maps, and controls
- **Visual Separators**: Clear sections with dividers for better organization
- **Welcome Message**: Helpful introduction for new users
- **Conversation Memory**: Full conversation history is maintained and sent to Gemini
- **Responsive Design**: Better use of screen space with sidebar map integration

## 🚀 Getting Started

### Prerequisites
- Python 3.12 or higher
- Google Gemini API key
- Internet connection for geocoding and API calls

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_travel_agent
   ```

2. **Set up environment**
   ```bash
   # Create virtual environment
   uv venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
 
   # using uv:
   uv sync
   ```

4. **Set up API key**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

5. **Run the application**
   ```bash
   streamlit run main.py
   ```

## 🔧 How Function Calling Works

### The `show_map` Function

When you ask Gemini about travel destinations, it automatically calls the `show_map` function with location data:

```json
{
  "name": "show_map",
  "parameters": {
    "locations": [
      {
        "name": "Paris",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "description": "Capital of France, known for art and culture"
      }
    ],
    "zoom_level": 12
  }
}
```

### Example Conversations

**User**: "Show me a map of Paris, France"

**Gemini**: *Automatically calls show_map function and displays Paris on the map*

**User**: "I want to visit Tokyo and Kyoto in Japan"

**Gemini**: *Calls show_map function with both cities and shows them on the map*

## 📱 Usage Examples

### Basic Travel Queries
- "What are the best places to visit in Europe?"
- "Show me popular destinations in Asia"
- "I'm planning a trip to New York, what should I see?"

### Map-Related Queries
- "Display Paris on a map"
- "Show me the locations of London and Paris"
- "Can you map out a route from Tokyo to Kyoto?"

### Expense Analysis
- Upload PDF expense reports
- Ask: "Analyze my travel expenses and suggest a budget for my next trip"

## 🛠️ Technical Details

### Dependencies
- `google-generativeai`: Gemini API integration
- `folium`: Interactive map generation
- `streamlit`: Web application framework
- `requests`: HTTP requests for geocoding
- `PyPDF2`: PDF text extraction

### Architecture
- **Frontend**: Streamlit web interface
- **AI Backend**: Gemini API with function calling
- **Mapping**: Folium maps with OpenStreetMap tiles
- **Geocoding**: Nominatim (OpenStreetMap) service

### Function Calling Flow
1. User asks about travel destinations
2. Gemini analyzes the request
3. If locations are mentioned, Gemini calls `show_map` function
4. Function generates interactive map with markers
5. Map is displayed in the Streamlit interface



## 🔒 Security & Privacy

- API keys are stored in environment variables
- No location data is stored permanently
- Uses open-source geocoding services
- All data processing happens locally

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:
1. Check your API key is correctly set
2. Ensure all dependencies are installed
3. Verify internet connection for geocoding
4. Check the console for error messages

## 🔮 Future Enhancements

- [ ] Route planning between multiple locations
- [ ] Integration with travel booking APIs
- [ ] Weather information overlay on maps
- [ ] Offline map support
- [ ] Multi-language support
- [ ] Travel itinerary generation
