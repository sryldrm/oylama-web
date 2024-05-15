from flask import Blueprint, render_template, request, flash, redirect,url_for
from flask_login import login_required, current_user,logout_user
from .models import Group,Poll,Vote
from . import db
import json
from .models import get_user_votes,get_user_groups


views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/create_poll', methods = ['GET', 'POST'])
def create_poll():
    form = OylamaForm()
    group = None
    if form.validate_on_submit():
        question = form.question.data
        options = form.options.data.split('\n')

        if current_user.is_authenticated:
            group = current_user.groups[0] 

        new_poll = Poll(question=question, options='\n'.join(options))
        db.session.add(new_poll)
        db.session.commit()

        vote_code = create_vote_code()  

        return f"Anket başarıyla oluşturuldu!\n Oylama Katılım Kodu: {vote_code}"
    return render_template ('create_poll.html', user=current_user,group=group)

@views.route('/vote/<int:poll_id>', methods=['GET', 'POST'])
@login_required
def vote(poll_id):
    poll = Poll.query.get(poll_id)
    if request.method == 'POST':
        choice = request.form.get('choice') == 'yes'
        new_vote = Vote(user_id=current_user.id, poll_id=poll_id, choice=choice)
        db.session.add(new_vote)
        db.session.commit()
        flash('Oy başarıyla gönderildi!', category='success')
        return redirect(url_for('views.home'))
    return render_template("vote.html", user=current_user, poll=poll)

@views.route('/poll/<int:poll_id>/results')
@login_required
def view_results(poll_id):
    poll = Poll.query.get(poll_id)
    votes = Vote.query.filter_by(poll_id=poll_id).all()
    total_votes = len(votes)
    yes_votes = sum(1 for vote in votes if vote.choice)
    no_votes = total_votes - yes_votes
    return render_template("poll_results.html", user=current_user, poll=poll, total_votes=total_votes, yes_votes=yes_votes, no_votes=no_votes)


@views.route('/polls')
@login_required
def list_polls():
    # Kullanıcının üye olduğu grupları al
    user_groups = current_user.groups

    # Kullanıcının katılabileceği oylamaları depolamak için boş bir liste oluştur
    available_polls = []

    # Her bir gruptaki oylamaları al ve kullanıcının katılabileceği oylamalar listesine ekle
    for group in user_groups:
        polls = Poll.query.filter_by(group_id=group.id).all()
        available_polls.extend(polls)

    return render_template("polls.html", user=current_user, polls=available_polls)

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
