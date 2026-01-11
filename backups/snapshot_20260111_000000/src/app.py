try:
    # Preferência: executar como pacote (python -m src.app)
    from src import clientes, destinos, reservas
except Exception:
    try:
        # Executando diretamente a partir da pasta src (python app.py)
        import clientes, destinos, reservas
    except Exception:
        # Última tentativa: import relativo quando executado como módulo interno
        from . import clientes, destinos, reservas

def clientes_menu():
    while True:
        print("\n--- Menu Clientes ---")
        print("1. Cadastrar cliente")
        print("2. Listar clientes")
        print("3. Editar cliente")
        print("4. Excluir cliente")
        print("0. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Nome: ")
            email = input("Email: ")
            telefone = input("Telefone: ")
            clientes.criar_cliente(nome, email, telefone)

        elif opcao == "2":
            clientes.listar_clientes()

        elif opcao == "3":
            clientes.listar_clientes()
            try:
                cliente_id = int(input("ID do cliente a editar: "))
            except ValueError:
                print("ID inválido.")
                continue
            nome = input("Novo nome (Enter para manter): ")
            email = input("Novo email (Enter para manter): ")
            telefone = input("Novo telefone (Enter para manter): ")
            clientes.editar_cliente(cliente_id,
                                    nome if nome != "" else None,
                                    email if email != "" else None,
                                    telefone if telefone != "" else None)

        elif opcao == "4":
            clientes.listar_clientes()
            try:
                cliente_id = int(input("ID do cliente a excluir: "))
            except ValueError:
                print("ID inválido.")
                continue
            clientes.excluir_cliente(cliente_id)

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


def destinos_menu():
    while True:
        print("\n--- Menu Destinos ---")
        print("1. Cadastrar destino")
        print("2. Listar destinos")
        print("3. Editar destino")
        print("4. Excluir destino")
        print("0. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cidade = input("Cidade: ")
            pais = input("País: ")
            try:
                vagas = int(input("Número de vagas: "))
            except ValueError:
                print("Número inválido.")
                continue
            destinos.criar_destino(cidade, pais, vagas)

        elif opcao == "2":
            destinos.listar_destinos()

        elif opcao == "3":
            destinos.listar_destinos()
            try:
                destino_id = int(input("ID do destino a editar: "))
            except ValueError:
                print("ID inválido.")
                continue
            cidade = input("Nova cidade (Enter para manter): ")
            pais = input("Novo país (Enter para manter): ")
            vagas = input("Novo número de vagas (Enter para manter): ")
            destinos.editar_destino(destino_id,
                                    cidade if cidade != "" else None,
                                    pais if pais != "" else None,
                                    int(vagas) if vagas != "" else None)

        elif opcao == "4":
            destinos.listar_destinos()
            try:
                destino_id = int(input("ID do destino a excluir: "))
            except ValueError:
                print("ID inválido.")
                continue
            destinos.excluir_destino(destino_id)

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


def reservas_menu():
    while True:
        print("\n--- Menu Reservas ---")
        print("1. Criar reserva")
        print("2. Listar reservas")
        print("3. Editar/Excluir reserva")
        print("0. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            clientes.listar_clientes()
            try:
                cliente_id = int(input("ID do cliente: "))
            except ValueError:
                print("ID inválido.")
                continue

            destinos.listar_destinos()
            try:
                destino_id = int(input("ID do destino: "))
                vagas = int(input("Número de vagas: "))
            except ValueError:
                print("Número inválido.")
                continue

            reservas.criar_reserva(cliente_id, destino_id, vagas)

        elif opcao == "2":
            reservas.listar_reservas()

        elif opcao == "3":
            reservas.listar_reservas()
            try:
                reserva_id = int(input("ID da reserva a editar: "))
            except ValueError:
                print("ID inválido.")
                continue
            reservas.editar_reserva(reserva_id)

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


def menu_principal():
    while True:
        print("\n=== Sistema de Viagens ===")
        print("1. Clientes")
        print("2. Destinos")
        print("3. Reservas")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            clientes_menu()
        elif opcao == "2":
            destinos_menu()
        elif opcao == "3":
            reservas_menu()
        elif opcao == "0":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu_principal()
