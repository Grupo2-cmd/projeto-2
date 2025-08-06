from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from models.usuario import Usuario
from database import db
import hashlib
from .forms import LoginForm
from .forms import RegistrarForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        nome = form.nomeForm.data
        senha = form.senhaForm.data

        usuario = Usuario.query.filter_by(nome=nome).first()
        if usuario:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            if usuario.senha_hash == senha_hash:
                login_user(usuario)
                flash(f'Bem-vindo, {usuario.nome}!', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Senha incorreta.', 'error')
        else:
            flash('Usuário não encontrado.', 'error')
    
    return render_template('login.html', form=form)


@auth_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    form = RegistrarForm()

    if form.validate_on_submit():
        nome = form.nomeForm.data
        senha = form.senhaForm.data
        confirma_senha = form.confirmaSenhaForm.data
        email = form.emailForm.data

        if Usuario.query.filter_by(nome=nome).first():
            flash('Nome de usuário já existe.', 'error')
            return render_template('registrar.html', form=form)

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        novo_usuario = Usuario(nome=nome, senha_hash=senha_hash, email=email or None)

        try:
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Conta criada com sucesso! Você pode fazer login agora.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'error')

    return render_template('registrar.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('main.home'))

from .forms import RedefinirSenhaForm

@auth_bp.route('/redefinir_senha', methods=['GET', 'POST'])
def redefinir_senha():
    form = RedefinirSenhaForm()
    if form.validate_on_submit():
        nome = form.nomeForm.data
        nova_senha = form.novaSenhaForm.data

        usuario = Usuario.query.filter_by(nome=nome).first()
        if not usuario:
            flash('Usuário não encontrado.', 'error')
            return render_template('redefinir_senha.html', form=form)
        
        usuario.senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
        try:
            db.session.commit()
            flash('Senha redefinida com sucesso! Você pode fazer login agora.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            db.session.rollback()
            flash('Erro ao redefinir senha. Tente novamente.', 'error')

    return render_template('redefinir_senha.html', form=form)
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models import Usuario

auth_routes = Blueprint('auth_routes', __name__)

def hash(txt):
    return hashlib.sha256(txt.encode('utf-8')).hexdigest()

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('produto_routes.site'))

    if request.method == 'GET':
        return render_template('login.html')
    else:
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        user = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()

        if not user:
            return 'Nome ou senha incorretos.'

        login_user(user)
        return redirect(url_for('produto_routes.site'))

@auth_routes.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'GET':
        return render_template('registrar.html')

    nome = request.form['nomeForm']
    senha = request.form['senhaForm']

    if db.session.query(Usuario).filter_by(nome=nome).first():
        return render_template('registrar.html', erro='Usuário já cadastrado.')

    novo_usuario = Usuario(nome=nome, senha=hash(senha))
    db.session.add(novo_usuario)
    db.session.commit()
    login_user(novo_usuario)
    return redirect(url_for('produto_routes.site'))

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('produto_routes.site'))

@auth_routes.route('/redefinir_senha', methods=['GET', 'POST'])
def redefinir_senha():
    if request.method == 'POST':
        nome = request.form['nome']
        nova_senha = request.form['nova_senha']
        confirma_senha = request.form['confirma_senha']

        if nova_senha != confirma_senha:
            return 'As senhas não conferem.'

        usuario = db.session.query(Usuario).filter_by(nome=nome).first()
        if not usuario:
            return 'Usuário não encontrado.'

        usuario.senha = hash(nova_senha)
        db.session.commit()
        return redirect(url_for('auth_routes.login'))

    return render_template('redefinir_senha.html')
