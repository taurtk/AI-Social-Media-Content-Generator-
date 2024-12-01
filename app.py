import http.client
import json
import re
import streamlit as st
from langchain_groq import ChatGroq

class ContentFeedAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = ChatGroq(model="gemma2-9b-it", temperature=0.6, api_key=self.api_key)

    def is_url_accessible(self, url):
        """Check if the given URL is accessible."""
        parsed_url = re.match(r'https?://([^/]+)(.*)', url)
        if not parsed_url:
            st.error("Invalid URL format.")
            return False

        host = parsed_url.group(1)
        path = parsed_url.group(2) or "/"

        try:
            conn = http.client.HTTPSConnection(host)
            conn.request("GET", path)
            res = conn.getresponse()
            return res.status == 200  # Return True if accessible
        except Exception as e:
            st.error(f"Error checking URL accessibility: {e}")
            return False

    def search_similar_content(self, content_link):
        """Search for similar content using Serper API."""
        # Validate the content link before making an API call
        

        serper_api_key = "7c748181570a86f0b2f5d26c92dd4c92ad35e7ae"  # Replace with your actual Serper API key
        headers = {"Authorization": f"Bearer {serper_api_key}"}

        try:
            conn = http.client.HTTPSConnection("api.serper.dev")
            conn.request("GET", f"/search?url={content_link}", headers=headers)
            res = conn.getresponse()

            

            data = res.read()
            response_data = json.loads(data.decode("utf-8"))
            return [result['link'] for result in response_data.get('organic_results', [])]

        except Exception as e:
            st.error(f"Error fetching similar content: {e}")
            return []

    def process_content_feed(self, content_link, post_frequency, tone_description):
        """Process the content feed and generate social media posts."""
        similar_content_links = self.search_similar_content(content_link)

        prompt = f"""
        Content Feed URL/Text: {content_link}

        Similar Content Links: {', '.join(similar_content_links) if similar_content_links else 'None'}

        Generate social media posts based on the following guidelines:
        - Posting Frequency: {post_frequency}
        - Desired Tone: {tone_description}
        - Platform: Twitter/X
        - Character Limit: 280 characters

        Requirements:
        1. Create diverse, engaging posts that reflect the source content
        2. Use appropriate hashtags
        3. Maintain a consistent brand voice
        4. Ensure posts are original and not direct copies

        Generate 10 sample posts that could be automatically shared:
        """

        try:
            response = self.llm.invoke(prompt)
            generated_posts = response.content if hasattr(response, 'content') else str(response)
            return generated_posts
        except Exception as e:
            st.error(f"Error generating posts: {e}")
            return None

def main():
    st.title("🤖 AI Social Media Content Generator")

    # API Key Input
    api_key = st.text_input("Enter Groq API Key", type="password")

    # Content Feed Input
    content_link = st.text_input("Enter Content Feed Link or Text")

    # Posting Frequency
    post_frequency = st.selectbox(
        "Posting Frequency",
        ["Daily", "Every Other Day", "Weekly"]
    )

    # Tone Selection
    tone_description = st.text_area(
        "Describe the Tone of Your Posts",
        "Professional, informative, with a touch of humor and industry insights"
    )

    # Generate Posts Button
    if st.button("Generate AI Posts"):
        if not api_key:
            st.error("Please enter a valid API key")
            return

        if not content_link:
            st.error("Please provide a content feed link or text")
            return

        # Initialize Agents
        content_feed_agent = ContentFeedAgent(api_key)

        # Generate Posts
        generated_posts = content_feed_agent.process_content_feed(
            content_link,
            post_frequency,
            tone_description
        )

        # Display Generated Posts
        if generated_posts:
            st.subheader("🚀 Generated Social Media Posts")
            st.code(generated_posts)

            # Optional: Save to file with UTF-8 encoding
            with open('generated_posts.txt', 'w', encoding='utf-8') as f:
                f.write(generated_posts)
            st.success("Posts saved to generated_posts.txt")

if __name__ == "__main__":
    main()