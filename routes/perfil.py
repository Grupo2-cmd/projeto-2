from flask_login import login_required, current_user
from flask import render_template, request, redirect, url_for, flash
from models import Produto
from database import db
from flask import Blueprint

perfil_bp = Blueprint('perfil', __name__)



@perfil_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        nome = request.form.get('nomeProduto')
        preco = request.form.get('precoProduto')
        descricao = request.form.get('descricaoProduto')

        if not nome or not preco:
            flash("Nome e preço são obrigatórios.", "error")
            return redirect(url_for('main.perfil'))

        try:
            preco_float = float(preco.replace(',', '.'))  # Caso use vírgula
        except ValueError:
            flash("Preço inválido.", "error")
            return redirect(url_for('main.perfil'))

        novo_produto = Produto(
            nome=nome,
            preco=preco_float,
            descricao=descricao,
            usuario_id=current_user.id  # Assumindo que Produto tem esse campo
        )
        try:
            db.session.add(novo_produto)
            db.session.commit()
            flash("Produto adicionado com sucesso!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Erro ao adicionar produto.", "error")

        return redirect(url_for('main.perfil'))

    # GET — mostrar produtos do usuário no perfil
    produtos = Produto.query.filter_by(usuario_id=current_user.id).all()
    return render_template('perfil.html', produtos=produtos)
