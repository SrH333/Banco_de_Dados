try:
    from src.db import get_conn
except Exception:
    try:
        from db import get_conn
    except Exception:
        from .db import get_conn


def _get_destinos_columns():
    conn = get_conn()
    try:
        cur = conn.execute("PRAGMA table_info(destinos)")
        # resultado: (cid, name, type, notnull, dflt_value, pk)
        return [row[1] for row in cur.fetchall()]
    finally:
        conn.close()

def criar_destino(cidade, pais, vagas):
    conn = get_conn()
    try:
        cols = _get_destinos_columns()
        if "vagas" in cols:
            conn.execute(
                "INSERT INTO destinos (cidade, pais, vagas) VALUES (?, ?, ?)",
                (cidade, pais, vagas)
            )
        elif "vagas_total" in cols and "vagas_disponiveis" in cols:
            conn.execute(
                "INSERT INTO destinos (cidade, pais, vagas_total, vagas_disponiveis) VALUES (?, ?, ?, ?)",
                (cidade, pais, vagas, vagas)
            )
        else:
            conn.execute(
                "INSERT INTO destinos (cidade, pais, vagas) VALUES (?, ?, ?)",
                (cidade, pais, vagas)
            )
        conn.commit()
        print(f"Destino '{cidade}/{pais}' cadastrado com sucesso.")
    except Exception as e:
        print(f"Erro ao cadastrar destino: {e}")
    finally:
        conn.close()


def listar_destinos():
    conn = get_conn()
    try:
        cur = conn.execute("SELECT * FROM destinos ORDER BY id")
        destinos = cur.fetchall()
        if not destinos:
            print("Nenhum destino cadastrado.")
        else:
            for row in destinos:
                # compatibilidade com diferentes esquemas de colunas
                if 'vagas' in row.keys():
                    vagas_disp = row['vagas']
                elif 'vagas_disponiveis' in row.keys():
                    vagas_disp = row['vagas_disponiveis']
                elif 'vagas_total' in row.keys():
                    vagas_disp = row['vagas_total']
                else:
                    vagas_disp = 'N/A'

                print(f"ID: {row['id']} | Cidade: {row['cidade']} | País: {row['pais']} | Vagas: {vagas_disp}")
    finally:
        conn.close()


def buscar_destinos():
    """Retorna lista de destinos (id, cidade, país) para uso em reservas."""
    conn = get_conn()
    try:
        cur = conn.execute("SELECT id, cidade, pais FROM destinos ORDER BY id")
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def editar_destino(destino_id, cidade=None, pais=None, vagas=None):
    conn = get_conn()
    try:
        cur = conn.execute("SELECT * FROM destinos WHERE id = ?", (destino_id,))
        destino = cur.fetchone()
        if not destino:
            print("Destino não encontrado.")
            return

        nova_cidade = cidade if cidade else destino["cidade"]
        novo_pais = pais if pais else destino["pais"]
        cols = _get_destinos_columns()
        if vagas is not None:
            novas_vagas = vagas
        else:
            if 'vagas' in destino.keys():
                novas_vagas = destino['vagas']
            elif 'vagas_disponiveis' in destino.keys():
                novas_vagas = destino['vagas_disponiveis']
            elif 'vagas_total' in destino.keys():
                novas_vagas = destino['vagas_total']
            else:
                novas_vagas = None

        if 'vagas' in cols:
            conn.execute(
                "UPDATE destinos SET cidade = ?, pais = ?, vagas = ? WHERE id = ?",
                (nova_cidade, novo_pais, novas_vagas, destino_id)
            )
        elif 'vagas_total' in cols and 'vagas_disponiveis' in cols:
            conn.execute(
                "UPDATE destinos SET cidade = ?, pais = ?, vagas_total = ?, vagas_disponiveis = ? WHERE id = ?",
                (nova_cidade, novo_pais, novas_vagas, novas_vagas, destino_id)
            )
        else:
            conn.execute(
                "UPDATE destinos SET cidade = ?, pais = ?, vagas = ? WHERE id = ?",
                (nova_cidade, novo_pais, novas_vagas, destino_id)
            )
        conn.commit()
        print("Destino atualizado com sucesso.")
    except Exception as e:
        print(f"Erro ao editar destino: {e}")
    finally:
        conn.close()


def excluir_destino(destino_id):
    conn = get_conn()
    try:
        # Verifica se há reservas vinculadas
        cur = conn.execute("SELECT COUNT(*) AS total FROM reservas WHERE destino_id = ?", (destino_id,))
        total = cur.fetchone()["total"]
        if total > 0:
            print("Não é possível excluir: destino possui reservas vinculadas.")
            return

        cur = conn.execute("SELECT * FROM destinos WHERE id = ?", (destino_id,))
        destino = cur.fetchone()
        if not destino:
            print("Destino não encontrado.")
            return

        confirm = input(f"Confirmar exclusão do destino '{destino['cidade']}/{destino['pais']}'? (s/n): ").strip().lower()
        if confirm != "s":
            print("Exclusão cancelada.")
            return

        conn.execute("DELETE FROM destinos WHERE id = ?", (destino_id,))
        conn.commit()
        print("Destino excluído com sucesso.")
    except Exception as e:
        print(f"Erro ao excluir destino: {e}")
    finally:
        conn.close()