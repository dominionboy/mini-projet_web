from flask import Flask, render_template, request, session
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///produits.db'
app.debug = True
db = SQLAlchemy(app)


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
            'taille': taille
            'quantite': 1
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
    if request.method == 'POST':
        # Ici tu pourrais enregistrer les infos si besoin
        
        return render_template('paiement_confirmee.html')
    produits = Produit.query.all()
    return render_template('paiement.html', prods=produits,tot=total, panier=panier)

@app.route('/supprimer_panier/<int:index>')
def supprimer_panier(index):
    panier = session.get('panier', [])
    if 0 <= index < len(panier):
        panier.pop(index)
        session['panier'] = panier
    return redirect(url_for('panier'))

@app.route('/augemanter/<int: index>')
def augemanter(index):
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




if __name__ == "__main__":
    app.run(debug=True)

