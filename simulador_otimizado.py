#!/usr/bin/env python3
"""
SIMULADOR OTIMIZADO DE INVESTIMENTOS v4.1
Layout eficiente sem scroll + todas as modalidades + RELATÓRIO DETALHADO + ATUALIZAÇÃO AUTOMÁTICA
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import threading
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import pickle

class TemaOtimizado:
    """Tema otimizado com cores amigáveis"""
    
    CORES = {
        # Cores principais - amigáveis
        'primario': '#2563eb',      # Azul confiável
        'secundario': '#059669',    # Verde natural
        'destaque': '#dc2626',      # Vermelho suave
        'aviso': '#d97706',         # Laranja caloroso
        'info': '#0891b2',          # Ciano
        'sucesso': '#16a34a',       # Verde sucesso
        
        # Tons neutros
        'fundo': '#f8fafc',         # Cinza muito claro
        'card': '#ffffff',          # Branco puro
        'borda': '#e2e8f0',         # Cinza claro
        'texto': '#1e293b',         # Cinza escuro
        'texto_claro': '#64748b',   # Cinza médio
    }
    
    # Fontes otimizadas
    FONTES = {
        'titulo': ('Segoe UI', 14, 'bold'),
        'subtitulo': ('Segoe UI', 11, 'bold'),
        'corpo': ('Segoe UI', 9),
        'corpo_medio': ('Segoe UI', 10),
        'botao': ('Segoe UI', 9, 'bold'),
        'pequeno': ('Segoe UI', 8),
    }

class GerenciadorDados:
    """Gerenciador de dados do Banco Central com cache e atualização automática"""
    
    def __init__(self):
        self.arquivo_cache = "dados_bc_cache.pkl"
        self.url_selic = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        self.intervalo_atualizacao = timedelta(hours=12)  # 12 horas
        
        # Dados padrão
        self.dados = {
            'taxa_selic_anual': 12.75,
            'taxa_selic_mensal': 0.01,
            'ultima_atualizacao': None,
            'data_referencia': None,
            'sucesso_atualizacao': False
        }
        
        # Carregar cache se existir
        self.carregar_cache()
    
    def carregar_cache(self):
        """Carrega dados do cache se existir"""
        try:
            if os.path.exists(self.arquivo_cache):
                with open(self.arquivo_cache, 'rb') as f:
                    dados_cache = pickle.load(f)
                    self.dados.update(dados_cache)
        except Exception:
            pass  # Usar dados padrão se erro no cache
    
    def salvar_cache(self):
        """Salva dados no cache"""
        try:
            with open(self.arquivo_cache, 'wb') as f:
                pickle.dump(self.dados, f)
        except Exception:
            pass  # Continuar mesmo se não conseguir salvar
    
    def precisa_atualizar(self):
        """Verifica se precisa atualizar (mais de 12 horas)"""
        if not self.dados['ultima_atualizacao']:
            return True
        
        agora = datetime.now()
        tempo_decorrido = agora - self.dados['ultima_atualizacao']
        return tempo_decorrido > self.intervalo_atualizacao
    
    def atualizar_dados(self):
        """Atualiza dados do Banco Central"""
        try:
            response = requests.get(self.url_selic, timeout=10)
            if response.status_code == 200:
                dados_api = response.json()
                if dados_api and len(dados_api) > 0:
                    # Processar dados
                    ultimo_dado = dados_api[0]
                    taxa_anual = float(ultimo_dado['valor'])
                    taxa_mensal = (1 + taxa_anual/100)**(1/12) - 1
                    
                    # Validar se a taxa é realista
                    if 0 <= taxa_anual <= 50:
                        self.dados.update({
                            'taxa_selic_anual': taxa_anual,
                            'taxa_selic_mensal': taxa_mensal,
                            'ultima_atualizacao': datetime.now(),
                            'data_referencia': ultimo_dado.get('data', 'N/A'),
                            'sucesso_atualizacao': True
                        })
                        
                        # Salvar no cache
                        self.salvar_cache()
                        return True
            
            # Se chegou aqui, falhou
            self.dados['sucesso_atualizacao'] = False
            return False
            
        except Exception:
            self.dados['sucesso_atualizacao'] = False
            return False
    
    def obter_dados(self, force_update=False):
        """Obtém dados, atualizando se necessário"""
        if force_update or self.precisa_atualizar():
            self.atualizar_dados()
        
        return self.dados.copy()
    
    def obter_info_atualizacao(self):
        """Retorna informações sobre a última atualização"""
        if not self.dados['ultima_atualizacao']:
            return "Dados não atualizados", TemaOtimizado.CORES['aviso']
        
        agora = datetime.now()
        tempo_decorrido = agora - self.dados['ultima_atualizacao']
        
        if tempo_decorrido < timedelta(minutes=30):
            return f"Atualizado há {int(tempo_decorrido.total_seconds() // 60)} min", TemaOtimizado.CORES['sucesso']
        elif tempo_decorrido < timedelta(hours=2):
            return f"Atualizado há {int(tempo_decorrido.total_seconds() // 3600)}h", TemaOtimizado.CORES['sucesso']
        elif tempo_decorrido < timedelta(hours=12):
            horas = int(tempo_decorrido.total_seconds() // 3600)
            return f"Atualizado há {horas}h", TemaOtimizado.CORES['info']
        else:
            return "Dados desatualizados", TemaOtimizado.CORES['aviso']

class ModalidadeInvestimento:
    """Classe para modalidades de investimento"""
    
    def __init__(self, nome, percentual_cdi, tem_ir, liquidez_dias, risco, descricao):
        self.nome = nome
        self.percentual_cdi = percentual_cdi
        self.tem_ir = tem_ir
        self.liquidez_dias = liquidez_dias
        self.risco = risco
        self.descricao = descricao

class FormatadorOtimizado:
    """Formatador brasileiro otimizado"""
    
    @staticmethod
    def formatar_moeda(valor: float, compacto=False) -> str:
        """Formatar valor como moeda brasileira"""
        if compacto and valor >= 1000000:
            return f"R$ {valor/1000000:.1f}M"
        elif compacto and valor >= 1000:
            return f"R$ {valor/1000:.0f}K"
        
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def parse_valor(texto: str) -> float:
        """Converter texto brasileiro para float"""
        if not texto or texto.strip() == "":
            return 0.0
        
        texto = texto.strip().replace('R$', '').replace(' ', '')
        
        if ',' in texto and '.' in texto:
            partes = texto.split(',')
            if len(partes) == 2:
                inteira = partes[0].replace('.', '')
                decimal = partes[1]
                texto = f"{inteira}.{decimal}"
        elif ',' in texto and '.' not in texto:
            texto = texto.replace(',', '.')
        elif texto.count('.') == 1 and len(texto.split('.')[1]) == 3:
            texto = texto.replace('.', '')
        elif texto.count('.') > 1:
            texto = texto.replace('.', '')
        
        try:
            return float(texto)
        except ValueError:
            raise ValueError(f"Formato numérico inválido: {texto}")

class CalculadoraIR:
    """Calculadora de Imposto de Renda"""
    
    TABELA_IR = [
        (180, 0.225),   # Até 180 dias: 22,5%
        (360, 0.20),    # 181-360 dias: 20%
        (720, 0.175),   # 361-720 dias: 17,5%
        (float('inf'), 0.15)  # Acima de 720 dias: 15%
    ]
    
    @staticmethod
    def calcular_ir(rendimento: float, dias: int) -> float:
        """Calcula IR sobre rendimento"""
        if rendimento <= 0:
            return 0
        
        for limite_dias, aliquota in CalculadoraIR.TABELA_IR:
            if dias <= limite_dias:
                return rendimento * aliquota
        return rendimento * 0.15

class SimuladorOtimizado:
    """Simulador Otimizado v4.1 - Layout eficiente sem scroll + RELATÓRIO DETALHADO + ATUALIZAÇÃO AUTOMÁTICA"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Simulador Otimizado v4.1 - Com Atualização Automática")
        
        # Configurar janela otimizada (sem scroll)
        self.configurar_janela_otimizada()
        
        # Variáveis
        self.formatador = FormatadorOtimizado()
        self.gerenciador_dados = GerenciadorDados()
        self.resultados_df = None
        self.dados_ultima_simulacao = None
        
        # Modalidades completas restauradas
        self.modalidades = {
            'CDI 100%': ModalidadeInvestimento('CDI 100%', 100.0, True, 0, 'Baixo', 'Renda fixa tradicional'),
            'CDI 102%': ModalidadeInvestimento('CDI 102%', 102.0, True, 30, 'Baixo', 'CDB com pequeno prêmio'),
            'CDI 103%': ModalidadeInvestimento('CDI 103%', 103.0, True, 30, 'Baixo', 'CDB com prêmio'),
            'CDI 105%': ModalidadeInvestimento('CDI 105%', 105.0, True, 60, 'Baixo', 'CDB com prêmio médio'),
            'CDI 110%': ModalidadeInvestimento('CDI 110%', 110.0, True, 90, 'Baixo', 'CDB com bom prêmio'),
            'CDI 115%': ModalidadeInvestimento('CDI 115%', 115.0, True, 180, 'Baixo', 'CDB premium'),
            'CDI 116%': ModalidadeInvestimento('CDI 116%', 116.0, True, 180, 'Baixo', 'CDB com alto prêmio'),
            'CDI 120%': ModalidadeInvestimento('CDI 120%', 120.0, True, 360, 'Baixo', 'CDB com carência'),
            'Poupança': ModalidadeInvestimento('Poupança', 70.0, False, 0, 'Baixo', 'Caderneta tradicional'),
            'Tesouro Selic': ModalidadeInvestimento('Tesouro Selic', 100.0, True, 0, 'Baixo', 'Título público pós-fixado'),
            'LCI/LCA': ModalidadeInvestimento('LCI/LCA', 90.0, False, 90, 'Baixo', 'Imóvel/Agro sem IR'),
            'Fundos DI': ModalidadeInvestimento('Fundos DI', 95.0, True, 30, 'Baixo', 'Fundos referenciados'),
            'Tesouro IPCA+': ModalidadeInvestimento('Tesouro IPCA+', 105.0, True, 0, 'Médio', 'Protegido da inflação'),
            'CRI/CRA': ModalidadeInvestimento('CRI/CRA', 110.0, False, 180, 'Médio', 'Certificados imobiliários'),
            'Debêntures': ModalidadeInvestimento('Debêntures', 115.0, True, 360, 'Médio', 'Títulos corporativos'),
            'Renda Variável': ModalidadeInvestimento('Renda Variável', 150.0, True, 0, 'Alto', 'Ações e ETFs'),
            'Personalizado': ModalidadeInvestimento('Personalizado', 105.0, True, 90, 'Variável', 'Configure seu próprio %')
        }
        
        # Configurar interface
        self.configurar_estilos()
        self.criar_interface_otimizada()
        self.carregar_dados_mercado()
    
    def configurar_janela_otimizada(self):
        """Configura janela otimizada sem scroll"""
        # Obter dimensões da tela
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        
        # Calcular tamanho otimizado (85% da tela)
        largura_ideal = min(max(int(largura_tela * 0.85), 1200), 1600)
        altura_ideal = min(max(int(altura_tela * 0.85), 800), 1000)
        
        # Centralizar
        x = (largura_tela - largura_ideal) // 2
        y = (altura_tela - altura_ideal) // 2
        
        self.root.geometry(f"{largura_ideal}x{altura_ideal}+{x}+{y}")
        self.root.minsize(1200, 800)
        self.root.configure(bg=TemaOtimizado.CORES['fundo'])
        
        # Configurar peso das colunas/linhas
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def configurar_estilos(self):
        """Configura estilos otimizados"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('Card.TFrame', background=TemaOtimizado.CORES['card'])
        self.style.configure('Modern.TLabel', 
                           background=TemaOtimizado.CORES['card'],
                           foreground=TemaOtimizado.CORES['texto'],
                           font=TemaOtimizado.FONTES['corpo'])
    
    def criar_interface_otimizada(self):
        """Cria interface otimizada sem scroll"""
        # Container principal fixo (sem scroll)
        main_container = tk.Frame(self.root, bg=TemaOtimizado.CORES['fundo'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header compacto
        self.criar_header_compacto(main_container)
        
        # Corpo otimizado
        self.criar_corpo_otimizado(main_container)
    
    def criar_header_compacto(self, parent):
        """Cria header compacto com informações de atualização"""
        header_frame = tk.Frame(parent, bg=TemaOtimizado.CORES['fundo'], height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Título à esquerda
        titulo = tk.Label(header_frame,
                         text="💰 Simulador Otimizado v4.1 + Auto-Update",
                         font=TemaOtimizado.FONTES['titulo'],
                         bg=TemaOtimizado.CORES['fundo'],
                         fg=TemaOtimizado.CORES['primario'])
        titulo.pack(side=tk.LEFT, anchor='w')
        
        # Info à direita
        info_frame = tk.Frame(header_frame, bg=TemaOtimizado.CORES['fundo'])
        info_frame.pack(side=tk.RIGHT, anchor='e')
        
        # Taxa Selic atual
        self.info_selic = tk.Label(info_frame,
                                  text="Carregando Selic...",
                                  font=TemaOtimizado.FONTES['corpo'],
                                  bg=TemaOtimizado.CORES['fundo'],
                                  fg=TemaOtimizado.CORES['sucesso'])
        self.info_selic.pack(anchor='e')
        
        # Última atualização
        self.info_atualizacao = tk.Label(info_frame,
                                        text="Verificando atualização...",
                                        font=TemaOtimizado.FONTES['pequeno'],
                                        bg=TemaOtimizado.CORES['fundo'],
                                        fg=TemaOtimizado.CORES['texto_claro'])
        self.info_atualizacao.pack(anchor='e', pady=(2, 0))
        
        # Botão atualizar manual
        self.btn_atualizar = tk.Button(info_frame,
                                      text="🔄 Atualizar",
                                      command=self.atualizar_manual,
                                      font=TemaOtimizado.FONTES['pequeno'],
                                      bg=TemaOtimizado.CORES['info'],
                                      fg='white',
                                      relief='flat',
                                      padx=8, pady=2)
        self.btn_atualizar.pack(anchor='e', pady=(3, 0))
    
    def criar_corpo_otimizado(self, parent):
        """Cria corpo otimizado que preenche a tela"""
        corpo_frame = tk.Frame(parent, bg=TemaOtimizado.CORES['fundo'])
        corpo_frame.pack(fill=tk.BOTH, expand=True)
        
        # PanedWindow otimizado
        self.paned_window = tk.PanedWindow(corpo_frame, 
                                          orient=tk.HORIZONTAL,
                                          bg=TemaOtimizado.CORES['fundo'],
                                          sashwidth=6,
                                          sashrelief='flat')
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Painel esquerdo - Configuração (35%)
        self.config_panel = tk.Frame(self.paned_window, bg=TemaOtimizado.CORES['fundo'])
        self.paned_window.add(self.config_panel, minsize=400)
        
        # Painel direito - Resultados (65%)
        self.resultado_panel = tk.Frame(self.paned_window, bg=TemaOtimizado.CORES['fundo'])
        self.paned_window.add(self.resultado_panel, minsize=600)
        
        # Criar conteúdo dos painéis
        self.criar_painel_config_compacto()
        self.criar_painel_resultados_otimizado()
    
    def criar_painel_config_compacto(self):
        """Cria painel de configuração compacto"""
        # Card único para tudo
        main_card = tk.Frame(self.config_panel, 
                           bg=TemaOtimizado.CORES['card'],
                           relief='solid', bd=1)
        main_card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Padding interno
        content = tk.Frame(main_card, bg=TemaOtimizado.CORES['card'])
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Seção 1: Modalidade (compacta)
        self.criar_secao_modalidade(content)
        
        # Seção 2: Valores (compacta)
        self.criar_secao_valores(content)
        
        # Seção 3: Opções (compacta)
        self.criar_secao_opcoes(content)
        
        # Seção 4: Botões (compacta)
        self.criar_secao_botoes(content)
        
        # Seção 5: Comparativo (nova)
        self.criar_secao_comparativo(content)
    
    def criar_secao_modalidade(self, parent):
        """Cria seção de modalidade compacta"""
        # Título
        titulo = tk.Label(parent, text="🎯 Modalidade",
                         font=TemaOtimizado.FONTES['subtitulo'],
                         bg=TemaOtimizado.CORES['card'],
                         fg=TemaOtimizado.CORES['texto'])
        titulo.pack(anchor='w', pady=(0, 5))
        
        # Frame horizontal para modalidade + %
        modal_frame = tk.Frame(parent, bg=TemaOtimizado.CORES['card'])
        modal_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Combobox modalidade
        self.modalidade_var = tk.StringVar(value="CDI 105%")
        modalidade_combo = ttk.Combobox(modal_frame,
                                       textvariable=self.modalidade_var,
                                       values=list(self.modalidades.keys()),
                                       state="readonly",
                                       font=TemaOtimizado.FONTES['corpo'],
                                       width=18)
        modalidade_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        modalidade_combo.bind('<<ComboboxSelected>>', self.on_modalidade_change)
        
        # Percentual CDI
        tk.Label(modal_frame, text="% CDI:",
                font=TemaOtimizado.FONTES['corpo'],
                bg=TemaOtimizado.CORES['card'],
                fg=TemaOtimizado.CORES['texto']).pack(side=tk.LEFT, padx=(10, 5))
        
        self.perc_entry = tk.Entry(modal_frame,
                                  font=TemaOtimizado.FONTES['corpo'],
                                  width=8,
                                  justify='center')
        self.perc_entry.pack(side=tk.LEFT)
        self.perc_entry.bind('<KeyRelease>', self.on_percentual_change)
        
        # Taxa calculada
        self.taxa_label = tk.Label(parent,
                                  text="Taxa mensal: Calculando...",
                                  font=TemaOtimizado.FONTES['pequeno'],
                                  bg=TemaOtimizado.CORES['card'],
                                  fg=TemaOtimizado.CORES['info'])
        self.taxa_label.pack(anchor='w', pady=(0, 15))
    
    def criar_secao_valores(self, parent):
        """Cria seção de valores compacta"""
        # Título
        titulo = tk.Label(parent, text="💰 Valores",
                         font=TemaOtimizado.FONTES['subtitulo'],
                         bg=TemaOtimizado.CORES['card'],
                         fg=TemaOtimizado.CORES['texto'])
        titulo.pack(anchor='w', pady=(0, 5))
        
        # Toggle para modo de cálculo
        toggle_frame = tk.Frame(parent, bg=TemaOtimizado.CORES['card'])
        toggle_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Variável para modo de cálculo
        self.modo_calculo = tk.StringVar(value="normal")
        
        # Radio buttons para alternar modo
        modo_normal = tk.Radiobutton(toggle_frame,
                                    text="📊 Calcular Rendimento",
                                    variable=self.modo_calculo,
                                    value="normal",
                                    command=self.alternar_modo_calculo,
                                    font=TemaOtimizado.FONTES['pequeno'],
                                    bg=TemaOtimizado.CORES['card'],
                                    fg=TemaOtimizado.CORES['texto'])
        modo_normal.pack(side=tk.LEFT, padx=(0, 15))
        
        modo_reverso = tk.Radiobutton(toggle_frame,
                                     text="🎯 Calcular Valor Necessário",
                                     variable=self.modo_calculo,
                                     value="reverso",
                                     command=self.alternar_modo_calculo,
                                     font=TemaOtimizado.FONTES['pequeno'],
                                     bg=TemaOtimizado.CORES['card'],
                                     fg=TemaOtimizado.CORES['texto'])
        modo_reverso.pack(side=tk.LEFT)
        
        # Grid para valores - será alterado dinamicamente
        self.valores_frame = tk.Frame(parent, bg=TemaOtimizado.CORES['card'])
        self.valores_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Configurar grid
        self.valores_frame.grid_columnconfigure(1, weight=1)
        
        # Criar campos iniciais (modo normal)
        self.criar_campos_modo_normal()
    
    def alternar_modo_calculo(self):
        """Alterna entre modo normal e reverso"""
        # Limpar frame atual
        for widget in self.valores_frame.winfo_children():
            widget.destroy()
        
        if self.modo_calculo.get() == "normal":
            self.criar_campos_modo_normal()
        else:
            self.criar_campos_modo_reverso()
    
    def criar_campos_modo_normal(self):
        """Cria campos para modo normal (calcular rendimento)"""
        # Valor inicial
        tk.Label(self.valores_frame, text="Inicial:",
                font=TemaOtimizado.FONTES['corpo'],
                bg=TemaOtimizado.CORES['card'],
                fg=TemaOtimizado.CORES['texto']).grid(row=0, column=0, sticky='w', pady=3)
        
        self.valor_inicial_entry = tk.Entry(self.valores_frame,
                                           font=TemaOtimizado.FONTES['corpo'])
        self.valor_inicial_entry.grid(row=0, column=1, sticky='ew', padx=(5, 0), pady=3)
        self.valor_inicial_entry.insert(0, "30.000,00")
        
        # Aporte mensal
        tk.Label(self.valores_frame, text="Mensal:",
                font=TemaOtimizado.FONTES['corpo'],
                bg=TemaOtimizado.CORES['card'],
                fg=TemaOtimizado.CORES['texto']).grid(row=1, column=0, sticky='w', pady=3)
        
        self.aporte_entry = tk.Entry(self.valores_frame,
                                    font=TemaOtimizado.FONTES['corpo'])
        self.aporte_entry.grid(row=1, column=1, sticky='ew', padx=(5, 0), pady=3)
        self.aporte_entry.insert(0, "2.500,00")
        
        # Meta
        tk.Label(self.valores_frame, text="Meta:",
                font=TemaOtimizado.FONTES['corpo'],
                bg=TemaOtimizado.CORES['card'],
                fg=TemaOtimizado.CORES['texto']).grid(row=2, column=0, sticky='w', pady=3)
        
        self.meta_entry = tk.Entry(self.valores_frame,
                                  font=TemaOtimizado.FONTES['corpo'])
        self.meta_entry.grid(row=2, column=1, sticky='ew', padx=(5, 0), pady=3)
        self.meta_entry.insert(0, "500.000,00")
    
    def criar_campos_modo_reverso(self):
        """Cria campos para modo reverso (calcular valor necessário)"""
        # Rendimento mensal desejado
        tk.Label(self.valores_frame, text="Rendimento Desejado:",
                font=TemaOtimizado.FONTES['corpo'],
                bg=TemaOtimizado.CORES['card'],
                fg=TemaOtimizado.CORES['texto']).grid(row=0, column=0, sticky='w', pady=3)
        
        self.rendimento_desejado_entry = tk.Entry(self.valores_frame,
                                                 font=TemaOtimizado.FONTES['corpo'])
        self.rendimento_desejado_entry.grid(row=0, column=1, sticky='ew', padx=(5, 0), pady=3)
        self.rendimento_desejado_entry.insert(0, "5.000,00")
        
        # Prazo em meses
        tk.Label(self.valores_frame, text="Prazo (meses):",
                font=TemaOtimizado.FONTES['corpo'],
                bg=TemaOtimizado.CORES['card'],
                fg=TemaOtimizado.CORES['texto']).grid(row=1, column=0, sticky='w', pady=3)
        
        self.prazo_entry = tk.Entry(self.valores_frame,
                                   font=TemaOtimizado.FONTES['corpo'])
        self.prazo_entry.grid(row=1, column=1, sticky='ew', padx=(5, 0), pady=3)
        self.prazo_entry.insert(0, "12")
        
        # Aporte mensal (opcional)
        tk.Label(self.valores_frame, text="Aporte Mensal:",
                font=TemaOtimizado.FONTES['corpo'],
                bg=TemaOtimizado.CORES['card'],
                fg=TemaOtimizado.CORES['texto']).grid(row=2, column=0, sticky='w', pady=3)
        
        self.aporte_reverso_entry = tk.Entry(self.valores_frame,
                                            font=TemaOtimizado.FONTES['corpo'])
        self.aporte_reverso_entry.grid(row=2, column=1, sticky='ew', padx=(5, 0), pady=3)
        self.aporte_reverso_entry.insert(0, "0,00")
    
    def criar_secao_opcoes(self, parent):
        """Cria seção de opções compacta"""
        # Título
        titulo = tk.Label(parent, text="⚙️ Opções",
                         font=TemaOtimizado.FONTES['subtitulo'],
                         bg=TemaOtimizado.CORES['card'],
                         fg=TemaOtimizado.CORES['texto'])
        titulo.pack(anchor='w', pady=(0, 5))
        
        # Checkboxes horizontais
        opcoes_frame = tk.Frame(parent, bg=TemaOtimizado.CORES['card'])
        opcoes_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.considerar_ir = tk.BooleanVar(value=True)
        ir_check = tk.Checkbutton(opcoes_frame, 
                                 text="IR",
                                 variable=self.considerar_ir,
                                 font=TemaOtimizado.FONTES['corpo'],
                                 bg=TemaOtimizado.CORES['card'],
                                 fg=TemaOtimizado.CORES['texto'])
        ir_check.pack(side=tk.LEFT, padx=(0, 15))
        
        self.considerar_inflacao = tk.BooleanVar(value=False)
        inflacao_check = tk.Checkbutton(opcoes_frame, 
                                       text="Inflação",
                                       variable=self.considerar_inflacao,
                                       font=TemaOtimizado.FONTES['corpo'],
                                       bg=TemaOtimizado.CORES['card'],
                                       fg=TemaOtimizado.CORES['texto'])
        inflacao_check.pack(side=tk.LEFT)
    
    def criar_secao_botoes(self, parent):
        """Cria seção de botões compacta"""
        botoes_frame = tk.Frame(parent, bg=TemaOtimizado.CORES['card'])
        botoes_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Botão principal
        btn_calcular = tk.Button(botoes_frame, 
                               text="🚀 Calcular",
                               command=self.calcular,
                               font=TemaOtimizado.FONTES['botao'],
                               bg=TemaOtimizado.CORES['primario'],
                               fg='white',
                               relief='flat',
                               pady=8)
        btn_calcular.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        # Botões secundários - mesmo tamanho e alinhamento
        btn_limpar = tk.Button(botoes_frame, 
                             text="🗑️",
                             command=self.limpar_formulario,
                             font=TemaOtimizado.FONTES['botao'],
                             bg=TemaOtimizado.CORES['destaque'],
                             fg='white',
                             relief='flat',
                             width=3,
                             height=1,
                             pady=8)
        btn_limpar.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_comparar = tk.Button(botoes_frame, 
                               text="⚖️",
                               command=self.comparar_modalidades,
                               font=TemaOtimizado.FONTES['botao'],
                               bg=TemaOtimizado.CORES['aviso'],
                               fg='white',
                               relief='flat',
                               width=3,
                               height=1,
                               pady=8)
        btn_comparar.pack(side=tk.LEFT)
        
        # Adicionar tooltips aos botões
        self.criar_tooltip(btn_limpar, "Limpar formulário")
        self.criar_tooltip(btn_comparar, "Comparar modalidades")
    
    def criar_secao_comparativo(self, parent):
        """Cria seção de comparativo rápido"""
        # Título
        titulo = tk.Label(parent, text="⚖️ Comparativo Rápido",
                         font=TemaOtimizado.FONTES['subtitulo'],
                         bg=TemaOtimizado.CORES['card'],
                         fg=TemaOtimizado.CORES['texto'])
        titulo.pack(anchor='w', pady=(0, 5))
        
        # Frame para comparativo
        comp_frame = tk.Frame(parent, bg=TemaOtimizado.CORES['card'])
        comp_frame.pack(fill=tk.X)
        
        # Botões de comparação rápida
        btn_frame = tk.Frame(comp_frame, bg=TemaOtimizado.CORES['card'])
        btn_frame.pack(fill=tk.X)
        
        # Comparações comuns
        comparacoes = [
            ("Poupança vs CDI", lambda: self.comparacao_rapida(['Poupança', 'CDI 105%'])),
            ("Tesouro vs CDI", lambda: self.comparacao_rapida(['Tesouro Selic', 'CDI 110%'])),
            ("Baixo vs Alto Risco", lambda: self.comparacao_rapida(['LCI/LCA', 'Renda Variável']))
        ]
        
        for i, (texto, comando) in enumerate(comparacoes):
            btn = tk.Button(btn_frame,
                          text=texto,
                          command=comando,
                          font=TemaOtimizado.FONTES['pequeno'],
                          bg=TemaOtimizado.CORES['secundario'],
                          fg='white',
                          relief='flat',
                          pady=4)
            btn.pack(fill=tk.X, pady=2)
    
    def criar_painel_resultados_otimizado(self):
        """Cria painel de resultados otimizado"""
        # Notebook otimizado
        self.notebook = ttk.Notebook(self.resultado_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba Dashboard
        self.dash_frame = tk.Frame(self.notebook, bg=TemaOtimizado.CORES['fundo'])
        self.notebook.add(self.dash_frame, text="🎯 Dashboard")
        
        # Aba Comparativo
        self.comparativo_frame = tk.Frame(self.notebook, bg=TemaOtimizado.CORES['fundo'])
        self.notebook.add(self.comparativo_frame, text="⚖️ Comparativo")
        
        # Aba Relatório
        self.relatorio_frame = tk.Frame(self.notebook, bg=TemaOtimizado.CORES['fundo'])
        self.notebook.add(self.relatorio_frame, text="📄 Relatório")
        
        # Dashboard inicial
        self.criar_dashboard_inicial()
        
        # Criar aba relatório
        self.criar_aba_relatorio()
    
    def criar_aba_relatorio(self):
        """Cria aba de relatório detalhado"""
        # Toolbar com botões de exportação
        toolbar_frame = tk.Frame(self.relatorio_frame, bg=TemaOtimizado.CORES['fundo'])
        toolbar_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botão Exportar TXT
        btn_exportar = tk.Button(toolbar_frame, 
                               text="📄 Exportar TXT",
                               command=self.exportar_relatorio,
                               font=TemaOtimizado.FONTES['botao'],
                               bg=TemaOtimizado.CORES['primario'],
                               fg='white',
                               relief='flat',
                               padx=15, pady=6)
        btn_exportar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Copiar
        btn_copiar = tk.Button(toolbar_frame, 
                             text="📋 Copiar",
                             command=self.copiar_relatorio,
                             font=TemaOtimizado.FONTES['botao'],
                             bg=TemaOtimizado.CORES['secundario'],
                             fg='white',
                             relief='flat',
                             padx=15, pady=6)
        btn_copiar.pack(side=tk.LEFT)
        
        # Frame para área de texto
        text_frame = tk.Frame(self.relatorio_frame, bg=TemaOtimizado.CORES['fundo'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Área de texto com scroll
        self.relatorio_text = tk.Text(text_frame, 
                                     font=('Consolas', 10), 
                                     wrap=tk.WORD,
                                     bg=TemaOtimizado.CORES['card'],
                                     fg=TemaOtimizado.CORES['texto'],
                                     relief='solid', bd=1)
        
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", 
                               command=self.relatorio_text.yview)
        self.relatorio_text.configure(yscrollcommand=scrollbar.set)
        
        self.relatorio_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Placeholder inicial
        self.relatorio_text.insert(tk.END, 
                                  "📄 RELATÓRIO DETALHADO\n\n" +
                                  "Execute uma simulação para gerar o relatório completo.\n\n" +
                                  "O relatório incluirá:\n" +
                                  "• Informações gerais da simulação\n" +
                                  "• Resumo financeiro completo\n" +
                                  "• Análise de performance\n" +
                                  "• Evolução mensal detalhada\n" +
                                  "• Dados exportáveis em TXT")
        self.relatorio_text.config(state=tk.DISABLED)
    
    def criar_dashboard_inicial(self):
        """Cria dashboard inicial otimizado"""
        # Limpar dashboard
        for widget in self.dash_frame.winfo_children():
            widget.destroy()
        
        # Container principal
        dash_container = tk.Frame(self.dash_frame, bg=TemaOtimizado.CORES['fundo'])
        dash_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo = tk.Label(dash_container,
                         text="🎯 Dashboard do Simulador",
                         font=TemaOtimizado.FONTES['titulo'],
                         bg=TemaOtimizado.CORES['fundo'],
                         fg=TemaOtimizado.CORES['texto'])
        titulo.pack(anchor='w', pady=(0, 20))
        
        # Card de instruções
        instrucoes_frame = tk.Frame(dash_container, 
                                   bg=TemaOtimizado.CORES['card'],
                                   relief='solid', bd=1)
        instrucoes_frame.pack(fill=tk.X, pady=(0, 15))
        
        instrucoes_content = tk.Frame(instrucoes_frame, bg=TemaOtimizado.CORES['card'])
        instrucoes_content.pack(fill=tk.X, padx=20, pady=15)
        
        instrucoes_titulo = tk.Label(instrucoes_content,
                                    text="📋 Como usar:",
                                    font=TemaOtimizado.FONTES['subtitulo'],
                                    bg=TemaOtimizado.CORES['card'],
                                    fg=TemaOtimizado.CORES['texto'])
        instrucoes_titulo.pack(anchor='w')
        
        instrucoes_texto = tk.Label(instrucoes_content,
                                   text="1. Configure a modalidade e valores no painel esquerdo\n"
                                        "2. Clique em '🚀 Calcular' para executar a simulação\n"
                                        "3. Explore as abas de Comparativo e Relatório\n"
                                        "4. Use os botões de exportação no Relatório",
                                   font=TemaOtimizado.FONTES['corpo'],
                                   bg=TemaOtimizado.CORES['card'],
                                   fg=TemaOtimizado.CORES['texto_claro'],
                                   justify=tk.LEFT)
        instrucoes_texto.pack(anchor='w', pady=(5, 0))
        
        # Placeholder para execução de simulação
        placeholder = tk.Label(dash_container,
                              text="▶️\n\nExecute uma simulação para ver os resultados aqui",
                              font=TemaOtimizado.FONTES['subtitulo'],
                              bg=TemaOtimizado.CORES['fundo'],
                              fg=TemaOtimizado.CORES['texto_claro'])
        placeholder.pack(expand=True)
    

    
    # Métodos de atualização automática
    def carregar_dados_mercado(self):
        """Carrega dados do mercado com atualização automática"""
        def carregar_async():
            try:
                # Obter dados (com verificação de 12h automática)
                dados = self.gerenciador_dados.obter_dados()
                
                # Atualizar interface no thread principal
                self.root.after(0, lambda: self.atualizar_interface_dados(dados))
                
            except Exception:
                self.root.after(0, lambda: self.info_selic.config(
                    text="📡 Erro ao carregar dados",
                    fg=TemaOtimizado.CORES['destaque']
                ))
        
        # Executar em thread separada
        thread = threading.Thread(target=carregar_async)
        thread.daemon = True
        thread.start()
    
    def atualizar_interface_dados(self, dados):
        """Atualiza interface com dados do Banco Central"""
        # Atualizar taxa Selic
        taxa_anual = dados['taxa_selic_anual']
        self.info_selic.config(
            text=f"🏛️ Selic: {taxa_anual:.2f}% a.a.",
            fg=TemaOtimizado.CORES['sucesso'] if dados['sucesso_atualizacao'] else TemaOtimizado.CORES['aviso']
        )
        
        # Atualizar informação de última atualização
        info_texto, cor = self.gerenciador_dados.obter_info_atualizacao()
        self.info_atualizacao.config(text=info_texto, fg=cor)
        
        # Atualizar taxa na modalidade
        self.atualizar_taxa_modalidade()
    
    def atualizar_manual(self):
        """Força atualização manual dos dados"""
        def atualizar_async():
            # Mostrar que está atualizando
            self.root.after(0, lambda: self.info_atualizacao.config(
                text="Atualizando...", 
                fg=TemaOtimizado.CORES['info']
            ))
            
            # Forçar atualização
            dados = self.gerenciador_dados.obter_dados(force_update=True)
            
            # Atualizar interface
            self.root.after(0, lambda: self.atualizar_interface_dados(dados))
            
            # Mostrar resultado
            if dados['sucesso_atualizacao']:
                self.root.after(0, lambda: messagebox.showinfo(
                    "✅ Atualização", 
                    f"Dados atualizados com sucesso!\n\n"
                    f"Taxa Selic: {dados['taxa_selic_anual']:.2f}% a.a.\n"
                    f"Data referência: {dados['data_referencia']}"
                ))
            else:
                self.root.after(0, lambda: messagebox.showwarning(
                    "⚠️ Aviso", 
                    "Não foi possível atualizar os dados.\n\n"
                    "Usando dados em cache ou padrão."
                ))
        
        thread = threading.Thread(target=atualizar_async)
        thread.daemon = True
        thread.start()
    
    # Métodos de evento
    def on_modalidade_change(self, event=None):
        """Quando modalidade muda"""
        modalidade_nome = self.modalidade_var.get()
        modalidade = self.modalidades.get(modalidade_nome)
        
        if modalidade:
            self.perc_entry.delete(0, tk.END)
            self.perc_entry.insert(0, str(modalidade.percentual_cdi))
        
        self.atualizar_taxa_modalidade()
    
    def on_percentual_change(self, event=None):
        """Quando percentual muda"""
        self.atualizar_taxa_modalidade()
    
    def atualizar_taxa_modalidade(self):
        """Atualiza taxa baseada no percentual"""
        try:
            perc_text = self.perc_entry.get()
            if perc_text:
                percentual = float(perc_text)
                dados = self.gerenciador_dados.obter_dados()
                taxa_mensal = dados['taxa_selic_mensal'] * (percentual / 100)
                self.taxa_label.config(
                    text=f"Taxa mensal: {taxa_mensal*100:.4f}%",
                    fg=TemaOtimizado.CORES['sucesso']
                )
            else:
                self.taxa_label.config(
                    text="Taxa mensal: Configure o %",
                    fg=TemaOtimizado.CORES['texto_claro']
                )
        except ValueError:
            self.taxa_label.config(
                text="Taxa mensal: Valor inválido",
                fg=TemaOtimizado.CORES['destaque']
            )
    
    def _validar_percentual_cdi(self):
        """Função auxiliar para validar percentual CDI (elimina duplicação)"""
        perc_text = self.perc_entry.get()
        if not perc_text:
            raise ValueError("Configure o percentual do CDI")
        
        try:
            percentual_cdi = float(perc_text)
        except ValueError:
            raise ValueError("Percentual CDI deve ser um número válido")
        
        if percentual_cdi <= 0 or percentual_cdi > 300:
            raise ValueError("Percentual CDI deve estar entre 0% e 300%")
        
        dados_bc = self.gerenciador_dados.obter_dados()
        taxa_mensal = dados_bc['taxa_selic_mensal'] * (percentual_cdi / 100)
        
        if taxa_mensal <= 0:
            raise ValueError("Taxa de rendimento deve ser positiva")
        
        return percentual_cdi, taxa_mensal
    
    def calcular(self):
        """Executa cálculo principal"""
        try:
            # Verificar modo de cálculo
            if self.modo_calculo.get() == "normal":
                self.calcular_modo_normal()
            else:
                self.calcular_modo_reverso()
                
        except ValueError as e:
            messagebox.showerror("❌ Erro de Validação", str(e))
        except Exception as e:
            messagebox.showerror("❌ Erro", f"Erro inesperado:\n{str(e)}")
    
    def calcular_modo_normal(self):
        """Executa cálculo no modo normal (calcular rendimento)"""
        # Validar dados
        dados = self.validar_dados_normal()
        modalidade = self.modalidades[dados['modalidade']]
        
        # Simular
        resultados = self.simular_investimento(dados, modalidade)
        
        # Salvar dados da última simulação
        self.dados_ultima_simulacao = dados
        
        # Atualizar interface
        self.atualizar_dashboard_com_dados(dados, resultados, modalidade)
        self.gerar_relatorio_detalhado(dados, resultados, modalidade)
        
        # Mudar para aba dashboard
        self.notebook.select(0)
    
    def calcular_modo_reverso(self):
        """Executa cálculo no modo reverso (calcular valor necessário)"""
        # Validar dados do modo reverso
        dados = self.validar_dados_reverso()
        modalidade = self.modalidades[dados['modalidade']]
        
        # Calcular valor necessário
        resultado_reverso = self.calcular_valor_necessario(dados, modalidade)
        
        # Salvar dados da última simulação
        self.dados_ultima_simulacao = dados
        self.dados_ultima_simulacao['resultado_reverso'] = resultado_reverso
        
        # Atualizar dashboard com resultado reverso
        self.atualizar_dashboard_reverso(dados, resultado_reverso, modalidade)
        self.gerar_relatorio_reverso(dados, resultado_reverso, modalidade)
        
        # Mudar para aba dashboard
        self.notebook.select(0)
    
    def validar_dados_normal(self):
        """Valida dados de entrada do modo normal"""
        # Obter valores
        valor_inicial = self.formatador.parse_valor(self.valor_inicial_entry.get())
        aporte_mensal = self.formatador.parse_valor(self.aporte_entry.get())
        meta = self.formatador.parse_valor(self.meta_entry.get())
        
        # Validar percentual CDI usando função auxiliar
        percentual_cdi, taxa_mensal = self._validar_percentual_cdi()
        
        # Validações específicas do modo normal
        if valor_inicial <= 0:
            raise ValueError("Valor inicial deve ser positivo")
        if aporte_mensal < 0:
            raise ValueError("Aporte mensal não pode ser negativo")
        if meta <= valor_inicial:
            raise ValueError("Meta deve ser maior que valor inicial")
        
        return {
            'valor_inicial': valor_inicial,
            'aporte_mensal': aporte_mensal,
            'meta': meta,
            'percentual_cdi': percentual_cdi,
            'taxa_mensal': taxa_mensal,
            'modalidade': self.modalidade_var.get(),
            'considerar_ir': self.considerar_ir.get(),
            'considerar_inflacao': self.considerar_inflacao.get(),
            'modo': 'normal'
        }
    
    def validar_dados_reverso(self):
        """Valida dados de entrada do modo reverso"""
        # Obter valores
        rendimento_desejado = self.formatador.parse_valor(self.rendimento_desejado_entry.get())
        try:
            prazo_meses = int(self.prazo_entry.get()) if self.prazo_entry.get().strip() else 0
        except ValueError:
            raise ValueError("Prazo deve ser um número inteiro")
        aporte_mensal = self.formatador.parse_valor(self.aporte_reverso_entry.get())
        
        # Validar percentual CDI usando função auxiliar
        percentual_cdi, taxa_mensal = self._validar_percentual_cdi()
        
        # Validações específicas do modo reverso
        if rendimento_desejado <= 0:
            raise ValueError("Rendimento desejado deve ser positivo")
        if prazo_meses <= 0 or prazo_meses > 600:
            raise ValueError("Prazo deve estar entre 1 e 600 meses")
        if aporte_mensal < 0:
            raise ValueError("Aporte mensal não pode ser negativo")
        
        return {
            'rendimento_desejado': rendimento_desejado,
            'prazo_meses': prazo_meses,
            'aporte_mensal': aporte_mensal,
            'percentual_cdi': percentual_cdi,
            'taxa_mensal': taxa_mensal,
            'modalidade': self.modalidade_var.get(),
            'considerar_ir': self.considerar_ir.get(),
            'considerar_inflacao': self.considerar_inflacao.get(),
            'modo': 'reverso'
        }
    
    def calcular_valor_necessario(self, dados, modalidade):
        """Calcula o valor inicial necessário para atingir o rendimento desejado"""
        rendimento_desejado = dados['rendimento_desejado']
        taxa_mensal = dados['taxa_mensal']
        prazo_meses = dados['prazo_meses']
        aporte_mensal = dados['aporte_mensal']
        
        # Fator de desconto do IR se aplicável
        fator_ir = 1.0
        if dados['considerar_ir'] and modalidade.tem_ir:
            # Estimar IR médio baseado no prazo
            dias_totais = prazo_meses * 30
            ir_estimado = CalculadoraIR.calcular_ir(1.0, dias_totais)  # IR sobre 1 real
            fator_ir = 1 - ir_estimado
        
        # Taxa líquida após IR
        taxa_liquida = taxa_mensal * fator_ir
        
        if taxa_liquida <= 0:
            raise ValueError("Taxa líquida deve ser positiva")
        
        # Cálculo iterativo para encontrar o valor inicial necessário
        # Começamos com uma estimativa e refinamos
        valor_inicial_estimado = rendimento_desejado / taxa_liquida
        
        # Considerando aportes mensais na equação
        if aporte_mensal > 0:
            # Ajustar considerando que aportes também geram rendimento
            # Valor futuro dos aportes: aporte * ((1+taxa)^n - 1) / taxa
            if taxa_liquida > 0:
                valor_futuro_aportes = aporte_mensal * (((1 + taxa_liquida) ** prazo_meses - 1) / taxa_liquida)
                # Rendimento dos aportes no último mês
                rendimento_aportes_ultimo_mes = valor_futuro_aportes * taxa_liquida / prazo_meses
                rendimento_necessario_capital = rendimento_desejado - rendimento_aportes_ultimo_mes
                valor_inicial_estimado = max(0, rendimento_necessario_capital / taxa_liquida)
        
        # Simular para verificar e ajustar
        melhor_valor = valor_inicial_estimado
        menor_diferenca = float('inf')
        
        # Busca binária para encontrar o valor exato
        valor_min = 0
        valor_max = max(valor_inicial_estimado * 3, rendimento_desejado * 100)  # Limite mais inteligente
        
        for iteracao in range(50):  # Máximo 50 iterações
            valor_teste = (valor_min + valor_max) / 2
            rendimento_simulado = self.simular_rendimento_mensal(valor_teste, dados, modalidade)
            
            diferenca = abs(rendimento_simulado - rendimento_desejado)
            
            if diferenca < menor_diferenca:
                menor_diferenca = diferenca
                melhor_valor = valor_teste
            
            # Critério de parada melhorado
            if diferenca < 1 or abs(valor_max - valor_min) < 1:  # Precisão de R$ 1,00 ou convergência
                break
            
            if rendimento_simulado < rendimento_desejado:
                valor_min = valor_teste
            else:
                valor_max = valor_teste
        
        # Validação final para garantir precisão
        if menor_diferenca > rendimento_desejado * 0.1:  # Erro maior que 10%
            raise ValueError("Não foi possível encontrar valor com precisão adequada. Tente ajustar os parâmetros.")
        
        return {
            'valor_inicial_necessario': melhor_valor,
            'rendimento_mensal_previsto': self.simular_rendimento_mensal(melhor_valor, dados, modalidade),
            'valor_total_investido': melhor_valor + (aporte_mensal * prazo_meses),
            'diferenca_rendimento': menor_diferenca
        }
    
    def simular_rendimento_mensal(self, valor_inicial, dados, modalidade):
        """Simula rendimento mensal para um valor inicial dado"""
        saldo = valor_inicial
        taxa_mensal = dados['taxa_mensal']
        prazo_meses = dados['prazo_meses']
        aporte_mensal = dados['aporte_mensal']
        
        rendimentos_mensais = []
        
        for mes in range(prazo_meses):
            rendimento_bruto = saldo * taxa_mensal
            
            # Calcular IR se aplicável
            ir = 0
            if dados['considerar_ir'] and modalidade.tem_ir:
                ir = CalculadoraIR.calcular_ir(rendimento_bruto, mes * 30)
            
            rendimento_liquido = rendimento_bruto - ir
            rendimentos_mensais.append(rendimento_liquido)
            
            saldo += rendimento_liquido + aporte_mensal
        
        # Retornar rendimento médio dos últimos meses
        if rendimentos_mensais:
            # Média dos últimos 3 meses ou todos se menos de 3
            ultimos_meses = min(3, len(rendimentos_mensais))
            return sum(rendimentos_mensais[-ultimos_meses:]) / ultimos_meses
        
        return 0
    
    def simular_investimento(self, dados, modalidade):
        """Simula o investimento"""
        resultados = []
        saldo = dados['valor_inicial']
        meses = 0
        
        while saldo < dados['meta'] and meses < 600:
            rendimento = saldo * dados['taxa_mensal']
            
            # Calcular IR baseado na modalidade
            ir = 0
            if dados['considerar_ir'] and modalidade.tem_ir:
                ir = CalculadoraIR.calcular_ir(rendimento, meses * 30)
            
            saldo += rendimento - ir + dados['aporte_mensal']
            meses += 1
            
            resultados.append({
                'mes': meses,
                'saldo': saldo,
                'rendimento': rendimento,
                'ir': ir,
                'aporte': dados['aporte_mensal']
            })
        
        self.resultados_df = pd.DataFrame(resultados)
        return resultados
    
    def atualizar_dashboard_com_dados(self, dados, resultados, modalidade):
        """Atualiza dashboard com dados reais"""
        # Limpar dashboard
        for widget in self.dash_frame.winfo_children():
            widget.destroy()
        
        # Container otimizado
        dashboard_container = tk.Frame(self.dash_frame, bg=TemaOtimizado.CORES['fundo'])
        dashboard_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Grid de métricas 2x3
        self.criar_grid_metricas_otimizado(dashboard_container, dados, resultados, modalidade)
        
        # Resumo adicional
        self.criar_resumo_adicional(dashboard_container, dados, resultados, modalidade)
    
    def criar_grid_metricas_otimizado(self, parent, dados, resultados, modalidade):
        """Cria grid otimizado de métricas"""
        if not resultados:
            return
        
        # Calcular métricas
        meses = len(resultados)
        valor_final = resultados[-1]['saldo']
        total_investido = dados['valor_inicial'] + (dados['aporte_mensal'] * meses)
        total_rendimento = sum(r['rendimento'] for r in resultados)
        total_ir = sum(r['ir'] for r in resultados)
        rentabilidade = ((valor_final - total_investido) / total_investido) * 100
        
        # Grid container
        grid_container = tk.Frame(parent, bg=TemaOtimizado.CORES['fundo'])
        grid_container.pack(fill=tk.X, pady=(0, 15))
        
        # Configurar grid 2x3
        for i in range(3):
            grid_container.grid_columnconfigure(i, weight=1)
        
        # Cards de métricas
        self.criar_card_metrica_compacto(grid_container, "🎯 Meta",
                                        self.formatador.formatar_moeda(valor_final, True),
                                        f"{meses} meses", 0, 0, 'sucesso')
        
        anos = meses // 12
        meses_resto = meses % 12
        self.criar_card_metrica_compacto(grid_container, "⏱️ Prazo",
                                        f"{anos}a {meses_resto}m",
                                        f"{meses} meses", 0, 1, 'info')
        
        self.criar_card_metrica_compacto(grid_container, "📈 Rentabilidade",
                                        f"{rentabilidade:.1f}%",
                                        "total", 0, 2, 'primario')
        
        self.criar_card_metrica_compacto(grid_container, "💰 Investido",
                                        self.formatador.formatar_moeda(total_investido, True),
                                        "capital", 1, 0, 'secundario')
        
        self.criar_card_metrica_compacto(grid_container, "💸 Rendimento",
                                        self.formatador.formatar_moeda(total_rendimento, True),
                                        "bruto", 1, 1, 'secundario')
        
        self.criar_card_metrica_compacto(grid_container, "🧾 IR",
                                        self.formatador.formatar_moeda(total_ir, True),
                                        "imposto", 1, 2, 'aviso')
    
    def criar_card_metrica_compacto(self, parent, titulo, valor, descricao, row, col, cor):
        """Cria card de métrica compacto"""
        card_frame = tk.Frame(parent, 
                             bg=TemaOtimizado.CORES['card'],
                             relief='solid', bd=1)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Padding interno compacto
        content = tk.Frame(card_frame, bg=TemaOtimizado.CORES['card'])
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Título
        titulo_label = tk.Label(content, text=titulo,
                               font=TemaOtimizado.FONTES['pequeno'],
                               bg=TemaOtimizado.CORES['card'],
                               fg=TemaOtimizado.CORES['texto_claro'])
        titulo_label.pack(anchor='w')
        
        # Valor principal
        valor_label = tk.Label(content, text=valor,
                              font=('Segoe UI', 12, 'bold'),
                              bg=TemaOtimizado.CORES['card'],
                              fg=TemaOtimizado.CORES[cor])
        valor_label.pack(anchor='w')
        
        # Descrição
        desc_label = tk.Label(content, text=descricao,
                             font=TemaOtimizado.FONTES['pequeno'],
                             bg=TemaOtimizado.CORES['card'],
                             fg=TemaOtimizado.CORES['texto_claro'])
        desc_label.pack(anchor='w')
    
    def criar_resumo_adicional(self, parent, dados, resultados, modalidade):
        """Cria resumo adicional"""
        resumo_frame = tk.Frame(parent, 
                               bg=TemaOtimizado.CORES['card'],
                               relief='solid', bd=1)
        resumo_frame.pack(fill=tk.X)
        
        content = tk.Frame(resumo_frame, bg=TemaOtimizado.CORES['card'])
        content.pack(fill=tk.X, padx=15, pady=10)
        
        # Informações da modalidade
        info_text = f"Modalidade: {modalidade.nome} • Risco: {modalidade.risco} • Liquidez: {modalidade.liquidez_dias} dias"
        if modalidade.tem_ir:
            info_text += " • Com IR"
        else:
            info_text += " • Sem IR"
        
        info_label = tk.Label(content, text=info_text,
                             font=TemaOtimizado.FONTES['corpo'],
                             bg=TemaOtimizado.CORES['card'],
                             fg=TemaOtimizado.CORES['texto'])
        info_label.pack(anchor='w')
        
        # Descrição
        desc_label = tk.Label(content, text=modalidade.descricao,
                             font=TemaOtimizado.FONTES['pequeno'],
                             bg=TemaOtimizado.CORES['card'],
                             fg=TemaOtimizado.CORES['texto_claro'])
        desc_label.pack(anchor='w', pady=(3, 0))
    
    def atualizar_dashboard_reverso(self, dados, resultado_reverso, modalidade):
        """Atualiza dashboard com resultados do cálculo reverso"""
        # Limpar dashboard
        for widget in self.dash_frame.winfo_children():
            widget.destroy()
        
        # Container otimizado
        dashboard_container = tk.Frame(self.dash_frame, bg=TemaOtimizado.CORES['fundo'])
        dashboard_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título específico para modo reverso
        titulo = tk.Label(dashboard_container,
                         text="🎯 Resultado: Valor Necessário para Rendimento Desejado",
                         font=TemaOtimizado.FONTES['titulo'],
                         bg=TemaOtimizado.CORES['fundo'],
                         fg=TemaOtimizado.CORES['texto'])
        titulo.pack(anchor='w', pady=(0, 20))
        
        # Grid de métricas do modo reverso
        self.criar_grid_metricas_reverso(dashboard_container, dados, resultado_reverso, modalidade)
        
        # Resumo adicional para modo reverso
        self.criar_resumo_reverso(dashboard_container, dados, resultado_reverso, modalidade)
    
    def criar_grid_metricas_reverso(self, parent, dados, resultado_reverso, modalidade):
        """Cria grid de métricas para modo reverso"""
        # Grid container
        grid_container = tk.Frame(parent, bg=TemaOtimizado.CORES['fundo'])
        grid_container.pack(fill=tk.X, pady=(0, 15))
        
        # Configurar grid 2x3
        for i in range(3):
            grid_container.grid_columnconfigure(i, weight=1)
        
        # Cards de métricas específicas para modo reverso
        self.criar_card_metrica_compacto(grid_container, "💰 Valor Inicial Necessário",
                                        self.formatador.formatar_moeda(resultado_reverso['valor_inicial_necessario'], True),
                                        "investimento", 0, 0, 'primario')
        
        self.criar_card_metrica_compacto(grid_container, "📈 Rendimento Previsto",
                                        self.formatador.formatar_moeda(resultado_reverso['rendimento_mensal_previsto'], True),
                                        "por mês", 0, 1, 'sucesso')
        
        self.criar_card_metrica_compacto(grid_container, "⏱️ Prazo",
                                        f"{dados['prazo_meses']} meses",
                                        f"{dados['prazo_meses']//12}a {dados['prazo_meses']%12}m", 0, 2, 'info')
        
        self.criar_card_metrica_compacto(grid_container, "🎯 Rendimento Desejado",
                                        self.formatador.formatar_moeda(dados['rendimento_desejado'], True),
                                        "objetivo", 1, 0, 'destaque')
        
        self.criar_card_metrica_compacto(grid_container, "💸 Total Investido",
                                        self.formatador.formatar_moeda(resultado_reverso['valor_total_investido'], True),
                                        "capital + aportes", 1, 1, 'secundario')
        
        precisao = resultado_reverso['diferenca_rendimento']
        cor_precisao = 'sucesso' if precisao < 50 else 'aviso' if precisao < 200 else 'destaque'
        self.criar_card_metrica_compacto(grid_container, "🎯 Precisão",
                                        f"±{self.formatador.formatar_moeda(precisao, True)}",
                                        "diferença", 1, 2, cor_precisao)
    
    def criar_resumo_reverso(self, parent, dados, resultado_reverso, modalidade):
        """Cria resumo adicional para modo reverso"""
        resumo_frame = tk.Frame(parent, 
                               bg=TemaOtimizado.CORES['card'],
                               relief='solid', bd=1)
        resumo_frame.pack(fill=tk.X)
        
        content = tk.Frame(resumo_frame, bg=TemaOtimizado.CORES['card'])
        content.pack(fill=tk.X, padx=15, pady=10)
        
        # Informações da modalidade
        info_text = f"Modalidade: {modalidade.nome} • {dados['percentual_cdi']:.1f}% CDI • Risco: {modalidade.risco}"
        if modalidade.tem_ir:
            info_text += " • Com IR"
        else:
            info_text += " • Sem IR"
        
        info_label = tk.Label(content, text=info_text,
                             font=TemaOtimizado.FONTES['corpo'],
                             bg=TemaOtimizado.CORES['card'],
                             fg=TemaOtimizado.CORES['texto'])
        info_label.pack(anchor='w')
        
        # Instruções adicionais
        instrucoes = tk.Label(content, 
                             text=f"💡 Para obter R$ {dados['rendimento_desejado']:,.2f} mensais, invista R$ {resultado_reverso['valor_inicial_necessario']:,.2f} inicialmente",
                             font=TemaOtimizado.FONTES['pequeno'],
                             bg=TemaOtimizado.CORES['card'],
                             fg=TemaOtimizado.CORES['info'],
                             wraplength=600)
        instrucoes.pack(anchor='w', pady=(5, 0))
        
        # Aportes adicionais se houver
        if dados['aporte_mensal'] > 0:
            aportes_text = f"+ R$ {dados['aporte_mensal']:,.2f} de aportes mensais por {dados['prazo_meses']} meses"
            aportes_label = tk.Label(content, text=aportes_text,
                                   font=TemaOtimizado.FONTES['pequeno'],
                                   bg=TemaOtimizado.CORES['card'],
                                   fg=TemaOtimizado.CORES['secundario'])
            aportes_label.pack(anchor='w', pady=(2, 0))
    
    def gerar_relatorio_reverso(self, dados, resultado_reverso, modalidade):
        """Gera relatório detalhado para modo reverso"""
        # Obter dados atuais do BC
        dados_bc = self.gerenciador_dados.obter_dados()
        
        # Habilitar edição do texto
        self.relatorio_text.config(state=tk.NORMAL)
        self.relatorio_text.delete(1.0, tk.END)
        
        # Gerar relatório
        relatorio = "=" * 80 + "\n"
        relatorio += "         RELATÓRIO DE CÁLCULO REVERSO - VALOR NECESSÁRIO v4.1\n"
        relatorio += "=" * 80 + "\n\n"
        
        # Informações gerais
        relatorio += "📊 INFORMAÇÕES GERAIS:\n"
        relatorio += f"   • Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n"
        relatorio += f"   • Modo de Cálculo: Valor Necessário para Rendimento Desejado\n"
        relatorio += f"   • Modalidade: {modalidade.nome}\n"
        relatorio += f"   • Percentual CDI: {dados['percentual_cdi']:.1f}%\n"
        relatorio += f"   • Risco: {modalidade.risco}\n"
        relatorio += f"   • Liquidez: {modalidade.liquidez_dias} dias\n"
        relatorio += f"   • Prazo da Simulação: {dados['prazo_meses']} meses\n"
        configs = []
        if dados['considerar_ir']:
            configs.append("IR")
        if dados['considerar_inflacao']:
            configs.append("Inflação")
        relatorio += f"   • Configurações: {', '.join(configs) if configs else 'Padrão'}\n\n"
        
        # Dados do Banco Central
        relatorio += "🏛️ DADOS DO BANCO CENTRAL:\n"
        relatorio += f"   • Taxa Selic: {dados_bc['taxa_selic_anual']:.2f}% a.a.\n"
        relatorio += f"   • Data referência: {dados_bc['data_referencia']}\n"
        if dados_bc['ultima_atualizacao']:
            relatorio += f"   • Última atualização: {dados_bc['ultima_atualizacao'].strftime('%d/%m/%Y às %H:%M:%S')}\n"
        relatorio += f"   • Status: {'Atualizado' if dados_bc['sucesso_atualizacao'] else 'Cache/Padrão'}\n\n"
        
        # Objetivo da simulação
        relatorio += "🎯 OBJETIVO DA SIMULAÇÃO:\n"
        relatorio += f"   • Rendimento Mensal Desejado: {self.formatador.formatar_moeda(dados['rendimento_desejado'])}\n"
        relatorio += f"   • Prazo para Alcançar: {dados['prazo_meses']} meses ({dados['prazo_meses']//12} anos e {dados['prazo_meses']%12} meses)\n"
        relatorio += f"   • Aportes Mensais Adicionais: {self.formatador.formatar_moeda(dados['aporte_mensal'])}\n\n"
        
        # Resultado calculado
        relatorio += "💰 RESULTADO CALCULADO:\n"
        relatorio += f"   • Valor Inicial Necessário: {self.formatador.formatar_moeda(resultado_reverso['valor_inicial_necessario'])}\n"
        relatorio += f"   • Rendimento Mensal Previsto: {self.formatador.formatar_moeda(resultado_reverso['rendimento_mensal_previsto'])}\n"
        relatorio += f"   • Total de Capital Investido: {self.formatador.formatar_moeda(resultado_reverso['valor_total_investido'])}\n"
        relatorio += f"   • Precisão do Cálculo: ±{self.formatador.formatar_moeda(resultado_reverso['diferenca_rendimento'])}\n\n"
        
        # Análise de viabilidade
        relatorio += "📈 ANÁLISE DE VIABILIDADE:\n"
        taxa_mensal_pct = dados['taxa_mensal'] * 100
        relatorio += f"   • Taxa Mensal da Modalidade: {taxa_mensal_pct:.4f}%\n"
        rentabilidade_anual = ((1 + dados['taxa_mensal']) ** 12 - 1) * 100
        relatorio += f"   • Rentabilidade Anual Estimada: {rentabilidade_anual:.2f}%\n"
        
        if resultado_reverso['valor_inicial_necessario'] > 1000000:
            relatorio += f"   • ⚠️ ATENÇÃO: Valor alto necessário (acima de R$ 1 milhão)\n"
        elif resultado_reverso['valor_inicial_necessario'] < 1000:
            relatorio += f"   • ✅ Valor acessível para investimento inicial\n"
        else:
            relatorio += f"   • ✅ Valor moderado para investimento inicial\n"
        
        # Comparativo com outras modalidades
        relatorio += "\n⚖️ COMPARATIVO COM OUTRAS MODALIDADES:\n"
        if dados['percentual_cdi'] < 100:
            relatorio += f"   • Com CDI 100%: Precisaria de ~{resultado_reverso['valor_inicial_necessario'] * (dados['percentual_cdi']/100):,.0f}\n"
        if dados['percentual_cdi'] != 105:
            relatorio += f"   • Com CDI 105%: Precisaria de ~{resultado_reverso['valor_inicial_necessario'] * (dados['percentual_cdi']/105):,.0f}\n"
        
        # Projeção temporal
        relatorio += "\n📅 PROJEÇÃO TEMPORAL:\n"
        relatorio += f"   • Início do Investimento: {datetime.now().strftime('%m/%Y')}\n"
        data_final = datetime.now() + timedelta(days=dados['prazo_meses']*30)
        relatorio += f"   • Meta Alcançada em: {data_final.strftime('%m/%Y')}\n"
        relatorio += f"   • Rendimento Total no Período: {self.formatador.formatar_moeda(resultado_reverso['rendimento_mensal_previsto'] * dados['prazo_meses'])}\n"
        
        relatorio += "\n" + "=" * 80 + "\n"
        relatorio += "📌 OBSERVAÇÕES IMPORTANTES:\n"
        relatorio += "   • Este cálculo é uma estimativa baseada na taxa atual\n"
        relatorio += "   • Taxas de juros podem variar ao longo do tempo\n"
        relatorio += "   • IR calculado conforme tabela regressiva oficial\n"
        relatorio += "   • Considere diversificação de investimentos\n"
        relatorio += "   • Consulte sempre um consultor financeiro qualificado\n"
        relatorio += "   • Simulação não considera inflação ou outros fatores externos\n"
        relatorio += "=" * 80
        
        # Inserir no campo de texto
        self.relatorio_text.insert(tk.END, relatorio)
        self.relatorio_text.config(state=tk.DISABLED)
    
    def gerar_relatorio_detalhado(self, dados, resultados, modalidade):
        """Gera relatório detalhado completo"""
        if not resultados:
            return
        
        # Calcular métricas
        meses = len(resultados)
        valor_final = resultados[-1]['saldo']
        total_investido = dados['valor_inicial'] + (dados['aporte_mensal'] * meses)
        total_rendimento = sum(r['rendimento'] for r in resultados)
        total_ir = sum(r['ir'] for r in resultados)
        rendimento_liquido = total_rendimento - total_ir
        
        # Obter dados atuais do BC
        dados_bc = self.gerenciador_dados.obter_dados()
        
        # Habilitar edição do texto
        self.relatorio_text.config(state=tk.NORMAL)
        self.relatorio_text.delete(1.0, tk.END)
        
        # Gerar relatório
        relatorio = "=" * 80 + "\n"
        relatorio += "            RELATÓRIO DETALHADO DE SIMULAÇÃO DE INVESTIMENTO v4.1\n"
        relatorio += "=" * 80 + "\n\n"
        
        # Informações gerais
        relatorio += "📊 INFORMAÇÕES GERAIS:\n"
        relatorio += f"   • Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n"
        relatorio += f"   • Modalidade: {modalidade.nome}\n"
        relatorio += f"   • Percentual CDI: {dados['percentual_cdi']:.1f}%\n"
        relatorio += f"   • Risco: {modalidade.risco}\n"
        relatorio += f"   • Liquidez: {modalidade.liquidez_dias} dias\n"
        relatorio += f"   • Configurações: "
        configs = []
        if dados['considerar_ir']:
            configs.append("IR")
        if dados['considerar_inflacao']:
            configs.append("Inflação")
        relatorio += ", ".join(configs) if configs else "Padrão"
        relatorio += "\n\n"
        
        # Dados do Banco Central
        relatorio += "🏛️ DADOS DO BANCO CENTRAL:\n"
        relatorio += f"   • Taxa Selic: {dados_bc['taxa_selic_anual']:.2f}% a.a.\n"
        relatorio += f"   • Data referência: {dados_bc['data_referencia']}\n"
        if dados_bc['ultima_atualizacao']:
            relatorio += f"   • Última atualização: {dados_bc['ultima_atualizacao'].strftime('%d/%m/%Y às %H:%M:%S')}\n"
        relatorio += f"   • Status: {'Atualizado' if dados_bc['sucesso_atualizacao'] else 'Cache/Padrão'}\n\n"
        
        # Resumo financeiro
        relatorio += "💰 RESUMO FINANCEIRO:\n"
        relatorio += f"   • Valor Inicial: {self.formatador.formatar_moeda(dados['valor_inicial'])}\n"
        relatorio += f"   • Aporte Mensal: {self.formatador.formatar_moeda(dados['aporte_mensal'])}\n"
        relatorio += f"   • Meta: {self.formatador.formatar_moeda(dados['meta'])}\n"
        relatorio += f"   • Prazo: {meses} meses ({meses//12} anos e {meses%12} meses)\n"
        relatorio += f"   • Valor Final: {self.formatador.formatar_moeda(valor_final)}\n"
        relatorio += f"   • Total Investido: {self.formatador.formatar_moeda(total_investido)}\n"
        relatorio += f"   • Rendimento Bruto: {self.formatador.formatar_moeda(total_rendimento)}\n"
        relatorio += f"   • IR Total: {self.formatador.formatar_moeda(total_ir)}\n"
        relatorio += f"   • Rendimento Líquido: {self.formatador.formatar_moeda(rendimento_liquido)}\n\n"
        
        # Análise de performance
        rentabilidade = (rendimento_liquido / total_investido) * 100
        relatorio += "📈 ANÁLISE DE PERFORMANCE:\n"
        relatorio += f"   • Rentabilidade Total: {rentabilidade:.2f}%\n"
        relatorio += f"   • Taxa Mensal Aplicada: {dados['taxa_mensal']*100:.4f}%\n"
        relatorio += f"   • Multiplicador: {valor_final/dados['valor_inicial']:.2f}x\n"
        relatorio += f"   • Tempo para dobrar: {np.log(2) / np.log(1 + dados['taxa_mensal']):.0f} meses\n\n"
        
        # Características da modalidade
        relatorio += "🎯 CARACTERÍSTICAS DA MODALIDADE:\n"
        relatorio += f"   • Descrição: {modalidade.descricao}\n"
        relatorio += f"   • Tributação IR: {'Sim' if modalidade.tem_ir else 'Não'}\n"
        relatorio += f"   • Carência: {modalidade.liquidez_dias} dias\n"
        relatorio += f"   • Categoria de Risco: {modalidade.risco}\n"
        if modalidade.tem_ir:
            aliquota_ir = "22,5%" if meses * 30 <= 180 else "20%" if meses * 30 <= 360 else "17,5%" if meses * 30 <= 720 else "15%"
            relatorio += f"   • Alíquota IR aplicada: {aliquota_ir}\n"
        relatorio += "\n"
        
        # Evolução mensal (últimos 12 meses ou todos se menos de 12)
        qtd_meses_mostrar = min(12, len(resultados))
        relatorio += f"📊 EVOLUÇÃO MENSAL (Últimos {qtd_meses_mostrar} meses):\n"
        relatorio += "-" * 80 + "\n"
        relatorio += f"{'Mês':>4} | {'Saldo':>20} | {'Rendimento':>15} | {'IR':>12} | {'Aporte':>15}\n"
        relatorio += "-" * 80 + "\n"
        
        inicio = max(0, len(resultados) - 12)
        for i in range(inicio, len(resultados)):
            r = resultados[i]
            saldo_fmt = self.formatador.formatar_moeda(r['saldo'])
            rend_fmt = self.formatador.formatar_moeda(r['rendimento'])
            ir_fmt = self.formatador.formatar_moeda(r['ir'])
            aporte_fmt = self.formatador.formatar_moeda(r['aporte'])
            relatorio += f"{r['mes']:>4} | {saldo_fmt:>20} | {rend_fmt:>15} | {ir_fmt:>12} | {aporte_fmt:>15}\n"
        
        # Análise comparativa
        relatorio += "\n" + "⚖️ ANÁLISE COMPARATIVA:\n"
        relatorio += f"   • VS Poupança (70% CDI): Você ganha {(dados['percentual_cdi'] - 70):.1f} pontos percentuais\n"
        relatorio += f"   • VS CDI 100%: Você ganha {(dados['percentual_cdi'] - 100):.1f} pontos percentuais\n"
        
        # Cenário de melhoria
        if dados['percentual_cdi'] < 120:
            relatorio += f"   • Melhorando para CDI 120%: Economizaria ~{((np.log(dados['meta'] / dados['valor_inicial']) / np.log(1 + dados_bc['taxa_selic_mensal'] * 1.2)) - meses):.0f} meses\n"
        
        relatorio += "\n" + "=" * 80 + "\n"
        relatorio += "📌 OBSERVAÇÕES:\n"
        relatorio += "   • Simulação baseada na taxa Selic atual do Banco Central\n"
        relatorio += "   • Dados atualizados automaticamente a cada 12 horas\n"
        relatorio += "   • Valores sujeitos a oscilações do mercado financeiro\n"
        relatorio += "   • IR calculado conforme tabela regressiva oficial\n"
        relatorio += "   • Consulte sempre um consultor financeiro qualificado\n"
        relatorio += "=" * 80
        
        # Inserir no campo de texto
        self.relatorio_text.insert(tk.END, relatorio)
        self.relatorio_text.config(state=tk.DISABLED)
    
    def exportar_relatorio(self):
        """Exporta relatório em arquivo TXT"""
        conteudo = self.relatorio_text.get(1.0, tk.END).strip()
        if not conteudo or "Execute uma simulação" in conteudo:
            messagebox.showwarning("⚠️ Aviso", "Execute uma simulação primeiro para gerar o relatório!")
            return
        
        # Diálogo para salvar arquivo
        arquivo = filedialog.asksaveasfilename(
            title="Salvar Relatório Detalhado",
            defaultextension=".txt",
            filetypes=[
                ("Arquivos de Texto", "*.txt"),
                ("Todos os arquivos", "*.*")
            ],
            initialfile=f"relatorio_investimento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if arquivo:
            try:
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                messagebox.showinfo("✅ Sucesso", f"Relatório exportado com sucesso!\n\nArquivo: {arquivo}")
            except Exception as e:
                messagebox.showerror("❌ Erro", f"Erro ao exportar relatório:\n{str(e)}")
    
    def copiar_relatorio(self):
        """Copia relatório para área de transferência"""
        conteudo = self.relatorio_text.get(1.0, tk.END).strip()
        if not conteudo or "Execute uma simulação" in conteudo:
            messagebox.showwarning("⚠️ Aviso", "Execute uma simulação primeiro para gerar o relatório!")
            return
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(conteudo)
            messagebox.showinfo("✅ Sucesso", "Relatório copiado para área de transferência!")
        except Exception as e:
            messagebox.showerror("❌ Erro", f"Erro ao copiar relatório:\n{str(e)}")
    
    def comparacao_rapida(self, modalidades_nomes):
        """Executa comparação rápida entre modalidades"""
        try:
            # Obter valores atuais do formulário
            valor_inicial = self.formatador.parse_valor(self.valor_inicial_entry.get())
            aporte_mensal = self.formatador.parse_valor(self.aporte_entry.get())
            meta = self.formatador.parse_valor(self.meta_entry.get())
            
            dados_bc = self.gerenciador_dados.obter_dados()
            resultados_comp = []
            
            for modalidade_nome in modalidades_nomes:
                if modalidade_nome in self.modalidades:
                    modalidade = self.modalidades[modalidade_nome]
                    taxa_mensal = dados_bc['taxa_selic_mensal'] * (modalidade.percentual_cdi / 100)
                    
                    # Simular
                    saldo = valor_inicial
                    meses = 0
                    total_ir = 0
                    
                    while saldo < meta and meses < 600:
                        rendimento = saldo * taxa_mensal
                        ir = CalculadoraIR.calcular_ir(rendimento, meses * 30) if modalidade.tem_ir else 0
                        total_ir += ir
                        saldo += rendimento - ir + aporte_mensal
                        meses += 1
                    
                    resultados_comp.append({
                        'nome': modalidade_nome,
                        'meses': meses,
                        'valor_final': saldo,
                        'total_ir': total_ir,
                        'risco': modalidade.risco
                    })
            
            # Mostrar comparativo
            self.mostrar_comparativo(resultados_comp)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na comparação: {str(e)}")
    
    def mostrar_comparativo(self, resultados_comp):
        """Mostra comparativo na aba correspondente"""
        # Limpar aba comparativo
        for widget in self.comparativo_frame.winfo_children():
            widget.destroy()
        
        # Container
        comp_container = tk.Frame(self.comparativo_frame, bg=TemaOtimizado.CORES['fundo'])
        comp_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo = tk.Label(comp_container, text="⚖️ Comparativo de Modalidades",
                         font=TemaOtimizado.FONTES['titulo'],
                         bg=TemaOtimizado.CORES['fundo'],
                         fg=TemaOtimizado.CORES['texto'])
        titulo.pack(anchor='w', pady=(0, 15))
        
        # Cards de comparação
        for i, resultado in enumerate(resultados_comp):
            self.criar_card_comparativo(comp_container, resultado, i)
        
        # Mudar para aba comparativo
        self.notebook.select(2)
    
    def criar_card_comparativo(self, parent, resultado, indice):
        """Cria card de comparativo"""
        card = tk.Frame(parent, 
                       bg=TemaOtimizado.CORES['card'],
                       relief='solid', bd=1)
        card.pack(fill=tk.X, pady=5)
        
        content = tk.Frame(card, bg=TemaOtimizado.CORES['card'])
        content.pack(fill=tk.X, padx=15, pady=10)
        
        # Header
        header_frame = tk.Frame(content, bg=TemaOtimizado.CORES['card'])
        header_frame.pack(fill=tk.X)
        
        # Posição
        pos_label = tk.Label(header_frame, text=f"{indice + 1}º",
                            font=('Segoe UI', 14, 'bold'),
                            bg=TemaOtimizado.CORES['card'],
                            fg=TemaOtimizado.CORES['primario'])
        pos_label.pack(side=tk.LEFT)
        
        # Nome
        nome_label = tk.Label(header_frame, text=resultado['nome'],
                             font=TemaOtimizado.FONTES['subtitulo'],
                             bg=TemaOtimizado.CORES['card'],
                             fg=TemaOtimizado.CORES['texto'])
        nome_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Risco
        risco_label = tk.Label(header_frame, text=f"Risco: {resultado['risco']}",
                              font=TemaOtimizado.FONTES['pequeno'],
                              bg=TemaOtimizado.CORES['card'],
                              fg=TemaOtimizado.CORES['texto_claro'])
        risco_label.pack(side=tk.RIGHT)
        
        # Métricas
        metricas_frame = tk.Frame(content, bg=TemaOtimizado.CORES['card'])
        metricas_frame.pack(fill=tk.X, pady=(10, 0))
        
        anos = resultado['meses'] // 12
        meses_resto = resultado['meses'] % 12
        
        metricas_text = f"Prazo: {anos}a {meses_resto}m • "
        metricas_text += f"Valor Final: {self.formatador.formatar_moeda(resultado['valor_final'], True)} • "
        metricas_text += f"IR: {self.formatador.formatar_moeda(resultado['total_ir'], True)}"
        
        metricas_label = tk.Label(metricas_frame, text=metricas_text,
                                 font=TemaOtimizado.FONTES['corpo'],
                                 bg=TemaOtimizado.CORES['card'],
                                 fg=TemaOtimizado.CORES['texto'])
        metricas_label.pack(anchor='w')
    
    def comparar_modalidades(self):
        """Compara todas as modalidades principais"""
        modalidades_principais = ['Poupança', 'CDI 105%', 'Tesouro Selic', 'LCI/LCA', 'Renda Variável']
        self.comparacao_rapida(modalidades_principais)
    
    def limpar_formulario(self):
        """Limpa o formulário baseado no modo atual"""
        # Resetar para modo normal
        self.modo_calculo.set("normal")
        self.alternar_modo_calculo()
        
        # Limpar campos do modo normal (que agora estão criados)
        if hasattr(self, 'valor_inicial_entry') and self.valor_inicial_entry:
            self.valor_inicial_entry.delete(0, tk.END)
            self.valor_inicial_entry.insert(0, "30.000,00")
        
        if hasattr(self, 'aporte_entry') and self.aporte_entry:
            self.aporte_entry.delete(0, tk.END)
            self.aporte_entry.insert(0, "2.500,00")
        
        if hasattr(self, 'meta_entry') and self.meta_entry:
            self.meta_entry.delete(0, tk.END)
            self.meta_entry.insert(0, "500.000,00")
        
        # Limpar percentual CDI
        if hasattr(self, 'perc_entry') and self.perc_entry:
            self.perc_entry.delete(0, tk.END)
            self.perc_entry.insert(0, "105.0")
        
        # Resetar modalidade
        self.modalidade_var.set("CDI 105%")
        
        # Limpar resultados
        self.criar_dashboard_inicial()
        for widget in self.comparativo_frame.winfo_children():
            widget.destroy()
        
        # Limpar relatório
        self.relatorio_text.config(state=tk.NORMAL)
        self.relatorio_text.delete(1.0, tk.END)
        self.relatorio_text.insert(tk.END, 
                                  "RELATÓRIO DETALHADO\n\n" +
                                  "Execute uma simulação para gerar o relatório completo.\n\n" +
                                  "O relatório incluirá:\n" +
                                  "• Informações gerais da simulação\n" +
                                  "• Resumo financeiro completo\n" +
                                  "• Análise de performance\n" +
                                  "• Evolução mensal detalhada\n" +
                                  "• Dados exportáveis em TXT")
        self.relatorio_text.config(state=tk.DISABLED)

    def criar_tooltip(self, widget, texto):
        """Cria tooltip para um widget com melhor gestão de memória"""
        def mostrar_tooltip(event):
            # Evitar múltiplos tooltips
            if hasattr(widget, 'tooltip') and widget.tooltip and widget.tooltip.winfo_exists():
                return
                
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg='#1e293b')
            
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + 25
            tooltip.geometry(f"+{x}+{y}")
            
            label = tk.Label(tooltip, text=texto,
                           font=TemaOtimizado.FONTES['pequeno'],
                           bg='#1e293b', fg='white',
                           padx=8, pady=4)
            label.pack()
            
            widget.tooltip = tooltip
            
            # Auto-destruir após 5 segundos para evitar vazamentos
            tooltip.after(5000, lambda: esconder_tooltip(None))
            
        def esconder_tooltip(event):
            if hasattr(widget, 'tooltip') and widget.tooltip:
                try:
                    if widget.tooltip.winfo_exists():
                        widget.tooltip.destroy()
                except tk.TclError:
                    pass  # Widget já foi destruído
                finally:
                    widget.tooltip = None
        
        widget.bind('<Enter>', mostrar_tooltip)
        widget.bind('<Leave>', esconder_tooltip)



def main():
    """Função principal"""
    try:
        root = tk.Tk()
        app = SimuladorOtimizado(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("❌ Erro Fatal", f"Erro ao iniciar aplicação:\n{str(e)}")

if __name__ == "__main__":
    main() 