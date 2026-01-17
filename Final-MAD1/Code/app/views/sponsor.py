from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.forms import CampaignForm, AdRequestForm
from app.models import Campaign, AdRequest, User, InfluencerProfile


sponsor_bp = Blueprint('sponsor', __name__)

@sponsor_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch campaigns owned by the sponsor
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()

    # Fetch ad requests related to the sponsor's campaigns
    ad_requests = AdRequest.query.filter(AdRequest.campaign_id.in_(
        [campaign.id for campaign in campaigns])).all()

    # Check if the sponsor is flagged
    flagged = current_user.flagged  # Assuming 'flagged' is a column in the User model

    return render_template('sponsor/dashboard.html', campaigns=campaigns, ad_requests=ad_requests, flagged=flagged)



@sponsor_bp.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    form = CampaignForm()
    if form.validate_on_submit():
        campaign = Campaign(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            visibility=form.visibility.data,
            goals=form.goals.data,
            sponsor_id=current_user.id
        )
        db.session.add(campaign)
        db.session.commit()
        flash('Your campaign has been created!', 'success')
        return redirect(url_for('sponsor.dashboard'))
    return render_template('sponsor/create_campaign.html', form=form)

@sponsor_bp.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    form = CampaignForm()
    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.description = form.description.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.budget = form.budget.data
        campaign.visibility = form.visibility.data
        campaign.goals = form.goals.data
        db.session.commit()
        flash('Your campaign has been updated!', 'success')
        return redirect(url_for('sponsor.dashboard'))
    elif request.method == 'GET':
        form.name.data = campaign.name
        form.description.data = campaign.description
        form.start_date.data = campaign.start_date
        form.end_date.data = campaign.end_date
        form.budget.data = campaign.budget
        form.visibility.data = campaign.visibility
        form.goals.data = campaign.goals
    return render_template('sponsor/edit_campaign.html', form=form)

@sponsor_bp.route('/sponsor/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    # Check if the campaign has any associated ad requests
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()

    if ad_requests:
        flash('Ad-requests already exist, so Campaign cannot be deleted.', 'danger')
        return redirect(url_for('sponsor.dashboard'))

    try:
        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error occurred while deleting the campaign.', 'danger')

    return redirect(url_for('sponsor.dashboard'))

@sponsor_bp.route('/create_ad_request', methods=['GET', 'POST'])
@login_required
def create_ad_request():
    form = AdRequestForm()
    form.campaign_id.choices = [(c.id, c.name) for c in Campaign.query.filter_by(sponsor_id=current_user.id).all()]
    form.influencer_id.choices = [(i.id, i.username) for i in User.query.filter_by(role='influencer').all()]
    if form.validate_on_submit():
        ad_request = AdRequest(
            campaign_id=form.campaign_id.data,
            influencer_id=form.influencer_id.data,
            messages=form.messages.data,
            requirements=form.requirements.data,
            payment_amount=form.payment_amount.data,
            status=form.status.data
        )
        db.session.add(ad_request)
        db.session.commit()
        flash('Your ad request has been created!', 'success')
        return redirect(url_for('sponsor.dashboard'))
    return render_template('sponsor/create_ad_request.html', form=form)

@sponsor_bp.route('/view_ad_request/<int:ad_request_id>')
@login_required
def view_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    return render_template('sponsor/view_ad_request.html', ad_request=ad_request)


@sponsor_bp.route('/edit_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
def edit_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    form = AdRequestForm()

    # Set choices for campaigns and influencers as before
    form.campaign_id.choices = [(c.id, c.name) for c in Campaign.query.filter_by(sponsor_id=current_user.id).all()]
    form.influencer_id.choices = [(i.id, i.username) for i in User.query.filter_by(role='influencer').all()]

    if form.validate_on_submit():
        # Update the ad request details
        ad_request.campaign_id = form.campaign_id.data
        ad_request.influencer_id = form.influencer_id.data
        ad_request.messages = form.messages.data
        ad_request.requirements = form.requirements.data
        ad_request.payment_amount = form.payment_amount.data

        # Check for status change (e.g., negotiation)
        if ad_request.status == 'Pending' and form.status.data == 'Negotiating':
            ad_request.status = 'Negotiating'
        elif form.status.data == 'Accepted':
            ad_request.status = 'Accepted'
        elif form.status.data == 'Rejected':
            ad_request.status = 'Rejected'

        db.session.commit()
        flash('Ad request updated!', 'success')
        return redirect(url_for('sponsor.dashboard'))

    elif request.method == 'GET':
        # Populate form fields for editing
        form.campaign_id.data = ad_request.campaign_id
        form.influencer_id.data = ad_request.influencer_id
        form.messages.data = ad_request.messages
        form.requirements.data = ad_request.requirements
        form.payment_amount.data = ad_request.payment_amount
        form.status.data = ad_request.status

    return render_template('sponsor/edit_ad_request.html', form=form)


@sponsor_bp.route('/delete_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit() 
    flash('Your ad request has been deleted!', 'success')
    return redirect(url_for('sponsor.dashboard'))

@sponsor_bp.route('/view_all_influencers')
def view_all_influencers():
    # Fetch all users with the role of 'influencer' and their associated profile details
    influencers = User.query.filter_by(role='influencer').all()
    
    # Return both user details and the corresponding influencer profiles
    return render_template('sponsor/view_all_influencers.html', influencers=influencers)

@sponsor_bp.route('/influencer/<int:user_id>')
def view_influencer_profile(user_id):
    influencer = User.query.get_or_404(user_id)
    return render_template('sponsor/view_influencer_profile.html', influencer=influencer)


@sponsor_bp.route('/test')
def test():
    return "Sponsor Blueprint is working!"