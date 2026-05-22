"""
Reports & Analytics Manager
مدير التقارير والتحليلات
"""

from database import get_db, Campaign, CampaignRecipient, EmailOpen, Bounce, Unsubscribe, Contact
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy import func

class ReportsManager:
    """Generate comprehensive reports"""
    
    def get_daily_stats(self, days: int = 7) -> Dict:
        """Get daily statistics for last N days"""
        db = get_db()
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            daily_stats = []
            for i in range(days):
                date = since + timedelta(days=i)
                date_start = date.replace(hour=0, minute=0, second=0)
                date_end = date.replace(hour=23, minute=59, second=59)
                
                # Count opens for this day
                opens = db.query(EmailOpen).filter(
                    EmailOpen.opened_at >= date_start,
                    EmailOpen.opened_at <= date_end
                ).count()
                
                # Count bounces for this day
                bounces = db.query(Bounce).filter(
                    Bounce.bounced_at >= date_start,
                    Bounce.bounced_at <= date_end
                ).count()
                
                # Count unsubscribes for this day
                unsubscribes = db.query(Unsubscribe).filter(
                    Unsubscribe.unsubscribed_at >= date_start,
                    Unsubscribe.unsubscribed_at <= date_end
                ).count()
                
                daily_stats.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'opens': opens,
                    'bounces': bounces,
                    'unsubscribes': unsubscribes
                })
            
            return {'status': 'success', 'daily_stats': daily_stats}
        finally:
            db.close()
    
    def get_country_analytics(self) -> Dict:
        """Get analytics by country"""
        db = get_db()
        try:
            # Get opens by country
            country_stats = db.query(
                EmailOpen.country,
                func.count(EmailOpen.id).label('count')
            ).filter(
                EmailOpen.country.isnot(None)
            ).group_by(EmailOpen.country).all()
            
            country_data = {country: count for country, count in country_stats}
            
            return {'status': 'success', 'country_analytics': country_data}
        finally:
            db.close()
    
    def export_contacts_csv(self) -> str:
        """Export contacts to CSV format"""
        db = get_db()
        try:
            contacts = db.query(Contact).limit(10000).all()
            
            csv_lines = ["Email,First Name,Last Name,Phone,Status,Created"]
            for contact in contacts:
                csv_lines.append(
                    f"{contact.email},{contact.first_name or ''},{contact.last_name or ''},"
                    f"{contact.phone or ''},{contact.status},{contact.created_at or ''}"
                )
            
            return "\n".join(csv_lines)
        finally:
            db.close()
    
    def export_opens_csv(self, campaign_id: int = None) -> str:
        """Export email opens to CSV"""
        db = get_db()
        try:
            query = db.query(EmailOpen)
            if campaign_id:
                query = query.filter(EmailOpen.campaign_id == campaign_id)
            
            opens = query.all()
            
            csv_lines = ["Email,Campaign ID,Opened At,Open Count,IP Address,Country"]
            for open_record in opens:
                csv_lines.append(
                    f"{open_record.email},{open_record.campaign_id},"
                    f"{open_record.opened_at or ''},{open_record.open_count},"
                    f"{open_record.ip_address or ''},{open_record.country or ''}"
                )
            
            return "\n".join(csv_lines)
        finally:
            db.close()
    
    def export_clicks_csv(self, campaign_id: int = None) -> str:
        """Export clicks to CSV"""
        db = get_db()
        try:
            query = db.query(CampaignRecipient).filter(
                CampaignRecipient.click_count > 0
            )
            if campaign_id:
                query = query.filter(CampaignRecipient.campaign_id == campaign_id)
            
            recipients = query.all()
            
            csv_lines = ["Email,Campaign ID,Clicked At,Click Count"]
            for recipient in recipients:
                contact = recipient.contact
                csv_lines.append(
                    f"{contact.email},{recipient.campaign_id},"
                    f"{recipient.clicked_at or ''},{recipient.click_count}"
                )
            
            return "\n".join(csv_lines)
        finally:
            db.close()
    
    def get_comprehensive_report(self) -> Dict:
        """Get comprehensive report with all statistics"""
        db = get_db()
        try:
            # Overall stats
            total_contacts = db.query(Contact).count()
            active_contacts = db.query(Contact).filter(Contact.status == 'active').count()
            unsubscribed = db.query(Unsubscribe).count()
            bounced = db.query(Bounce).filter(Bounce.bounce_type == 'hard').count()
            
            # Campaign stats
            total_campaigns = db.query(Campaign).count()
            sent_campaigns = db.query(Campaign).filter(Campaign.status == 'sent').count()
            
            # Email stats
            total_sent = db.query(CampaignRecipient).filter(
                CampaignRecipient.status == 'sent'
            ).count()
            total_opens = db.query(EmailOpen).count()
            total_clicks = db.query(CampaignRecipient).filter(
                CampaignRecipient.click_count > 0
            ).count()
            
            # Calculate rates
            open_rate = (total_opens / total_sent * 100) if total_sent > 0 else 0
            click_rate = (total_clicks / total_sent * 100) if total_sent > 0 else 0
            bounce_rate = (bounced / total_sent * 100) if total_sent > 0 else 0
            unsubscribe_rate = (unsubscribed / total_sent * 100) if total_sent > 0 else 0
            
            return {
                'status': 'success',
                'contacts': {
                    'total': total_contacts,
                    'active': active_contacts,
                    'unsubscribed': unsubscribed,
                    'bounced': bounced
                },
                'campaigns': {
                    'total': total_campaigns,
                    'sent': sent_campaigns
                },
                'emails': {
                    'total_sent': total_sent,
                    'total_opens': total_opens,
                    'total_clicks': total_clicks,
                    'total_bounces': bounced,
                    'total_unsubscribes': unsubscribed
                },
                'rates': {
                    'open_rate': round(open_rate, 2),
                    'click_rate': round(click_rate, 2),
                    'bounce_rate': round(bounce_rate, 2),
                    'unsubscribe_rate': round(unsubscribe_rate, 2)
                }
            }
        finally:
            db.close()

