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


@views.route('/create-poll', methods=['POST'])
@login_required
def create_poll():
    if request.method == 'POST':
        question = request.form.get('question')
        group_id = request.form.get('group_id')  # Grup kimliğini formdan al
        options = request.form.getlist('option') #Seçenek almak için
        
        new_poll = Poll(question=question, options=options, group_id=group_id)  

        # Kullanıcının üye olduğu grupları al
        user_groups = get_user_groups(current_user.id)
        # Eğer kullanıcı herhangi bir gruba üye değilse, bir hata mesajı göster veya uygun bir işlem yap
        if not user_groups:
            flash('Oylama oluşturmak için bir gruba üye olmalısınız.', category='error')
            return redirect(url_for('views.home'))
        
        # İlk gruba ait bir anket oluştur
        new_poll.group_id = user_groups[0].id

        db.session.add(new_poll)
        db.session.commit()
        flash('Anket başarıyla oluşturuldu!', category='success')
        return redirect(url_for('views.list_polls'))
    
    user_groups = current_user.groups
    return render_template("create_poll.html", user=current_user)

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