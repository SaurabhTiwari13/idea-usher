#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install requests beautifulsoup4


# In[2]:


pip install openai


# In[3]:


# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import openai 
import time

# Set OpenAI API key
openai.api_key = 'your_openai_api_key'

# Function to generate a personalized message using OpenAI's text generation
def generate_personalized_message(profile_data):
    # Construct prompt for the OpenAI API
    prompt = f"Generate a personalized connection request message for a LinkedIn profile. Profile details:\n{profile_data}"
    
    # Call OpenAI API for text generation
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
        n=1,
    )
    # Extract and return the generated message
    message = response['choices'][0]['text'].strip()
    return message

# Function to log in to LinkedIn
def login_linkedin(username, password):
    # Define LinkedIn login URL and set headers
    login_url = "https://www.linkedin.com/login"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    # Create a session and initiate a GET request to the login page
    session = requests.Session()
    response = session.get(login_url, headers=headers)
    
    # Parse the response to extract CSRF token
    soup = BeautifulSoup(response.content, "html.parser")
    csrf_token = soup.find("input", {"name": "loginCsrfParam"}).get("value")

    # Construct login payload
    login_payload = {
        "session_key": username,
        "session_password": password,
        "loginCsrfParam": csrf_token,
    }

    # Perform POST request to log in
    session.post(login_url, data=login_payload, headers=headers)
    return session

# Function to retrieve new connections from a LinkedIn profile
def get_new_connections(session, competitor_profile_url):
    # Perform GET request to retrieve competitor's profile
    competitor_profile = session.get(competitor_profile_url)
    competitor_soup = BeautifulSoup(competitor_profile.content, "html.parser")

    # Extract connection elements from the HTML
    connection_elements = competitor_soup.find_all("li", class_="mn-connection-card")
    
    # Extract and return connection URLs
    new_connections = [connection.find("a")["href"] for connection in connection_elements]
    return new_connections

# Function to analyze a LinkedIn profile
def analyze_profile(session, connection_url):
    # Perform GET request to retrieve connection's profile
    connection_profile = session.get(connection_url)
    connection_soup = BeautifulSoup(connection_profile.content, "html.parser")

    # Extract 'About' section text
    about_section = connection_soup.find("section", class_="pv-about-section")
    about_text = about_section.find("p").text.strip() if about_section else "No 'About' section available."

    # Extract job description from 'Experience' section
    experience_section = connection_soup.find("section", class_="experience-section")
    job_description = experience_section.text.strip() if experience_section else "No job description available."

    # Extract recent posts from the 'Posts' section
    posts_section = connection_soup.find("section", class_="core-rail")
    recent_posts = [post.text.strip() for post in posts_section.find_all("div", class_="occludable-update")]

    # Return a dictionary with analyzed profile data
    return {
        "About": about_text,
        "Job Description": job_description,
        "Recent Posts": recent_posts,
    }

# Function to send a connection request on LinkedIn
def send_connection_request(session, connection_url, personalized_message):
    # Extract user's ID from the connection URL
    user_id = connection_url.split("/")[-1]

    # Construct URL for sending connection request
    connection_request_url = f"https://www.linkedin.com/voyager/api/relationships/connect?resId={user_id}"
    request_data = {
        'message': personalized_message,
        'trackingId': f'contact-{user_id}',
    }
    # Perform POST request to send the connection request
    session.post(connection_request_url, json=request_data)

# Example usage
competitor_username = "your_competitor_username"
competitor_password = "your_competitor_password"
competitor_profile_url = "https://www.linkedin.com/in/competitor_profile"

# Log in to LinkedIn using provided credentials
session = login_linkedin(competitor_username, competitor_password)

# Retrieve new connections from the competitor's profile
new_connections = get_new_connections(session, competitor_profile_url)

# Introduce a delay to avoid potential issues with LinkedIn's rate limiting
time.sleep(2)

# Iterate over new connections and perform analysis, generate personalized messages, and send connection requests
for connection_url in new_connections:
    # Analyze the profile of each connection
    profile_data = analyze_profile(session, connection_url)
    print(f"Analysis for {connection_url}:")
    print(profile_data)

    # Generate a personalized connection request message
    personalized_message = generate_personalized_message(profile_data)
    print(f"Generated Message: {personalized_message}")

    # Send the connection request with the personalized message
    send_connection_request(session, connection_url, personalized_message)
    print(f"Connection request sent to {connection_url} with the personalized message.")

