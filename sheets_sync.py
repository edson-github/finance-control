# sheets_sync.py - será preenchido com o código completo

import os
import sys
import argparse
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configurações
CSV_FILES = {
    'receitas': 'dados/receitas.csv',
    'despesas': 'dados/despesas.csv',
    'metas': 'dados/metas.csv',
}
SHEET_NAME = 'Finance Control'
WORKSHEET_TITLES = {
    'receitas': 'Receitas',
    'despesas': 'Despesas',
    'metas': 'Metas',
}
# Caminho para o arquivo de credenciais do Google
CREDENTIALS_FILE = 'google-credentials.json'

# Colunas esperadas
COLUMNS = {
    'receitas': ['data', 'descricao', 'valor', 'categoria'],
    'despesas': ['data', 'descricao', 'valor', 'categoria'],
    'metas': ['data', 'descricao', 'valor', 'categoria'],
}


def get_gspread_client():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, scope
    )
    client = gspread.authorize(creds)
    return client


def get_or_create_sheet(client, sheet_name):
    try:
        return client.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        return client.create(sheet_name)


def get_or_create_worksheet(sheet, title, cols):
    try:
        ws = sheet.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(
            title=title, rows="1000", cols=str(len(cols))
        )
        ws.append_row(cols)
    return ws


def export_to_sheets():
    client = get_gspread_client()
    sheet = get_or_create_sheet(client, SHEET_NAME)
    for key, csv_path in CSV_FILES.items():
        df = pd.read_csv(csv_path)
        ws = get_or_create_worksheet(
            sheet, WORKSHEET_TITLES[key], COLUMNS[key]
        )
        ws.clear()
        ws.append_row(COLUMNS[key])
        for row in df[COLUMNS[key]].astype(str).values.tolist():
            ws.append_row(row)
    print('Exportação concluída com sucesso!')


def import_from_sheets():
    client = get_gspread_client()
    sheet = get_or_create_sheet(client, SHEET_NAME)
    for key, csv_path in CSV_FILES.items():
        ws = get_or_create_worksheet(
            sheet, WORKSHEET_TITLES[key], COLUMNS[key]
        )
        data = ws.get_all_values()
        if not data or data[0] != COLUMNS[key]:
            print(
                f"Aba '{WORKSHEET_TITLES[key]}' não possui cabeçalho "
                "esperado. Pulando..."
            )
            continue
        df = pd.DataFrame(data[1:], columns=COLUMNS[key])
        df.to_csv(csv_path, index=False)
    print('Importação concluída com sucesso!')


def main():
    parser = argparse.ArgumentParser(
        description='Sincroniza dados locais com Google Sheets.'
    )
    parser.add_argument(
        'action',
        choices=['export', 'import'],
        help='Ação: export (CSV → Sheets) ou import (Sheets → CSV)'
    )
    args = parser.parse_args()

    if not os.path.exists(CREDENTIALS_FILE):
        print(
            f"Arquivo de credenciais '{CREDENTIALS_FILE}' não encontrado. "
            "Siga as instruções do README para obter."
        )
        sys.exit(1)

    if args.action == 'export':
        export_to_sheets()
    elif args.action == 'import':
        import_from_sheets()


if __name__ == '__main__':
    main()

# Instruções de uso:
# 1. Crie um projeto e credenciais de conta de serviço no Google Cloud,
#    compartilhe a planilha com o email do serviço.
# 2. Salve o JSON das credenciais como 'google-credentials.json' na raiz do
#    projeto.
# 3. Execute:
#    python sheets_sync.py export   # Para exportar CSVs locais para o Google
#                                  # Sheets
#    python sheets_sync.py import   # Para importar do Google Sheets para os
#                                  # CSVs locais
