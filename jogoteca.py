from flask import Flask, render_template, request, redirect, session, flash, url_for
from dao import JogoDao, UsuarioDao
from flask_mysqldb import MySQL
from models import Jogo, Usuario
from jinja2 import Environment, PackageLoader
# -*- coding: utf-8 -*

app = Flask(__name__)
app.secret_key = 'alura'

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "admin"
app.config['MYSQL_DB'] = "jogoteca"
app.config['MYSQL_PORT'] = 3306

db = MySQL(app)
jogo_dao = JogoDao(db)
usuario_dao = UsuarioDao(db)

@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('form.html', titulo='formulario')

@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)


@app.route('/autenticar', methods=['POST', ])
def autenticar():
    usuario = usuario_dao.buscar_por_id(request.form['usuario'])
    if usuario:
        if usuario.senha == request.form['senha']:
            session['usuario_logado'] = usuario.id
            flash(usuario.nome + ' logou com sucesso!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)
    else:
        flash('Não logado, tente denovo!')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('index'))


app.run(debug=True)

@apps.route('/send_contact', methods=['POST'])
def send_contact():


    data = dict(
        asn=request.form['asn'],
        company=request.form['company'],
        local=request.form['local'],
        IPV4=request.form['ipv4'],
        IPV6=request.form['ipv6']
    )
    resp = response.json()
    if resp['success']:
         with
            open('templates') as file_:
                 arquivos_de_saida = Template(file_.read())
                 template.render(name='John')
        return render_template('form_validation.html', ASN=data['AS'])

    # formatando a saida de acordo com o tipo de arquivo a ser salvo
    arq_saida = f"{settings.SAIDA}{localidade.upper()}/{self._variables['tipo'].upper()}/"

    try:
        # caso nao exista o diretorio, tentar cria-lo
        try:
            os.makedirs(arq_saida)
        except FileExistsError:
            pass

        output_file = f"{self._variables['asn']}_{self._variables['nome']}_{localidade.upper()}_{self._variables['tipo'].upper()}_{date}"
        file_loader = FileSystemLoader(settings.TEMPLATES)
        env = Environment(loader=file_loader)

        template = env.get_template(f"{localidade.upper()}.j2")

        output = template.render(conf=self._variables)

        with open(f"{arq_saida}{output_file}.txt", "w") as outfile:
            outfile.write(output)

        (f"Arquivo de configuracao salvo em {arq_saida}{output_file}.txt")

    except Exception as err:
        raise err
