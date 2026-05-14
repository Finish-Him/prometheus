# 🎯 GEM 2.0 - Guia de Uso Rápido

## O Que é o GEM?

**GEM** (Global Evolutionary Model) é o sistema de IA do Prometheus para análise de apostas em Dota 2, especializado na Europa Pro League.

---

## 🚀 Quick Start

### 1. Usar com ChatGPT

1. Vá em https://chat.openai.com/gpts/editor
2. Clique "Create"
3. Em **Instructions**, cole o conteúdo de `GPT_Prometheus_config.md`
4. Em **Knowledge**, faça upload de:
   - `GEM_EPL_master.json`
   - `EPL_teams_database.json`
   - `EPL_heroes_meta.json`
   - `EPL_strategy_weights.json`
   - `draft_analyzer.json`
5. Salve e comece a usar!

### 2. Usar com Google Gemini

1. Vá em https://aistudio.google.com/
2. Clique "Create new prompt" → "Chat prompt"
3. Em **System Instructions**, cole o conteúdo de `GEM_Gemini_config.md`
4. Configure Temperature: 0.3-0.5
5. Adicione os JSONs como contexto
6. Comece a analisar!

### 3. Upload Pack

Para facilitar, use a pasta `upload_pack/` que contém:
- Todos os JSONs necessários
- `INSTRUCTIONS.md` - Prompt compacto

---

## 📋 Como Analisar uma Partida

### Passo 1: Informar os Times
```
Analisar: Team Spirit vs Gaimin Gladiators
```

### Passo 2: Passar o Draft
```
Radiant (Spirit): Morphling, Puck, Mars, Chen, Rubick
Dire (GG): Faceless Void, Storm Spirit, Primal Beast, Shadow Shaman, Tusk
```

### Passo 3: Receber Análise

O GEM vai retornar:
- Análise de timing de cada lineup
- Key matchups de lane
- Win conditions
- Previsões com % de confiança
- Recomendação de aposta (se edge > 3%)

---

## 📊 Formato de Análise

```
📊 ANÁLISE: [Time A] vs [Time B] | EPL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 RADIANT - [Time]:
[5 heróis]
⏱️ Timing: [Early/Mid/Late]
🎯 Win Condition: [Como ganham]

🔵 DIRE - [Time]:
[5 heróis]
⏱️ Timing: [Early/Mid/Late]
🎯 Win Condition: [Como ganham]

⚔️ MATCHUPS CHAVE:
• Mid: [Herói vs Herói] - [Vantagem]

📈 PREVISÕES:
| Mercado | Pick | Odds | Conf | Edge |
|---------|------|------|------|------|
| Winner  | X    | 1.XX | XX%  | X.X% |
| Kills   | O/U  | 1.XX | XX%  | X.X% |

💰 VALUE BET: [Se edge > 3% e conf > 78%]
⚠️ RISCOS: [Fatores de incerteza]
```

---

## 🎯 Regras de Aposta

| Parâmetro | Valor |
|-----------|-------|
| Confiança Mínima | 78% |
| Edge Mínimo | 3% |
| Kelly Fraction | 25% |
| Stake Máximo | 5% |
| Max Concurrent | 5 bets |

---

## 📁 Arquivos do GEM

| Arquivo | Função |
|---------|--------|
| `GEM_EPL_master.json` | Config principal, thresholds |
| `EPL_teams_database.json` | 13 times com perfis |
| `EPL_heroes_meta.json` | Tier list, power spikes |
| `EPL_strategy_weights.json` | Pesos de cálculo |
| `draft_analyzer.json` | Combos, counters |
| `conversation_memory.json` | Memória de sessão |
| `prediction_validation_log.json` | Tracking |

---

## 💡 Dicas

1. **Sempre passe o draft completo** - 5 heróis de cada lado
2. **Mencione a liga** - EPL, Hyper League, etc.
3. **Informe odds** - Se tiver, para cálculo de edge
4. **Acompanhe resultados** - Para o sistema aprender

---

*GEM 2.0 - Prometheus EPL Specialist*
