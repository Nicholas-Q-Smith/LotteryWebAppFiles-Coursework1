# IMPORTS
import copy
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from app import db
from models import Draw, User


# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery', methods=['GET', 'POST'])
@login_required
def lottery():
    return render_template('lottery.html')


@lottery_blueprint.route('/add_draw', methods=['POST'])
@login_required
def add_draw():
    submitted_draw = ''
    for i in range(6):
        submitted_draw += request.form.get('no' + str(i + 1)) + ' '

    submitted_draw.strip()

    current_winning_draw = Draw.query.filter_by(win=True).first()
    round_number = 0

    if current_winning_draw:
        round_number = current_winning_draw.round

    # create a new draw with the form data.
    new_draw = Draw(user_id=current_user.id, draw=submitted_draw, win=False, round=round_number, draw_key=current_user.draw_key)
    # add the new draw to the database
    db.session.add(new_draw)
    db.session.commit()

    # re-render lottery.page
    flash('Draw %s submitted.' % submitted_draw)
    return lottery()


# view all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
@login_required
def view_draws():
    playable_draws = Draw.query.filter_by(played=False, user_id=current_user.id).all()

    decrypted_playable_draws = []

    draw_copies = list(map(lambda x: copy.deepcopy(x), playable_draws))

    # decrypts the playable draws and adds them to an array
    for d in draw_copies:
        user = User.query.filter_by(id=d.user_id).first()
        d.view_draw(user.draw_key)
        decrypted_playable_draws.append(d)

    # if playable draws exist
    if len(playable_draws) != 0:
        # re-render lottery page with playable draws
        return render_template('lottery.html', playable_draws=decrypted_playable_draws)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
def check_draws():

    decrypted_played_draws = []

    played_draws = Draw.query.filter_by(played=True, user_id=current_user.id).all()
    draw_copies = list(map(lambda x: copy.deepcopy(x), played_draws))

    # decrypts the played draws and adds them to an array
    for d in draw_copies:
        d.view_draw(current_user.draw_key)
        if d.match:
            d.win = True
        decrypted_played_draws.append(d)

    # if played draws exist
    if len(decrypted_played_draws) != 0:
        return render_template('lottery.html', results=decrypted_played_draws, played=True)

    # if no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
@login_required
def play_again():
    Draw.query.filter_by(user_id=current_user.id, played=True).delete()
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()


