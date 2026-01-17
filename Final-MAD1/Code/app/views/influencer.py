from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Campaign, AdRequest
from app.forms import AdRequestForm
from app.forms import InfluencerProfileForm
from app.models import InfluencerProfile

influencer_bp = Blueprint('influencer', __name__)

@influencer_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch ad requests for the influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    
    # Check if the influencer is flagged
    flagged = current_user.flagged  # Assuming 'flagged' is a column in the User model

    return render_template('influencer/dashboard.html', ad_requests=ad_requests, flagged=flagged)


@influencer_bp.route('/view_ad_request/<int:ad_request_id>')
@login_required
def view_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    # Ensure the current user is the owner of the ad request
    if ad_request.influencer_id != current_user.id:
        flash('You are not authorized to view this ad request.', 'danger')
        return redirect(url_for('influencer.dashboard'))
    
    return render_template('influencer/view_ad_request.html', ad_request=ad_request)

@influencer_bp.route('/accept_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    # Ensure the current user is the owner of the ad request
    if ad_request.influencer_id != current_user.id:
        flash('You are not authorized to accept this ad request.', 'danger')
        return redirect(url_for('influencer.dashboard'))

    ad_request.status = 'Accepted'
    db.session.commit()
    flash('Ad request accepted.', 'success')
    return redirect(url_for('influencer.dashboard'))

@influencer_bp.route('/reject_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    # Ensure the current user is the owner of the ad request
    if ad_request.influencer_id != current_user.id:
        flash('You are not authorized to reject this ad request.', 'danger')
        return redirect(url_for('influencer.dashboard'))

    ad_request.status = 'Rejected'
    db.session.commit()
    flash('Ad request rejected.', 'success')
    return redirect(url_for('influencer.dashboard'))

@influencer_bp.route('/negotiate_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
def negotiate_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    if current_user.id != ad_request.influencer_id:
        flash('You do not have permission to negotiate this ad request.', 'danger')
        return redirect(url_for('influencer.dashboard'))

    form = AdRequestForm()

    # Populate choices for campaign and influencer
    form.campaign_id.choices = [(ad_request.campaign.id, ad_request.campaign.name)]
    form.influencer_id.choices = [(ad_request.influencer.id, ad_request.influencer.username)]

    if form.validate_on_submit():
        try:
            ad_request.messages = form.messages.data
            ad_request.payment_amount = form.payment_amount.data
            ad_request.status = 'Negotiating'  # Set the status to Negotiating

            db.session.commit()
            flash('Your negotiation request has been sent!', 'success')
            return redirect(url_for('influencer.dashboard'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
            db.session.rollback()
    elif request.method == 'GET':
        form.messages.data = ad_request.messages
        form.requirements.data = ad_request.requirements
        form.payment_amount.data = ad_request.payment_amount
    
    # Log form errors if validation fails
    if form.errors:
        print("Form errors:", form.errors)

    return render_template('influencer/negotiate_ad_request.html', form=form)



@influencer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Ensure the user has a profile, if not, create one
    if not current_user.influencer_profile:
        profile = InfluencerProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    form = InfluencerProfileForm()

    # Populate form fields if the profile exists
    if request.method == 'GET':
        form.category.data = current_user.influencer_profile.category
        form.niche.data = current_user.influencer_profile.niche
        form.reach.data = current_user.influencer_profile.reach

    if form.validate_on_submit():
        current_user.influencer_profile.category = form.category.data
        current_user.influencer_profile.niche = form.niche.data
        current_user.influencer_profile.reach = form.reach.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('influencer.dashboard'))

    return render_template('influencer/profile.html', form=form)

@influencer_bp.route('/public-ad')
@login_required
def public_ad_requests():
    if current_user.role != 'influencer':
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # Query all public campaigns
    public_campaigns = Campaign.query.filter_by(visibility='public').all()

    # Get ad requests related to public campaigns
    public_ad_requests = AdRequest.query.filter(AdRequest.campaign_id.in_(
        [campaign.id for campaign in public_campaigns])).all()

    return render_template('influencer/public_ad.html', public_ad_requests=public_ad_requests)

