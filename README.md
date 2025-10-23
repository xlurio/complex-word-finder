# Complex Word Finder

Uma ferramenta de linha de comando para analisar palavras polissilábicas em textos em português brasileiro, contar sílabas e encontrar sinônimos.

## Características

- ✅ Análise de textos em português brasileiro
- 📊 Contagem precisa de sílabas usando regras fonéticas portuguesas
- 🔍 Busca automática de sinônimos online
- 📈 Ordenação por número de sílabas e frequência
- 💾 Múltiplos formatos de saída (tabela, JSON, CSV)
- 🎨 Interface colorida e intuitiva
- ⚡ Processamento eficiente com indicadores de progresso

## Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd complex-word-finder

# Instale as dependências
pip install -e .
```

## Uso

### Uso Básico

```bash
complex-word-finder texto.txt
```

### Opções Avançadas

```bash
# Definir número mínimo de sílabas (padrão: 3)
complex-word-finder texto.txt --min-syllables 4

# Salvar resultados em arquivo
complex-word-finder texto.txt --output resultados.json --format json

# Limitar número de palavras processadas
complex-word-finder texto.txt --limit 50

# Desativar busca de sinônimos
complex-word-finder texto.txt --no-synonyms

# Formato CSV para análise em planilha
complex-word-finder texto.txt --output dados.csv --format csv
```

### Formatos de Saída

- **table** (padrão): Tabela formatada no terminal
- **json**: Formato JSON estruturado
- **csv**: Formato CSV para planilhas

### Parâmetros

| Parâmetro | Descrição | Padrão |
|-----------|-----------|---------|
| `--min-syllables, -m` | Número mínimo de sílabas | 3 |
| `--output, -o` | Arquivo de saída | - |
| `--format` | Formato de saída (table/json/csv) | table |
| `--limit, -l` | Limite de palavras a processar | - |
| `--synonyms/--no-synonyms` | Buscar sinônimos | Ativado |

## Exemplos

### Análise Básica
```bash
complex-word-finder artigo.txt
```

Output:
```
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Word                ┃ Syllables ┃ Count ┃ Synonyms                                          ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ desenvolvimento     │         5 │     8 │ evolução, progresso, crescimento...               │
│ características     │         5 │     3 │ qualidades, propriedades, atributos...            │
│ responsabilidade    │         6 │     2 │ obrigação, compromisso, dever...                  │
└─────────────────────┴───────────┴───────┴───────────────────────────────────────────────────┘
```

### Análise com Saída em JSON
```bash
complex-word-finder artigo.txt --format json --output resultados.json
```

### Análise Focada em Palavras Complexas
```bash
complex-word-finder texto.txt --min-syllables 5 --limit 20
```

## Tecnologias

- **Click**: Interface de linha de comando
- **NLTK**: Processamento de linguagem natural
- **Pyphen**: Hifenização e contagem de sílabas
- **Rich**: Interface rica no terminal
- **BeautifulSoup**: Scraping para sinônimos
- **Requests**: Requisições HTTP

## Funcionamento

1. **Extração de Palavras**: Remove stopwords e mantém apenas palavras alfabéticas
2. **Análise de Sílabas**: Usa regras fonéticas portuguesas e algoritmos de hifenização
3. **Busca de Sinônimos**: Consulta fontes online respeitando rate limits
4. **Ordenação**: Por número de sílabas (decrescente) e depois por frequência
5. **Apresentação**: Tabela colorida com opções de export

## Limitações

- Conexão com internet necessária para busca de sinônimos
- Rate limiting implementado para ser respeitoso com as fontes online
- Precisão da contagem de sílabas pode variar para palavras muito especializadas

## Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.