# database.py - será preenchido com o código completo

import sqlite3
import pandas as pd
from datetime import date
from typing import Optional, List, Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gerenciador de banco de dados para o controle financeiro"""
    
    def __init__(self, db_path: str = "finance_control.db"):
        """
        Inicializa o gerenciador de banco de dados
        
        Args:
            db_path: Caminho para o arquivo SQLite
        """
        self.db_path = db_path
        self.connection = None
        self._create_tables()
    
    def _create_tables(self):
        """Cria as tabelas necessárias se não existirem"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # Tabela de receitas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS receitas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data DATE NOT NULL,
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL,
                    categoria TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de despesas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS despesas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data DATE NOT NULL,
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL,
                    categoria TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de metas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_limite DATE NOT NULL,
                    descricao TEXT NOT NULL,
                    valor_meta REAL NOT NULL,
                    categoria TEXT NOT NULL,
                    status TEXT DEFAULT 'ativa',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de configurações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chave TEXT UNIQUE NOT NULL,
                    valor TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.connection.commit()
            logger.info("Tabelas criadas/verificadas com sucesso")

        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            raise
        finally:
            if self.connection:
                self.connection.close()

    def _get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)

    def _execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """
        Executa uma query e retorna os resultados

        Args:
            query: Query SQL a ser executada
            params: Parâmetros da query

        Returns:
            Lista de tuplas com os resultados
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            results = cursor.fetchall()
            conn.commit()
            conn.close()

            return results

        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            raise

    def _execute_insert(self, query: str, params: tuple) -> int:
        """
        Executa uma query de inserção e retorna o ID do registro inserido

        Args:
            query: Query SQL de inserção
            params: Parâmetros da query

        Returns:
            ID do registro inserido
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(query, params)
            last_id = cursor.lastrowid

            conn.commit()
            conn.close()

            return last_id

        except Exception as e:
            logger.error(f"Erro ao executar inserção: {e}")
            raise

    # Métodos para Receitas
    def adicionar_receita(self, data: date, descricao: str, valor: float,
                         categoria: str) -> int:
        """
        Adiciona uma nova receita

        Args:
            data: Data da receita
            descricao: Descrição da receita
            valor: Valor da receita
            categoria: Categoria da receita

        Returns:
            ID da receita inserida
        """
        query = '''
            INSERT INTO receitas (data, descricao, valor, categoria)
            VALUES (?, ?, ?, ?)
        '''
        params = (data, descricao, valor, categoria)
        return self._execute_insert(query, params)

    def obter_receitas(self, data_inicio: Optional[date] = None,
                      data_fim: Optional[date] = None,
                      categoria: Optional[str] = None) -> pd.DataFrame:
        """
        Obtém receitas com filtros opcionais

        Args:
            data_inicio: Data de início para filtro
            data_fim: Data de fim para filtro
            categoria: Categoria para filtro

        Returns:
            DataFrame com as receitas
        """
        query = "SELECT * FROM receitas WHERE 1=1"
        params = []

        if data_inicio:
            query += " AND data >= ?"
            params.append(data_inicio)

        if data_fim:
            query += " AND data <= ?"
            params.append(data_fim)

        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)

        query += " ORDER BY data DESC"

        results = self._execute_query(query, tuple(params))

        if results:
            df = pd.DataFrame(results, columns=[
                'id', 'data', 'descricao', 'valor', 'categoria',
                'created_at', 'updated_at'
            ])
            df['data'] = pd.to_datetime(df['data'])
            return df
        else:
            return pd.DataFrame(columns=[
                'id', 'data', 'descricao', 'valor', 'categoria',
                'created_at', 'updated_at'
            ])

    def excluir_receita(self, receita_id: int) -> bool:
        """
        Exclui uma receita pelo ID

        Args:
            receita_id: ID da receita a ser excluída

        Returns:
            True se excluída com sucesso
        """
        query = "DELETE FROM receitas WHERE id = ?"
        try:
            self._execute_query(query, (receita_id,))
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir receita: {e}")
            return False

    def atualizar_receita(self, receita_id: int, data: date, descricao: str,
                         valor: float, categoria: str) -> bool:
        """
        Atualiza uma receita existente

        Args:
            receita_id: ID da receita
            data: Nova data
            descricao: Nova descrição
            valor: Novo valor
            categoria: Nova categoria

        Returns:
            True se atualizada com sucesso
        """
        query = '''
            UPDATE receitas 
            SET data = ?, descricao = ?, valor = ?, categoria = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        try:
            self._execute_query(
                query, (data, descricao, valor, categoria, receita_id)
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar receita: {e}")
            return False

    # Métodos para Despesas
    def adicionar_despesa(self, data: date, descricao: str, valor: float,
                         categoria: str) -> int:
        """
        Adiciona uma nova despesa

        Args:
            data: Data da despesa
            descricao: Descrição da despesa
            valor: Valor da despesa
            categoria: Categoria da despesa

        Returns:
            ID da despesa inserida
        """
        query = '''
            INSERT INTO despesas (data, descricao, valor, categoria)
            VALUES (?, ?, ?, ?)
        '''
        params = (data, descricao, valor, categoria)
        return self._execute_insert(query, params)

    def obter_despesas(self, data_inicio: Optional[date] = None,
                      data_fim: Optional[date] = None,
                      categoria: Optional[str] = None) -> pd.DataFrame:
        """
        Obtém despesas com filtros opcionais

        Args:
            data_inicio: Data de início para filtro
            data_fim: Data de fim para filtro
            categoria: Categoria para filtro

        Returns:
            DataFrame com as despesas
        """
        query = "SELECT * FROM despesas WHERE 1=1"
        params = []

        if data_inicio:
            query += " AND data >= ?"
            params.append(data_inicio)

        if data_fim:
            query += " AND data <= ?"
            params.append(data_fim)

        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)

        query += " ORDER BY data DESC"

        results = self._execute_query(query, tuple(params))

        if results:
            df = pd.DataFrame(results, columns=[
                'id', 'data', 'descricao', 'valor', 'categoria',
                'created_at', 'updated_at'
            ])
            df['data'] = pd.to_datetime(df['data'])
            return df
        else:
            return pd.DataFrame(columns=[
                'id', 'data', 'descricao', 'valor', 'categoria',
                'created_at', 'updated_at'
            ])

    def excluir_despesa(self, despesa_id: int) -> bool:
        """
        Exclui uma despesa pelo ID

        Args:
            despesa_id: ID da despesa a ser excluída

        Returns:
            True se excluída com sucesso
        """
        query = "DELETE FROM despesas WHERE id = ?"
        try:
            self._execute_query(query, (despesa_id,))
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir despesa: {e}")
            return False

    def atualizar_despesa(self, despesa_id: int, data: date, descricao: str,
                         valor: float, categoria: str) -> bool:
        """
        Atualiza uma despesa existente

        Args:
            despesa_id: ID da despesa
            data: Nova data
            descricao: Nova descrição
            valor: Novo valor
            categoria: Nova categoria

        Returns:
            True se atualizada com sucesso
        """
        query = '''
            UPDATE despesas 
            SET data = ?, descricao = ?, valor = ?, categoria = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        try:
            self._execute_query(
                query, (data, descricao, valor, categoria, despesa_id)
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar despesa: {e}")
            return False

    # Métodos para Metas
    def adicionar_meta(self, data_limite: date, descricao: str, valor_meta: float,
                      categoria: str) -> int:
        """
        Adiciona uma nova meta

        Args:
            data_limite: Data limite da meta
            descricao: Descrição da meta
            valor_meta: Valor da meta
            categoria: Categoria da meta

        Returns:
            ID da meta inserida
        """
        query = '''
            INSERT INTO metas (data_limite, descricao, valor_meta, categoria)
            VALUES (?, ?, ?, ?)
        '''
        params = (data_limite, descricao, valor_meta, categoria)
        return self._execute_insert(query, params)

    def obter_metas(self, status: Optional[str] = None,
                   categoria: Optional[str] = None) -> pd.DataFrame:
        """
        Obtém metas com filtros opcionais

        Args:
            status: Status da meta (ativa, concluída, etc.)
            categoria: Categoria para filtro

        Returns:
            DataFrame com as metas
        """
        query = "SELECT * FROM metas WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)

        query += " ORDER BY data_limite ASC"

        results = self._execute_query(query, tuple(params))

        if results:
            df = pd.DataFrame(results, columns=[
                'id', 'data_limite', 'descricao', 'valor_meta', 'categoria',
                'status', 'created_at', 'updated_at'
            ])
            df['data_limite'] = pd.to_datetime(df['data_limite'])
            return df
        else:
            return pd.DataFrame(columns=[
                'id', 'data_limite', 'descricao', 'valor_meta', 'categoria',
                'status', 'created_at', 'updated_at'
            ])

    def excluir_meta(self, meta_id: int) -> bool:
        """
        Exclui uma meta pelo ID

        Args:
            meta_id: ID da meta a ser excluída

        Returns:
            True se excluída com sucesso
        """
        query = "DELETE FROM metas WHERE id = ?"
        try:
            self._execute_query(query, (meta_id,))
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir meta: {e}")
            return False

    def atualizar_meta(self, meta_id: int, data_limite: date, descricao: str,
                      valor_meta: float, categoria: str, status: str = None) -> bool:
        """
        Atualiza uma meta existente

        Args:
            meta_id: ID da meta
            data_limite: Nova data limite
            descricao: Nova descrição
            valor_meta: Novo valor da meta
            categoria: Nova categoria
            status: Novo status

        Returns:
            True se atualizada com sucesso
        """
        if status:
            query = '''
                UPDATE metas 
                SET data_limite = ?, descricao = ?, valor_meta = ?, 
                    categoria = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            '''
            params = (data_limite, descricao, valor_meta, categoria, status, meta_id)
        else:
            query = '''
                UPDATE metas 
                SET data_limite = ?, descricao = ?, valor_meta = ?, 
                    categoria = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            '''
            params = (data_limite, descricao, valor_meta, categoria, meta_id)

        try:
            self._execute_query(query, params)
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar meta: {e}")
            return False

    # Métodos de Estatísticas
    def obter_estatisticas_gerais(self, data_inicio: Optional[date] = None,
                                 data_fim: Optional[date] = None) -> Dict[str, Any]:
        """
        Obtém estatísticas gerais do período

        Args:
            data_inicio: Data de início
            data_fim: Data de fim

        Returns:
            Dicionário com estatísticas
        """
        # Filtros de data
        data_filter = ""
        params = []

        if data_inicio and data_fim:
            data_filter = "WHERE data BETWEEN ? AND ?"
            params = [data_inicio, data_fim]
        elif data_inicio:
            data_filter = "WHERE data >= ?"
            params = [data_inicio]
        elif data_fim:
            data_filter = "WHERE data <= ?"
            params = [data_fim]

        # Receitas
        receitas_query = f"SELECT SUM(valor) FROM receitas {data_filter}"
        receitas_result = self._execute_query(receitas_query, tuple(params))
        total_receitas = (receitas_result[0][0] 
                         if receitas_result and receitas_result[0][0] else 0)

        # Despesas
        despesas_query = f"SELECT SUM(valor) FROM despesas {data_filter}"
        despesas_result = self._execute_query(despesas_query, tuple(params))
        total_despesas = (despesas_result[0][0] 
                         if despesas_result and despesas_result[0][0] else 0)

        # Saldo
        saldo = total_receitas - total_despesas

        # Percentual de despesas
        percentual_despesas = ((total_despesas / total_receitas * 100) 
                              if total_receitas > 0 else 0)

        # Contagem de registros
        count_receitas_query = f"SELECT COUNT(*) FROM receitas {data_filter}"
        count_receitas_result = self._execute_query(
            count_receitas_query, tuple(params)
        )
        count_receitas = (count_receitas_result[0][0] 
                         if count_receitas_result else 0)

        count_despesas_query = f"SELECT COUNT(*) FROM despesas {data_filter}"
        count_despesas_result = self._execute_query(
            count_despesas_query, tuple(params)
        )
        count_despesas = (count_despesas_result[0][0] 
                         if count_despesas_result else 0)
        
        return {
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'saldo': saldo,
            'percentual_despesas': percentual_despesas,
            'count_receitas': count_receitas,
            'count_despesas': count_despesas
        }
    
    def obter_despesas_por_categoria(self, data_inicio: Optional[date] = None,
                                   data_fim: Optional[date] = None) -> pd.DataFrame:
        """
        Obtém despesas agrupadas por categoria
        
        Args:
            data_inicio: Data de início
            data_fim: Data de fim
            
        Returns:
            DataFrame com despesas por categoria
        """
        data_filter = ""
        params = []
        
        if data_inicio and data_fim:
            data_filter = "WHERE data BETWEEN ? AND ?"
            params = [data_inicio, data_fim]
        elif data_inicio:
            data_filter = "WHERE data >= ?"
            params = [data_inicio]
        elif data_fim:
            data_filter = "WHERE data <= ?"
            params = [data_fim]
        
        query = f'''
            SELECT categoria, SUM(valor) as total, COUNT(*) as quantidade
            FROM despesas {data_filter}
            GROUP BY categoria
            ORDER BY total DESC
        '''
        
        results = self._execute_query(query, tuple(params))
        
        if results:
            return pd.DataFrame(
                results, columns=['categoria', 'total', 'quantidade']
            )
        else:
            return pd.DataFrame(columns=['categoria', 'total', 'quantidade'])
    
    def obter_receitas_por_categoria(self, data_inicio: Optional[date] = None,
                                   data_fim: Optional[date] = None) -> pd.DataFrame:
        """
        Obtém receitas agrupadas por categoria
        
        Args:
            data_inicio: Data de início
            data_fim: Data de fim
            
        Returns:
            DataFrame com receitas por categoria
        """
        data_filter = ""
        params = []
        
        if data_inicio and data_fim:
            data_filter = "WHERE data BETWEEN ? AND ?"
            params = [data_inicio, data_fim]
        elif data_inicio:
            data_filter = "WHERE data >= ?"
            params = [data_inicio]
        elif data_fim:
            data_filter = "WHERE data <= ?"
            params = [data_fim]
        
        query = f'''
            SELECT categoria, SUM(valor) as total, COUNT(*) as quantidade
            FROM receitas {data_filter}
            GROUP BY categoria
            ORDER BY total DESC
        '''
        
        results = self._execute_query(query, tuple(params))
        
        if results:
            return pd.DataFrame(
                results, columns=['categoria', 'total', 'quantidade']
            )
        else:
            return pd.DataFrame(columns=['categoria', 'total', 'quantidade'])
    
    # Métodos de Backup e Restauração
    def exportar_dados(self) -> Dict[str, pd.DataFrame]:
        """
        Exporta todos os dados do banco
        
        Returns:
            Dicionário com DataFrames de cada tabela
        """
        return {
            'receitas': self.obter_receitas(),
            'despesas': self.obter_despesas(),
            'metas': self.obter_metas()
        }
    
    def importar_dados(self, dados: Dict[str, pd.DataFrame]) -> bool:
        """
        Importa dados para o banco
        
        Args:
            dados: Dicionário com DataFrames para importar
            
        Returns:
            True se importado com sucesso
        """
        try:
            # Limpar dados existentes
            self._execute_query("DELETE FROM receitas")
            self._execute_query("DELETE FROM despesas")
            self._execute_query("DELETE FROM metas")
            
            # Importar receitas
            if 'receitas' in dados and not dados['receitas'].empty:
                for _, row in dados['receitas'].iterrows():
                    self.adicionar_receita(
                        row['data'].date(), row['descricao'], 
                        row['valor'], row['categoria']
                    )
            
            # Importar despesas
            if 'despesas' in dados and not dados['despesas'].empty:
                for _, row in dados['despesas'].iterrows():
                    self.adicionar_despesa(
                        row['data'].date(), row['descricao'], 
                        row['valor'], row['categoria']
                    )
            
            # Importar metas
            if 'metas' in dados and not dados['metas'].empty:
                for _, row in dados['metas'].iterrows():
                    self.adicionar_meta(
                        row['data_limite'].date(), row['descricao'], 
                        row['valor_meta'], row['categoria']
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao importar dados: {e}")
            return False
    
    def limpar_dados(self) -> bool:
        """
        Remove todos os dados do banco
        
        Returns:
            True se limpo com sucesso
        """
        try:
            self._execute_query("DELETE FROM receitas")
            self._execute_query("DELETE FROM despesas")
            self._execute_query("DELETE FROM metas")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar dados: {e}")
            return False
    
    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()


# Função de conveniência para criar instância do banco
def criar_banco(db_path: str = "finance_control.db") -> DatabaseManager:
    """
    Cria uma instância do gerenciador de banco de dados
    
    Args:
        db_path: Caminho para o arquivo SQLite
        
    Returns:
        Instância do DatabaseManager
    """
    return DatabaseManager(db_path)


# Exemplo de uso
if __name__ == "__main__":
    # Criar instância do banco
    db = criar_banco()
    
    # Exemplo de adicionar uma receita
    receita_id = db.adicionar_receita(
        date.today(), "Salário", 5000.0, "Salário"
    )
    print(f"Receita adicionada com ID: {receita_id}")
    
    # Exemplo de obter estatísticas
    stats = db.obter_estatisticas_gerais()
    print(f"Estatísticas: {stats}")
    
    # Fechar conexão
    db.fechar_conexao()
