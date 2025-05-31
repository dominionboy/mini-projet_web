from flask import Flask, render_template, request, session
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///produits.db'
app.debug = True
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nom=db.Column(db.String(50))
    prenom=db.Column(db.String(50))
    adresse=db.Column(db.String(200))
    ville=db.Column(db.String(100))
    code_postal=db.Column(db.String(20))
    pays=db.Column(db.String(100))


class Produit(db.Model):    #attention ici "Produit", les 3 ont une utilité différente
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

    if Produit.query.count() == 0:
        produits = [
            Produit(nom='Suisse 2024/25', prix=79.95, image='suisse.png'),
            Produit(nom='Ajax 2024/25', prix=69.95, image='ajax.png'),
            Produit(nom='Allemagne 2024/25', prix=79.95, image='allemagne.png'),
            Produit(nom='Arsenal 2024/25', prix=69.95, image='arsenal.png'),
            Produit(nom='Barcelone 2024/25', prix=69.95, image='barca.png'),
            Produit(nom="Côte d’Ivoire 2024/25", prix=79.95, image='cote.png'),
            Produit(nom='Espagne 2024/25', prix=79.95, image='espagne.png'),
            Produit(nom='Real Madrid 2024/25', prix=69.95, image='real.png'),
            Produit(nom='Japon 2024/25', prix=79.95, image='japon1.png'),
            Produit(nom='Brésil 2024/25', prix=79.95, image='bresil1.png'),
            Produit(nom='Mexique 2024/25', prix=79.95, image='mexique1.png'),
            Produit(nom='Barcelone 2015/16', prix=20.00, image='barcelone_2015-2016.png'),
            Produit(nom='Paris 2021/22', prix=109.98, image='Paris.png'),
            Produit(nom='Barcelone 2009/10 maillot enfant (Messi)', prix=49.98, image='barcamessi.png'),
            Produit(nom='Italie Euro 2024', prix=35.00, image='italie enfant.jpg'),
        ]
        db.session.add_all(produits)
        db.session.commit()

@app.route('/')
def produits():     #attention ici "produits"
    produits = Produit.query.all()
    return render_template('produits.html', produits=produits)

@app.route('/ajouter_panier/<int:id>', methods=['POST'])
def ajouter_panier(id):
    produit = Produit.query.get_or_404(id)  #attention ici "produit"
    taille = request.form.get('taille', 'M') 

    if 'panier' not in session:
        session['panier'] = []
    
    panier = session['panier']

    for item in panier:
        if item['id'] == produit.id and item['taille'] == taille:
            item['quantite'] += 1
            break
    else:
        panier.append({
            'id': produit.id,
            'nom': produit.nom,
            'prix': produit.prix,
            'image': produit.image,
            'taille': taille,
            'quantite': 1,
    })
    session['panier'] = panier  #mise a jour session panier
    return redirect(url_for('produits'))


@app.route('/panier')
def panier():
    panier = session.get('panier', [])
    
    return render_template('panier.html', panier=panier,tot=prix_total())

@app.route('/vider_panier')
def vider_panier():
    session.pop('panier', None)
    return redirect(url_for('panier'))



@app.route('/recherche')
def recherche():
    query = request.args.get('requete','').lower()
    resultats = Produit.query.filter(Produit.nom.ilike(f'%{query}%')).all()
    return render_template('produits.html', produits=resultats)


def prix_total():
    panier = session.get('panier', [])
    return sum(item['prix']* item['quantite'] for item in panier)

@app.route('/paiement', methods=['GET', 'POST'])
def paiement():
    total=prix_total()
    panier=session.pop('panier', None)

    user=None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

    if request.method == 'POST':
        if user:
            pass
        else:
            nom=request.form['nom']
            prenom=request.form['prenom']
            email=request.form['email']
            adresse=request.form['adresse']
            code_postal=request.form['code_postal']
            pays=request.form['pays']
            ville=request.form['ville']
            return render_template('paiement_confirmee.html', nom=nom, prenom=prenom,
                email=email, adresse=adresse, ville=ville,
                code_postal=code_postal, pays=pays)
    produits = Produit.query.all()
    return render_template('paiement.html', prods=produits,tot=total, panier=panier,user=user if user else'', nom=user.nom if user else'', 
                           prenom=user.prenom if user else'',email=user.email if user else'',
                           adresse=user.adresse if user else'',ville=user.ville if user else'',
                           code_postal=user.code_postal if user else'',pays=user.pays if user else'')

@app.route('/supprimer_panier/<int:index>')
def supprimer_panier(index):
    panier = session.get('panier', [])
    if 0 <= index < len(panier):
        panier.pop(index)
        session['panier'] = panier
    return redirect(url_for('panier'))

@app.route('/augmanter/<int:index>')
def augmanter(index):
    panier = session.get('panier', [])
    if 0 <= index < len(panier):
        panier[index]['quantite'] += 1
        session['panier'] = panier
    return redirect(url_for('panier'))

@app.route('/diminuer/<int:index>')
def diminuer(index):
    panier = session.get('panier', [])
    if 0 <= index < len(panier):
        if panier[index]['quantite'] > 1:
            panier[index]['quantite'] -= 1
        else:
            panier.pop(index)
        session['panier'] = panier
    return redirect(url_for('panier'))

#partie login
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        nom=request.form['nom']
        prenom=request.form['prenom']
        adresse=request.form['adresse']
        ville = request.form['ville']
        code_postal = request.form['code_postal']
        pays = request.form['pays']
        user = User(username=username, email=email,
                    nom=nom,prenom=prenom,
                    adresse=adresse,ville=ville,
                    code_postal=code_postal,pays=pays)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('produits'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        user = User.query.filter_by(username=username, email=email).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('produits'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('produits'))




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)