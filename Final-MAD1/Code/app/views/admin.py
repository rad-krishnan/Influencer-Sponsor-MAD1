from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Campaign, AdRequest
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch statistics for admin
    total_users = User.query.count()
    total_campaigns = Campaign.query.count()
    total_ad_requests = AdRequest.query.count()
    
    # Fetch all users, campaigns, and ad requests
    users = User.query.filter(User.id != current_user.id).all()  # Exclude current admin
    campaigns = Campaign.query.all()
    ad_requests = AdRequest.query.all()
    
    # Show flagged users or campaigns (filter example, assuming flag field exists)
    flagged_users = User.query.filter_by(flagged=True).all()
    flagged_campaigns = Campaign.query.filter_by(flagged=True).all()

    return render_template('admin/dashboard.html', total_users=total_users, total_campaigns=total_campaigns, total_ad_requests=total_ad_requests,
                           users=users, campaigns=campaigns, ad_requests=ad_requests,
                           flagged_users=flagged_users, flagged_campaigns=flagged_campaigns)

@admin_bp.route('/flag_user/<int:user_id>', methods=['POST'])
@login_required
def flag_user(user_id):
    user = User.query.get_or_404(user_id)
    user.flagged = True  # Assuming User model has 'flagged' field
    db.session.commit()
    flash('User has been flagged.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/flag_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def flag_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.flagged = True  # Assuming Campaign model has 'flagged' field
    db.session.commit()
    flash('Campaign has been flagged.', 'success')
    return redirect(url_for('admin.dashboard'))
