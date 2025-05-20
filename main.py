import os
import time
import PyPDF2
import folium
import streamlit as st
from pathlib import Path
from streamlit_folium import folium_static
from dotenv import load_dotenv, find_dotenv
from google.generativeai import GenerativeModel, configure

# Load environment variables
_: bool = load_dotenv(find_dotenv())

# Get the Gemini API key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")

# If API key is not found, show error and stop execution
if not API_KEY:
    st.error("⚠️ API Key is missing! Set GEMINI_API_KEY in your environment.")
    st.stop()

configure(api_key=API_KEY)

system_instructions: str = """
You are an AI Travel Assistant. Your sole purpose is to assist users with travel-related queries. 

🔹 **Allowed Topics:**
- Travel destinations, tourist attractions, and itineraries
- Flights, hotels, accommodations, and transportation
- Budgeting and expense management for trips
- Visa, travel documents, and customs regulations
- Best times to visit specific locations
- Packing tips, safety advice, and cultural insights
- Local food, festivals, and activities

🚫 **Strictly Prohibited Topics:**
- Any topic unrelated to travel (e.g., politics, finance, health, coding, etc.)
- Personal opinions, emotional support, or philosophical discussions
- Legal, medical, or business consulting services
- Any controversial, unethical, or speculative topics
- Avoid discussing unrelated topics.

💡 **Behavior Guidelines:**
- If a user asks a **non-travel-related** question, politely redirect them:
  - Example: "I specialize in travel assistance! How can I help with your trip planning?"
- Keep responses **concise, factual, and helpful**.
- Never make up information; use general travel knowledge.
- Ensure clarity and **avoid ambiguity** in recommendations.
- Always respond in an **engaging and friendly tone**.

🎯 **Special Features:**
- If the user provides an **expense report (PDF)**, analyze it and offer relevant travel budgeting advice.
- If the user asks about **popular destinations**, suggest places with their coordinates for mapping.
- Keep track of **previous user interactions** to ensure a smooth conversation.
- Keep responses concise and informative.

"""
model = GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=system_instructions,
)

# 🔄 Session State Initialization (Prevents Flickering)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "travel_locations" not in st.session_state:
    st.session_state.travel_locations = []
if "map_initialized" not in st.session_state:
    st.session_state.map_initialized = False


# 📄 Extract Text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        extracted_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
        return extracted_text.strip()
    except Exception:
        return None


# 🌍 Streamlit UI
st.set_page_config(page_title="AI Travel Assistant", layout="wide")
st.title("🌍 AI Travel Assistant")

# 📂 Sidebar - File Upload
st.sidebar.header("📄 Upload Expense Reports")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDFs", type=["pdf"], accept_multiple_files=True
)

# 🔄 Reset Chat Button
if st.sidebar.button("🔄 Reset Chat"):
    st.session_state.chat_history = []
    st.session_state.travel_locations = []
    st.session_state.map_initialized = False
    st.sidebar.success("✅ Chat reset successfully!")
    st.rerun()

# Process Uploaded PDFs (Persisted in session_state)
for uploaded_file in uploaded_files:
    if uploaded_file.name not in st.session_state.user_data:
        extracted_text = extract_text_from_pdf(uploaded_file)
        if extracted_text:
            st.session_state.user_data[uploaded_file.name] = extracted_text
            st.sidebar.success(f"✅ {uploaded_file.name} uploaded!")

# 🧠 Chat Display
st.subheader("💬 Chat with AI")

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["message"])

# 💬 Handle User Input
user_input = st.chat_input("Ask about travel expenses, destinations, etc.")

if user_input:
    st.session_state.chat_history.append({"role": "user", "message": user_input})

    # Prepare prompt
    combined_prompt = "\n".join(
        [
            f"{msg['role'].capitalize()}: {msg['message']}"
            for msg in st.session_state.chat_history
        ]
    )

    if st.session_state.user_data:
        uploaded_texts = "\n".join(st.session_state.user_data.values())
        combined_prompt += f"\nUser uploaded details:\n{uploaded_texts}"

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("⏳ Generate text..."):
            placeholder = st.empty()
            response_text = ""

            # 🔥 Stream AI response with smooth effect (No Flickering)
            for chunk in model.generate_content(combined_prompt, stream=True):
                for char in chunk.text:
                    response_text += char
                    placeholder.markdown(response_text + " ▌")  # Blinking cursor effect
                    time.sleep(0.02)

            # 🛑 Remove cursor after final response
            placeholder.markdown(response_text)

            st.session_state.chat_history.append(
                {"role": "assistant", "message": response_text}
            )

# 🗺️ Suggested Travel Locations
travel_db = {
    "Paris": [48.8566, 2.3522],
    "New York": [40.7128, -74.0060],
    "Tokyo": [35.682839, 139.759455],
    "London": [51.5074, -0.1278],
    "Dubai": [25.276987, 55.296249],
}

# Extract New Locations from AI Response (Prevent Duplicates)
new_locations = [
    (city, coords)
    for city, coords in travel_db.items()
    if any(
        city.lower() in msg["message"].lower()
        for msg in st.session_state.chat_history
        if msg["role"] == "assistant"
    )
]

for city, coords in new_locations:
    if (city, coords) not in st.session_state.travel_locations:
        st.session_state.travel_locations.append((city, coords))
        st.session_state.map_initialized = False  # Trigger map update

# Display Map if Locations Exist
if st.session_state.travel_locations:
    st.subheader("📍 Suggested Travel Locations")

    # 🔥 FIX: Only Update Map if a New Location is Added
    if not st.session_state.map_initialized:
        first_location = st.session_state.travel_locations[0][1]
        m = folium.Map(location=first_location, zoom_start=4, width="100%", height=400)

        for city, coords in st.session_state.travel_locations:
            folium.Marker(coords, tooltip=city, icon=folium.Icon(color="blue")).add_to(
                m
            )

        st.session_state.map_initialized = True  # Mark as initialized
        folium_static(m, width=450, height=300)  # Bigger display
