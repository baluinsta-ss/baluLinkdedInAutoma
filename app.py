import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import os
import time
import random


# Page config
st.set_page_config(
    page_title="LinkedIn Automation Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Google Sheets setup with validation and retry logic
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
except FileNotFoundError:
    st.error("❌ credentials.json not found. Please place it in the project directory.")
    st.stop()
except Exception as e:
    st.error(f"❌ Failed to authenticate with Google Sheets: {str(e)}")
    st.stop()


# Initialize Google Sheets with reduced API calls and retry
def init_sheets():
    """Initialize Google Sheets with minimal API calls and retry on quota errors"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Posts Sheet
            try:
                posts_sheet = client.open("LinkedIn_Posts").worksheet("posts")
            except gspread.exceptions.SpreadsheetNotFound:
                posts_sheet = client.create("LinkedIn_Posts").add_worksheet("posts", 1, 10)
                posts_sheet.append_row([
                    'id', 'series', 'topic', 'content', 'status',
                    'scheduled_date', 'image_url', 'post_url',
                    'created_at', 'published_at'
                ])
            except gspread.exceptions.APIError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    st.warning(f"Quota exceeded. Retrying in {wait_time:.1f} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                raise
            else:
                headers = ['id', 'series', 'topic', 'content', 'status',
                          'scheduled_date', 'image_url', 'post_url',
                          'created_at', 'published_at']
                if not posts_sheet.get_all_values():
                    posts_sheet.clear()
                    posts_sheet.append_row(headers)


            # Resources Sheet
            try:
                resources_sheet = client.open("LinkedIn_Resources").worksheet("resources")
            except gspread.exceptions.SpreadsheetNotFound:
                resources_sheet = client.create("LinkedIn_Resources").add_worksheet("resources", 1, 8)
                resources_sheet.append_row([
                    'id', 'title', 'url', 'resource_type', 'source',
                    'summary', 'relevance_score', 'created_at'
                ])
            except gspread.exceptions.APIError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    st.warning(f"Quota exceeded. Retrying in {wait_time:.1f} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                raise
            else:
                headers = ['id', 'title', 'url', 'resource_type', 'source',
                          'summary', 'relevance_score', 'created_at']
                if not resources_sheet.get_all_values():
                    resources_sheet.clear()
                    resources_sheet.append_row(headers)


            # Enhanced Content Sheet
            try:
                enhanced_sheet = client.open("LinkedIn_Enhanced_Content").worksheet("enhanced_content")
            except gspread.exceptions.SpreadsheetNotFound:
                enhanced_sheet = client.create("LinkedIn_Enhanced_Content").add_worksheet("enhanced_content", 1, 5)
                enhanced_sheet.append_row([
                    'id', 'original_idea', 'enhanced_versions',
                    'add_emojis', 'created_at'
                ])
            except gspread.exceptions.APIError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    st.warning(f"Quota exceeded. Retrying in {wait_time:.1f} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                raise
            else:
                headers = ['id', 'original_idea', 'enhanced_versions',
                          'add_emojis', 'created_at']
                if not enhanced_sheet.get_all_values():
                    enhanced_sheet.clear()
                    enhanced_sheet.append_row(headers)
            break
        except gspread.exceptions.APIError as e:
            if e.response.status_code == 429 and attempt == max_retries - 1:
                st.error(f"❌ Failed to initialize Google Sheets after {max_retries} attempts: Quota exceeded. Please wait and try again later.")
                st.stop()
            elif e.response.status_code != 429:
                st.error(f"❌ Failed to initialize Google Sheets: {str(e)}")
                st.stop()


init_sheets()


# Import services
from services.ai_service import AIService
from services.linkedin_service import LinkedInService
from services.curation_service import CurationService
from services.scheduler_service import SchedulerService


# Initialize session state
if 'ai_service' not in st.session_state:
    st.session_state.ai_service = AIService()
if 'linkedin_service' not in st.session_state:
    st.session_state.linkedin_service = LinkedInService()
if 'curation_service' not in st.session_state:
    st.session_state.curation_service = CurationService()
if 'scheduler_service' not in st.session_state:
    st.session_state.scheduler_service = SchedulerService()


# Sidebar Navigation
st.sidebar.title("🚀 LinkedIn Automation")
st.sidebar.markdown("---")


page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "✨ Content Enhancer", "📅 Post Scheduler", "📚 Resource Curator", "⚙️ Settings"]
)


st.sidebar.markdown("---")


# Scheduler status in sidebar
st.sidebar.subheader("⏰ Scheduler Status")
scheduler = st.session_state.scheduler_service


if st.sidebar.button("▶️ Start Scheduler" if not scheduler.is_running() else "⏸️ Stop Scheduler"):
    if scheduler.is_running():
        scheduler.stop()
        st.sidebar.success("Scheduler stopped")
    else:
        scheduler.start()
        st.sidebar.success("Scheduler started")


if scheduler.is_running():
    st.sidebar.success("✅ Running")
    next_post_time = scheduler.get_next_run_time('daily_post')
    next_curation_time = scheduler.get_next_run_time('daily_curation')
    if next_post_time:
        st.sidebar.info(f"Next Post: {next_post_time.strftime('%I:%M %p')}")
    if next_curation_time:
        st.sidebar.info(f"Next Curation: {next_curation_time.strftime('%I:%M %p')}")
else:
    st.sidebar.warning("⏸️ Stopped")


st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ using Streamlit")


# Helper function to convert sheet to DataFrame
def sheet_to_df(sheet):
    data = sheet.get_all_records()
    if not data:
        headers = sheet.row_values(1)
        if headers:
            return pd.DataFrame(columns=[h.strip() for h in headers])
        return pd.DataFrame()
    return pd.DataFrame(data)


# Helper function to append row to sheet with debugging
def append_to_sheet(sheet, row):
    try:
        sheet.append_row([str(v) for v in row.values])
        st.success("Row appended successfully!")
        data = sheet.get_all_records()
        # st.info(f"Sheet data after append: {data}")
    except Exception as e:
        st.error(f"Append failed: {str(e)}")


# Helper function to update sheet
def update_sheet(sheet, df):
    sheet.clear()
    sheet.append_row(list(df.columns))
    for _, row in df.iterrows():
        sheet.append_row([str(v) for v in row.values])


# ============================================================================
# PAGE: DASHBOARD
# ============================================================================
if page == "🏠 Dashboard":
    st.title("🏠 LinkedIn Automation Dashboard")
    st.markdown("### Your automation hub at a glance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    posts_sheet = client.open("LinkedIn_Posts").worksheet("posts")
    resources_sheet = client.open("LinkedIn_Resources").worksheet("resources")
    enhanced_sheet = client.open("LinkedIn_Enhanced_Content").worksheet("enhanced_content")
    
    posts_df = sheet_to_df(posts_sheet)
    resources_df = sheet_to_df(resources_sheet)
    enhanced_df = sheet_to_df(enhanced_sheet)
    
    with col1:
        pending_posts = len(posts_df[posts_df['status'] == 'pending']) if not posts_df.empty and 'status' in posts_df.columns else 0
        st.metric("📝 Pending Posts", pending_posts)
    with col2:
        published_posts = len(posts_df[posts_df['status'] == 'published']) if not posts_df.empty and 'status' in posts_df.columns else 0
        st.metric("✅ Published Posts", published_posts)
    with col3:
        curated_resources = len(resources_df) if not resources_df.empty else 0
        st.metric("📚 Curated Resources", curated_resources)
    with col4:
        enhanced_content = len(enhanced_df) if not enhanced_df.empty else 0
        st.metric("✨ Enhanced Content", enhanced_content)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📅 Upcoming Posts")
        if not posts_df.empty and 'status' in posts_df.columns and 'scheduled_date' in posts_df.columns:
            upcoming = posts_df[posts_df['status'] == 'pending'].head(5)
            if len(upcoming) > 0:
                for _, post in upcoming.iterrows():
                    with st.expander(f"📌 {post['topic']}", expanded=False):
                        st.write(f"**Series:** {post['series']}")
                        st.write(f"**Scheduled:** {post['scheduled_date']}")
                        st.write(f"**Content Preview:** {post['content'][:200] + '...'}")
            else:
                st.info("No upcoming posts. Create some in the Post Scheduler!")
        else:
            st.info("No posts yet. Get started in the Post Scheduler!")
    with col2:
        st.subheader("📚 Recent Resources")
        if not resources_df.empty and 'created_at' in resources_df.columns:
            recent = resources_df.sort_values('created_at', ascending=False).head(5)
            for _, resource in recent.iterrows():
                with st.expander(f"🔗 {resource['title']}", expanded=False):
                    st.write(f"**Type:** {resource['resource_type']}")
                    st.write(f"**Source:** {resource['source']}")
                    st.write(f"**Relevance Score:** {resource['relevance_score']}/10")
                    st.write(f"**URL:** [{resource['url']}]({resource['url']})")
                    if pd.notna(resource['summary']):
                        st.write(f"**Summary:** {resource['summary']}")
        else:
            st.info("No resources yet. Start curating in the Resource Curator!")


# ============================================================================
# PAGE: CONTENT ENHANCER
# ============================================================================
elif page == "✨ Content Enhancer":
    st.title("✨ Content Enhancer")
    st.markdown("### Transform your ideas into professional LinkedIn posts")
    
    with st.form("enhance_form"):
        idea = st.text_area("💡 Your Idea or Source", placeholder="Example: I learned about FastAPI async endpoints today...", height=150)
        col1, col2 = st.columns(2)
        with col1:
            add_emojis = st.checkbox("Add Professional Emojis", value=True)
        with col2:
            variations = st.slider("Number of Variations", 1, 5, 3)
        submitted = st.form_submit_button("✨ Enhance Content", use_container_width=True)
    
    if submitted and idea:
        with st.spinner("🤖 AI is enhancing your content..."):
            try:
                enhanced_versions = st.session_state.ai_service.enhance_content(idea=idea, add_emojis=add_emojis, variations=variations)
                enhanced_sheet = client.open("LinkedIn_Enhanced_Content").worksheet("enhanced_content")
                enhanced_df = sheet_to_df(enhanced_sheet)
                new_id = len(enhanced_df) + 1 if not enhanced_df.empty else 1
                new_row = pd.DataFrame([{
                    'id': new_id,
                    'original_idea': idea,
                    'enhanced_versions': json.dumps(enhanced_versions),
                    'add_emojis': add_emojis,
                    'created_at': datetime.now().isoformat()
                }])
                append_to_sheet(enhanced_sheet, new_row.iloc[0])
                st.success("✅ Content enhanced successfully!")
                st.markdown("---")
                for i, version in enumerate(enhanced_versions, 1):
                    with st.expander(f"📝 Version {i}", expanded=(i == 1)):
                        st.markdown(version)
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if st.button(f"📋 Copy Version {i}", key=f"copy_{i}"):
                                st.code(version, language=None)
                        with col2:
                            if st.button(f"➕ Add to Queue", key=f"add_{i}"):
                                posts_sheet = client.open("LinkedIn_Posts").worksheet("posts")
                                posts_df = sheet_to_df(posts_sheet)
                                new_post_id = len(posts_df) + 1 if not posts_df.empty else 1
                                new_post = pd.DataFrame([{
                                    'id': new_post_id,
                                    'series': 'Enhanced Content',
                                    'topic': idea[:50] + "...",
                                    'content': version,
                                    'status': 'pending',
                                    'scheduled_date': (datetime.now() + timedelta(days=1)).isoformat(),
                                    'image_url': '',
                                    'post_url': '',
                                    'created_at': datetime.now().isoformat(),
                                    'published_at': ''
                                }])
                                append_to_sheet(posts_sheet, new_post.iloc[0])
                                st.success(f"✅ Version {i} added to post queue!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    st.subheader("📜 Enhancement History")
    enhanced_sheet = client.open("LinkedIn_Enhanced_Content").worksheet("enhanced_content")
    enhanced_df = sheet_to_df(enhanced_sheet)
    if not enhanced_df.empty and 'created_at' in enhanced_df.columns:
        enhanced_df['created_at'] = pd.to_datetime(enhanced_df['created_at'])
        enhanced_df = enhanced_df.sort_values('created_at', ascending=False)
        for _, row in enhanced_df.head(10).iterrows():
            with st.expander(f"💡 {row['original_idea'][:60]}... - {row['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                st.write("**Original Idea:**")
                st.info(row['original_idea'])
                versions = json.loads(row['enhanced_versions'])
                st.write(f"**Generated {len(versions)} versions** (Emojis: {'✅' if row['add_emojis'] else '❌'})")
    else:
        st.info("No enhancement history yet.")


# ============================================================================
# PAGE: POST SCHEDULER
# ============================================================================
elif page == "📅 Post Scheduler":
    st.title("📅 LinkedIn Post Scheduler")
    st.markdown("### Schedule and manage your LinkedIn posts")
    
    tab1, tab2, tab3, tab4 = st.tabs(["✍️ Manual Post", "🤖 AI Auto-Generate", "📋 Post Queue", "📊 Analytics"])
    
    # ============================================================================
    # TAB 1: MANUAL POST
    # ============================================================================
    with tab1:
        st.subheader("Create Post Manually")

        with st.form("manual_post_form"):
            series = st.text_input("📚 Series Name", placeholder="Python Mastery, Daily Tips, etc.")
            topic = st.text_input("📝 Topic", placeholder="Day 1: List Comprehensions")
            content = st.text_area("✍️ Content", height=200,
                                   placeholder="Write your LinkedIn post here...")
            
            col1, col2 = st.columns(2)
            with col1:
                scheduled_date = st.date_input("📅 Schedule Date",
                                              value=datetime.now() + timedelta(days=1))
            with col2:
                scheduled_time = st.time_input("⏰ Schedule Time",
                                              value=datetime.now().replace(hour=9, minute=0))
            
            # Image upload
            uploaded_image = st.file_uploader("🖼️ Upload Image (Optional)", type=["png", "jpg", "jpeg"])

            col_btn1, col_btn2 = st.columns([1, 1])  # ✅ CORRECT
            submit_queue = col_btn1.form_submit_button("➕ Add to Queue", use_container_width=True)
            submit_instant = col_btn2.form_submit_button("🚀 Post Instantly", use_container_width=True)

        # Handle image upload
        image_path = None
        if uploaded_image is not None:
            temp_dir = "temp_images"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            image_path = os.path.join(temp_dir, uploaded_image.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
            st.info(f"📸 Image '{uploaded_image.name}' ready")

        # ADD TO QUEUE
        if submit_queue and series and topic and content:
            posts_sheet = client.open("LinkedIn_Posts").worksheet("posts")
            posts_df = sheet_to_df(posts_sheet)
            new_id = len(posts_df) + 1 if not posts_df.empty else 1

            scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)

            new_post = pd.DataFrame([{
                'id': new_id,
                'series': series,
                'topic': topic,
                'content': content,
                'status': 'pending',
                'scheduled_date': scheduled_datetime.isoformat(),
                'image_url': image_path if image_path else '',
                'post_url': '',
                'created_at': datetime.now().isoformat(),
                'published_at': ''
            }])

            append_to_sheet(posts_sheet, new_post.iloc)
            st.success(f"✅ Post added to queue! Scheduled for {scheduled_datetime.strftime('%Y-%m-%d %I:%M %p')}")
            st.balloons()

        # POST INSTANTLY
        if submit_instant and topic and content:
            with st.spinner("Opening browser and posting…"):
                try:
                    post_url = st.session_state.linkedin_service.create_post(
                        content=content,
                        image_url=image_path
                    )
                    
                    now_iso = datetime.now().isoformat()
                    
                    if "failed" in post_url.lower() or "error" in post_url.lower() or "draft" in post_url.lower():
                        status = "failed"
                        st.error("❌ Posting failed or saved as draft.")
                    else:
                        status = "published"
                        st.success(f"✅ Posted instantly!")
                        st.balloons()
                    
                    posts_sheet = client.open("LinkedIn_Posts").worksheet("posts")
                    posts_df = sheet_to_df(posts_sheet)
                    new_id = len(posts_df) + 1 if not posts_df.empty else 1
                    
                    new_row = pd.DataFrame([{
                        'id': new_id,
                        'series': series,
                        'topic': topic,
                        'content': content,
                        'status': status,
                        'scheduled_date': now_iso,
                        'image_url': image_path if image_path else '',
                        'post_url': post_url,
                        'created_at': now_iso,
                        'published_at': now_iso if status == "published" else ''
                    }])
                    
                    append_to_sheet(posts_sheet, new_row.iloc)
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    # ============================================================================
    # TAB 2: AI AUTO-GENERATE
    # ============================================================================
    with tab2:
        st.subheader("🤖 AI Auto-Generate Post Series")
        st.markdown("Generate multiple posts automatically and schedule them")

        with st.form("ai_auto_generate_form"):
            ai_series_name = st.text_input("📚 Series Name", 
                                        placeholder="Python Mastery, JavaScript Tips, etc.",
                                        value="Python Mastery")
            
            ai_topic = st.text_area("📝 Topic/Theme", 
                                placeholder="Python intermediate concepts, FastAPI basics, etc.",
                                height=100,
                                value="Python intermediate programming concepts")
            
            col1, col2 = st.columns(2)
            with col1:
                num_posts = st.slider("📊 Number of Posts", min_value=1, max_value=30, value=10)
                add_emojis = st.checkbox("✨ Add Professional Emojis", value=True)
            
            with col2:
                start_date = st.date_input("📅 Start Date", value=datetime.now() + timedelta(days=1))
                post_time = st.time_input("⏰ Daily Post Time", value=datetime.now().replace(hour=9, minute=0))
            
            st.markdown("---")
            st.info(f"💡 This will generate **{num_posts} posts** starting from **{start_date.strftime('%B %d, %Y')}** at **{post_time.strftime('%I:%M %p')}** daily")
            
            generate_button = st.form_submit_button("🤖 Generate Series", use_container_width=True, type="primary")

        # Generate posts when button is clicked
        if generate_button and ai_series_name and ai_topic:
            with st.spinner(f"🤖 AI is generating {num_posts} posts about '{ai_topic}'... This may take 30-60 seconds..."):
                try:
                    # Generate posts using AI
                    generated_posts = st.session_state.ai_service.generate_post_series(
                        topic=ai_topic,
                        num_posts=num_posts,
                        add_emojis=add_emojis
                    )
                    
                    st.success(f"✅ Generated {len(generated_posts)} posts!")
                    
                    # Store generated posts in session state
                    st.session_state['generated_posts'] = generated_posts
                    st.session_state['ai_series_name'] = ai_series_name
                    st.session_state['start_date'] = start_date
                    st.session_state['post_time'] = post_time
                    
                except Exception as e:
                    st.error(f"❌ AI generation failed: {e}")

        # Display generated posts for review
        if 'generated_posts' in st.session_state:
            st.markdown("---")
            st.subheader("📝 Generated Posts - Review Before Scheduling")
            
            generated_posts = st.session_state['generated_posts']
            ai_series_name = st.session_state['ai_series_name']
            start_date = st.session_state['start_date']
            post_time = st.session_state['post_time']
            
            # Display each post in a nice card format
            for i, post in enumerate(generated_posts):
                scheduled_date = start_date + timedelta(days=i)
                scheduled_datetime = datetime.combine(scheduled_date, post_time)
                
                with st.expander(
                    f"📅 Day {post.get('day', i+1)}: {post.get('title', 'Untitled')} "
                    f"(Scheduled: {scheduled_datetime.strftime('%b %d at %I:%M %p')})",
                    expanded=(i == 0)  # Expand first post by default
                ):
                    st.markdown(f"**Series:** {ai_series_name}")
                    st.markdown(f"**Post Date:** {scheduled_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}")
                    st.markdown("**Content:**")
                    st.text_area(
                        label="Post Content",
                        value=post['content'],
                        height=200,
                        key=f"generated_post_{i}",
                        label_visibility="collapsed"
                    )
                    
                    # Character count
                    char_count = len(post['content'])
                    if char_count > 3000:
                        st.warning(f"⚠️ Post is {char_count} characters (LinkedIn limit is 3000)")
                    else:
                        st.info(f"✅ {char_count} characters")
            
            st.markdown("---")
            
            # Action buttons
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])  # ✅ CORRECT
            
            with col1:
                if st.button("✅ Schedule All Posts to Queue", use_container_width=True, type="primary"):
                    with st.spinner("Scheduling all posts..."):
                        try:
                            posts_sheet = client.open("LinkedIn_Posts").worksheet("posts")
                            posts_df = sheet_to_df(posts_sheet)
                            base_id = len(posts_df) + 1 if not posts_df.empty else 1
                            
                            scheduled_count = 0
                            for i, post in enumerate(generated_posts):
                                scheduled_date = start_date + timedelta(days=i)
                                scheduled_datetime = datetime.combine(scheduled_date, post_time)
                                
                                # Create new post row
                                new_post_data = {
                                    'id': base_id + i,
                                    'series': ai_series_name,
                                    'topic': f"Day {post.get('day', i+1)}: {post.get('title', 'Untitled')}",
                                    'content': post['content'],
                                    'status': 'pending',
                                    'scheduled_date': scheduled_datetime.isoformat(),
                                    'image_url': '',
                                    'post_url': '',
                                    'created_at': datetime.now().isoformat(),
                                    'published_at': ''
                                }
                                
                                # Append to sheet - FIXED: Use posts_sheet, not 'sheet'
                                try:
                                    posts_sheet.append_row([str(v) for v in new_post_data.values()])
                                    scheduled_count += 1
                                except Exception as append_error:
                                    st.error(f"Failed to schedule post {i+1}: {append_error}")
                            
                            if scheduled_count > 0:
                                st.success(f"✅ Successfully scheduled {scheduled_count}/{len(generated_posts)} posts!")
                                st.balloons()
                                
                                # Clear session state
                                del st.session_state['generated_posts']
                                del st.session_state['ai_series_name']
                                del st.session_state['start_date']
                                del st.session_state['post_time']
                                
                                time.sleep(2)  # Brief pause before rerun
                                st.rerun()
                            else:
                                st.error("❌ Failed to schedule any posts. Check the errors above.")
                                
                        except Exception as e:
                            st.error(f"❌ Scheduling failed: {str(e)}")

                        
            with col2:
                if st.button("💾 Save as Draft", use_container_width=True):
                    with st.spinner("Saving as drafts..."):
                        try:
                            posts_sheet = client.open("LinkedIn_Posts").worksheet("posts")
                            posts_df = sheet_to_df(posts_sheet)
                            base_id = len(posts_df) + 1 if not posts_df.empty else 1
                            
                            saved_count = 0
                            for i, post in enumerate(generated_posts):
                                new_draft_data = {
                                    'id': base_id + i,
                                    'series': ai_series_name,
                                    'topic': f"Day {post.get('day', i+1)}: {post.get('title', 'Untitled')}",
                                    'content': post['content'],
                                    'status': 'draft',
                                    'scheduled_date': '',
                                    'image_url': '',
                                    'post_url': '',
                                    'created_at': datetime.now().isoformat(),
                                    'published_at': ''
                                }
                                
                                try:
                                    posts_sheet.append_row([str(v) for v in new_draft_data.values()])
                                    saved_count += 1
                                except Exception as append_error:
                                    st.error(f"Failed to save draft {i+1}: {append_error}")
                            
                            if saved_count > 0:
                                st.success(f"✅ Saved {saved_count}/{len(generated_posts)} posts as drafts!")
                                
                                # Clear session state
                                del st.session_state['generated_posts']
                                del st.session_state['ai_series_name']
                                del st.session_state['start_date']
                                del st.session_state['post_time']
                                
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Failed to save any drafts.")
                                
                        except Exception as e:
                            st.error(f"❌ Save failed: {str(e)}")

            with col3:
                if st.button("🔄 Regenerate", use_container_width=True):
                    del st.session_state['generated_posts']
                    st.rerun()

            with col4:
                if st.button("❌ Cancel", use_container_width=True):
                    del st.session_state['generated_posts']
                    del st.session_state['ai_series_name']
                    del st.session_state['start_date']
                    del st.session_state['post_time']
                    st.rerun()

                    # ============================================================================
                    # TAB 3: POST QUEUE (same as before)
                    # ============================================================================
                    # TAB 3: POST QUEUE
                    with tab3:
                        st.subheader("Post Queue Management")
                        posts_sheet = client.open("LinkedIn_Posts").worksheet("posts")
                        posts_df = sheet_to_df(posts_sheet)
                        
                        if not posts_df.empty and 'status' in posts_df.columns and 'scheduled_date' in posts_df.columns:
                            # Add "draft" to filter options
                            status_filter = st.selectbox("Filter by Status", ["All", "pending", "draft", "published", "failed"])
                            
                            if status_filter != "All":
                                filtered_df = posts_df[posts_df['status'] == status_filter]
                            else:
                                filtered_df = posts_df
                            
                            filtered_df['scheduled_date'] = pd.to_datetime(filtered_df['scheduled_date'], errors='coerce')
                            filtered_df = filtered_df.sort_values('scheduled_date')
                            
                            st.write(f"**Total Posts:** {len(filtered_df)}")
                            
                            # Show counts by status
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                pending_count = len(posts_df[posts_df['status'] == 'pending'])
                                st.metric("⏳ Pending", pending_count)
                            with col2:
                                draft_count = len(posts_df[posts_df['status'] == 'draft'])
                                st.metric("📝 Drafts", draft_count)
                            with col3:
                                published_count = len(posts_df[posts_df['status'] == 'published'])
                                st.metric("✅ Published", published_count)
                            with col4:
                                failed_count = len(posts_df[posts_df['status'] == 'failed'])
                                st.metric("❌ Failed", failed_count)
                            
                            st.markdown("---")
                            
                            for index, post in filtered_df.iterrows():
                                # Status emojis
                                status_emoji = {
                                    'pending': '⏳',
                                    'draft': '📝',
                                    'published': '✅',
                                    'failed': '❌'
                                }.get(post['status'], '📄')
                                
                                # Show scheduled date or "No date" for drafts
                                date_str = post['scheduled_date'].strftime('%Y-%m-%d %I:%M %p') if pd.notna(post['scheduled_date']) else 'No date set'
                                
                                with st.expander(f"{status_emoji} {post['topic']} - {date_str}"):
                                    st.write(f"**Series:** {post['series']}")
                                    st.write(f"**Status:** {post['status'].upper()}")
                                    if pd.notna(post['scheduled_date']):
                                        st.write(f"**Scheduled:** {post['scheduled_date'].strftime('%Y-%m-%d %I:%M %p')}")
                                    
                                    st.markdown("**Content:**")
                                    st.text_area("", value=post['content'], height=150, key=f"content_{post['id']}", disabled=True)
                                    
                                    col1, col2 = st.columns([3, 1])
                                    with col2:
                                        # Show different buttons based on status
                                        if post['status'] in ['pending', 'draft']:
                                            if st.button("🚀 Post Now", key=f"post_now_{post['id']}"):
                                                with st.spinner("Publishing..."):
                                                    try:
                                                        post_url = st.session_state.linkedin_service.create_post(
                                                            content=post['content'],
                                                            image_url=post['image_url'] if post['image_url'] else None
                                                        )
                                                        posts_df.loc[posts_df['id'] == post['id'], 'status'] = 'published'
                                                        posts_df.loc[posts_df['id'] == post['id'], 'post_url'] = post_url
                                                        posts_df.loc[posts_df['id'] == post['id'], 'published_at'] = datetime.now().isoformat()
                                                        update_sheet(posts_sheet, posts_df)
                                                        st.success(f"✅ Published!")
                                                        st.rerun()
                                                    except Exception as e:
                                                        st.error(f"❌ Error: {str(e)}")
                                        
                                        if st.button("🗑️ Delete", key=f"delete_{post['id']}"):
                                            posts_df = posts_df[posts_df['id'] != post['id']]
                                            update_sheet(posts_sheet, posts_df)
                                            st.success("Deleted!")
                                            st.rerun()
                        else:
                            st.info("No posts in queue.")

                    # ============================================================================
                    # TAB 4: ANALYTICS (same as before)
                    # ============================================================================
                    with tab4:
                        st.subheader("Post Analytics")
                        posts_sheet = client.open("LinkedIn_Posts").worksheet("posts")
                        posts_df = sheet_to_df(posts_sheet)
                        
                        if not posts_df.empty and 'status' in posts_df.columns:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Posts", len(posts_df))
                            with col2:
                                published = len(posts_df[posts_df['status'] == 'published'])
                                st.metric("Published", published)
                            with col3:
                                pending = len(posts_df[posts_df['status'] == 'pending'])
                                st.metric("Pending", pending)
                            
                            if 'series' in posts_df.columns:
                                st.subheader("Posts by Series")
                                series_counts = posts_df['series'].value_counts()
                                st.bar_chart(series_counts)
                        else:
                            st.info("No data yet.")


# ============================================================================
# PAGE: RESOURCE CURATOR (SlideShare PDF)
# ============================================================================
elif page == "📚 Resource Curator":
    st.title("📚 SlideShare PDF Curator & Poster")
    st.markdown("### Find, download, and share SlideShare presentations")
    
    tab1, tab2 = st.tabs(["🔍 Search & Download", "📤 My Resources"])
    
    # ============================================================================
    # TAB 1: SEARCH & DOWNLOAD
    # ============================================================================
    with tab1:
        st.subheader("What topics are you looking for?")
            
        st.markdown("""
        Enter the topics you want to find **FREE PDFs** about. 
        I'll search Google Drive for publicly shared PDFs, download them, and generate LinkedIn post drafts! 🚀
        
        **Example topics:**
        - Python programming notes
        - Data structures interview prep
        - Web development tutorial
        - Machine learning basics
        - DSA placement notes
        """)
        # Topic input section
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("**Enter topics (one per line):**")
            topics_text = st.text_area(
                "Topics",
                placeholder="Example:\nPython automation\nFastAPI tutorial\nLinkedIn API\nN8N workflows\nWeb scraping",
                height=150,
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**Settings:**")
            max_per_topic = st.number_input(
                "Max results per topic",
                min_value=3,
                max_value=10,
                value=5
            )
            
            auto_post = st.checkbox("Auto-post top result", value=False)
        
        # Parse topics
        topics = [t.strip() for t in topics_text.split('\n') if t.strip()]
        
        if topics:
            st.success(f"✅ Found {len(topics)} topics to search")
            
            with st.expander("📋 Topics to search:", expanded=False):
                for i, topic in enumerate(topics, 1):
                    st.write(f"{i}. {topic}")
        
        # Search button
        if st.button("🚀 Search SlideShare & Download PDFs", type="primary", disabled=not topics):
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(progress, message):
                progress_bar.progress(progress)
                status_text.text(message)
            
            # Run curation
            with st.spinner("Searching SlideShare..."):
                try:
                    resources = st.session_state.curation_service.curate_resources_from_topics(
                        topics=topics,
                        max_per_topic=max_per_topic,
                        progress_callback=update_progress
                    )
                    
                    if resources:
                        st.balloons()
                        st.success(f"✅ Successfully downloaded {len(resources)} PDFs!")
                        
                        # Display results
                        st.subheader("📥 Downloaded Resources")
                        
                        for resource in resources:
                            with st.expander(f"📄 {resource['title']} (Score: {resource['relevance_score']:.1f}/10)"):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.write(f"**Topic:** {resource['search_query']}")
                                    st.write(f"**URL:** {resource['url']}")
                                    st.write(f"**PDF Path:** `{resource.get('local_pdf_path', 'N/A')}`")
                                    
                                    if resource.get('draft_post'):
                                        st.markdown("**📝 LinkedIn Draft Post:**")
                                        st.text_area(
                                            "Draft",
                                            value=resource['draft_post'],
                                            height=200,
                                            key=f"draft_{resource['title'][:20]}",
                                            label_visibility="collapsed"
                                        )
                                
                                with col2:
                                    if st.button("📤 Post Now", key=f"post_{resource['title'][:20]}"):
                                        with st.spinner("Posting to LinkedIn..."):
                                            try:
                                                if resource.get('local_pdf_path'):
                                                    post_url = st.session_state.linkedin_service.create_post_with_pdf(
                                                        content=resource['draft_post'],
                                                        pdf_path=resource['local_pdf_path']
                                                    )
                                                else:
                                                    post_url = st.session_state.linkedin_service.create_post(
                                                        content=resource['draft_post']
                                                    )
                                                
                                                st.success(f"✅ Posted! {post_url}")
                                            except Exception as e:
                                                st.error(f"❌ Failed: {e}")
                        
                        # Auto-post top result if enabled
                        if auto_post and resources:
                            st.info("🤖 Auto-posting top result...")
                            top_resource = resources[0]
                            try:
                                if top_resource.get('local_pdf_path'):
                                    post_url = st.session_state.linkedin_service.create_post_with_pdf(
                                        content=top_resource['draft_post'],
                                        pdf_path=top_resource.get('local_pdf_path', '')
                                    )
                                else:
                                    post_url = st.session_state.linkedin_service.create_post(
                                        content=top_resource['draft_post']
                                    )
                                st.success(f"✅ Auto-posted: {post_url}")
                            except Exception as e:
                                st.error(f"❌ Auto-post failed: {e}")
                    
                    else:
                        st.warning("⚠️ No resources found. Try different topics.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    # ============================================================================
    # TAB 2: MY RESOURCES
    # ============================================================================
    with tab2:
        st.subheader("📤 Previously Downloaded Resources")
        
        # Load from Google Sheets
        try:
            resources_sheet = client.open("LinkedIn_Resources").worksheet("resources")
            resources_df = sheet_to_df(resources_sheet)
            
            if not resources_df.empty:
                st.dataframe(resources_df[['title', 'search_query', 'relevance_score', 'download_status', 'created_at']])
                
                st.markdown("---")
                st.markdown("**Post a resource to LinkedIn:**")
                
                selected_title = st.selectbox(
                    "Select resource",
                    options=resources_df['title'].tolist()
                )
                
                if selected_title:
                    resource_row = resources_df[resources_df['title'] == selected_title].iloc[0]
                    
                    st.text_area(
                        "Draft Post",
                        value=resource_row.get('draft_post', ''),
                        height=200,
                        key="selected_draft"
                    )
                    
                    if st.button("📤 Post to LinkedIn"):
                        with st.spinner("Posting..."):
                            try:
                                if resource_row.get('local_pdf_path'):
                                    post_url = st.session_state.linkedin_service.create_post_with_pdf(
                                        content=resource_row['draft_post'],
                                        pdf_path=resource_row.get('local_pdf_path', '')
                                    )
                                else:
                                    post_url = st.session_state.linkedin_service.create_post(
                                        content=resource_row['draft_post']
                                    )
                                st.success(f"✅ Posted! {post_url}")
                            except Exception as e:
                                st.error(f"❌ Failed: {e}")
            else:
                st.info("No resources yet. Go to the Search tab to find some!")
                
        except Exception as e:
            st.error(f"❌ Error loading resources: {e}")

# ============================================================================
# PAGE: SETTINGS
# ============================================================================
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.markdown("### Configure your automation")
    
    tab1, tab2 = st.tabs(["🔑 API Keys", "📅 Schedule"])
    
    with tab1:
        st.subheader("API Configuration")
        with st.form("api_keys_form"):
            st.markdown("#### AI Services")
            gemini_key = st.text_input("Gemini API Key", type="password", value=os.getenv('GEMINI_API_KEY', ''))
            st.markdown("#### LinkedIn Credentials")
            linkedin_email = st.text_input("LinkedIn Email", value=os.getenv('LINKEDIN_EMAIL', ''))
            linkedin_password = st.text_input("LinkedIn Password", type="password", value=os.getenv('LINKEDIN_PASSWORD', ''))
            if st.form_submit_button("💾 Save Settings"):
                with open('.env', 'w') as f:
                    f.write(f"GEMINI_API_KEY={gemini_key}\n")
                    f.write(f"LINKEDIN_EMAIL={linkedin_email}\n")
                    f.write(f"LINKEDIN_PASSWORD={linkedin_password}\n")
                st.success("✅ Settings saved! Restart the app for changes to take effect.")
    
    with tab2:
        st.subheader("Automation Schedule")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📅 Post Schedule")
            post_hour = st.slider("Hour (24h)", 0, 23, 9, key="post_hour")
            post_minute = st.slider("Minute", 0, 59, 0, key="post_minute")
            st.info(f"Posts will be published daily at {post_hour:02d}:{post_minute:02d}")
        with col2:
            st.markdown("#### 📚 Curation Schedule")
            curation_hour = st.slider("Hour (24h)", 0, 23, 8, key="curation_hour")
            curation_minute = st.slider("Minute", 0, 59, 0, key="curation_minute")
            st.info(f"Curation will run daily at {curation_hour:02d}:{curation_minute:02d}")
        if st.button("💾 Update Schedule"):
            scheduler = st.session_state.scheduler_service
            scheduler.update_schedule('daily_post', post_hour, post_minute)
            scheduler.update_schedule('daily_curation', curation_hour, curation_minute)
            st.success("✅ Schedule updated!")
