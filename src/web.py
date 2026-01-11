from flask import Flask, render_template, request, redirect, url_for, flash
from src.db import get_conn

app = Flask(__name__)
app.secret_key = "dev-secret"


def get_columns(table_name):
    conn = get_conn()
    try:
        cur = conn.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cur.fetchall()]
    finally:
        conn.close()


def rows_to_dicts(rows):
    return [dict(r) for r in rows]


def detect_vagas_column(destino_row):
    if 'vagas' in destino_row.keys():
        return 'vagas', destino_row['vagas']
    if 'vagas_disponiveis' in destino_row.keys():
        return 'vagas_disponiveis', destino_row['vagas_disponiveis']
    if 'vagas_total' in destino_row.keys():
        return 'vagas_total', destino_row['vagas_total']
    return None, None


def reservas_vagas_column():
    cols = get_columns('reservas')
    if 'vagas_reservadas' in cols:
        return 'vagas_reservadas'
    if 'vagas' in cols:
        return 'vagas'
    return cols[0] if cols else 'vagas'


@app.route('/')
def index():
    return redirect(url_for('listar_clientes'))


@app.route('/clientes', methods=['GET', 'POST'])
def listar_clientes():
    conn = get_conn()
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        try:
            conn.execute("INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)", (nome, email or None, telefone or None))
            conn.commit()
            flash('Cliente cadastrado com sucesso.', 'success')
        except Exception as e:
            flash(f'Erro ao cadastrar cliente: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('listar_clientes'))

    try:
        cur = conn.execute('SELECT * FROM clientes ORDER BY id')
        clientes = rows_to_dicts(cur.fetchall())
    finally:
        conn.close()
    return render_template('clientes.html', clientes=clientes)


@app.route('/destinos', methods=['GET', 'POST'])
def listar_destinos():
    conn = get_conn()
    if request.method == 'POST':
        cidade = request.form.get('cidade')
        pais = request.form.get('pais')
        try:
            vagas = int(request.form.get('vagas') or 0)
        except ValueError:
            vagas = 0

        cols = get_columns('destinos')
        try:
            if 'vagas' in cols:
                conn.execute('INSERT INTO destinos (cidade, pais, vagas) VALUES (?, ?, ?)', (cidade, pais, vagas))
            elif 'vagas_total' in cols and 'vagas_disponiveis' in cols:
                conn.execute('INSERT INTO destinos (cidade, pais, vagas_total, vagas_disponiveis) VALUES (?, ?, ?, ?)', (cidade, pais, vagas, vagas))
            else:
                conn.execute('INSERT INTO destinos (cidade, pais, vagas) VALUES (?, ?, ?)', (cidade, pais, vagas))
            conn.commit()
            flash('Destino cadastrado com sucesso.', 'success')
        except Exception as e:
            flash(f'Erro ao cadastrar destino: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('listar_destinos'))

    try:
        cur = conn.execute('SELECT * FROM destinos ORDER BY id')
        destinos = rows_to_dicts(cur.fetchall())
    finally:
        conn.close()
    return render_template('destinos.html', destinos=destinos)


@app.route('/reservas', methods=['GET', 'POST'])
def listar_reservas():
    conn = get_conn()
    if request.method == 'POST':
        try:
            cliente_id = int(request.form.get('cliente_id'))
            destino_id = int(request.form.get('destino_id'))
            vagas_req = int(request.form.get('vagas'))
        except Exception:
            flash('Dados inválidos.', 'danger')
            return redirect(url_for('listar_reservas'))

        try:
            # verifica existência
            cur = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
            cl = cur.fetchone()
            if not cl:
                flash('Cliente não encontrado.', 'danger')
                return redirect(url_for('listar_reservas'))

            cur = conn.execute('SELECT * FROM destinos WHERE id = ?', (destino_id,))
            destino = cur.fetchone()
            if not destino:
                flash('Destino não encontrado.', 'danger')
                return redirect(url_for('listar_reservas'))

            vagas_col, vagas_disp = detect_vagas_column(destino)
            if vagas_col is None:
                flash('Não foi possível determinar vagas do destino.', 'danger')
                return redirect(url_for('listar_reservas'))

            if vagas_req > vagas_disp:
                flash(f'Não há vagas suficientes. Disponíveis: {vagas_disp}', 'warning')
                return redirect(url_for('listar_reservas'))

            reservas_col = reservas_vagas_column()
            # insere reserva usando a coluna detectada
            conn.execute(f"INSERT INTO reservas (cliente_id, destino_id, {reservas_col}) VALUES (?, ?, ?)", (cliente_id, destino_id, vagas_req))

            # atualiza destino
            if vagas_col == 'vagas':
                conn.execute('UPDATE destinos SET vagas = vagas - ? WHERE id = ?', (vagas_req, destino_id))
            elif vagas_col == 'vagas_disponiveis':
                conn.execute('UPDATE destinos SET vagas_disponiveis = vagas_disponiveis - ? WHERE id = ?', (vagas_req, destino_id))
            elif vagas_col == 'vagas_total':
                conn.execute('UPDATE destinos SET vagas_total = vagas_total - ? WHERE id = ?', (vagas_req, destino_id))

            conn.commit()
            flash('Reserva criada com sucesso.', 'success')
        except Exception as e:
            flash(f'Erro ao criar reserva: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('listar_reservas'))

    try:
        cur = conn.execute('''
            SELECT r.id, c.nome AS cliente, d.cidade, d.pais, r.*
            FROM reservas r
            JOIN clientes c ON r.cliente_id = c.id
            JOIN destinos d ON r.destino_id = d.id
            ORDER BY r.id
        ''')
        reservas = rows_to_dicts(cur.fetchall())
        cur = conn.execute('SELECT id, nome FROM clientes ORDER BY id')
        clientes = rows_to_dicts(cur.fetchall())
        cur = conn.execute('SELECT id, cidade, pais FROM destinos ORDER BY id')
        destinos = rows_to_dicts(cur.fetchall())
    finally:
        conn.close()

    return render_template('reservas.html', reservas=reservas, clientes=clientes, destinos=destinos)


@app.route('/clientes/<int:cliente_id>/edit', methods=['GET', 'POST'])
def editar_cliente(cliente_id):
    conn = get_conn()
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        try:
            conn.execute('UPDATE clientes SET nome = ?, email = ?, telefone = ? WHERE id = ?', (nome, email or None, telefone or None, cliente_id))
            conn.commit()
            flash('Cliente atualizado com sucesso.', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar cliente: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('listar_clientes'))

    try:
        cur = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
        cliente = cur.fetchone()
        if cliente:
            cliente = dict(cliente)
    finally:
        conn.close()
    if not cliente:
        flash('Cliente não encontrado.', 'danger')
        return redirect(url_for('listar_clientes'))
    return render_template('cliente_edit.html', cliente=cliente)


@app.route('/clientes/<int:cliente_id>/delete', methods=['POST'])
def excluir_cliente(cliente_id):
    conn = get_conn()
    try:
        cur = conn.execute('SELECT COUNT(*) as total FROM reservas WHERE cliente_id = ?', (cliente_id,))
        total = cur.fetchone()[0]
        if total > 0:
            flash('Não é possível excluir: cliente possui reservas vinculadas.', 'warning')
            return redirect(url_for('listar_clientes'))
        conn.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
        conn.commit()
        flash('Cliente excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir cliente: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('listar_clientes'))


@app.route('/destinos/<int:destino_id>/edit', methods=['GET', 'POST'])
def editar_destino(destino_id):
    conn = get_conn()
    cols = get_columns('destinos')
    if request.method == 'POST':
        cidade = request.form.get('cidade')
        pais = request.form.get('pais')
        try:
            vagas = int(request.form.get('vagas') or 0)
        except ValueError:
            vagas = 0
        try:
            if 'vagas' in cols:
                conn.execute('UPDATE destinos SET cidade = ?, pais = ?, vagas = ? WHERE id = ?', (cidade, pais, vagas, destino_id))
            elif 'vagas_total' in cols and 'vagas_disponiveis' in cols:
                conn.execute('UPDATE destinos SET cidade = ?, pais = ?, vagas_total = ?, vagas_disponiveis = ? WHERE id = ?', (cidade, pais, vagas, vagas, destino_id))
            else:
                conn.execute('UPDATE destinos SET cidade = ?, pais = ?, vagas = ? WHERE id = ?', (cidade, pais, vagas, destino_id))
            conn.commit()
            flash('Destino atualizado com sucesso.', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar destino: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('listar_destinos'))

    try:
        cur = conn.execute('SELECT * FROM destinos WHERE id = ?', (destino_id,))
        destino = cur.fetchone()
        if destino:
            destino = dict(destino)
    finally:
        conn.close()
    if not destino:
        flash('Destino não encontrado.', 'danger')
        return redirect(url_for('listar_destinos'))
    return render_template('destino_edit.html', destino=destino)


@app.route('/destinos/<int:destino_id>/delete', methods=['POST'])
def excluir_destino(destino_id):
    conn = get_conn()
    try:
        cur = conn.execute('SELECT COUNT(*) as total FROM reservas WHERE destino_id = ?', (destino_id,))
        total = cur.fetchone()[0]
        if total > 0:
            flash('Não é possível excluir: destino possui reservas vinculadas.', 'warning')
            return redirect(url_for('listar_destinos'))
        conn.execute('DELETE FROM destinos WHERE id = ?', (destino_id,))
        conn.commit()
        flash('Destino excluído com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro ao excluir destino: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('listar_destinos'))


def detect_reserva_vagas(reserva):
    if 'vagas_reservadas' in reserva:
        return 'vagas_reservadas', reserva['vagas_reservadas']
    if 'vagas' in reserva:
        return 'vagas', reserva['vagas']
    # fallback: take any int-like column
    for k, v in reserva.items():
        if isinstance(v, int):
            return k, v
    return None, None


@app.route('/reservas/<int:reserva_id>/edit', methods=['GET', 'POST'])
def editar_reserva(reserva_id):
    conn = get_conn()
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            amount = int(request.form.get('amount') or 0)
        except ValueError:
            amount = 0

        try:
            cur = conn.execute('SELECT * FROM reservas WHERE id = ?', (reserva_id,))
            reserva = dict(cur.fetchone() or {})
            if not reserva:
                flash('Reserva não encontrada.', 'danger')
                return redirect(url_for('listar_reservas'))

            cur = conn.execute('SELECT * FROM destinos WHERE id = ?', (reserva['destino_id'],))
            destino = dict(cur.fetchone() or {})
            vagas_col_dest, vagas_disp = detect_vagas_column(destino)
            vagas_col_res, vagas_res = detect_reserva_vagas(reserva)

            if action == 'increase':
                if amount <= 0:
                    flash('Quantidade inválida.', 'warning')
                elif amount > vagas_disp:
                    flash(f'Não há vagas suficientes. Disponíveis: {vagas_disp}', 'warning')
                else:
                    conn.execute(f'UPDATE reservas SET {vagas_col_res} = {vagas_col_res} + ? WHERE id = ?', (amount, reserva_id))
                    if vagas_col_dest == 'vagas':
                        conn.execute('UPDATE destinos SET vagas = vagas - ? WHERE id = ?', (amount, reserva['destino_id']))
                    elif vagas_col_dest == 'vagas_disponiveis':
                        conn.execute('UPDATE destinos SET vagas_disponiveis = vagas_disponiveis - ? WHERE id = ?', (amount, reserva['destino_id']))
                    elif vagas_col_dest == 'vagas_total':
                        conn.execute('UPDATE destinos SET vagas_total = vagas_total - ? WHERE id = ?', (amount, reserva['destino_id']))
                    conn.commit()
                    flash('Reserva aumentada com sucesso.', 'success')

            elif action == 'decrease':
                if amount <= 0 or amount > reserva.get(vagas_col_res, 0):
                    flash('Quantidade inválida.', 'warning')
                else:
                    conn.execute(f'UPDATE reservas SET {vagas_col_res} = {vagas_col_res} - ? WHERE id = ?', (amount, reserva_id))
                    if vagas_col_dest == 'vagas':
                        conn.execute('UPDATE destinos SET vagas = vagas + ? WHERE id = ?', (amount, reserva['destino_id']))
                    elif vagas_col_dest == 'vagas_disponiveis':
                        conn.execute('UPDATE destinos SET vagas_disponiveis = vagas_disponiveis + ? WHERE id = ?', (amount, reserva['destino_id']))
                    elif vagas_col_dest == 'vagas_total':
                        conn.execute('UPDATE destinos SET vagas_total = vagas_total + ? WHERE id = ?', (amount, reserva['destino_id']))
                    conn.commit()
                    flash('Reserva diminuída com sucesso.', 'success')

            elif action == 'delete':
                vagas = reserva.get(vagas_col_res, 0)
                if vagas_col_dest == 'vagas':
                    conn.execute('UPDATE destinos SET vagas = vagas + ? WHERE id = ?', (vagas, reserva['destino_id']))
                elif vagas_col_dest == 'vagas_disponiveis':
                    conn.execute('UPDATE destinos SET vagas_disponiveis = vagas_disponiveis + ? WHERE id = ?', (vagas, reserva['destino_id']))
                elif vagas_col_dest == 'vagas_total':
                    conn.execute('UPDATE destinos SET vagas_total = vagas_total + ? WHERE id = ?', (vagas, reserva['destino_id']))
                conn.execute('DELETE FROM reservas WHERE id = ?', (reserva_id,))
                conn.commit()
                flash('Reserva excluída e vagas devolvidas ao destino.', 'success')

        except Exception as e:
            flash(f'Erro ao editar reserva: {e}', 'danger')
        finally:
            conn.close()
        return redirect(url_for('listar_reservas'))

    try:
        cur = conn.execute("SELECT r.id, r.*, c.nome AS cliente, d.cidade, d.pais FROM reservas r JOIN clientes c ON r.cliente_id = c.id JOIN destinos d ON r.destino_id = d.id WHERE r.id = ?", (reserva_id,))
        row = cur.fetchone()
        reserva = dict(row) if row else None
    finally:
        conn.close()
    if not reserva:
        flash('Reserva não encontrada.', 'danger')
        return redirect(url_for('listar_reservas'))
    return render_template('reserva_edit.html', reserva=reserva)


if __name__ == '__main__':
    app.run(debug=True)
