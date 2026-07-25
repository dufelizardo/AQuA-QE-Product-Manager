# North Star Framework

> Baseado no North Star Framework, popularizado por Sean Ellis e sistematizado por John Cutler (Amplitude).

## O que é

Um framework para alinhar times de produto em torno de uma única métrica — a **North Star Metric (NSM)** — que captura o valor central que o produto entrega aos clientes, de forma que também prediz sucesso de negócio a longo prazo.

## Características de uma boa North Star Metric

- **Expressa valor para o cliente**, não apenas valor para o negócio (ex.: "número de viagens concluídas" em vez de "receita bruta").
- **Reflete a visão e a estratégia do produto** — conecta o dia a dia do time à direção de longo prazo.
- **É um indicador antecedente (leading indicator)** de resultado de negócio, não um indicador atrasado (lagging indicator) como receita ou lucro.
- **É mensurável de forma consistente e recorrente**, não um evento único.

## Métricas de entrada (input metrics)

A North Star Metric sozinha não é acionável — o framework a decompõe em métricas de entrada (input metrics), fatores que o time pode influenciar diretamente e que, juntos, movem a NSM (ex.: se a NSM é "documentos processados por semana", as métricas de entrada podem ser "número de novos usuários ativados" × "taxa de conclusão do fluxo principal").

## Armadilhas comuns (segundo o framework)

- Escolher uma métrica de vaidade (ex.: downloads, page views) que não reflete valor real entregue.
- Escolher uma métrica de negócio pura (ex.: receita) sem conexão direta com o comportamento do usuário.
- Definir a métrica antes de entender o job to be done do usuário (ver `jtbd.md`) — a métrica deve derivar do valor, não o contrário.

## Relevância para este agente

`generate_product_vision` usa este framework para orientar o campo `north_star_metric`: a métrica só é preenchida quando rastreável ao problema/job identificado na descoberta, nunca escolhida por ser "uma métrica comum do setor" — na ausência de base clara na fonte, o campo fica vazio e o agente sinaliza a lacuna (GR-M3, ver `../../docs/agent/guardrails.md`), em vez de sugerir uma métrica genérica.
