# admin/routes.py
import os
from app import db
from . import admin
from app.forms import TenderForm
from app.models import Tender, Bid
from app.utils import evaluate_bids
from flask_login import login_required
from flask import current_app, render_template, redirect, session, url_for, flash, request, send_from_directory, jsonify

@admin.route('/dashboard')
@login_required
def dashboard():
    tenders = Tender.query.all()
    return render_template('admin_dashboard.html', tenders=tenders)

@admin.route('/create-tender', methods=['GET', 'POST'])
@login_required
def create_tender():
    form = TenderForm()
    if form.validate_on_submit():
        new_tender = Tender(
            title=form.title.data,  # Use title instead of name
            description=form.description.data,
            tender_number=form.tender_number.data,  # Added tender_number
            required_experience=form.required_experience.data,
            additional_criteria=form.additional_criteria.data,
            price=form.price.data,  # Added price
            delivery_time=form.delivery_time.data,  # Added delivery_time
            start_date=form.start_date.data,  # Added start_date
            end_date=form.end_date.data  # Added end_date
        )
        db.session.add(new_tender)
        db.session.commit()
        flash('Tender created successfully.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('create_tender.html', form=form)

@admin.route('/close_tender/<int:tender_id>', methods=['GET', 'POST'])
@login_required
def close_tender(tender_id):
    tender = Tender.query.get_or_404(tender_id)
    bids = Bid.query.filter_by(tender_id=tender_id).all()

    if request.method == 'POST':
        try:
            # Prepare parameters for evaluation
            bid_documents = [(bid.id, bid.document_path) for bid in bids]

            general_tender_description = tender.description
            project_timeline = {
                'start_date': tender.start_date,
                'end_date': tender.end_date,
            }
            
            bid_amounts = tender.price
            required_experience = tender.required_experience
            additional_criteria = tender.additional_criteria

            # Evaluate bids
            evaluated_results = evaluate_bids(
                bid_documents,
                general_tender_description,
                project_timeline,
                bid_amounts,
                required_experience,
                additional_criteria
            )

            # Update tender status
            tender.status = 'closed'
            db.session.commit()
            # For example, using Flask's session (make sure to import session)
            session['evaluated_results'] = evaluated_results

            # Redirect to evaluation results page
            return redirect(url_for('admin.evaluation_results', tender_id=tender_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error closing tender: {str(e)}', 'danger')

    return render_template('close_tender.html', tender=tender, bids=bids)

@admin.route('/evaluation_results/<int:tender_id>', methods=['GET'])
@login_required
def evaluation_results(tender_id):
    evaluated_results = session.get('evaluated_results', None)  
    tender = Tender.query.get_or_404(tender_id)
    return render_template('evaluation_results.html', evaluated_results=evaluated_results, tender=tender)

@admin.route('/uploads/bids/<path:filename>')
def serve_bid_file(filename):
    # Using os.path.join to create the correct file path
    uploads_dir = os.path.join(current_app.root_path, '..', 'uploads', 'bids')
    return send_from_directory(uploads_dir, filename)

@admin.route('/update_bid_status/<int:bid_id>', methods=['POST'])
@login_required
def update_bid_status(bid_id):
    tenders = Tender.query.all()
    id = bid_id

    evaluated_results = session.get('evaluated_results', [])

    try:
        # Fetch the winning bid by bid_id and update its status to 'winner'
        winner_bid = Bid.query.get(id)
        tender_id = winner_bid.tender_id

        if winner_bid:
            winner_bid.decision = 'winner'
            winner_bid.status = 'decided'  # Mark status as 'decided'

            # Find the matching result in evaluated_results by bid_id
            result = next((res for res in evaluated_results if res['bid_id'] == id), None)
            if result:
                winner_bid.ranking_score = result['Score']
                winner_bid.company_name = result['Company']  # Update company name for the winner

        # Update all other bids related to the same tender
        other_bids = Bid.query.filter(Bid.id != id, Bid.tender_id == winner_bid.tender_id).all()
        for bid in other_bids:
            bid.status = 'decided'  
            bid.decision = 'lost'  

            # Find the matching result for other bids in evaluated_results using bid.id
            other_result = next((res for res in evaluated_results if res['bid_id'] == bid.id), None)
            if other_result:
                bid.ranking_score = other_result['Score']
                bid.company_name = other_result['Company']  

        # Commit all the changes to the database
        db.session.commit()
        # Flash success and redirect to the winner_lossers function
        flash('Tender Bidding Completed.', 'success')
        return redirect(url_for('admin.winner_losers', tender_id=tender_id))

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin.route('/winner_losers/<int:tender_id>', methods=['GET'])
@login_required
def winner_losers(tender_id):
    # Get the tender and related bids
    tender = Tender.query.get_or_404(tender_id)
    bids = Bid.query.filter_by(tender_id=tender_id).all()

    # Separate the winner and losers
    winner = Bid.query.filter_by(tender_id=tender_id, decision='winner').first()
    losers = Bid.query.filter_by(tender_id=tender_id, decision='lost').all()

    return render_template('winner_losers.html', tender=tender, winner=winner, losers=losers)

