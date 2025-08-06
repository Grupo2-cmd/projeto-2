from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.produto import Produto
from database import db
import os
from .forms import ProdutoForm

produto_bp = Blueprint('produto', __name__)

@produto_bp.route('/')
def site():
    busca = request.args.get('q', '')  # pega o parâmetro 'q' da query string
    if busca:
        # filtro com LIKE, case insensitive
        produtos = db.session.query(Produto).filter(Produto.nome.ilike(f'%{busca}%')).all()
    else:
        produtos = db.session.query(Produto).all()
    return render_template('site.html', produtos=produtos, busca=busca)

@produto_bp.route('/buscar')
def buscar_produtos():
    busca = request.args.get('q', '')
    if busca:
        produtos = db.session.query(Produto).filter(Produto.nome.ilike(f'%{busca}%')).all()
    else:
        produtos = []
    return render_template('buscar.html', produtos=produtos, busca=busca)

@produto_bp.route('/adicionar_produtos', methods=['GET', 'POST'])
@login_required
def adicionar_produtos():
    form = ProdutoForm()

    if form.validate_on_submit():
        nome = form.nomeForm.data
        descricao = form.descricaoForm.data
        preco = float(form.precoForm.data)
        categoria = form.categoriaForm.data
        cidade = form.cidadeForm.data
        imagem = form.imagem.data

        caminho_relativo = None
        if imagem:
            filename = secure_filename(imagem.filename)
            if filename:
                upload_folder = os.path.join('static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                caminho_relativo = os.path.join('uploads', filename)
                caminho_completo = os.path.join('static', caminho_relativo)
                imagem.save(caminho_completo)

        novo_produto = Produto(
            nome=nome,
            descricao=descricao,
            preco=preco,
            categoria=categoria,
            cidade=cidade,
            imagem=caminho_relativo,
            usuario_id=current_user.id
        )

        try:
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
            return redirect(url_for('main.home'))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar produto: {e}")
            flash('Erro ao adicionar produto. Tente novamente.', 'error')

    return render_template('adicionar_produtos.html', form=form)

@produto_bp.route('/excluir_produto/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = Produto.query.get_or_404(id)

    if produto.usuario_id != current_user.id:
        flash('Você não tem permissão para excluir este produto.', 'error')
        return redirect(url_for('main.home'))

    try:
        if produto.imagem:
            caminho_imagem = os.path.join('static', produto.imagem)
            if os.path.exists(caminho_imagem):
                os.remove(caminho_imagem)

        db.session.delete(produto)
        db.session.commit()
        flash('Produto excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir produto: {e}")
        flash('Erro ao excluir produto. Tente novamente.', 'error')

    return redirect(url_for('main.home'))
import os
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from database import db
from models import Produto
from werkzeug.utils import secure_filename

produto_routes = Blueprint('produto_routes', __name__)

@produto_routes.route('/')
def site():
    produtos = db.session.query(Produto).all()
    return render_template('site.html', produtos=produtos)

@produto_routes.route('/adicionar_produtos', methods=['GET', 'POST'])
@login_required
def adicionar_produtos():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        descricao = request.form['descricao']
        imagem = request.files.get('imagem')

        caminho_relativo = None

        if imagem and imagem.filename != '':
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filename = secure_filename(imagem.filename)
            caminho_relativo = os.path.join('uploads', filename)
            caminho_completo = os.path.join('static', caminho_relativo)
            imagem.save(caminho_completo)

        novo_produto = Produto(
            nome=nome,
            preco=preco,
            descricao=descricao,
            imagem=caminho_relativo if caminho_relativo else ''
        )

        db.session.add(novo_produto)
        db.session.commit()

        return redirect(url_for('produto_routes.site'))

    return render_template('adicionar_produtos.html')

@produto_routes.route('/excluir_produto/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = db.session.query(Produto).filter_by(id=id).first()
    if produto:
        db.session.delete(produto)
        db.session.commit()
    return redirect(url_for('produto_routes.site'))