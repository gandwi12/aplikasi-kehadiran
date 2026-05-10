from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Fix DATABASE_URL untuk PostgreSQL Railway
database_url = os.environ.get('DATABASE_URL', 'sqlite:///kehadiran.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Kehadiran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    nim = db.Column(db.String(20), nullable=False)
    tanggal = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), default='hadir')

with app.app_context():
    db.create_all()

@app.route('/')
def beranda():
    return render_template('index.html')

@app.route('/api')
def api_info():
    return jsonify({
        'pesan': 'Aplikasi Pencatatan Kehadiran Mahasiswa',
        'status': 'aktif',
        'versi': '1.0.0',
        'endpoints': ['/api', '/kesehatan', '/kehadiran']
    })

@app.route('/kesehatan')
def cek_kesehatan():
    return jsonify({'status': 'sehat', 'database': 'terhubung'})

@app.route('/kehadiran', methods=['GET'])
def lihat_kehadiran():
    data = Kehadiran.query.all()
    hasil = [{'id': d.id, 'nama': d.nama, 'nim': d.nim,
              'tanggal': d.tanggal, 'status': d.status} for d in data]
    return jsonify({'total': len(hasil), 'data': hasil})

@app.route('/kehadiran', methods=['POST'])
def tambah_kehadiran():
    body = request.get_json()
    baru = Kehadiran(
        nama=body['nama'],
        nim=body['nim'],
        tanggal=body['tanggal'],
        status=body.get('status', 'hadir')
    )
    db.session.add(baru)
    db.session.commit()
    return jsonify({'pesan': 'Kehadiran berhasil dicatat', 'id': baru.id}), 201

@app.route('/kehadiran/<int:id>', methods=['DELETE'])
def hapus_kehadiran(id):
    data = Kehadiran.query.get_or_404(id)
    db.session.delete(data)
    db.session.commit()
    return jsonify({'pesan': f'Data id {id} berhasil dihapus'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)