try:
    from src.db import get_conn
except Exception:
    try:
        from db import get_conn
    except Exception:
        from .db import get_conn

def criar_reserva(cliente_id, destino_id, vagas):
    conn = get_conn()
    try:
        # Verifica se cliente existe
        cur = conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cur.fetchone()
        if not cliente:
            print("Cliente não encontrado.")
            return

        # Verifica se destino existe
        cur = conn.execute("SELECT * FROM destinos WHERE id = ?", (destino_id,))
        destino = cur.fetchone()
        if not destino:
            print("Destino não encontrado.")
            return

        # Verifica vagas disponíveis (compatibilidade com diferentes esquemas)
        if 'vagas' in destino.keys():
            vagas_disp = destino['vagas']
            vagas_col = 'vagas'
        elif 'vagas_disponiveis' in destino.keys():
            vagas_disp = destino['vagas_disponiveis']
            vagas_col = 'vagas_disponiveis'
        elif 'vagas_total' in destino.keys():
            vagas_disp = destino['vagas_total']
            vagas_col = 'vagas_total'
        else:
            print('Não foi possível determinar vagas do destino.')
            return

        if vagas > vagas_disp:
            print(f"Não há vagas suficientes. Disponíveis: {vagas_disp}")
            return

        # Cria reserva
        # ajusta para o esquema existente que usa 'vagas_reservadas'
        conn.execute(
            "INSERT INTO reservas (cliente_id, destino_id, vagas_reservadas) VALUES (?, ?, ?)",
            (cliente_id, destino_id, vagas)
        )

        # Atualiza vagas do destino conforme coluna disponível
        if vagas_col == 'vagas':
            conn.execute(
                "UPDATE destinos SET vagas = vagas - ? WHERE id = ?",
                (vagas, destino_id)
            )
        elif vagas_col == 'vagas_disponiveis':
            conn.execute(
                "UPDATE destinos SET vagas_disponiveis = vagas_disponiveis - ? WHERE id = ?",
                (vagas, destino_id)
            )
        elif vagas_col == 'vagas_total':
            # se só existe vagas_total, decrementa esse valor
            conn.execute(
                "UPDATE destinos SET vagas_total = vagas_total - ? WHERE id = ?",
                (vagas, destino_id)
            )

        conn.commit()
        print(f"Reserva criada com sucesso para {cliente['nome']} em {destino['cidade']}/{destino['pais']}.")
    except Exception as e:
        print(f"Erro ao criar reserva: {e}")
    finally:
        conn.close()


def listar_reservas():
    conn = get_conn()
    try:
        cur = conn.execute("""
            SELECT r.id, c.nome AS cliente, d.cidade, d.pais, r.vagas_reservadas AS vagas
            FROM reservas r
            JOIN clientes c ON r.cliente_id = c.id
            JOIN destinos d ON r.destino_id = d.id
            ORDER BY r.id
        """)
        reservas = cur.fetchall()
        if not reservas:
            print("Nenhuma reserva encontrada.")
        else:
            for row in reservas:
                print(f"ID: {row['id']} | Cliente: {row['cliente']} | Destino: {row['cidade']}/{row['pais']} | Vagas: {row['vagas']}")
    finally:
        conn.close()


def _detect_vagas_column(destino):
    if 'vagas' in destino.keys():
        return 'vagas', destino['vagas']
    if 'vagas_disponiveis' in destino.keys():
        return 'vagas_disponiveis', destino['vagas_disponiveis']
    if 'vagas_total' in destino.keys():
        return 'vagas_total', destino['vagas_total']
    return None, None


def aumentar_reserva(reserva_id, amount):
    conn = get_conn()
    try:
        cur = conn.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,))
        reserva = cur.fetchone()
        if not reserva:
            print("Reserva não encontrada.")
            return

        cur = conn.execute("SELECT * FROM destinos WHERE id = ?", (reserva['destino_id'],))
        destino = cur.fetchone()
        if not destino:
            print("Destino não encontrado.")
            return

        vagas_col, vagas_disp = _detect_vagas_column(destino)
        if vagas_col is None:
            print('Não foi possível determinar coluna de vagas do destino.')
            return

        if amount <= 0:
            print('Valor inválido para aumentar.')
            return

        if amount > vagas_disp:
            print(f"Não há vagas suficientes. Disponíveis: {vagas_disp}")
            return

        # atualiza reserva
        conn.execute(
            "UPDATE reservas SET vagas_reservadas = vagas_reservadas + ? WHERE id = ?",
            (amount, reserva_id)
        )

        # atualiza destino conforme coluna
        if vagas_col == 'vagas':
            conn.execute("UPDATE destinos SET vagas = vagas - ? WHERE id = ?", (amount, reserva['destino_id']))
        elif vagas_col == 'vagas_disponiveis':
            conn.execute("UPDATE destinos SET vagas_disponiveis = vagas_disponiveis - ? WHERE id = ?", (amount, reserva['destino_id']))
        elif vagas_col == 'vagas_total':
            conn.execute("UPDATE destinos SET vagas_total = vagas_total - ? WHERE id = ?", (amount, reserva['destino_id']))

        conn.commit()
        print(f"Reserva {reserva_id} aumentada em {amount} vagas.")
    except Exception as e:
        print(f"Erro ao aumentar reserva: {e}")
    finally:
        conn.close()


def diminuir_reserva(reserva_id, amount):
    conn = get_conn()
    try:
        cur = conn.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,))
        reserva = cur.fetchone()
        if not reserva:
            print("Reserva não encontrada.")
            return

        if amount <= 0:
            print('Valor inválido para diminuir.')
            return

        if amount > reserva['vagas_reservadas']:
            print('Não é possível diminuir mais do que o reservado.')
            return

        cur = conn.execute("SELECT * FROM destinos WHERE id = ?", (reserva['destino_id'],))
        destino = cur.fetchone()
        if not destino:
            print("Destino não encontrado.")
            return

        vagas_col, _ = _detect_vagas_column(destino)
        # atualiza reserva
        conn.execute("UPDATE reservas SET vagas_reservadas = vagas_reservadas - ? WHERE id = ?", (amount, reserva_id))

        # devolve vagas ao destino
        if vagas_col == 'vagas':
            conn.execute("UPDATE destinos SET vagas = vagas + ? WHERE id = ?", (amount, reserva['destino_id']))
        elif vagas_col == 'vagas_disponiveis':
            conn.execute("UPDATE destinos SET vagas_disponiveis = vagas_disponiveis + ? WHERE id = ?", (amount, reserva['destino_id']))
        elif vagas_col == 'vagas_total':
            conn.execute("UPDATE destinos SET vagas_total = vagas_total + ? WHERE id = ?", (amount, reserva['destino_id']))

        conn.commit()
        print(f"Reserva {reserva_id} diminuída em {amount} vagas.")
    except Exception as e:
        print(f"Erro ao diminuir reserva: {e}")
    finally:
        conn.close()


def excluir_reserva(reserva_id):
    conn = get_conn()
    try:
        cur = conn.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,))
        reserva = cur.fetchone()
        if not reserva:
            print("Reserva não encontrada.")
            return

        vagas = reserva['vagas_reservadas']
        cur = conn.execute("SELECT * FROM destinos WHERE id = ?", (reserva['destino_id'],))
        destino = cur.fetchone()
        if not destino:
            print("Destino não encontrado.")
            return

        vagas_col, _ = _detect_vagas_column(destino)
        # devolve vagas ao destino
        if vagas_col == 'vagas':
            conn.execute("UPDATE destinos SET vagas = vagas + ? WHERE id = ?", (vagas, reserva['destino_id']))
        elif vagas_col == 'vagas_disponiveis':
            conn.execute("UPDATE destinos SET vagas_disponiveis = vagas_disponiveis + ? WHERE id = ?", (vagas, reserva['destino_id']))
        elif vagas_col == 'vagas_total':
            conn.execute("UPDATE destinos SET vagas_total = vagas_total + ? WHERE id = ?", (vagas, reserva['destino_id']))

        conn.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
        conn.commit()
        print(f"Reserva {reserva_id} excluída e {vagas} vagas devolvidas ao destino.")
    except Exception as e:
        print(f"Erro ao excluir reserva: {e}")
    finally:
        conn.close()


def editar_reserva(reserva_id):
    try:
        reserva_id = int(reserva_id)
    except Exception:
        print('ID inválido.')
        return

    while True:
        conn = get_conn()
        try:
            cur = conn.execute("SELECT r.id, r.vagas_reservadas, c.nome AS cliente, d.cidade, d.pais FROM reservas r JOIN clientes c ON r.cliente_id = c.id JOIN destinos d ON r.destino_id = d.id WHERE r.id = ?", (reserva_id,))
            row = cur.fetchone()
            if not row:
                print('Reserva não encontrada.')
                return
            print(f"Reserva {row['id']} - Cliente: {row['cliente']} - Destino: {row['cidade']}/{row['pais']} - Vagas reservadas: {row['vagas_reservadas']}")
        finally:
            conn.close()

        print('\n1. Aumentar vagas')
        print('2. Diminuir vagas')
        print('3. Excluir reserva')
        print('0. Voltar')
        opc = input('Escolha uma opção: ')
        if opc == '1':
            try:
                q = int(input('Quantas vagas adicionar? '))
            except ValueError:
                print('Número inválido.')
                continue
            aumentar_reserva(reserva_id, q)
        elif opc == '2':
            try:
                q = int(input('Quantas vagas remover? '))
            except ValueError:
                print('Número inválido.')
                continue
            diminuir_reserva(reserva_id, q)
        elif opc == '3':
            confirm = input('Confirmar exclusão da reserva? (s/n): ').strip().lower()
            if confirm == 's':
                excluir_reserva(reserva_id)
                return
            else:
                print('Exclusão cancelada.')
        elif opc == '0':
            return
        else:
            print('Opção inválida.')
