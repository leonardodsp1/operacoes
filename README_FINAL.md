# Simulador de Investimentos

Simulador para análise de investimentos do mercado financeiro brasileiro com integração ao Banco Central.

## Funcionalidades

### Modos de Cálculo
- **Normal**: Calcular rendimento baseado no valor investido
- **Reverso**: Calcular valor necessário para atingir rendimento desejado

### Modalidades
- CDI (100% a 120%)
- Poupança
- Tesouro Selic/IPCA+
- LCI/LCA
- CRI/CRA
- Debêntures
- Ações e ETFs
- Fundos DI
- Personalizado

### Recursos
- Integração automática com API do Banco Central
- Cálculo de IR conforme tabela oficial
- Relatórios detalhados exportáveis
- Interface responsiva

## Instalação

```bash
pip install -r requirements_avancado.txt
```

## Execução

```bash
python simulador_otimizado.py
```

## Dependências

- Python 3.8+
- requests (API Banco Central)
- pandas (manipulação dados)
- numpy (cálculos)

## Observações

- Simulações baseadas em taxas atuais do Banco Central
- Valores sujeitos a oscilações do mercado
- Para fins educacionais e de planejamento
- Consulte um profissional antes de investir 