import google.generativeai as genai
from typing import List
import json
import os
from dotenv import load_dotenv

class AIService:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            raise Exception("Gemini API key not configured. Please set GEMINI_API_KEY in .env file.")

    def enhance_content(self, idea: str, add_emojis: bool = False, variations: int = 3) -> List[str]:
        if not self.model:
            raise Exception("Gemini API key not configured")

        emoji_instruction = "Include relevant professional emojis strategically." if add_emojis else "Do not use any emojis."

        prompt = f"Transform this idea into {variations} different professional LinkedIn posts:\n\n" \
                 f"Idea: {idea}\n\nRequirements:\n" \
                 f"- Elaborate with industry insights and practical examples\n" \
                 f"- Maintain authentic, conversational tone\n" \
                 f"- Keep each version 150-300 words\n" \
                 f"- Add relevant hashtags (3-5 per post)\n" \
                 f"- {emoji_instruction}\n" \
                 f"- Make each variation unique in style\n\n" \
                 f"Return ONLY a JSON array:\n" \
                 f'[{{"version": 1, "content": "post text"}}, {{"version": 2, "content": "post text"}}]'

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            triple_backticks = "```"
            if result_text.startswith(triple_backticks):
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1])
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()

            posts = json.loads(result_text)
            return [post['content'] for post in posts]

        except json.JSONDecodeError:
            return [response.text]
        except Exception as e:
            raise Exception(f"AI enhancement failed: {str(e)}")

    def summarize_resource(self, text: str) -> str:
        if not self.model:
            return "Summary unavailable - API key not configured"

        prompt = f"Summarize in 2-3 sentences for a tech professional:\n\n{text[:2000]}"

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return "Summary unavailable"

    def score_relevance(self, resource: dict, interests: List[str]) -> float:
        if not self.model:
            return 5.0

        prompt = f"Rate 0-10 relevance for developer interested in: {', '.join(interests)}\n\n" \
                 f"Resource: {resource['title']}\nDescription: {resource.get('summary', '')}\n\n" \
                 f"Return ONLY a number 0-10."

        try:
            response = self.model.generate_content(prompt)
            score = float(response.text.strip())
            return min(max(score, 0), 10)
        except:
            return 5.0

    def generate_post_series(self, topic: str, num_posts: int, add_emojis: bool = True) -> List[dict]:
        """Generate a series of posts for a topic (e.g., 10-day Python Mastery series)"""
        if not self.model:
            raise Exception("Gemini API key not configured")

        emoji_instruction = "Include relevant professional emojis strategically." if add_emojis else "Do not use any emojis."

        # Generate in batches if num_posts > 5 to avoid token limits
        all_posts = []
        batch_size = 5  # Generate max 5 posts at a time
        
        for batch_num in range(0, num_posts, batch_size):
            posts_in_batch = min(batch_size, num_posts - batch_num)
            start_day = batch_num + 1
            
            prompt = f"""Create {posts_in_batch} LinkedIn posts for a series about: {topic}

    This is part of a {num_posts}-post series. Generate posts for Day {start_day} to Day {start_day + posts_in_batch - 1}.

    Requirements:
    - Each post should be 150-300 words
    - Include practical examples and code snippets where relevant
- Add relevant hashtags (3-5 per post)
- {emoji_instruction}
- Make posts progress from beginner to intermediate concepts

CRITICAL: Return ONLY valid JSON array, no markdown, no extra text.
Format:
[
  {{"day": {start_day}, "title": "Topic Title", "content": "Full post text..."}},
  {{"day": {start_day + 1}, "title": "Next Topic", "content": "Full post text..."}}
]"""

            try:
                # Configure generation for JSON output
                generation_config = {
                    "temperature": 0.8,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                result_text = response.text.strip()

                # Clean markdown code blocks if present
                triple_backticks = "```"
                if result_text.startswith(triple_backticks):
                    lines = result_text.split('\n')
                    result_text = '\n'.join(lines[1:-1])
                    if result_text.startswith('json'):
                        result_text = result_text[4:].strip()

                # Additional cleanup
                result_text = result_text.replace(',]', ']').replace(',}', '}')
                
                # Try to parse JSON
                batch_posts = json.loads(result_text)
                
                # Validate structure
                if isinstance(batch_posts, list):
                    for post in batch_posts:
                        if all(key in post for key in ['day', 'title', 'content']):
                            all_posts.append(post)
                
            except Exception as e:
                # If batch fails, create placeholder posts
                for i in range(posts_in_batch):
                    day_num = start_day + i
                    all_posts.append({
                        "day": day_num,
                        "title": f"Python Concept {day_num}",
                        "content": f"[Placeholder] Post content for day {day_num} about {topic}. Please regenerate this post."
                    })
        
        # Sort by day number and return
        all_posts.sort(key=lambda x: x.get('day', 0))
        return all_posts[:num_posts]  # Ensure we return exactly num_posts



    def score_slideshare_relevance(self, resource: dict, user_topics: List[str]) -> float:
        """Score SlideShare presentation relevance based on user topics"""
        if not self.model:
            return 7.0
        
        prompt = f"""Rate the relevance (0-10) of this SlideShare presentation for someone interested in: {', '.join(user_topics)}

    Presentation Title: {resource['title']}
    Search Query: {resource.get('search_query', '')}
    Description: {resource.get('summary', '')}

    Consider:
    - How well does the title match the user's interests?
    - Is this a high-quality educational resource?
    - Would this be valuable for a software developer/tech professional?

    Return ONLY a number between 0-10."""

        try:
            response = self.model.generate_content(prompt)
            score = float(response.text.strip())
            return min(max(score, 0), 10)
        except:
            return 7.0

    def generate_pdf_post_draft(self, resource: dict) -> str:
        """Generate LinkedIn post draft for SlideShare PDF resource"""
        if not self.model:
            raise Exception("Gemini API key not configured")
        
        prompt = f"""Create a professional LinkedIn post to share this SlideShare presentation:

    Title: {resource['title']}
    Topic: {resource.get('search_query', 'Technology')}
    Source: SlideShare
    URL: {resource['url']}

    Requirements:
    - Start with an attention-grabbing hook (question or bold statement)
    - Explain why this resource is valuable (2-3 key learning points)
    - Mention it's from SlideShare and FREE to access
    - Include a call-to-action to check it out
    - Add 5-6 relevant hashtags
    - Use 2-3 professional emojis strategically
    - Keep it 150-250 words
    - Make it engaging and conversational

    Return ONLY the post text, no formatting or extra text."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Fallback
            return f"""📚 Resource Alert!

    Just discovered this gem on SlideShare: "{resource['title']}"

    Perfect for anyone diving into {resource.get('search_query', 'tech')}! This presentation breaks down complex concepts into digestible insights. 🚀

    ✅ Free access
    ✅ Visual learning
    ✅ Expert knowledge

    Check it out: {resource['url']}

    What resources have you found useful lately? Drop them below! 👇

    #{resource.get('search_query', 'Tech').replace(' ', '')} #Learning #TechResources #SlideShare #ContinuousLearning #SoftwareDevelopment"""
