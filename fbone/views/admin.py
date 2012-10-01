# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, g, redirect, url_for, request, flash, jsonify
from flask.ext.login import login_required, current_user
from fbone.forms import NewGroupForm, EditPageForm, NewProjectForm, SetSessionForm, NewOfferForm, SetOfferForm, NewActForm
from fbone.extensions import db

from fbone.models import User, Group, Page, Project, Session, Offer, Act
from fbone.decorators import keep_login_url, admin_required
import datetime
from werkzeug import secure_filename, generate_password_hash, check_password_hash
import os, zipfile, shutil

admin = Blueprint('admin', __name__, url_prefix='/admin')
UPLOAD_FOLDER = '/tmp/'
admin.config = dict()
admin.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def render_projects(objects):
    for object in objects:
        object.sesiones = len(object.sessions)
        object.ofertas = len(object.offers)
        object.usuarios = len(object.users)
    return render_template('list.html', title="Proyectos", objects=objects, fields=["id","activation_key", "term","type", "name", "sesiones", "ofertas","usuarios"], actions=[['Ver Sesiones', "view_session", 'icon-camera'], ['Asignar Sesiones', "set_session", 'icon-hand-right'], ['Ver Ofertas', "view_offer", 'icon-shopping-cart'], ['Asignar Ofertas', "set_offer", 'icon-hand-right'], ['Borrar',"del",'icon-trash']], active='project_list', current_user=current_user)

def set_offers(offers, projects):
    form = SetOfferForm(request.form)
    offers_choices = [ (offer.id, offer.name) for offer in offers]
    projects_choices = [ (project.id, project.activation_key) for project in projects]
    form.offers_id.choices = offers_choices
    form.projects_id.choices = projects_choices
    if request.method == 'POST':
        for offer_id in form.offers_id.data:
            offer = Offer.query.filter_by(id=offer_id).first()
            for project_id in form.projects_id.data:
                project = Project.query.filter_by(id=project_id).first()
                project.set_offer(offer)
                
        db.session.commit()
        return redirect(form.next.data or url_for('admin.project_list'))
    return render_template('admin_set_offer.html', form=form,
                           current_user=current_user)

def set_sessions(sessions, projects):
    if len(sessions) > 1:
        sessions_from_today = [ session for session in sessions if session.begin > datetime.datetime.now() ]
    else:
        sessions_from_today = sessions
    form = SetSessionForm(request.form)
    sessions_choices = [ (session.id, session.begin) for session in sessions_from_today]
    projects_choices = [ (project.id, project.activation_key) for project in projects]
    form.sessions_id.choices = sessions_choices
    form.projects_id.choices = projects_choices
    if request.method == 'POST':
        for session_id in form.sessions_id.data:
            session = Session.query.filter_by(id=session_id).first()
            for project_id in form.projects_id.data:
                project = Project.query.filter_by(id=project_id).first()
                project.set_session(session)
                
        db.session.commit()
        return redirect(form.next.data or url_for('admin.project_list'))
    return render_template('admin_set_session.html', form=form,
                           current_user=current_user)

@admin.route('/offer/<project_id>/del/<offer_id>', methods=['GET'])
@login_required
def remove_offer(project_id, offer_id):
    project = Project.query.filter_by(id=project_id).first()
    offer = Offer.query.filter_by(id=offer_id).first()
    project.remove_offer(offer)
    db.session.commit()
    return redirect(form.next.data or '/admin/offer/'+project_id)


@admin.route('/offers/<id>', methods=['GET'])
@admin.route('/offers/', methods=['GET'])
@login_required
def offers(id=None):
    project = None
    if len(current_user.projects):
        project = current_user.projects[-1] #FIXME
    if project:
        offers = project.offers
        offer_ids = [str(offer.id) for offer in offers]
        if id: 
            if(str(id) in offer_ids):
                node = Offer.query.filter_by(id=id).first()
                tree = [(x.id, x.jsonify_full()) for x in node.children]
            else:
                tree = []
        else:
            offers = [offer for offer in offers if offer.depth == 0]
            tree = [(x.id, x.jsonify_full()) for x in offers]

    else:
        if id:
            node = Offer.query.filter_by(id=id).first()
            tree = db.session.query(Offer.id,Offer.name).filter_by(parent=node).all()
        else:
            tree = [(x.id, x.jsonify_full()) for x in Offer.query.filter_by(depth=0)]
    return jsonify(tree)
    
@admin.route('/offers/type/<type>', methods=['GET'])
@login_required
def offers_types(type=1):
    project = None
    tree = []
    if len(current_user.projects):
        project = current_user.projects[-1] #FIXME
    if project:
        offers = project.offers
        offer_types = [str(offer.type) for offer in offers]
        if(str(type) in offer_types):
            nodes = [offer for offer in offers if (offer.depth == 0 and str(offer.type)==str(type))]
            tree = [(x.id, x.jsonify_full()) for x in nodes]
    return jsonify(tree)
    
@admin.route('/project/list/<name>')
@login_required
@admin_required
def project_list_name(name):
    objects = db.session.query(Project).filter(Project.name!='0', Project.term==name).all()
    return render_projects(objects)

@admin.route('/project/list')
@login_required
@admin_required
def project_list():
    objects = db.session.query(Project).filter(Project.name!='0').all()
    return render_projects(objects)

@admin.route('/group/list')
@login_required 
@admin_required
def group_list():
    return render_template('list.html', title="Grupos", objects=Group.query.all(), active='group_list', actions=[['Editar', "edit", 'icon-pencil'], ['Borrar',"del",'icon-trash']], current_user=current_user)

@admin.route('/page/list')
@login_required
@admin_required
def page_list():
    objects = db.session.query(Page).all()
    return render_template('list.html', title=u"Páginas", objects=objects, active='page_list', fields=['name'], actions=[['Editar', "edit", 'icon-pencil'],], current_user=current_user)

@admin.route('/act/list')
@login_required
@admin_required
def act_list():
    objects = db.session.query(Act).all()
    return render_template('list.html', title=u"Actos de Graduación", objects=objects, active='act_list', actions=[['Borrar',"del",'icon-trash']], fields=["password",], current_user=current_user)


@admin.route('/project/del/<id>')
@login_required 
@admin_required
def project_delete(id):
    project = Project.query.filter_by(id=id).first_or_404()
    db.session.delete(project)
    db.session.commit()
    return redirect(form.next.data or url_for('admin.project_list'))

@admin.route('/group/del/<id>')
@login_required 
@admin_required
def group_delete(id):
    group = Group.query.filter_by(id=id).first_or_404()
    db.session.delete(group)
    db.session.commit()
    return redirect(form.next.data or url_for('admin.group_list'))

@admin.route('/offer/del/<id>')
@login_required 
@admin_required
def offer_delete(id):
    offer = Offer.query.filter_by(id=id).first_or_404()
    db.session.delete(offer)
    db.session.commit()
    return redirect(url_for('admin.offer_list'))

@admin.route('/offer/set/<id>', methods=['GET', 'POST'])
@login_required 
@admin_required
def set_offer_id(id):
    projects = Project.query.all()
    offers = [ db.session.query(Offer).filter(Offer.id==id).first(),]
    return set_offers(offers, projects)

@admin.route('/project/set_offer/<id>', methods=['GET', 'POST'])
@login_required 
@admin_required
def set_project_offer_id(id):
    offers = Offer.query.all()
    projects = [ db.session.query(Project).filter(Project.id==id).first(),]
    return set_offers(offers, projects)

@admin.route('/project/view_offer/<id>')
@login_required 
@admin_required
def project_view_offers(id):
    return redirect('admin/offer/'+id)

@admin.route('/project/set_session/<id>', methods=['GET', 'POST'])
@login_required 
@admin_required
def set_session_id(id):
    sessions = Session.query.all()
    projects = [ db.session.query(Project).filter(Project.id==id).first(),]
    return set_sessions(sessions, projects)

@admin.route('/project_set_session/<term>', methods=['GET', 'POST'])
@login_required 
@admin_required
def set_session_term(term):
    sessions = Session.query.all()
    projects = db.session.query(Project).filter(Project.name!='0', Project.term==term).all()
    return set_sessions(sessions, projects)

@admin.route('/project_set_session/', methods=['GET', 'POST'])
@login_required 
@admin_required
def set_session():
    sessions = Session.query.all()
    projects = db.session.query(Project).filter(Project.name!='0').all()
    return set_sessions(sessions, projects)

@admin.route('/session/set/<id>', methods=['GET', 'POST'])
@login_required 
@admin_required
def set_project(id):
    sessions = [Session.query.filter_by(id=id).first(), ]
    projects = db.session.query(Project).filter(Project.name!='0').all()
    return set_sessions(sessions, projects)

@admin.route('/project/view_session/<id>')
@login_required 
@admin_required
def project_view_sessions(id):
    return redirect('session/list/'+id)

@admin.route('/offer/copy/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def copy_offer(id=None):
    offer = db.session.query(Offer).get(id)
    if id:
        form = NewOfferForm(request.form, obj=offer)
        form.copy.data = True
        return render_template("admin_new_offer.html",
                           form=form,
                           filename=offer.picture)

@admin.route('/act/del/<id>')
@login_required
@admin_required
def del_act(id):
    act = Act.query.filter_by(id=id).first()
    dir_path = os.path.join(os.path.join(admin.root_path, '../static/acts/'),act.password_hash)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    db.session.delete(act)
    db.session.commit()
    return redirect(url_for('admin.act_list'))

@admin.route('/new_act/', methods=['GET', 'POST'])
@login_required
@admin_required
def new_act():
    form = NewActForm(request.form)
    if request.method == 'POST':
        password = form.password.data
        password_hash = generate_password_hash(password)
        file = request.files['zipfile']
        if file:
            filename = secure_filename(file.filename)
            dir_path = os.path.join(os.path.join(admin.root_path, '../static/acts/'),password_hash)
            if not os.path.exists(dir_path):
                act = Act(password=password, password_hash=password_hash)
                db.session.add(act)
                db.session.commit()
                os.mkdir(dir_path)
                file_path = os.path.join(dir_path, filename) 
                file.save(file_path)
                zip_file = zipfile.ZipFile(file_path)
                zip_file.extractall(dir_path)
                
                flash(u'Acto creado exitosamente','success')
                return redirect(form.next.data or url_for('admin.act_list'))
            else:
                flash(u'Ya existe un acto con esa contraseña','error')
            
    return render_template("admin_new_act.html",
                           form=form
                           )



@admin.route('/new_offer/', methods=['GET', 'POST'])
@admin.route('/offer/edit/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def new_offer(id=None):
    offer = None
    if id:
        offer = db.session.query(Offer).get(id)
        form = NewOfferForm(request.form, obj=offer)
    else:
        form = NewOfferForm(request.form)
    depth = 0
    parent = None

    if request.method == 'POST':
        if form.id.data:
            offer = db.session.query(Offer).get(form.id.data)
            prev_offer = offer
        if not form.id.data or form.copy.data:
            offer = Offer(name=form.name.data, description=form.description.data,
                     type=form.type.data, price=form.price.data,
                      default=form.default.data)
        else:
            offer.name = form.name.data
            offer.type = form.type.data
            offer.description = form.description.data
            offer.price = form.price.data
            offer.default = form.default.data
        if form.parent.data:
            parent = Offer.query.filter_by(id=form.parent.data).first()
            if parent:
                offer.parent_id = form.parent.data
                depth = parent.depth + 1
        offer.depth = depth 
        file = request.files['picture']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.path.join(admin.root_path, '../static/offers/'), filename))
            offer.picture = filename
        else:
            if form.copy.data or form.id.data:
                offer.picture = prev_offer.picture
            else:
                return redirect(form.next.data or url_for('admin.offer_list'))
        if not id: #FIXME cuando hay que hacer add?
            db.session.add(offer)
        db.session.commit()
        return redirect(form.next.data or url_for('admin.offer_list'))
    else:
        filename = None
        return render_template("admin_new_offer.html",
                           form=form,
                           filename=filename)
    return redirect(form.next.data or url_for('admin.offer_list'))
    
@admin.route('/offer/view/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def uploaded_file(id):
    offer = Offer.query.filter_by(id=id).first()
    return render_template("template.html", name=offer.name, description=offer.description, price=offer.price, filename=offer.picture)

@admin.route('/offer/', methods=['GET', 'POST'])
@admin.route('/offer/<id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def offer_list(id=None):
    offers = None
    actions = None
    if id:
        actions=[['Quitar del Proyecto',"del",'icon-trash']]
        project = Project.query.filter_by(id=id).first()
        objects = project.offers
    else:
        actions=[['Asignar Proyectos', "set", 'icon-hand-right'], ['Ver', "view", 'icon-eye-open'], ['Editar', "edit", 'icon-pencil'], ['Clonar', "copy", 'icon-share-alt'], ['Borrar',"del",'icon-trash']]
        objects = db.session.query(Offer).all()
    return render_template('list.html', title="Ofertas", objects=objects, fields=['name', 'description', 'default', 'price', 'parent_id', 'type'], actions=actions , active='offer_list', current_user=current_user)

@admin.route('/set_offer/', methods=['GET', 'POST'])
@login_required
@admin_required
def set_offer():
    offers = Offer.query.all()
    projects = db.session.query(Project).filter(Project.name!='0').all()
    return set_offers(offers, projects)


@admin.route('/new_project/', methods=['GET', 'POST'])
@login_required
@admin_required
def new_project():
    group = None
    project = None
    form = NewProjectForm(request.form)
    if form.validate_on_submit():
        term = form.term.data

        if form.group.data:
            group = Group.query.filter_by(id=form.group.data).first()
        project = Project.query.filter_by(id=form.project_id.data).first()
        if not form.project_id.data or form.project_id.data == '':
            project = Project.query.filter_by(term=form.term.data,name='0').first()
            if not project:
                project = Project(term=term, name='0')
                db.session.add(project)
        else:
            project = Project.query.filter_by(id=form.project_id.data).first()
            project.term = term

        if group:
            project.create(group)
        
        db.session.commit()
        flash('Datos actualizados correctamente', 'success')
        return redirect(form.next.data or url_for('admin.new_project'))

    return render_template('admin_new_project.html', form=form,
                           current_user=current_user, project=project)

@admin.route('/new_group/', methods=['GET', 'POST'])
@login_required
@admin_required
def new_group():
    depth = 0
    parent = None
    node = None
    form = NewGroupForm(request.form)
    if 'uni' in request.values:
        node = request.values['uni']
        node = Group.query.filter_by(id=node).first()
    if form.validate_on_submit():
        name = form.name.data
        activation_key = form.activation_key.data
        #if not form.type.data or form.type.data == "":
        type = form.choosetype.data
        if form.parent.data:
            parent = Group.query.filter_by(id=form.parent.data).first()
            depth = parent.depth + 1
        #else:
        #    type = form.type.data
        
        if not form.group_id.data or form.group_id.data == '':
            if parent:
                node = Group(name=name, activation_key = activation_key,depth=depth, type=type, parent_id=parent.id)
            else:
                node = Group(name=name, activation_key = activation_key,depth=depth, type=type)
            db.session.add(node)
        else:
            node = Group.query.filter_by(id=form.group_id.data).first()
            node.name = name
            node.activation_key = activation_key
            node.type = type
            node.depth = depth
            if parent:
                node.parent_id = parent.id
                node.depth = parent.depth + 1
        
        db.session.commit()
        flash('Datos actualizados correctamente', 'success')
        return redirect(form.next.data or url_for('admin.new_group'))

    return render_template('admin_new_group.html', form=form,
                           current_user=current_user, node=node)


@admin.route('/group/edit/<id>')
@admin.route('/group/<id>')
@login_required 
@admin_required
def group_edit(id):
    node = Group.query.filter_by(id=id).first()
    form = NewGroupForm(request.form)
    return render_template('admin_new_group.html', form=form,
                           current_user=current_user, node=node)

@admin.route('/grouptypes/', methods=['GET'])
@login_required
@admin_required
def grouptypes():
    types = db.session.query(Group.type,Group.type).distinct()
    return jsonify(types)
    

@admin.route('/groups/', methods=['GET'])
@login_required
@admin_required
def groups():
    if 'parent' in request.values:
        node_id = request.values['parent']
        node = Group.query.filter_by(id=node_id).first()
        tree = db.session.query(Group.id,Group.name).filter_by(parent=node).all()
    else:
        tree = [(x.id, x.jsonify()) for x in Group.query.filter_by(depth=0)]
    return jsonify(tree)
    

@admin.route('/page/edit/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_page(id):
    form = EditPageForm(request.form, next=url_for('admin.page_list'))
    #if form.validate_on_submit():
    if request.method == 'POST':
        page = Page.query.get(id)
        page.content = form.textarea.data
        db.session.commit()
        return redirect(form.next.data or url_for('admin.page_list'))
    page = Page.query.get(id)
    return render_template('edit_proceso.html', page=page, form=form)


@admin.route('/')
@login_required
def index():
    return render_template('user_index.html', current_user=current_user)


@admin.route('/<name>')
def pub(name):
    if current_user.is_authenticated() and current_user.name == name:
        return redirect(url_for('user.index'))

    user = User.query.filter_by(name=name).first_or_404()
    return render_template('user_pub.html', user=user)
