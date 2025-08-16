import os
import time
import PyPDF2
import folium
import streamlit as st
from pathlib import Path
from streamlit_folium import folium_static
from dotenv import load_dotenv, find_dotenv
from google.generativeai import GenerativeModel, configure
import json
import requests

# ----------------------------
#  Environment
# ----------------------------


_: bool = load_dotenv(find_dotenv())

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ API Key is missing! Set GEMINI_API_KEY in your environment.")
    st.stop()

configure(api_key=API_KEY)



# ----------------------------
#  System Instructions
# ----------------------------

system_instructions: str = """
You are an AI Travel Assistant. Your sole purpose is to assist users with travel-related queries. 

🔹 Allowed Topics:
- Travel destinations, tourist attractions, and itineraries
- Flights, hotels, accommodations, and transportation
- Budgeting and expense management for trips
- Visa, travel documents, and customs regulations
- Best times to visit specific locations
- Packing tips, safety advice, and cultural insights
- Local food, festivals, and activities

🚫 Strictly Prohibited Topics:
- Any topic unrelated to travel (e.g., politics, finance, coding, etc.)
- Personal opinions, emotional support, or philosophical discussions
- Legal, medical, or business consulting services
- Any controversial, unethical, or speculative topics

💡 Behavior Guidelines:
- If a user asks a non-travel-related question, politely redirect them.
- Keep responses concise, factual, and helpful.
- Never make up information; use general travel knowledge.
- Always respond in an engaging and friendly tone.

🗺️ IMPORTANT: When discussing travel destinations, cities, countries, or specific locations:
- ALWAYS use the show_map function to display locations on a map
- Send location names as simple strings in the locations array
- Examples: locations=["Paris", "Tokyo", "New York"]
- The function will automatically find coordinates and create the map
- Use this for ANY location discussion: "Show me Paris", "Tell me about Tokyo", "What's in New York?"

🎯 Special Features:
- If the user provides an expense report (PDF), analyze it and offer relevant travel budgeting advice.
- If the user asks about popular destinations, suggest places and ALWAYS show them on the map using the show_map function.
- Keep track of previous user interactions naturally.
"""

# ----------------------------
#  Function Definitions
# ----------------------------

functions = [
    {
        "function_declarations": [
            {
                "name": "show_map",
                "description": "Display a map with travel locations and attractions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "locations": {
                            "type": "array",
                            "description": "List of location names to show on the map (can be city names, country names, etc.)",
                            "items": {
                                "type": "string",
                                "description": "Name of the location (e.g., 'Paris', 'Tokyo', 'New York')"
                            }
                        },
                        "zoom_level": {
                            "type": "integer",
                            "description": "Map zoom level (1-18)"
                        }
                    },
                    "required": ["locations"]
                }
            }
        ]
    }
]

model = GenerativeModel(
    "gemini-2.0-flash",
    system_instruction=system_instructions,
)

# ----------------------------
#  Session State
# ----------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "map_data" not in st.session_state:
    st.session_state.map_data = None
if "map_initialized" not in st.session_state:
    st.session_state.map_initialized = False
if "notifications" not in st.session_state:
    st.session_state.notifications = []


# ----------------------------
#  Helper Functions
# ----------------------------

def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        extracted_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
        return extracted_text.strip()
    except Exception:
        return None

def geocode_location(location_name):
    """Geocode a location name to get coordinates"""
    try:
        # Using Nominatim (OpenStreetMap) for geocoding
        url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
        response = requests.get(url, headers={'User-Agent': 'AI-Travel-Assistant/1.0'})
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        st.warning(f"Could not geocode {location_name}: {str(e)}")
    return None

def extract_locations_from_text(text):
    """Extract potential location names from text"""
    import re
    
    # Common location patterns
    location_patterns = [
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:City|Town|Village|Airport|Station|Hotel|Restaurant|Museum|Park|Beach|Mountain|Island|Country|State|Province|Region)\b',
        r'\b(?:Paris|London|Tokyo|New York|Los Angeles|Chicago|Miami|San Francisco|Toronto|Vancouver|Sydney|Melbourne|Brisbane|Perth|Adelaide|Hobart|Darwin|Canberra|Brisbane|Gold Coast|Sunshine Coast|Townsville|Cairns|Toowoomba|Rockhampton|Mackay|Bundaberg|Hervey Bay|Gladstone|Maryborough|Gympie|Nambour|Caloundra|Maroochydore|Noosa|Bribie Island|Moreton Island|Fraser Island|Whitsunday Islands|Great Barrier Reef|Uluru|Kakadu|Kings Canyon|Litchfield|Nitmiluk|Katherine Gorge|Kakadu|Litchfield|Nitmiluk|Katherine Gorge)\b',
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|Avenue|Road|Boulevard|Drive|Lane|Way|Place|Court|Terrace|Highway|Freeway|Expressway|Bridge|Tunnel|Plaza|Square|Circle|Park|Garden|Reserve|Beach|Bay|Harbor|Port|Airport|Station|Terminal|Center|Mall|Market|Shop|Store|Restaurant|Cafe|Bar|Hotel|Motel|Resort|Villa|Apartment|House|Building|Tower|Skyscraper|Monument|Statue|Fountain|Clock|Bell|Flag|Banner|Sign|Poster|Billboard|Screen|Display|Show|Exhibition|Gallery|Museum|Library|School|University|College|Hospital|Clinic|Office|Factory|Warehouse|Depot|Yard|Lot|Field|Farm|Ranch|Vineyard|Orchard|Garden|Park|Forest|Jungle|Desert|Mountain|Hill|Valley|Canyon|Gorge|Cave|Waterfall|River|Lake|Ocean|Sea|Gulf|Bay|Harbor|Port|Island|Peninsula|Cape|Point|Beach|Shore|Coast|Border|Boundary|Limit|Edge|Corner|Side|Face|Surface|Top|Bottom|Front|Back|Left|Right|North|South|East|West|Center|Middle|Half|Quarter|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\b'
    ]
    
    locations = []
    for pattern in location_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match.strip()) > 2:  # Filter out very short matches
                locations.append(match.strip())
    
    # Remove duplicates and return
    return list(set(locations))

def show_map_function(locations, zoom_level=10):
    """Create and display a map with the given locations"""
    try:
        # Debug: Show what we received
        # st.toast(f"Creating map for locations: {locations}")
        
        # Create a map centered on the first location or default to world view
        if locations and len(locations) > 0:
            # Get coordinates from the first location
            first_location = locations[0]
            if isinstance(first_location, dict):
                lat = first_location.get('latitude', 0)
                lon = first_location.get('longitude', 0)
            else:
                # If it's just a string location name, try to geocode it
                coords = geocode_location(str(first_location))
                if coords:
                    lat, lon = coords
                else:
                    lat, lon = 0, 0
        else:
            lat, lon = 0, 0
        
        # st.toast(f"Map center: {lat}, {lon}")
        
        # Create the map
        map_obj = folium.Map(location=[lat, lon], zoom_start=zoom_level)
        
        # Add markers for all locations
        for location in locations:
            if isinstance(location, dict):
                name = location.get('name', 'Unknown')
                lat = location.get('latitude', 0)
                lon = location.get('longitude', 0)
                desc = location.get('description', '')
            else:
                # If it's just a string, try to geocode it
                name = str(location)
                coords = geocode_location(name)
                if coords:
                    lat, lon = coords
                    desc = 'Location from conversation'
                else:
                    continue
            
            # Add marker to map
            folium.Marker(
                [lat, lon],
                popup=f"<b>{name}</b><br>{desc}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(map_obj)
        
        
        # Store map in session state
        st.session_state.map_data = map_obj
        st.session_state.map_initialized = True
        
        st.toast(f"Map created with {len(locations)} location(s) successfully", icon="🌍")

        return f"Map created with {len(locations)} location(s)"
        
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return f"Error creating map: {str(e)}"

# ----------------------------
#  UI
# ----------------------------

st.set_page_config(page_title="AI Travel Assistant", layout="wide")
st.title("🌍 AI Travel Assistant")

# 📂 Sidebar - File Upload and Map
with st.sidebar:
    st.header("📄 Upload Files")
    
    # Simple file upload
    uploaded_files = st.file_uploader(
        "Choose PDF files", 
        type=["pdf"], 
        accept_multiple_files=True,
        help="Upload your travel expense reports"
    )
    
    # Simple status with clean display
    new_files = []

    if uploaded_files:
        for f in uploaded_files:
            if f.name not in st.session_state.user_data:
                new_files.append(f)
        

    st.markdown("---")
    
    # Simple reset button
    if st.button("🔄 Reset Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.map_data = None
        st.session_state.map_initialized = False
        st.session_state.user_data = {}
        st.rerun()
    
    st.markdown("---")
    
    # 🗺️ Map Display - Only show when map is generated
    if st.session_state.map_data and st.session_state.map_initialized:
        st.header("🗺️ Travel Map")
        
        
        
        # Display the map
        try:
            folium_static(st.session_state.map_data, width=400, height=400)
            
            # Clear button below map
            if st.button("🗑️ Clear Map", use_container_width=True):
                st.session_state.map_data = None
                st.session_state.map_initialized = False
                st.rerun()
                
        except Exception as e:
            st.error(f"Map display error: {str(e)}")


for f in new_files:
    st.toast(f"{f.name} uploaded successfully", icon="✅")


# ----------------------------
#  Process Uploaded PDFs
# ----------------------------

if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.user_data:
            extracted_text = extract_text_from_pdf(uploaded_file)
            if extracted_text:
                st.session_state.user_data[uploaded_file.name] = extracted_text
                

# ----------------------------
#  Chat Display
# ----------------------------

# Simple header
st.subheader("💬 AI Travel Assistant")

# Display chat history
if st.session_state.chat_history:
    for idx, chat in enumerate(st.session_state.chat_history):
        with st.chat_message(chat["role"]):
            st.write(chat["message"])
else:
    st.info("👋 Welcome! Ask me about travel destinations, upload expense reports, or get travel advice. I can show you maps of locations we discuss!")

# ----------------------------
#  Handle User Input
# ----------------------------

user_input = st.chat_input("Ask about travel destinations, expenses, etc.")

if user_input:
    # Store user message
    st.session_state.chat_history.append({"role": "user", "message": user_input})

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # Add uploaded PDFs as context if available
    if st.session_state.user_data:
        context_info = "\n".join(st.session_state.user_data.values())
        user_input += f"\n\nHere are my uploaded expense details:\n{context_info}"

    # Generate AI response with function calling
    function_called = False
    
    response_text = ""
    with st.chat_message("assistant"):
        placeholder = st.empty()

        try:
            chat = model.start_chat(history=[
                {"role": "user" if msg["role"]=="user" else "model",
                "parts": [{"text": msg["message"]}]}
                    for msg in st.session_state.chat_history[:-1]
                ])

                # --- STREAMING RESPONSE ---
            response_stream = chat.send_message(user_input, tools=functions, stream=True)

            for chunk in response_stream:
                if chunk.candidates:
                    candidate = chunk.candidates[0]
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text += part.text
                                placeholder.markdown(response_text)
                            elif hasattr(part, 'function_call') and part.function_call:
                                # If Gemini triggers map creation
                                args = (part.function_call.args if hasattr(part.function_call.args, 'get')
                                        else json.loads(part.function_call.args))
                                locations = args.get("locations", [])
                                zoom_level = args.get("zoom_level", 10)
                                processed_locations = []
                                for loc in locations:
                                    coords = geocode_location(str(loc))
                                    if coords:
                                        processed_locations.append({
                                            "name": str(loc),
                                            "latitude": coords[0],
                                            "longitude": coords[1],
                                            "description": "Location from conversation"
                                        })
                                if processed_locations:
                                    placeholder.markdown(response_text)
                                    # Save assistant reply
                                    st.session_state.chat_history.append(
                                        {"role": "assistant", "message": response_text}
                                    )
                                    show_map_function(processed_locations, zoom_level)
                                    time.sleep(0.5)
                                    st.rerun()
            
        except Exception as e:
            response_text = f"Error: {str(e)}"
            placeholder.error(response_text)

    if not function_called:
        st.session_state.chat_history.append(
            {"role": "assistant", "message": response_text}
        )
