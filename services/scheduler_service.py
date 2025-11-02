from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class SchedulerService:
    """Background job scheduler"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone='Asia/Kolkata')
        self._running = False
        # Initialize Google Sheets client
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        self.client = gspread.authorize(creds)
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs"""
        
        # Daily post job - 9 AM
        self.scheduler.add_job(
            self._publish_scheduled_post,
            CronTrigger(hour=9, minute=0),
            id='daily_post',
            name='Daily LinkedIn Post',
            replace_existing=True
        )
        
        # Daily curation job - 8 AM
        self.scheduler.add_job(
            self._run_curation,
            CronTrigger(hour=8, minute=0),
            id='daily_curation',
            name='Daily Resource Curation',
            replace_existing=True
        )
    
    def _publish_scheduled_post(self):
        """Publish next scheduled post"""
        
        try:
            posts_sheet = self.client.open("LinkedIn_Posts").worksheet("posts")
            posts_df = pd.DataFrame(posts_sheet.get_all_records())
            
            # Get next pending post
            pending = posts_df[posts_df['status'] == 'pending']
            if len(pending) == 0:
                return
            
            pending['scheduled_date'] = pd.to_datetime(pending['scheduled_date'])
            pending = pending.sort_values('scheduled_date')
            next_post = pending.iloc[0]
            
            # Check if it's time to post
            now = datetime.now()
            scheduled = next_post['scheduled_date']
            
            if scheduled <= now:
                # Post to LinkedIn
                from services.linkedin_service import LinkedInService
                linkedin = LinkedInService()
                
                post_url = linkedin.create_post(
                    content=next_post['content'],
                    image_url=next_post['image_url'] if next_post['image_url'] else None
                )
                
                # Update status
                posts_df.loc[posts_df['id'] == next_post['id'], 'status'] = 'published'
                posts_df.loc[posts_df['id'] == next_post['id'], 'post_url'] = post_url
                posts_df.loc[posts_df['id'] == next_post['id'], 'published_at'] = now.isoformat()
                
                # Update Google Sheet
                posts_sheet.clear()
                posts_sheet.append_row(list(posts_df.columns))
                for _, row in posts_df.iterrows():
                    posts_sheet.append_row([str(v) for v in row.values])
                
                # Send notification
                self._send_notification(f"✅ Post published: {next_post['topic']}")
        
        except Exception as e:
            print(f"Error publishing post: {e}")
    
    def _run_curation(self):
        """Run resource curation"""
        
        try:
            from services.curation_service import CurationService
            curator = CurationService()
            
            resources = curator.curate_resources()
            
            self._send_notification(f"📚 Curated {len(resources)} new resources")
        
        except Exception as e:
            print(f"Error running curation: {e}")
    
    def _send_notification(self, message: str):
        """Send Telegram notification"""
        
        try:
            from services.notification_service import NotificationService
            notif = NotificationService()
            notif.send_message(message)
        except:
            pass
    
    def start(self):
        """Start scheduler"""
        if not self._running:
            self.scheduler.start()
            self._running = True
    
    def stop(self):
        """Stop scheduler"""
        if self._running:
            self.scheduler.shutdown()
            self._running = False
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self._running
    
    def get_next_run_time(self, job_id: str):
        """Get next run time for job"""
        job = self.scheduler.get_job(job_id)
        return job.next_run_time if job else None
    
    def update_schedule(self, job_id: str, hour: int, minute: int):
        """Update job schedule"""
        self.scheduler.reschedule_job(
            job_id,
            trigger=CronTrigger(hour=hour, minute=minute)
        )