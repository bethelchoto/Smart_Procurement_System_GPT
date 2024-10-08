# supplier/routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import supplier
from app import db
from app.models import Tender, Bid
from app.forms import BidForm
from app.utils import save_file

@supplier.route('/dashboard')
@login_required
def dashboard():
    bids = Bid.query.filter_by(supplier_id=current_user.id).all()
    return render_template('supplier_dashboard.html', bids=bids)

@supplier.route('/tenders')
@login_required
def tenders():
    # Fetch only open tenders
    tenders = Tender.query.filter_by(status='open').all()
    
    # Fetch all bids by the current supplier
    bids = Bid.query.filter_by(supplier_id=current_user.id).all()
    
    # Get a set of tender IDs for which the user has already submitted bids
    submitted_tender_ids = {bid.tender_id for bid in bids}
    
    return render_template('tenders.html', tenders=tenders, submitted_tender_ids=submitted_tender_ids)


@supplier.route('/upload-bid/<int:tender_id>', methods=['GET', 'POST'])
@login_required
def upload_bid(tender_id):
    tender = Tender.query.get_or_404(tender_id)
    form = BidForm()
    if form.validate_on_submit():
        # Save the file using the updated function
        file_path = save_file(form.bid_document.data, 'uploads/bids')
        new_bid = Bid(
            tender_id=tender.id,
            supplier_id=current_user.id,
            document_path=file_path,  # Ensure this matches your model field name
            status='Submitted'
        )
        db.session.add(new_bid)
        db.session.commit()
        flash('Bid submitted successfully.', 'success')
        return redirect(url_for('supplier.dashboard'))
    return render_template('upload_bids.html', form=form, tender=tender)

